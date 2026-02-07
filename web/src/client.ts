import { HoudiniClient, type ClientPlugin } from '$houdini';
import { env } from '$env/dynamic/public';
import { decodeJwt } from '$lib/utils';
import { browser } from '$app/environment';

const authPlugin: ClientPlugin = () => {
	return {
		async beforeNetwork(ctx, { next }) {
			const { session } = ctx;
			let token = session?.token;

			if (browser && token) {
				const payload = decodeJwt(token);
				// 5 minutes buffer
				if (payload?.exp && payload.exp * 1000 - Date.now() < 5 * 60 * 1000) {
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
			ctx.fetchParams = {
				...ctx.fetchParams,
				mode: 'cors',
				headers: {
					...ctx.fetchParams?.headers,
					'Content-Type': 'application/json',
					...(token ? { Authorization: `JWT ${token}` } : {})
				}
			};

			next(ctx);
		}
	};
};

export default new HoudiniClient({
	url: env.PUBLIC_GRAPHQL_ENDPOINT,
	plugins: [authPlugin]
});
