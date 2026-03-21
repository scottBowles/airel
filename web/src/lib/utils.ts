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
			} catch {
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
	} catch {
		return null;
	}
}

export function formatGameDate(date: Date | string | null | undefined): string {
	if (!date) return 'UNKNOWN DATE';
	try {
		const d = typeof date === 'string' ? new Date(date) : date;
		return d.toISOString().split('T')[0];
	} catch {
		return 'INVALID DATE';
	}
}

type EdgeWithUpdatedNode = {
	readonly node: {
		readonly updated: Date | string;
	};
};

export function sortEdgesByUpdatedDesc<TEdge extends EdgeWithUpdatedNode>(
	edges: readonly TEdge[] | null | undefined
): TEdge[] {
	return [...(edges ?? [])].sort((left, right) => {
		const leftUpdated = new Date(left.node.updated).getTime();
		const rightUpdated = new Date(right.node.updated).getTime();

		if (Number.isNaN(leftUpdated) && Number.isNaN(rightUpdated)) {
			return 0;
		}

		if (Number.isNaN(leftUpdated)) {
			return 1;
		}

		if (Number.isNaN(rightUpdated)) {
			return -1;
		}

		return rightUpdated - leftUpdated;
	});
}
