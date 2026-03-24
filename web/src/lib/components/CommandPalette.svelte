<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { env } from '$env/dynamic/public';
	import { cn } from '$lib/utils';
	import { Search, X, FileText, Users, MapPin, Swords, Gem, Globe, Dna } from 'lucide-svelte';
	import { algoliasearch } from 'algoliasearch';

	let {
		open = $bindable(false),
	}: {
		open?: boolean;
	} = $props();

	let query = $state('');
	let results = $state<Array<{ objectID: string; name: string; type: string; description?: string; global_id?: string }>>([]);
	let selectedIndex = $state(0);
	let inputEl = $state<HTMLInputElement | null>(null);
	let searching = $state(false);

	const client = algoliasearch(env.PUBLIC_ALGOLIA_APP_ID, env.PUBLIC_ALGOLIA_SEARCH_API_KEY);

	const typeIcons: Record<string, typeof Search> = {
		character: Users,
		place: MapPin,
		item: Swords,
		artifact: Gem,
		association: Globe,
		race: Dna,
		gamelog: FileText,
	};

	const typeRoutes: Record<string, string> = {
		character: '/database/characters',
		place: '/database/places',
		item: '/database/items',
		artifact: '/database/artifacts',
		association: '/database/associations',
		race: '/database/races',
		gamelog: '/chronicle',
	};

	function getIcon(type: string) {
		return typeIcons[type.toLowerCase()] ?? Search;
	}

	function getRoute(hit: { objectID: string; type: string; global_id?: string }) {
		const base = typeRoutes[hit.type.toLowerCase()] ?? '/database';
		return `${base}/${hit.global_id ?? hit.objectID}`;
	}

	const indexNames = ['Association', 'Artifact', 'Character', 'Item', 'Place', 'Race'];

	async function search(q: string) {
		if (!q.trim()) {
			results = [];
			return;
		}
		searching = true;
		try {
			const { results: searchResults } = await client.search({
				requests: indexNames.map((indexName) => ({ indexName, query: q, hitsPerPage: 5 })),
			});
			const merged: typeof results = [];
			for (let i = 0; i < searchResults.length; i++) {
				const res = searchResults[i];
				if ('hits' in res) {
					const typeName = indexNames[i].toLowerCase();
					for (const hit of res.hits as Array<{ objectID: string; name: string; description?: string; global_id?: string }>) {
						merged.push({ ...hit, type: typeName });
					}
				}
			}
			results = merged;
			selectedIndex = 0;
		} catch {
			results = [];
		} finally {
			searching = false;
		}
	}

	let debounceTimer: ReturnType<typeof setTimeout>;
	function handleInput() {
		clearTimeout(debounceTimer);
		debounceTimer = setTimeout(() => search(query), 200);
	}

	function navigate(hit: (typeof results)[number]) {
		open = false;
		query = '';
		results = [];
		goto(getRoute(hit));
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'ArrowDown') {
			e.preventDefault();
			selectedIndex = Math.min(selectedIndex + 1, results.length - 1);
		} else if (e.key === 'ArrowUp') {
			e.preventDefault();
			selectedIndex = Math.max(selectedIndex - 1, 0);
		} else if (e.key === 'Enter' && results[selectedIndex]) {
			e.preventDefault();
			navigate(results[selectedIndex]);
		} else if (e.key === 'Escape') {
			open = false;
		}
	}

	$effect(() => {
		if (open) {
			query = '';
			results = [];
			selectedIndex = 0;
			// Focus input after DOM update
			setTimeout(() => inputEl?.focus(), 10);
		}
	});

	onMount(() => {
		function globalKeydown(e: KeyboardEvent) {
			if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
				e.preventDefault();
				open = !open;
			}
		}
		window.addEventListener('keydown', globalKeydown);
		return () => window.removeEventListener('keydown', globalKeydown);
	});
</script>

{#if open}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		class="fixed inset-0 z-50 flex items-start justify-center bg-black/80 pt-[12vh] animate-fade-in"
		onkeydown={handleKeydown}
		onclick={() => (open = false)}
	>
		<!-- svelte-ignore a11y_no_static_element_interactions a11y_click_events_have_key_events -->
		<div
			class="w-full max-w-lg animate-slide-down border border-border-subtle bg-hull shadow-glow-amber"
			onclick={(e) => e.stopPropagation()}
		>
			<!-- Search header -->
			<div class="flex items-center gap-2 border-b border-border-dim px-3 py-2">
				<span class="machine-text text-[9px] text-accent-amber/50">QUERY&gt;</span>
				<Search class="h-3.5 w-3.5 shrink-0 text-accent-amber/40" />
				<input
					bind:this={inputEl}
					bind:value={query}
					oninput={handleInput}
					placeholder="SEARCH DATABASE..."
					class="flex-1 bg-transparent text-sm text-accent-amber placeholder:text-text-muted focus:outline-none"
				/>
				<button onclick={() => (open = false)} class="text-text-muted hover:text-accent-amber">
					<X class="h-3.5 w-3.5" />
				</button>
			</div>

			<!-- Results -->
			<div class="max-h-72 overflow-y-auto">
				{#if results.length > 0}
					{#each results as hit, i}
						{@const Icon = getIcon(hit.type)}
						<button
							class={cn(
								'flex w-full items-center gap-2.5 px-3 py-2 text-left text-xs transition-colors border-l-2',
								i === selectedIndex
									? 'bg-accent-amber/8 text-accent-amber border-accent-amber'
									: 'text-text-secondary hover:bg-accent-amber/5 hover:text-text-primary border-transparent',
							)}
							onclick={() => navigate(hit)}
							onmouseenter={() => (selectedIndex = i)}
						>
							<Icon class="h-3.5 w-3.5 shrink-0 opacity-50" />
							<div class="min-w-0 flex-1">
								<div class="truncate uppercase tracking-wider">{hit.name}</div>
								{#if hit.description}
									<div class="truncate text-xs text-text-secondary normal-case tracking-normal">{hit.description}</div>
								{/if}
							</div>
							<span class="machine-text shrink-0 text-[9px] text-text-muted">{hit.type}</span>
						</button>
					{/each}
				{:else if query && !searching}
					<div class="px-3 py-6 text-center">
						<p class="machine-text text-text-muted">NO RECORDS MATCH QUERY</p>
					</div>
				{:else if !query}
					<div class="px-3 py-6 text-center">
						<p class="machine-text text-text-muted">AWAITING INPUT...</p>
					</div>
				{:else}
					<div class="px-3 py-6 text-center">
						<p class="machine-text text-accent-amber/60">SCANNING DATABASE...</p>
					</div>
				{/if}
			</div>

			<!-- Footer -->
			<div class="flex items-center gap-4 border-t border-border-dim px-3 py-1.5">
				<span class="machine-text text-[9px] text-text-muted">
					<kbd class="border border-border-dim bg-void px-1 py-px text-[9px]">↑↓</kbd>
					NAV
				</span>
				<span class="machine-text text-[9px] text-text-muted">
					<kbd class="border border-border-dim bg-void px-1 py-px text-[9px]">↵</kbd>
					SELECT
				</span>
				<span class="machine-text text-[9px] text-text-muted">
					<kbd class="border border-border-dim bg-void px-1 py-px text-[9px]">ESC</kbd>
					CLOSE
				</span>
			</div>
		</div>
	</div>
{/if}
