<script lang="ts">
	import { User, Box, Orbit, Cpu, Network, Dna, FileText } from 'lucide-svelte';

	const {
		type
	}: { type: 'character' | 'item' | 'place' | 'race' | 'artifact' | 'association' | 'log' } =
		$props();

	const iconMap = {
		character: User,
		item: Box,
		place: Orbit,
		race: Dna,
		artifact: Cpu,
		association: Network,
		log: FileText
	};

	let Icon = $derived(iconMap[type] || Box);
</script>

<div
	class="relative flex h-10 w-10 shrink-0 items-center justify-center overflow-hidden rounded-sm border border-slate-800 bg-slate-950/50"
>
	<!-- Tech corners -->
	<div class="border-industrial-amber/50 absolute top-0 left-0 h-1 w-1 border-t border-l"></div>
	<div class="border-industrial-amber/50 absolute right-0 bottom-0 h-1 w-1 border-r border-b"></div>

	<!-- Icon -->
	<Icon
		class="text-industrial-amber/50 group-hover:text-industrial-amber transition-colors"
		size={18}
		strokeWidth={1.5}
	/>

	<!-- Scanline effect (subtle) -->
	<div
		class="pointer-events-none absolute inset-0 bg-[linear-gradient(transparent_50%,rgba(0,0,0,0.5)_50%)] bg-[length:100%_2px] opacity-20"
	></div>
</div>
