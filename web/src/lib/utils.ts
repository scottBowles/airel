export function decodeJwt(token: string) {
	try {
		const base64Url = token.split('.')[1];
		const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
		const jsonPayload = decodeURIComponent(
			atob(base64)
				.split('')
				.map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
				.join('')
		);
		let claims = JSON.parse(jsonPayload);

		// Handle nested payload quirk specific to this backend
		if (claims && typeof claims.payload === 'string') {
			try {
				claims = JSON.parse(claims.payload);
			} catch (e) {
				// ignore
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
	} catch (e) {
		return null;
	}
}
