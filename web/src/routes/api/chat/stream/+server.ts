import { env } from '$env/dynamic/public';
import type { RequestHandler } from './$types';

/**
 * SvelteKit server endpoint that proxies streaming chat requests to the Django backend.
 * This keeps the JWT token server-side and avoids CORS issues for SSE.
 */
export const POST: RequestHandler = async ({ request, locals }) => {
	const token = locals.token;
	if (!token) {
		return new Response(JSON.stringify({ error: 'Not authenticated' }), {
			status: 401,
			headers: { 'Content-Type': 'application/json' }
		});
	}

	const body = await request.json();
	const apiBase = env.PUBLIC_GRAPHQL_ENDPOINT.replace(/\/graphql\/?$/, '');
	const streamUrl = `${apiBase}/api/chat/stream/`;

	const upstreamResponse = await fetch(streamUrl, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `JWT ${token}`
		},
		body: JSON.stringify(body)
	});

	if (!upstreamResponse.ok) {
		const errorText = await upstreamResponse.text();
		return new Response(errorText, {
			status: upstreamResponse.status,
			headers: { 'Content-Type': 'application/json' }
		});
	}

	// Proxy the SSE stream through to the client
	return new Response(upstreamResponse.body, {
		headers: {
			'Content-Type': 'text/event-stream',
			'Cache-Control': 'no-cache',
			Connection: 'keep-alive'
		}
	});
};
