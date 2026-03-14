<script lang="ts">
	import { onMount } from 'svelte';
	import { env } from '$env/dynamic/public';
	import { page } from '$app/state';
	import { toast } from 'svelte-sonner';

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

	let buttonContainer = $state<HTMLDivElement | null>(null);
	let buttonShell = $state<HTMLDivElement | null>(null);
	let googleReady = $state(false);
	let googleButtonWidth = $state(250);

	function getGoogleButtonWidth() {
		if (!buttonShell) return 250;

		return Math.max(220, Math.min(320, Math.floor(buttonShell.clientWidth)));
	}

	function syncGoogleButtonWidth() {
		googleButtonWidth = getGoogleButtonWidth();
	}

	function renderGoogleButton() {
		const google = (window as unknown as { google?: GoogleGIS }).google;
		if (!google?.accounts || !buttonContainer) return;

		google.accounts.id.renderButton(buttonContainer, {
			type: 'standard',
			shape: 'rectangular',
			theme: 'filled_black',
			text: 'signin_with',
			size: 'large',
			logo_alignment: 'left',
			width: googleButtonWidth
		});
	}

	$effect(() => {
		if (!googleReady || !buttonContainer) return;

		renderGoogleButton();
	});

	onMount(() => {
		let resizeObserver: ResizeObserver | null = null;
		let googleInitialized = false;

		const initializeGoogle = () => {
			const google = (window as unknown as { google?: GoogleGIS }).google;
			if (google?.accounts && !googleInitialized) {
				googleInitialized = true;
				google.accounts.id.initialize({
					client_id: env.PUBLIC_GOOGLE_CLIENT_ID,
					callback: handleCredentialResponse,
					auto_select: true,
					itp_support: true,
					context: 'signin',
					ux_mode: 'popup'
				});
			}

			syncGoogleButtonWidth();
			googleReady = true;

			if (buttonShell && 'ResizeObserver' in window) {
				resizeObserver = new ResizeObserver(() => {
					syncGoogleButtonWidth();
				});
				resizeObserver.observe(buttonShell);
			}
		};

		const google = (window as unknown as { google?: GoogleGIS }).google;
		if (google?.accounts) {
			initializeGoogle();
		} else {
			const script = document.createElement('script');
			script.src = 'https://accounts.google.com/gsi/client';
			script.async = true;
			script.defer = true;
			script.onload = initializeGoogle;
			document.head.appendChild(script);
		}

		return () => {
			resizeObserver?.disconnect();

			const google = (window as unknown as { google?: GoogleGIS }).google;
			if (google?.accounts) {
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
			toast.error('Access Denied', {
				description: 'Invalid credentials or system error. Please try again.'
			});
		}
	}
</script>

<div
	class="relative flex min-h-full w-full items-start justify-center overflow-hidden bg-slate-950 py-4 sm:items-center sm:py-6"
>
	<div
		class="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(255,176,0,0.08),transparent_35%),linear-gradient(180deg,rgba(15,23,42,0.25),rgba(2,6,23,0.92))]"
	></div>

	<section
		class="panel-border panel-pad relative mx-auto flex w-full max-w-md flex-col gap-4 rounded-sm bg-slate-900/82 text-center shadow-[0_0_0_1px_rgba(255,255,255,0.03),0_18px_48px_rgba(0,0,0,0.32)]"
	>
		<p class="font-mono text-[11px] tracking-[0.28em] text-slate-500 uppercase">Computer Access</p>

		<div class="space-y-3">
			<h1 class="title-display text-industrial-amber text-2xl sm:text-3xl">System Access</h1>
			<p class="copy-readable mx-auto max-w-sm text-slate-400">
				Sign in to access the Kontularien's onboard systems.
			</p>
		</div>

		<div class="border-industrial-dim border-t pt-5 sm:pt-6">
			<div bind:this={buttonShell} class="mx-auto w-full max-w-[320px]">
				{#key googleButtonWidth}
					<div bind:this={buttonContainer} class="mx-auto min-h-11 w-full"></div>
				{/key}
			</div>
		</div>

		<p class="font-mono text-xs tracking-[0.2em] text-slate-500 uppercase">
			Authorized Personnel Only
		</p>
	</section>
</div>
