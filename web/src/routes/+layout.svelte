<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<!-- Preload fonts if we were hosting them, but we are using Google Fonts maybe? Need to add font setup -->
</svelte:head>

<div class="fixed inset-0 flex flex-row overflow-hidden bg-slate-950 font-body text-slate-200 selection:bg-industrial-amber selection:text-slate-900">
	<!-- Main Sidebar / Comms Array -->
	<nav class="flex w-64 flex-col gap-4 border-r border-slate-800 bg-slate-900/50 p-4 backdrop-blur-md">
		<!-- Ship Identity -->
		<div class="mb-4 border-b border-industrial-dim pb-4">
			<h1 class="font-display text-2xl font-bold tracking-widest text-white uppercase">
				<span class="text-industrial-amber">Kontularien</span>
				<span class="text-xs text-slate-500 block">System Interface v2.5</span>
			</h1>
		</div>

		<!-- Navigation Links -->
		<div class="flex flex-col gap-1">
			<a href="/bridge" class="machine-text group flex items-center gap-3 px-3 py-2 text-sm text-slate-400 hover:bg-slate-800 hover:text-industrial-amber transition-colors">
				<div class="h-1 w-1 bg-slate-600 group-hover:bg-industrial-amber"></div>
				BRIDGE
			</a>
			<a href="/logs" class="machine-text group flex items-center gap-3 px-3 py-2 text-sm text-slate-400 hover:bg-slate-800 hover:text-industrial-amber transition-colors">
				<div class="h-1 w-1 bg-slate-600 group-hover:bg-industrial-amber"></div>
				CHRONICLE
			</a>
			<a href="/database" class="machine-text group flex items-center gap-3 px-3 py-2 text-sm text-slate-400 hover:bg-slate-800 hover:text-industrial-amber transition-colors">
				<div class="h-1 w-1 bg-slate-600 group-hover:bg-industrial-amber"></div>
				DATABASE
			</a>
			<a href="/comms" class="machine-text group flex items-center gap-3 px-3 py-2 text-sm text-slate-400 hover:bg-slate-800 hover:text-industrial-amber transition-colors">
				<div class="h-1 w-1 bg-slate-600 group-hover:bg-industrial-amber"></div>
				COMMS
			</a>
		</div>

		<div class="flex-1"></div>

		<!-- Status Metrics (Decor only for now) -->
		<div class="border-t border-slate-800 pt-4 text-[10px] font-mono text-slate-600">
			<div class="flex justify-between">
				<span>SYS.LOAD</span>
				<span class="text-industrial-green">NOMINAL</span>
			</div>
			<div class="flex justify-between">
				<span>CONN</span>
				<span class="text-industrial-amber">SECURE</span>
			</div>
			<div class="flex justify-between mt-2">
				<span>KOZMO_AI</span>
				<span class="animate-pulse text-industrial-green">ONLINE</span>
			</div>
		</div>
	</nav>

	<!-- Main Content Viewport -->
	<main class="relative flex-1 flex flex-col min-w-0 overflow-hidden bg-[url('/grid.svg')] bg-[length:40px_40px]">
		<!-- Scanline Overlay (Optional, keep low opacity) -->
		<div class="pointer-events-none absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_2px,3px_100%] opacity-10"></div>
		
		<!-- Scrollable content area -->
		<div class="flex-1 overflow-y-auto p-8">
			{@render children()}
		</div>
	</main>
</div>
