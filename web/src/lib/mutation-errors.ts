export function extractMutationErrorMessage(
	error: unknown,
	responseErrors?: Array<{ message: string }> | null
): string | null {
	if (responseErrors?.[0]?.message) {
		return responseErrors[0].message;
	}

	if (error && typeof error === 'object') {
		const maybeError = error as {
			message?: string;
			errors?: Array<{ message?: string }>;
			graphQLErrors?: Array<{ message?: string }>;
			cause?: unknown;
		};

		if (maybeError.errors?.[0]?.message) {
			return maybeError.errors[0].message;
		}

		if (maybeError.graphQLErrors?.[0]?.message) {
			return maybeError.graphQLErrors[0].message;
		}

		if (maybeError.cause) {
			const causeMessage = extractMutationErrorMessage(maybeError.cause);

			if (causeMessage) {
				return causeMessage;
			}
		}

		if (typeof maybeError.message === 'string' && maybeError.message.trim()) {
			return maybeError.message;
		}
	}

	return null;
}

export function getOperationInfoMessage(
	payload:
		| { __typename?: string | null; messages?: Array<{ message?: string }> | null }
		| null
		| undefined,
	fallback: string
): string | null {
	if (payload?.__typename !== 'OperationInfo') {
		return null;
	}

	return payload.messages?.[0]?.message ?? fallback;
}
