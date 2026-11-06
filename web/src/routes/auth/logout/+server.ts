import { json } from '@sveltejs/kit';
import { clearAuthCookies } from '$lib/server/auth';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ cookies }) => {
	clearAuthCookies(cookies);
	return json({ success: true });
};
