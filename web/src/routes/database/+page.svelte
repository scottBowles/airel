<script lang="ts">
	import { Users, MapPin, Globe, Swords, Gem, Dna } from 'lucide-svelte';

	const categories = [
		{ slug: 'characters', label: 'CHARACTERS', code: 'CHR', description: 'Crew, NPCs, and notable figures', icon: Users },
		{ slug: 'places', label: 'PLACES', code: 'LOC', description: 'Planets, stations, and regions', icon: MapPin },
		{ slug: 'associations', label: 'ASSOCIATIONS', code: 'ASC', description: 'Factions, guilds, and organizations', icon: Globe },
		{ slug: 'items', label: 'ITEMS', code: 'ITM', description: 'Weapons, armor, and equipment', icon: Swords },
		{ slug: 'artifacts', label: 'ARTIFACTS', code: 'ART', description: 'Rare and powerful relics', icon: Gem },
		{ slug: 'races', label: 'RACES', code: 'RCE', description: 'Species and lineages', icon: Dna },
	];
</script>

<svelte:head>
	<title>Database — Kontularien</title>
</svelte:head>

<div class="content-pad db-page">
	<!-- Header bar -->
	<div class="border border-border-dim bg-hull">
		<div class="flex items-center justify-between border-b border-border-dim px-3 py-1.5">
			<div class="flex items-center gap-2">
				<span class="status-dot text-accent-green"></span>
				<span class="machine-text text-[9px] text-text-muted">DAT-02 // DATABASE</span>
			</div>
			<span class="machine-text text-[9px] text-text-muted">{categories.length} SUBSYSTEMS</span>
		</div>
		<div class="px-3 py-3">
			<h1 class="title-display text-lg text-accent-amber text-glow-amber">DATABASE</h1>
			<p class="machine-text text-[10px] text-text-muted mt-0.5">Ship knowledge archives</p>
		</div>
	</div>

	<div class="grid gap-px sm:grid-cols-2 lg:grid-cols-3 border border-border-dim">
		{#each categories as cat}
			<a
				href="/database/{cat.slug}"
				class="group relative flex flex-col gap-2 bg-panel px-3 py-3 transition-all hover:bg-panel-hover"
			>
				<div class="flex items-center justify-between">
					<span class="machine-text text-[9px] text-text-faint">{cat.code}</span>
					<cat.icon class="h-3.5 w-3.5 text-accent-amber/30 group-hover:text-accent-amber transition-colors" />
				</div>
				<h2 class="text-xs font-bold text-text-primary uppercase tracking-widest group-hover:text-accent-amber transition-colors">
					{cat.label}
				</h2>
				<p class="text-xs text-text-secondary leading-relaxed">{cat.description}</p>
				<div class="border-t border-border-dim pt-1.5 mt-auto">
					<span class="machine-text text-[9px] text-text-muted group-hover:text-accent-amber transition-colors">ACCESS &gt;</span>
				</div>
				<div class="absolute bottom-0 left-0 h-px w-0 bg-accent-amber transition-all duration-300 group-hover:w-full"></div>
			</a>
		{/each}
	</div>
</div>
