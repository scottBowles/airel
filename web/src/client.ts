import { HoudiniClient, type ClientPlugin } from '$houdini';
import { env } from '$env/dynamic/public';
import { decodeJwt } from '$lib/utils';
import { browser } from '$app/environment';

const authPlugin: ClientPlugin = () => {
	return {
		async beforeNetwork(ctx, client) {
			const { session } = ctx;
			let token = session?.token;

			if (browser && token) {
				const payload = decodeJwt(token);
				// 30 second buffer before expiry
				if (payload?.exp && payload.exp * 1000 - Date.now() < 30 * 1000) {
					try {
						const res = await fetch('/auth/refresh', { method: 'POST' });
						if (res.ok) {
							const data = await res.json();
							if (data.accessToken) {
								token = data.accessToken;
								// Update session for this request context so subsequent plugins see it
								if (ctx.session) {
									ctx.session.token = token;
								}
							}
						}
					} catch (e) {
						console.error('Token refresh failed', e);
					}
				}
			}

			// Merge auth header
			const existingHeaders = ctx.fetchParams?.headers;
			const requestHeaders =
				existingHeaders instanceof Headers
					? Object.fromEntries(existingHeaders.entries())
					: Array.isArray(existingHeaders)
						? Object.fromEntries(existingHeaders)
						: (existingHeaders ?? {});

			ctx.fetchParams = {
				...ctx.fetchParams,
				mode: 'cors',
				headers: {
					...requestHeaders,
					'Content-Type': 'application/json',
					...(token ? { Authorization: `JWT ${token}` } : {})
				}
			};

			return client.next(ctx);
		}
	};
};

export default new HoudiniClient({
	url: env.PUBLIC_GRAPHQL_ENDPOINT,
	plugins: [authPlugin]
});
