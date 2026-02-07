<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';

	let { data, children } = $props();
	let user = $derived(data.user);

	async function logout() {
		await fetch('/auth/logout', { method: 'POST' });
		window.location.href = '/login';
	}
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<!-- Preload fonts if we were hosting them, but we are using Google Fonts maybe? Need to add font setup -->
</svelte:head>

<div
	class="font-body selection:bg-industrial-amber fixed inset-0 flex flex-row overflow-hidden bg-slate-950 text-slate-200 selection:text-slate-900"
>
	<!-- Main Sidebar / Comms Array -->
	<nav
		class="flex w-64 flex-col gap-4 border-r border-slate-800 bg-slate-900/50 p-4 backdrop-blur-md"
	>
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
				href={resolve('/bridge')}
				class="machine-text group hover:text-industrial-amber flex items-center gap-3 px-3 py-2 text-sm text-slate-400 transition-colors hover:bg-slate-800"
			>
				<div class="group-hover:bg-industrial-amber h-1 w-1 bg-slate-600"></div>
				BRIDGE
			</a>
			<a
				href={resolve('/logs')}
				class="machine-text group hover:text-industrial-amber flex items-center gap-3 px-3 py-2 text-sm text-slate-400 transition-colors hover:bg-slate-800"
			>
				<div class="group-hover:bg-industrial-amber h-1 w-1 bg-slate-600"></div>
				CHRONICLE
			</a>
			<a
				href={resolve('/database')}
				class="machine-text group hover:text-industrial-amber flex items-center gap-3 px-3 py-2 text-sm text-slate-400 transition-colors hover:bg-slate-800"
			>
				<div class="group-hover:bg-industrial-amber h-1 w-1 bg-slate-600"></div>
				DATABASE
			</a>
			<a
				href={resolve('/comms')}
				class="machine-text group hover:text-industrial-amber flex items-center gap-3 px-3 py-2 text-sm text-slate-400 transition-colors hover:bg-slate-800"
			>
				<div class="group-hover:bg-industrial-amber h-1 w-1 bg-slate-600"></div>
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
				<a
					href={resolve(`/login?redirect=${encodeURIComponent(page.url.pathname)}`)}
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

	<!-- Main Content Viewport -->
	<main
		class="relative flex min-w-0 flex-1 flex-col overflow-hidden bg-[url('/grid.svg')] bg-[length:40px_40px]"
	>
		<!-- Scanline Overlay (Optional, keep low opacity) -->
		<div
			class="pointer-events-none absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_2px,3px_100%] opacity-10"
		></div>

		<!-- Scrollable content area -->
		<div class="flex-1 overflow-y-auto p-8">
			{@render children()}
		</div>
	</main>
</div>
