from django.conf import settings
import strawberry
import strawberry_django
from strawberry import auto, relay
from strawberry.scalars import JSON
from typing import List, Optional, Union, Any, TYPE_CHECKING, Sequence, AsyncGenerator

from strawberry_django.relay import DjangoListConnection
from . import models, services
import strawberry.experimental.pydantic
import strawberry.scalars
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async

from nucleus.types.user import User as UserType
from nucleus.permissions import IsSuperuser
from .permissions import CanUseRAGChat, CanStartChatSession, CanSendChatMessage
from .source_models import parse_sources
from strawberry import union
from nucleus.types.gamelog import GameLog as GameLogType
from character.types.character import Character as CharacterType
from place.types.place import Place as PlaceType
from item.types.item import Item as ItemType
from item.types.artifact import Artifact as ArtifactType
from association.types import Association as AssociationType
from race.types.race import Race as RaceType

# Import Django models for type annotations
from nucleus.models import GameLog
from character.models import Character
from place.models import Place
from item.models import Item, Artifact
from association.models import Association
from race.models import Race


# Subscription types for streaming
@strawberry.type
class ChatMessageChunk:
    session_id: str
    message_id: Optional[str] = None
    content: str
    is_complete: bool = False
    error: Optional[str] = None
    tokens_used: Optional[int] = None


@strawberry_django.type(models.ContentChunk)
class ContentChunkType(relay.Node):
    content_type: auto
    object_id: auto
    chunk_text: auto
    chunk_index: auto
    metadata: auto
    created_at: auto
    updated_at: auto


@strawberry_django.type(models.ChatSession)
class ChatSessionType(relay.Node):
    user: UserType
    title: auto
    created_at: auto
    updated_at: auto

    @strawberry_django.field
    def messages(self) -> List["ChatMessageType"]:
        return self.messages.all().order_by("created_at")


@strawberry_django.type(models.ChatMessage)
class ChatMessageType(relay.Node):
    session: "ChatSessionType"
    message: auto
    response: auto
    tokens_used: auto
    similarity_threshold: auto
    content_types_searched: auto
    created_at: auto

    # @strawberry_django.field
    # def sources(
    #     self,
    # ) -> Sequence[
    #     Union[
    #         GameLog,
    #         Character,
    #         Place,
    #         Item,
    #         Artifact,
    #         Race,
    #         Association,
    #     ]
    # ]:
    #     """Get the sources used for this chat message response."""
    #     # Access the actual model field data
    #     sources_data = getattr(self, "sources", None)
    #     if not sources_data:
    #         return []

    #     try:
    #         # Parse the sources from the stored JSON
    #         return parse_sources(sources_data).sources
    #     except Exception:
    #         # If parsing fails, return empty list
    #         return []


@strawberry_django.type(models.QueryCache)
class QueryCacheType(relay.Node):
    query_hash: auto
    query_text: auto
    response_data: auto
    tokens_saved: auto
    hit_count: auto
    expires_at: auto
    created_at: auto


# Content statistics type
@strawberry.type
class ContentStatsType:
    content_type: str
    chunk_count: int
    object_count: int
    processed_count: int


# Input types for mutations


@strawberry.input
class StartChatSessionInput:
    title: Optional[str] = None


@strawberry.input
class SendChatMessageInput:
    session_id: relay.GlobalID
    message: str
    similarity_threshold: Optional[float] = None


@strawberry.input
class ProcessContentInput:
    content_type: str
    object_id: str
    force_reprocess: Optional[bool] = False


# @strawberry.input
# class ProcessCustomContentInput:
#     title: str
#     content: str
#     object_id: Optional[str] = None
#     metadata: Optional[strawberry.scalars.JSON] = None


@strawberry.input
class ProcessAllContentInput:
    content_types: Optional[List[str]] = None
    force_reprocess: Optional[bool] = False
    limit: Optional[int] = None


# Output types for mutations


@strawberry.type
class SendChatMessagePayload:
    message: ChatMessageType
    session: ChatSessionType


@strawberry.type
class ProcessContentPayload:
    success: bool
    message: str
    task_id: Optional[str] = None
    chunks_created: Optional[int] = None


@strawberry.type
class ProcessAllContentPayload:
    success: bool
    message: str
    task_id: Optional[str] = None
    total_tasks: Optional[int] = None
    content_types: List[str]


# Query and Mutation classes


@strawberry.type
class RAGQuery:
    content_chunks: DjangoListConnection[ContentChunkType] = (
        strawberry_django.connection(permission_classes=[IsSuperuser])
    )
    query_cache: DjangoListConnection[QueryCacheType] = strawberry_django.connection(
        permission_classes=[IsSuperuser]
    )

    @strawberry_django.connection(
        DjangoListConnection[ChatSessionType], permission_classes=[CanUseRAGChat]
    )
    def chat_sessions(self, info) -> list[models.ChatSession]:
        user = info.context.request.user
        return models.ChatSession.objects.filter(user=user)

    @strawberry_django.connection(
        DjangoListConnection[ChatMessageType], permission_classes=[CanUseRAGChat]
    )
    def chat_messages(self, info) -> list[models.ChatMessage]:
        user = info.context.request.user
        return models.ChatMessage.objects.filter(session__user=user)

    @strawberry.field(permission_classes=[IsSuperuser])
    def content_stats(self) -> List[ContentStatsType]:
        """Get statistics about content by type"""
        from django.db.models import Count
        from django.apps import apps

        stats = []

        # Get chunk counts by content type
        chunk_stats = dict(
            models.ContentChunk.objects.values("content_type")
            .annotate(count=Count("id"))
            .values_list("content_type", "count")
        )

        # Model mapping for getting object counts
        model_map = {
            "gamelog": ("nucleus", "GameLog"),
            "character": ("character", "Character"),
            "place": ("place", "Place"),
            "item": ("item", "Item"),
            "artifact": ("item", "Artifact"),
            "race": ("race", "Race"),
            "association": ("association", "Association"),
        }

        for content_type, (app_label, model_name) in model_map.items():
            try:
                model = apps.get_model(app_label, model_name)
                object_count = model.objects.count()

                # Count processed objects (those with chunks)
                processed_count = (
                    models.ContentChunk.objects.filter(content_type=content_type)
                    .values("object_id")
                    .distinct()
                    .count()
                )

                stats.append(
                    ContentStatsType(
                        content_type=content_type,
                        chunk_count=chunk_stats.get(content_type, 0),
                        object_count=object_count,
                        processed_count=processed_count,
                    )
                )
            except Exception:
                # If model doesn't exist, skip it
                continue

        # Add custom content stats
        custom_chunk_count = chunk_stats.get("custom", 0)
        if custom_chunk_count > 0:
            custom_object_count = (
                models.ContentChunk.objects.filter(content_type="custom")
                .values("object_id")
                .distinct()
                .count()
            )
            stats.append(
                ContentStatsType(
                    content_type="custom",
                    chunk_count=custom_chunk_count,
                    object_count=custom_object_count,
                    processed_count=custom_object_count,
                )
            )

        return stats

    @strawberry.field(permission_classes=[IsSuperuser])
    def available_content_types(self) -> List[str]:
        """Get list of available content types"""
        from rag_chat.content_processors import CONTENT_PROCESSORS

        return list(CONTENT_PROCESSORS.keys())

    @strawberry.field(permission_classes=[IsSuperuser])
    def search_content(
        self,
        query: str,
        content_types: Optional[List[str]] = None,
        similarity_threshold: Optional[float] = None,
        limit: Optional[int] = 10,
    ) -> List[ContentChunkType]:
        """Search content chunks directly (for debugging/admin)"""
        rag_service = services.RAGService()

        results = rag_service.semantic_search(
            query=query,
            limit=limit,
            similarity_threshold=similarity_threshold,
            content_types=content_types,
        )

        # Convert results to ContentChunk objects for GraphQL
        chunks = []
        for result in results:
            try:
                chunk = models.ContentChunk.objects.get(id=result.chunk_id)
                chunks.append(chunk)
            except models.ContentChunk.DoesNotExist:
                continue

        return chunks


@strawberry.type
class RAGMutation:
    @strawberry.mutation(permission_classes=[CanStartChatSession])
    def start_chat_session(self, info, input: StartChatSessionInput) -> ChatSessionType:
        user = info.context.request.user
        rag_service = services.RAGService()
        session = rag_service.create_chat_session(user, title=input.title)
        return session

    @strawberry.mutation(permission_classes=[CanSendChatMessage])
    def send_chat_message(
        self, info, input: SendChatMessageInput
    ) -> SendChatMessagePayload:
        user = info.context.request.user

        # Use better model for staff users
        if user.is_staff:
            model = settings.OPENAI_BEST_CHAT_MODEL
        else:
            model = settings.OPENAI_CHEAP_CHAT_MODEL

        rag_service = services.RAGService(model=model)
        session = input.session_id.resolve_node_sync(
            info, ensure_type=models.ChatSession
        )

        # Verify user owns the session
        if session.user != user:
            raise Exception("You can only send messages to your own chat sessions.")

        # Create placeholder message
        message = models.ChatMessage.objects.create(
            session=session,
            message=input.message,
            response="",  # Will be updated as chunks come in
            tokens_used=0,
            similarity_threshold=input.similarity_threshold,
        )

        # Start streaming response generation
        from rag_chat.tasks import generate_streaming_response

        generate_streaming_response.delay(
            message_id=message.id,
            query=input.message,
            similarity_threshold=input.similarity_threshold,
            session_id=session.id,
        )

        return SendChatMessagePayload(message=message, session=session)

    @strawberry.mutation
    def process_content(
        self, info, input: ProcessContentInput
    ) -> ProcessContentPayload:
        user = info.context.request.user
        if not user.is_authenticated or not user.is_superuser:
            raise Exception("Only superusers can process content.")

        from rag_chat.tasks import process_content

        try:
            task = process_content.delay(
                content_type=input.content_type,
                object_id=input.object_id,
                force_reprocess=input.force_reprocess,
            )

            return ProcessContentPayload(
                success=True,
                message=f"Processing {input.content_type} {input.object_id}",
                task_id=task.id,
            )
        except Exception as e:
            return ProcessContentPayload(
                success=False, message=f"Failed to queue processing task: {str(e)}"
            )

    @strawberry.mutation
    def process_all_content(
        self, info, input: ProcessAllContentInput
    ) -> ProcessAllContentPayload:
        user = info.context.request.user
        if not user.is_authenticated or not user.is_superuser:
            raise Exception("Only superusers can process content.")

        from rag_chat.tasks import process_all_content

        try:
            task = process_all_content.delay(
                content_types=input.content_types,
                force_reprocess=input.force_reprocess,
                limit=input.limit,
            )

            content_types = input.content_types or [
                "gamelog",
                "character",
                "place",
                "item",
                "artifact",
                "race",
                "association",
            ]

            return ProcessAllContentPayload(
                success=True,
                message=f"Processing all content types: {', '.join(content_types)}",
                task_id=task.id,
                content_types=content_types,
            )
        except Exception as e:
            return ProcessAllContentPayload(
                success=False,
                message=f"Failed to queue processing task: {str(e)}",
                content_types=[],
            )

    @strawberry.mutation
    def cleanup_orphaned_chunks(self, info) -> ProcessContentPayload:
        user = info.context.request.user
        if not user.is_authenticated or not user.is_superuser:
            raise Exception("Only superusers can cleanup data.")

        from rag_chat.tasks import cleanup_orphaned_chunks

        try:
            task = cleanup_orphaned_chunks.delay()

            return ProcessContentPayload(
                success=True, message="Cleaning up orphaned chunks", task_id=task.id
            )
        except Exception as e:
            return ProcessContentPayload(
                success=False, message=f"Failed to start cleanup: {str(e)}"
            )


@strawberry.type
class RAGSubscription:
    @strawberry.subscription
    async def chat_message_stream(
        self, info, session_id: relay.GlobalID
    ) -> AsyncGenerator[ChatMessageChunk, None]:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required")

        # Resolve the session
        session = await sync_to_async(session_id.resolve_node_sync)(
            info, ensure_type=models.ChatSession
        )

        # Check ownership
        if session.user != user:
            raise Exception("Access denied")

        channel_layer = get_channel_layer()
        channel_name = f"chat_stream_{session.id}_{user.id}"

        # Create a unique group for this subscription
        group_name = f"chat_{session.id}"

        # Join the group
        await channel_layer.group_add(group_name, channel_name)

        try:
            # Listen for messages on this channel
            while True:
                message = await channel_layer.receive(channel_name)

                if message["type"] == "chat.message.chunk":
                    yield ChatMessageChunk(
                        session_id=str(session.id),
                        message_id=message.get("message_id"),
                        content=message["content"],
                        is_complete=message.get("is_complete", False),
                        error=message.get("error"),
                        tokens_used=message.get("tokens_used"),
                    )

                    if message.get("is_complete"):
                        break

        except Exception as e:
            yield ChatMessageChunk(
                session_id=str(session.id), content="", is_complete=True, error=str(e)
            )
        finally:
            # Leave the group when subscription ends
            await channel_layer.group_discard(group_name, channel_name)
