<script lang="ts">
	import '../app.css';
	import { Toaster } from 'svelte-sonner';
	import favicon from '$lib/assets/favicon.svg';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import { fromStore } from 'svelte/store';
	import { tick } from 'svelte';

	let { data, children } = $props();
	let mobileNavOpen = $state(false);
	let meResult = $derived.by(() => fromStore(data.Me).current);
	let mobileNavRef: HTMLElement | null = null;
	let mobileCloseButtonRef: HTMLButtonElement | null = null;
	let mobileMenuToggleRef: HTMLButtonElement | null = null;

	let user = $derived(meResult?.data?.me);

	function isActive(path: string) {
		if (path === '/') return page.url.pathname === path;
		return page.url.pathname === path || page.url.pathname.startsWith(`${path}/`);
	}

	async function logout() {
		await fetch('/auth/logout', { method: 'POST' });
		window.location.reload();
	}

	function toggleMobileNav() {
		mobileNavOpen = !mobileNavOpen;
	}

	function closeMobileNav() {
		mobileNavOpen = false;
	}

	function getMobileNavFocusableElements() {
		if (!mobileNavRef) return [];

		return Array.from(
			mobileNavRef.querySelectorAll<HTMLElement>(
				'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])'
			)
		).filter((element) => !element.hasAttribute('disabled'));
	}

	function handleMobileNavKeydown(event: KeyboardEvent) {
		if (!mobileNavOpen) return;

		if (event.key === 'Escape') {
			event.preventDefault();
			closeMobileNav();
			mobileMenuToggleRef?.focus();
			return;
		}

		if (event.key !== 'Tab') return;

		const focusableElements = getMobileNavFocusableElements();
		if (focusableElements.length === 0) {
			event.preventDefault();
			mobileNavRef?.focus();
			return;
		}

		const firstElement = focusableElements[0];
		const lastElement = focusableElements[focusableElements.length - 1];
		const activeElement = document.activeElement as HTMLElement | null;

		if (!activeElement || !mobileNavRef?.contains(activeElement)) {
			event.preventDefault();
			(event.shiftKey ? lastElement : firstElement).focus();
			return;
		}

		if (event.shiftKey && activeElement === firstElement) {
			event.preventDefault();
			lastElement.focus();
			return;
		}

		if (!event.shiftKey && activeElement === lastElement) {
			event.preventDefault();
			firstElement.focus();
		}
	}

	$effect(() => {
		if (!mobileNavOpen) return;

		void tick().then(() => {
			const focusableElements = getMobileNavFocusableElements();
			const firstTarget = mobileCloseButtonRef ?? focusableElements[0] ?? mobileNavRef;
			firstTarget?.focus();
		});
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<!-- Preload fonts if we were hosting them, but we are using Google Fonts maybe? Need to add font setup -->
</svelte:head>

<svelte:window onkeydown={handleMobileNavKeydown} />

<div
	class="font-body selection:bg-industrial-amber fixed inset-0 flex overflow-hidden bg-slate-950 text-slate-200 selection:text-slate-900"
>
	{#if mobileNavOpen}
		<button
			type="button"
			class="fixed inset-0 z-40 bg-slate-950/70 md:hidden"
			tabindex="-1"
			onclick={closeMobileNav}
			aria-label="Close navigation menu"
		></button>
	{/if}

	<!-- Mobile Slide-over Comms Array -->
	<nav
		id="mobile-nav"
		bind:this={mobileNavRef}
		tabindex="-1"
		class="fixed inset-y-0 left-0 z-50 flex w-72 max-w-[85vw] -translate-x-full flex-col gap-4 border-r border-slate-800 bg-slate-900/95 p-4 backdrop-blur-md transition-transform duration-150 ease-out md:hidden"
		class:translate-x-0={mobileNavOpen}
	>
		<!-- Mobile Nav Header -->
		<div class="mb-2 flex items-center justify-between border-b border-slate-800 pb-4">
			<h2 class="font-display text-sm tracking-widest text-slate-300 uppercase">Comms Array</h2>
			<button
				type="button"
				bind:this={mobileCloseButtonRef}
				onclick={closeMobileNav}
				class="machine-text flex h-9 w-9 items-center justify-center border border-slate-700 hover:border-slate-500"
				aria-label="Close navigation menu"
			>
				<span class="sr-only">Close menu</span>
				<span class="relative h-3 w-3" aria-hidden="true">
					<span
						class="bg-industrial-amber absolute top-1/2 left-0 h-px w-3 -translate-y-1/2 rotate-45"
					></span>
					<span class="absolute top-1/2 left-0 h-px w-3 -translate-y-1/2 -rotate-45 bg-slate-300"
					></span>
				</span>
			</button>
		</div>

		<!-- Ship Identity -->
		<div class="border-industrial-dim mb-4 border-b pb-4">
			<h1 class="font-display text-2xl font-bold tracking-widest text-white uppercase">
				<span class="text-industrial-amber">Kontularien</span>
				<span class="block text-xs text-slate-500">System Interface v2.5</span>
			</h1>
		</div>

		<!-- Navigation Links -->
		<div class="flex flex-col gap-1">
			<a
				href={resolve('/')}
				onclick={closeMobileNav}
				class="machine-text group hover:text-industrial-amber flex items-center gap-3 px-3 py-3 text-sm text-slate-400 transition-colors hover:bg-slate-800"
				class:text-industrial-amber={isActive('/')}
				class:bg-slate-800={isActive('/')}
			>
				<div
					class="group-hover:bg-industrial-amber h-1.5 w-1.5 bg-slate-600"
					class:bg-industrial-amber={isActive('/')}
				></div>
				BRIDGE
			</a>
			<a
				href={resolve('/logs')}
				onclick={closeMobileNav}
				class="machine-text group hover:text-industrial-amber flex items-center gap-3 px-3 py-3 text-sm text-slate-400 transition-colors hover:bg-slate-800"
				class:text-industrial-amber={isActive('/logs')}
				class:bg-slate-800={isActive('/logs')}
			>
				<div
					class="group-hover:bg-industrial-amber h-1.5 w-1.5 bg-slate-600"
					class:bg-industrial-amber={isActive('/logs')}
				></div>
				CHRONICLE
			</a>
			<a
				href={resolve('/database')}
				onclick={closeMobileNav}
				class="machine-text group hover:text-industrial-amber flex items-center gap-3 px-3 py-3 text-sm text-slate-400 transition-colors hover:bg-slate-800"
				class:text-industrial-amber={isActive('/database')}
				class:bg-slate-800={isActive('/database')}
			>
				<div
					class="group-hover:bg-industrial-amber h-1.5 w-1.5 bg-slate-600"
					class:bg-industrial-amber={isActive('/database')}
				></div>
				DATABASE
			</a>
			<a
				href={resolve('/comms')}
				onclick={closeMobileNav}
				class="machine-text group hover:text-industrial-amber flex items-center gap-3 px-3 py-3 text-sm text-slate-400 transition-colors hover:bg-slate-800"
				class:text-industrial-amber={isActive('/comms')}
				class:bg-slate-800={isActive('/comms')}
			>
				<div
					class="group-hover:bg-industrial-amber h-1.5 w-1.5 bg-slate-600"
					class:bg-industrial-amber={isActive('/comms')}
				></div>
				COMMS
			</a>
		</div>

		<div class="flex-1"></div>

		{#if user}
			<div class="mb-4 border-t border-slate-800 pt-4">
				<div class="mb-1 text-xs text-slate-400">OPERATOR</div>
				<div class="text-industrial-amber font-mono text-sm">{user.username}</div>
				<button onclick={logout} class="mt-2 min-h-11 text-xs text-red-400 hover:text-red-300">
					TERMINATE SESSION
				</button>
			</div>
		{:else}
			<div class="mb-4 border-t border-slate-800 pt-4">
				<a
					href={resolve('/login')}
					onclick={closeMobileNav}
					class="text-industrial-amber text-xs hover:underline"
				>
					INITIATE LOGIN
				</a>
			</div>
		{/if}

		<!-- Status Metrics (Decor only for now) -->
		<div class="border-t border-slate-800 pt-4 font-mono text-[10px] text-slate-600">
			<div class="flex justify-between">
				<span>SYS.LOAD</span>
				<span class="text-industrial-green">NOMINAL</span>
			</div>
			<div class="flex justify-between">
				<span>CONN</span>
				<span class="text-industrial-amber">SECURE</span>
			</div>
			<div class="mt-2 flex justify-between">
				<span>KOZMO_AI</span>
				<span class="text-industrial-green animate-pulse">ONLINE</span>
			</div>
		</div>
	</nav>

	<!-- Main Sidebar / Comms Array (Desktop) -->
	<nav
		inert={mobileNavOpen}
		aria-hidden={mobileNavOpen}
		class="hidden w-64 flex-col gap-4 border-r border-slate-800 bg-slate-900/50 p-4 backdrop-blur-md md:flex"
	>
		<div class="border-industrial-dim mb-4 border-b pb-4">
			<h1 class="font-display text-2xl font-bold tracking-widest text-white uppercase">
				<span class="text-industrial-amber">Kontularien</span>
				<span class="block text-xs text-slate-500">System Interface v2.5</span>
			</h1>
		</div>

		<div class="flex flex-col gap-1">
			<a
				href={resolve('/')}
				class="machine-text group hover:text-industrial-amber flex items-center gap-3 px-3 py-2 text-sm text-slate-400 transition-colors hover:bg-slate-800"
				class:text-industrial-amber={isActive('/')}
				class:bg-slate-800={isActive('/')}
			>
				<div
					class="group-hover:bg-industrial-amber h-1 w-1 bg-slate-600"
					class:bg-industrial-amber={isActive('/')}
				></div>
				BRIDGE
			</a>
			<a
				href={resolve('/logs')}
				class="machine-text group hover:text-industrial-amber flex items-center gap-3 px-3 py-2 text-sm text-slate-400 transition-colors hover:bg-slate-800"
				class:text-industrial-amber={isActive('/logs')}
				class:bg-slate-800={isActive('/logs')}
			>
				<div
					class="group-hover:bg-industrial-amber h-1 w-1 bg-slate-600"
					class:bg-industrial-amber={isActive('/logs')}
				></div>
				CHRONICLE
			</a>
			<a
				href={resolve('/database')}
				class="machine-text group hover:text-industrial-amber flex items-center gap-3 px-3 py-2 text-sm text-slate-400 transition-colors hover:bg-slate-800"
				class:text-industrial-amber={isActive('/database')}
				class:bg-slate-800={isActive('/database')}
			>
				<div
					class="group-hover:bg-industrial-amber h-1 w-1 bg-slate-600"
					class:bg-industrial-amber={isActive('/database')}
				></div>
				DATABASE
			</a>
			<a
				href={resolve('/comms')}
				class="machine-text group hover:text-industrial-amber flex items-center gap-3 px-3 py-2 text-sm text-slate-400 transition-colors hover:bg-slate-800"
				class:text-industrial-amber={isActive('/comms')}
				class:bg-slate-800={isActive('/comms')}
			>
				<div
					class="group-hover:bg-industrial-amber h-1 w-1 bg-slate-600"
					class:bg-industrial-amber={isActive('/comms')}
				></div>
				COMMS
			</a>
		</div>

		<div class="flex-1"></div>

		{#if user}
			<div class="mb-4 border-t border-slate-800 pt-4">
				<div class="mb-1 text-xs text-slate-400">OPERATOR</div>
				<div class="text-industrial-amber font-mono text-sm">{user.username}</div>
				<button onclick={logout} class="mt-2 text-xs text-red-400 hover:text-red-300">
					TERMINATE SESSION
				</button>
			</div>
		{:else}
			<div class="mb-4 border-t border-slate-800 pt-4">
				<a href={resolve('/login')} class="text-industrial-amber text-xs hover:underline">
					INITIATE LOGIN
				</a>
			</div>
		{/if}

		<div class="border-t border-slate-800 pt-4 font-mono text-[10px] text-slate-600">
			<div class="flex justify-between">
				<span>SYS.LOAD</span>
				<span class="text-industrial-green">NOMINAL</span>
			</div>
			<div class="flex justify-between">
				<span>CONN</span>
				<span class="text-industrial-amber">SECURE</span>
			</div>
			<div class="mt-2 flex justify-between">
				<span>KOZMO_AI</span>
				<span class="text-industrial-green animate-pulse">ONLINE</span>
			</div>
		</div>
	</nav>

	<!-- Main Content Viewport -->
	<main
		inert={mobileNavOpen}
		aria-hidden={mobileNavOpen}
		class="relative flex min-w-0 flex-1 flex-col overflow-hidden bg-[url('/grid.svg')] bg-size-[40px_40px]"
	>
		<!-- Mobile Command Header -->
		<header
			class="z-30 grid grid-cols-[auto_1fr_auto] items-center gap-2 border-b border-slate-800/80 bg-slate-900/85 px-3 py-2 backdrop-blur-md md:hidden"
		>
			<button
				type="button"
				bind:this={mobileMenuToggleRef}
				onclick={toggleMobileNav}
				class="machine-text flex h-11 w-11 items-center justify-center border border-slate-700 text-[11px] hover:border-slate-500"
				aria-expanded={mobileNavOpen}
				aria-controls="mobile-nav"
				aria-label="Toggle navigation menu"
			>
				<span class="sr-only">Toggle menu</span>
				<span class="flex flex-col items-center gap-1" aria-hidden="true">
					<span class="bg-industrial-amber h-px w-4"></span>
					<span class="h-px w-3 bg-slate-300"></span>
					<span class="bg-industrial-amber h-px w-4"></span>
				</span>
			</button>

			<div class="text-center">
				<p class="font-display text-sm leading-none tracking-widest text-white uppercase">
					Kontularien
				</p>
				<p class="text-[10px] text-slate-500 uppercase">System Interface</p>
			</div>

			<div class="machine-text text-industrial-green justify-self-end text-[10px]">ONLINE</div>
		</header>

		<!-- Scanline Overlay (Optional, keep low opacity) -->
		<div
			class="pointer-events-none absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-size-[100%_2px,3px_100%] opacity-10"
		></div>

		<!-- Scrollable content area -->
		<div class="flex-1 overflow-y-auto px-3 py-4 sm:px-4 sm:py-5 md:p-8">
			{@render children()}
		</div>
	</main>

	<Toaster richColors theme="dark" position="bottom-right" />
</div>
