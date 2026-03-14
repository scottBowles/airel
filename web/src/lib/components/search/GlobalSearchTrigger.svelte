<script lang="ts">
	import { Search } from 'lucide-svelte';

	let {
		mobile = false,
		shortcutLabel = null,
		onActivate = () => {}
	}: {
		mobile?: boolean;
		shortcutLabel?: string | null;
		onActivate?: () => void;
	} = $props();
</script>

{#if mobile}
	<button
		type="button"
		onclick={onActivate}
		class="machine-text flex h-11 w-11 items-center justify-center border border-slate-700 text-[11px] hover:border-slate-500"
		aria-haspopup="dialog"
		aria-label="Open global search"
	>
		<Search size={15} strokeWidth={1.75} />
	</button>
{:else}
	<button
		type="button"
		onclick={onActivate}
		class="group flex w-full items-center gap-3 border border-slate-700 bg-slate-950/70 px-3 py-3 text-left transition-colors hover:border-slate-500 hover:bg-slate-900"
		aria-haspopup="dialog"
		aria-label="Open global search"
	>
		<div
			class="group-hover:text-industrial-amber flex h-10 w-10 shrink-0 items-center justify-center border border-slate-800 bg-slate-900 text-slate-400 transition-colors"
		>
			<Search size={16} strokeWidth={1.75} />
		</div>
		<div class="min-w-0 flex-1">
			<div class="machine-text text-[10px] whitespace-normal">Database Search</div>
		</div>
		{#if shortcutLabel}
			<div
				class="hidden shrink-0 items-center border border-slate-700 px-2 py-2 font-mono text-xs tracking-[0.12em] text-slate-300 lg:inline-flex"
			>
				{shortcutLabel}
			</div>
		{/if}
	</button>
{/if}
