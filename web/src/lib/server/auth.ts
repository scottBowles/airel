import { env } from '$env/dynamic/public';
import type { Cookies } from '@sveltejs/kit';

const GRAPHQL_ENDPOINT = env.PUBLIC_GRAPHQL_ENDPOINT;

interface GoogleLoginResponse {
	data: {
		googleLogin: {
			success: boolean;
			errors: any;
			token: {
				token: string;
				payload: {
					exp: number;
					username: string;
				};
			};
			refreshToken: {
				token: string;
				expiresAt: string;
			};
			user: {
				id: string;
				username: string;
				email: string;
			};
		};
	};
}

interface RefreshTokenResponse {
	data: {
		refreshToken: {
			success: boolean;
			token: {
				token: string;
			};
			refreshToken: {
				token: string;
			};
		};
	};
}

export async function verifyGoogleLogin(googleToken: string) {
	const query = `
        mutation googleLogin($googleToken: String!) {
            googleLogin(googleToken: $googleToken) {
                success
                errors
                token {
                    token
                    payload {
                        exp
                        username
                    }
                }
                refreshToken {
                    token
                    expiresAt
                }
                user {
                    id
                    username
                    email
                }
            }
        }
    `;

	const response = await fetch(GRAPHQL_ENDPOINT, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			query,
			variables: { googleToken }
		})
	});

	const json = (await response.json()) as GoogleLoginResponse;
	return json?.data?.googleLogin;
}

export async function refreshAuthToken(refreshToken: string) {
	const query = `
        mutation refreshToken($refreshToken: String!) {
            refreshToken(input: { refreshToken: $refreshToken }) {
                success
                token {
                    token
                }
                refreshToken {
                    token
                }
            }
        }
    `;

	const response = await fetch(GRAPHQL_ENDPOINT, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			query,
			variables: { refreshToken }
		})
	});

	const json = (await response.json()) as RefreshTokenResponse;
	return json?.data?.refreshToken;
}

export function setAuthCookies(cookies: Cookies, accessToken: string, refreshToken: string) {
	// Access token - reasonably short life, but we can set checking logic in client
	// We'll set a standard time, e.g. 15 mins.
	cookies.set('access_token', accessToken, {
		path: '/',
		httpOnly: true,
		sameSite: 'strict',
		secure: process.env.NODE_ENV === 'production',
		maxAge: 60 * 15 // 15 minutes
	});

	// Refresh token - longer life
	cookies.set('refresh_token', refreshToken, {
		path: '/',
		httpOnly: true,
		sameSite: 'strict',
		secure: process.env.NODE_ENV === 'production',
		maxAge: 60 * 60 * 24 * 7 // 7 days
	});
}

export function clearAuthCookies(cookies: Cookies) {
	cookies.delete('access_token', { path: '/' });
	cookies.delete('refresh_token', { path: '/' });
}

export function decodeJwt(token: string) {
	try {
		const base64Url = token.split('.')[1];
		const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');

		let jsonPayload;
		try {
			// Isomorphic decode
			if (typeof Buffer !== 'undefined') {
				jsonPayload = Buffer.from(base64, 'base64').toString();
			} else {
				jsonPayload = decodeURIComponent(
					atob(base64)
						.split('')
						.map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
						.join('')
				);
			}

			let claims = JSON.parse(jsonPayload);

			// Handle nested payload quirk specific to this backend
			if (claims && typeof claims.payload === 'string') {
				try {
					claims = JSON.parse(claims.payload);
				} catch (e) {
					console.warn('Failed to parse nested JWT payload string', e);
				}
			}

			// Normalize 'exp' from ISO string to seconds (standard JWT format)
			if (claims && typeof claims.exp === 'string') {
				const ms = Date.parse(claims.exp);
				if (!isNaN(ms)) {
					claims.exp = Math.floor(ms / 1000);
				}
			}

			return claims;
		} catch (err) {
			console.error('Inner JWT decode failed', err);
			return null;
		}
	} catch (e) {
		console.error('JWT Decode error', e);
		return null;
	}
}
