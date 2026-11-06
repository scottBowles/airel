// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			user: {
				id: string;
				username: string;
				email: string;
			} | null;
			token: string | null;
		}
		interface Session {
			token?: string | null;
			user?: {
				id: string;
				username: string;
				email: string;
			} | null;
		}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}

	interface CloudinaryUploadWidget {
		open(): void;
		close(): void;
		destroy(): void;
	}

	interface CloudinaryUploadResult {
		event: string;
		info: {
			public_id: string;
			secure_url: string;
			[key: string]: unknown;
		};
	}

	interface Window {
		cloudinary?: {
			createUploadWidget(
				options: Record<string, unknown>,
				callback: (error: unknown, result: CloudinaryUploadResult) => void
			): CloudinaryUploadWidget;
		};
	}
}

export {};
