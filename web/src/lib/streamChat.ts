/**
 * Client-side utility for consuming the streaming chat SSE endpoint.
 * Uses Fetch API + ReadableStream to parse SSE events incrementally.
 */

export interface StreamChatOptions {
	sessionId: string;
	message: string;
	similarityThreshold?: number;
	onToken: (token: string) => void;
	onDone: (data: { messageId: number; tokensUsed: number; sources: unknown }) => void;
	onError: (error: string) => void;
	signal?: AbortSignal;
}

export async function streamChat(options: StreamChatOptions): Promise<void> {
	const { sessionId, message, similarityThreshold, onToken, onDone, onError, signal } = options;

	const response = await fetch('/api/chat/stream', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({
			session_id: sessionId,
			message,
			...(similarityThreshold != null && { similarity_threshold: similarityThreshold })
		}),
		signal
	});

	if (!response.ok) {
		const text = await response.text();
		let errorMsg: string;
		try {
			errorMsg = JSON.parse(text).error ?? text;
		} catch {
			errorMsg = text;
		}
		onError(errorMsg);
		return;
	}

	const reader = response.body?.getReader();
	if (!reader) {
		onError('No response body');
		return;
	}

	const decoder = new TextDecoder();
	let buffer = '';

	try {
		while (true) {
			const { done, value } = await reader.read();
			if (done) break;

			buffer += decoder.decode(value, { stream: true });

			// Parse SSE events from buffer
			const lines = buffer.split('\n');
			// Keep the last potentially incomplete line in the buffer
			buffer = lines.pop() ?? '';

			for (const line of lines) {
				if (!line.startsWith('data: ')) continue;
				const jsonStr = line.slice(6); // Remove "data: " prefix
				if (!jsonStr.trim()) continue;

				try {
					const data = JSON.parse(jsonStr);
					if (data.type === 'token') {
						onToken(data.token);
					} else if (data.type === 'done') {
						onDone({
							messageId: data.message_id,
							tokensUsed: data.tokens_used,
							sources: data.sources
						});
					} else if (data.type === 'error') {
						onError(data.error);
					}
				} catch {
					// Skip malformed JSON lines
				}
			}
		}
	} finally {
		reader.releaseLock();
	}
}
