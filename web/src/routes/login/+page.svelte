<script lang="ts">
	import { onMount } from 'svelte';
	import { env } from '$env/dynamic/public';
	import { page } from '$app/state';

	// Define the callback type for Google's GIS
	interface GoogleCredentialResponse {
		credential: string;
		select_by?: string;
	}

	interface GoogleGIS {
		accounts: {
			id: {
				initialize: (config: Record<string, unknown>) => void;
				renderButton: (parent: HTMLElement, options: Record<string, unknown>) => void;
				cancel: () => void;
			};
		};
	}

	let buttonContainer: HTMLDivElement;

	onMount(() => {
		// Function to initialize and render the button
		const renderGoogleButton = () => {
			const google = (window as unknown as { google?: GoogleGIS }).google;
			if (google && google.accounts) {
				google.accounts.id.initialize({
					client_id: env.PUBLIC_GOOGLE_CLIENT_ID,
					callback: handleCredentialResponse,
					auto_select: true,
					itp_support: true,
					context: 'signin',
					ux_mode: 'popup'
				});

				google.accounts.id.renderButton(buttonContainer, {
					type: 'standard',
					shape: 'rectangular',
					theme: 'filled_black', // Dark theme to match site
					text: 'signin_with',
					size: 'large',
					logo_alignment: 'left',
					width: 250
				});
			}
		};

		// Check if script is already loaded
		const google = (window as unknown as { google?: GoogleGIS }).google;
		if (google && google.accounts) {
			renderGoogleButton();
		} else {
			// Load the script manually
			const script = document.createElement('script');
			script.src = 'https://accounts.google.com/gsi/client';
			script.async = true;
			script.defer = true;
			script.onload = renderGoogleButton;
			document.head.appendChild(script);
		}

		return () => {
			const google = (window as unknown as { google?: GoogleGIS }).google;
			if (google && google.accounts) {
				google.accounts.id.cancel();
			}
		};
	});

	async function handleCredentialResponse(response: GoogleCredentialResponse) {
		const res = await fetch('/auth/login', {
			method: 'POST',
			body: JSON.stringify({ googleToken: response.credential }),
			headers: { 'Content-Type': 'application/json' }
		});

		if (res.ok) {
			const redirect = page.url.searchParams.get('redirect') || '/';
			window.location.href = redirect;
		} else {
			console.error('Login failed');
			// Optionally show an error message variable here
		}
	}
</script>

<div class="flex h-screen w-full items-center justify-center bg-slate-950">
	<div
		class="rounded-lg border border-slate-800 bg-slate-900/50 p-8 text-center shadow-md backdrop-blur-md"
	>
		<h1 class="text-industrial-amber font-display mb-6 text-2xl font-bold tracking-widest">
			SYSTEM ACCESS
		</h1>
		<div class="border-industrial-dim flex min-h-[50px] items-center justify-center border-t pt-6">
			<div bind:this={buttonContainer}></div>
		</div>
		<p class="mt-4 font-mono text-xs text-slate-500">AUTHORIZED PERSONNEL ONLY</p>
	</div>
</div>
