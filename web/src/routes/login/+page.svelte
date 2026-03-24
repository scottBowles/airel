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
	class="relative flex min-h-dvh w-full items-start justify-center overflow-hidden bg-void py-4 sm:items-center sm:py-6"
>
	<!-- Amber glow from top -->
	<div
		class="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(255,176,0,0.04),transparent_35%)]"
	></div>

	<!-- Grid background -->
	<div
		class="pointer-events-none absolute inset-0 opacity-[0.03]"
		style="background-image: linear-gradient(rgba(255,176,0,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(255,176,0,0.3) 1px, transparent 1px); background-size: 60px 60px;"
	></div>

	<section
		class="relative mx-auto flex w-full max-w-md flex-col gap-4 border border-border-dim bg-hull/90 px-6 py-5 text-center shadow-panel backdrop-blur-sm"
	>
		<div class="flex items-center justify-between border-b border-border-dim pb-2">
			<span class="machine-text text-[9px] text-text-faint">KSS-7742 // TERMINAL ACCESS</span>
			<span class="machine-text text-[9px] text-accent-amber/40">SEC-GATE</span>
		</div>

		<div class="space-y-2">
			<h1 class="title-display text-lg text-accent-amber text-glow-amber">SYSTEM ACCESS</h1>
			<p class="machine-text text-[10px] text-text-muted">
				Authenticate to access the Kontularien's onboard systems.
			</p>
		</div>

		<div class="border-t border-border-dim pt-4">
			<div bind:this={buttonShell} class="mx-auto w-full max-w-[320px]">
				{#key googleButtonWidth}
					<div bind:this={buttonContainer} class="mx-auto min-h-11 w-full"></div>
				{/key}
			</div>
		</div>

		<p class="machine-text text-[9px] tracking-[0.2em] text-text-faint uppercase">
			Authorized Personnel Only
		</p>
	</section>
</div>
