import { json } from '@sveltejs/kit';
import { verifyGoogleLogin, setAuthCookies } from '$lib/server/auth';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request, cookies }) => {
	const { googleToken } = await request.json();

	if (!googleToken) {
		return json({ error: 'Missing token' }, { status: 400 });
	}

	const result = await verifyGoogleLogin(googleToken);

	if (result?.success) {
		setAuthCookies(cookies, result.token.token, result.refreshToken.token);
		return json({
			user: result.user,
			accessToken: result.token.token
		});
	}

	return json({ error: 'Login failed', details: result?.errors }, { status: 401 });
};
