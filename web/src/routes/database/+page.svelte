<script lang="ts">
	import { resolve } from '$app/paths';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
	let { DatabaseStats } = $derived(data);

	let counts = $derived({
		characters: $DatabaseStats.data?.characters?.totalCount ?? '---',
		places: $DatabaseStats.data?.places?.totalCount ?? '---',
		items: $DatabaseStats.data?.items?.totalCount ?? '---',
		artifacts: $DatabaseStats.data?.artifacts?.totalCount ?? '---',
		associations: $DatabaseStats.data?.associations?.totalCount ?? '---',
		races: $DatabaseStats.data?.races?.totalCount ?? '---'
	});

	let modules = $derived([
		{
			name: 'Characters',
			href: '/database/characters',
			icon: '👤',
			count: counts.characters
		},
		{
			name: 'Places',
			href: '/database/places',
			icon: '📍',
			count: counts.places
		},
		{
			name: 'Items',
			href: '/database/items',
			icon: '📦',
			count: counts.items
		},
		{
			name: 'Artifacts',
			href: '/database/artifacts',
			icon: '🔮',
			count: counts.artifacts
		},
		{
			name: 'Associations',
			href: '/database/associations',
			icon: '🤝',
			count: counts.associations
		},
		{
			name: 'Races',
			href: '/database/races',
			icon: '🧬',
			count: counts.races
		}
	]);
</script>

<div class="space-y-8">
	<div class="border-industrial-dim flex items-center justify-between border-b pb-4">
		<h2 class="text-3xl font-bold tracking-widest text-slate-100 uppercase">Database Core</h2>
		<div class="text-industrial-amber font-mono text-xs">ACCESS LEVEL: UNRESTRICTED</div>
	</div>

	<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
		{#each modules as mod (mod.name)}
			<a
				href={resolve(mod.href as any)}
				class="group hover:border-industrial-green relative overflow-hidden border border-slate-700 bg-slate-900/40 p-6 transition-all duration-200"
			>
				<div
					class="font-display absolute top-0 right-0 p-2 text-6xl opacity-10 transition-all group-hover:scale-110 group-hover:opacity-20"
				>
					{mod.icon}
				</div>

				<h3
					class="font-display group-hover:text-industrial-green mb-2 text-2xl text-slate-200 uppercase"
				>
					{mod.name}
				</h3>

				<div class="group-hover:text-industrial-green/70 font-mono text-xs text-slate-500">
					RECORDS: {mod.count}
				</div>

				<div class="mt-4 h-1 w-full bg-slate-800">
					<div
						class="group-hover:bg-industrial-green h-full w-1/3 bg-slate-600 transition-all duration-500"
					></div>
				</div>
			</a>
		{/each}
	</div>
</div>
