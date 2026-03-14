<script lang="ts">
	import { resolve } from '$app/paths';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
	let { DatabaseStats, Me } = $derived(data);

	let accessLevel = $derived(
		$Me?.data?.me?.isStaff ? 'ACCESS LEVEL: UNRESTRICTED' : 'ACCESS LEVEL: RESTRICTED'
	);

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

<div class="db-page-wide">
	<div class="db-header">
		<h2 class="db-title">Database Core</h2>
		<div class="text-industrial-amber font-mono text-xs">{accessLevel}</div>
	</div>

	<div class="grid grid-cols-1 gap-4 sm:gap-6 md:grid-cols-2 lg:grid-cols-3">
		{#each modules as mod (mod.name)}
			<a
				href={mod.href}
				class="group hover:border-industrial-green relative overflow-hidden border border-slate-700 bg-slate-900/40 p-4 transition-all duration-200 sm:p-6"
			>
				<div
					class="font-display absolute top-0 right-0 p-2 text-5xl opacity-10 transition-all group-hover:scale-110 group-hover:opacity-20 sm:text-6xl"
				>
					{mod.icon}
				</div>

				<h3
					class="font-display group-hover:text-industrial-green mb-2 text-xl text-slate-200 uppercase sm:text-2xl"
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
