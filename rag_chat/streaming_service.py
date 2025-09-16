"""
Chat streaming service for real-time communication via Channels
"""

import asyncio
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from typing import Dict, Any, Optional
from . import models
import logging

logger = logging.getLogger(__name__)


class ChatStreamingService:
    def __init__(self):
        self.channel_layer = get_channel_layer()

    def send_chunk_to_group(self, session_id: int, chunk_data: Dict[str, Any]):
        """Send a chunk to all subscribers of a session"""
        group_name = f"chat_{session_id}"

        logger.debug(f"Sending chunk to group {group_name}: {chunk_data}")

        try:
            async_to_sync(self.channel_layer.group_send)(
                group_name, {"type": "chat.message.chunk", **chunk_data}
            )
        except Exception as e:
            logger.error(f"Error sending chunk to group {group_name}: {e}")

    def generate_streaming_response(
        self, message_id: int, query: str, similarity_threshold: Optional[float] = None
    ):
        """Generate response with streaming updates"""
        try:
            message = models.ChatMessage.objects.get(id=message_id)
            session = message.session

            # Send initial chunk to indicate processing started
            self.send_chunk_to_group(
                session.id,
                {"message_id": str(message_id), "content": "", "is_complete": False},
            )

            from . import services

            rag_service = services.RAGService()

            # Get search results first
            search_results = rag_service.semantic_search(
                query=query, similarity_threshold=similarity_threshold
            )

            # Generate streaming response
            full_response = ""
            token_count = 0

            for chunk in rag_service.generate_streaming_response_chunks(
                query, search_results
            ):
                full_response += chunk
                token_count += 1  # You'll need to implement proper token counting

                # Update message in database
                message.response = full_response
                message.tokens_used = token_count
                message.save()

                # Send chunk to subscribers
                self.send_chunk_to_group(
                    session.id,
                    {
                        "message_id": str(message_id),
                        "content": chunk,
                        "is_complete": False,
                        "tokens_used": token_count,
                    },
                )

            # Send completion message
            self.send_chunk_to_group(
                session.id,
                {
                    "message_id": str(message_id),
                    "content": "",
                    "is_complete": True,
                    "tokens_used": token_count,
                },
            )

        except Exception as e:
            logger.error(
                f"Error generating streaming response for message {message_id}: {e}"
            )
            # Send error to subscribers
            self.send_chunk_to_group(
                session.id,
                {
                    "message_id": str(message_id),
                    "content": "",
                    "is_complete": True,
                    "error": str(e),
                },
            )
            raise
