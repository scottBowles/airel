<script lang="ts">
	import { onMount, untrack } from 'svelte';
	import { goto, preloadData } from '$app/navigation';
	import { page } from '$app/state';
	import { env } from '$env/dynamic/public';
	import { cn } from '$lib/utils';
	import { filterCommands, getCategoryLabel, getCombinedRecents, recordCommandUsage, recordEntityVisit, type Command, type CommandCategory, type RecentItem } from '$lib/commands';
	import Search from '@lucide/svelte/icons/search';
	import X from '@lucide/svelte/icons/x';
	import FileText from '@lucide/svelte/icons/file-text';
	import Users from '@lucide/svelte/icons/users';
	import MapPin from '@lucide/svelte/icons/map-pin';
	import Swords from '@lucide/svelte/icons/swords';
	import Gem from '@lucide/svelte/icons/gem';
	import Globe from '@lucide/svelte/icons/globe';
	import Dna from '@lucide/svelte/icons/dna';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import Clock from '@lucide/svelte/icons/clock';
	import { algoliasearch } from 'algoliasearch';
	import { Dialog } from 'bits-ui';

	let {
		open = $bindable(false),
		isStaff = false,
	}: {
		open?: boolean;
		isStaff?: boolean;
	} = $props();

	let query = $state('');
	let entityResults = $state<Array<{ objectID: string; name: string; type: string; description?: string; global_id?: string }>>([]);
	let selectedIndex = $state(0);
	let inputEl = $state<HTMLInputElement | null>(null);
	let searching = $state(false);

	const client = algoliasearch(env.PUBLIC_ALGOLIA_APP_ID, env.PUBLIC_ALGOLIA_SEARCH_API_KEY);

	// ── Algolia entity search ──

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

	function getEntityIcon(type: string) {
		return typeIcons[type.toLowerCase()] ?? Search;
	}

	function getEntityRoute(hit: { objectID: string; type: string; global_id?: string }) {
		const base = typeRoutes[hit.type.toLowerCase()] ?? '/database';
		return `${base}/${hit.global_id ?? hit.objectID}`;
	}

	const indexNames = ['Association', 'Artifact', 'Character', 'Item', 'Place', 'Race'];

	async function searchEntities(q: string) {
		if (!q.trim()) {
			entityResults = [];
			return;
		}
		searching = true;
		try {
			const { results: searchResults } = await client.search({
				requests: indexNames.map((indexName) => ({ indexName, query: q, hitsPerPage: 5 })),
			});
			const merged: typeof entityResults = [];
			for (let i = 0; i < searchResults.length; i++) {
				const res = searchResults[i];
				if ('hits' in res) {
					const typeName = indexNames[i].toLowerCase();
					for (const hit of res.hits as Array<{ objectID: string; name: string; description?: string; global_id?: string }>) {
						merged.push({ ...hit, type: typeName });
					}
				}
			}
			entityResults = merged;
			selectedIndex = 0;
		} catch {
			entityResults = [];
		} finally {
			searching = false;
		}
	}

	// ── Command filtering ──

	let isCommandMode = $derived(query.startsWith('>'));
	let commandQuery = $derived(isCommandMode ? query.slice(1).trim() : query);

	let filteredCommands = $derived(filterCommands(commandQuery, { isStaff }));

	// Group commands by category for display
	let groupedCommands = $derived.by(() => {
		const groups: Array<{ category: CommandCategory; label: string; commands: Array<Command & { score: number }> }> = [];
		let lastCategory: CommandCategory | null = null;
		for (const cmd of filteredCommands) {
			if (cmd.category !== lastCategory) {
				lastCategory = cmd.category;
				groups.push({
					category: cmd.category,
					label: getCategoryLabel(cmd.category),
					commands: filteredCommands.filter((c) => c.category === cmd.category),
				});
			}
		}
		return groups;
	});

	// Recent items (commands + entities, balanced & sorted by frecency)
	let recentItems = $state<RecentItem[]>([]);

	// ── Unified result list ──

	type ResultItem =
		| { kind: 'command'; command: Command & { score: number } }
		| { kind: 'recent'; item: RecentItem }
		| { kind: 'entity'; hit: (typeof entityResults)[number] };

	let allItems = $derived.by((): ResultItem[] => {
		const items: ResultItem[] = [];
		// In empty state, prepend recents
		if (!query) {
			for (const ri of recentItems) {
				items.push({ kind: 'recent', item: ri });
			}
		}
		for (const cmd of filteredCommands) {
			items.push({ kind: 'command', command: cmd });
		}
		for (const hit of entityResults) {
			items.push({ kind: 'entity', hit });
		}
		return items;
	});

	// Track where entity results start for section headers
	let recentCount = $derived(!query ? recentItems.length : 0);
	let entityStartIndex = $derived(recentCount + filteredCommands.length);

	// ── Input handling ──

	let debounceTimer: ReturnType<typeof setTimeout>;
	function handleInput() {
		clearTimeout(debounceTimer);
		if (!isCommandMode && query.trim()) {
			debounceTimer = setTimeout(() => searchEntities(query), 200);
		} else {
			entityResults = [];
		}
	}

	function navigateToPath(path: string) {
		open = false;
		query = '';
		entityResults = [];
		goto(path);
	}

	function selectItem(item: ResultItem) {
		if (item.kind === 'command') {
			recordCommandUsage(item.command.id);
			navigateToPath(item.command.path);
		} else if (item.kind === 'recent') {
			const ri = item.item;
			if (ri.kind === 'command') {
				recordCommandUsage(ri.command.id);
				navigateToPath(ri.command.path);
			} else {
				recordEntityVisit({ id: ri.entity.id, name: ri.entity.name, type: ri.entity.type, route: ri.entity.route });
				navigateToPath(ri.entity.route);
			}
		} else {
			const route = getEntityRoute(item.hit);
			recordEntityVisit({ id: item.hit.global_id ?? item.hit.objectID, name: item.hit.name, type: item.hit.type, route });
			navigateToPath(route);
		}
	}

	// Prefetch the currently selected item
	$effect(() => {
		const item = allItems[selectedIndex];
		if (!item) return;
		if (item.kind === 'command') {
			preloadData(item.command.path);
		} else if (item.kind === 'recent') {
			const ri = item.item;
			preloadData(ri.kind === 'command' ? ri.command.path : ri.entity.route);
		} else {
			preloadData(getEntityRoute(item.hit));
		}
	});

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'ArrowDown') {
			e.preventDefault();
			selectedIndex = Math.min(selectedIndex + 1, allItems.length - 1);
		} else if (e.key === 'ArrowUp') {
			e.preventDefault();
			selectedIndex = Math.max(selectedIndex - 1, 0);
		} else if (e.key === 'Enter' && allItems[selectedIndex]) {
			e.preventDefault();
			selectItem(allItems[selectedIndex]);
		}
	}

	$effect(() => {
		if (!open) return;
		// Wrap in untrack so this effect ONLY depends on `open` — no other reactive state
		untrack(() => {
			const preserve = query;
			entityResults = [];
			selectedIndex = 0;
			if (!preserve) query = '';
			// Load recents from localStorage (client-side only), balanced 3+3 cap of 6
			recentItems = getCombinedRecents({ isStaff });
		});
	});

	// Close on page navigation
	$effect(() => {
		const _path = page.url.pathname;
		untrack(() => { open = false; });
	});

	onMount(() => {
		function globalKeydown(e: KeyboardEvent) {
			if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
				e.preventDefault();
				if (e.shiftKey) {
					// Shift+Cmd+K: open in command mode
					if (!open) {
						query = '>';
						open = true;
					} else {
						open = false;
					}
				} else {
					open = !open;
				}
			}
		}
		window.addEventListener('keydown', globalKeydown);
		return () => window.removeEventListener('keydown', globalKeydown);
	});

	// ── Helpers for section headers ──

	function commandIndexInFlat(cmdIndex: number): number {
		// The flat index of the nth command in allItems, after any recents
		return recentCount + cmdIndex;
	}

	let scrollContainer = $state<HTMLElement | null>(null);

	// Scroll selected item into view
	$effect(() => {
		const _idx = selectedIndex; // track
		if (scrollContainer) {
			const active = scrollContainer.querySelector('[data-active="true"]');
			if (active) {
				active.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
			}
		}
	});

	function isFirstInCategory(cmd: Command & { score: number }, cmdIndex: number): boolean {
		if (cmdIndex === 0) return true;
		return filteredCommands[cmdIndex - 1].category !== cmd.category;
	}
</script>

<Dialog.Root bind:open>
	<Dialog.Portal>
		<Dialog.Overlay
			class="fixed inset-0 z-50 bg-black/80 animate-fade-in"
		/>
		<Dialog.Content
			class="fixed inset-0 z-50 flex items-start justify-center pt-[12vh]"
			onOpenAutoFocus={(e) => {
				e.preventDefault();
				inputEl?.focus();
			}}
			onkeydown={handleKeydown}
		>
			<Dialog.Title class="sr-only">Command palette</Dialog.Title>
			<div
				class="w-full max-w-lg animate-slide-down border border-border-subtle bg-hull shadow-glow-amber"
			>
				<!-- Search header -->
				<div class="flex items-center gap-2 border-b border-border-dim px-3 py-2">
					<span class="machine-text text-[9px] text-accent-amber/50">{isCommandMode ? 'CMD>' : 'QUERY>'}</span>
					<Search class="h-3.5 w-3.5 shrink-0 text-accent-amber/40" />
					<input
						bind:this={inputEl}
						bind:value={query}
						oninput={handleInput}
						placeholder={isCommandMode ? 'TYPE A COMMAND...' : 'SEARCH ENTITIES AND COMMANDS...'}
						class="flex-1 bg-transparent text-sm text-accent-amber placeholder:text-text-muted focus:outline-none"
					/>
					<Dialog.Close class="text-text-muted hover:text-accent-amber">
						<X class="h-3.5 w-3.5" />
					</Dialog.Close>
				</div>

				<!-- Results -->
				<div class="max-h-80 overflow-y-auto" bind:this={scrollContainer}>
					{#if allItems.length > 0}
						<!-- Recent items (empty state only) -->
						{#if !query && recentItems.length > 0}
							<div class="px-3 pt-2 pb-1 flex items-center gap-1.5">
								<Clock class="h-3 w-3 text-text-muted opacity-50" />
								<span class="machine-text text-[9px] text-text-muted">RECENT</span>
							</div>
							{#each recentItems as ri, idx}
								{#if ri.kind === 'command'}
									{@const Icon = ri.command.icon}
									<button
										data-active={idx === selectedIndex}
										class={cn(
											'flex w-full items-center gap-2.5 px-3 py-2 text-left text-xs transition-colors border-l-2',
											idx === selectedIndex
												? 'bg-accent-amber/8 text-accent-amber border-accent-amber'
												: 'text-text-secondary hover:bg-accent-amber/5 hover:text-text-primary border-transparent',
										)}
										onclick={() => selectItem(allItems[idx])}
										onmouseenter={() => { selectedIndex = idx; preloadData(ri.command.path); }}
									>
										<Icon class="h-3.5 w-3.5 shrink-0 opacity-50" />
										<div class="min-w-0 flex-1">
											<div class="truncate uppercase tracking-wider">{ri.command.label}</div>
										</div>
										<ChevronRight class="h-3 w-3 shrink-0 opacity-30" />
									</button>
								{:else}
									{@const Icon = getEntityIcon(ri.entity.type)}
									<button
										data-active={idx === selectedIndex}
										class={cn(
											'flex w-full items-center gap-2.5 px-3 py-2 text-left text-xs transition-colors border-l-2',
											idx === selectedIndex
												? 'bg-accent-amber/8 text-accent-amber border-accent-amber'
												: 'text-text-secondary hover:bg-accent-amber/5 hover:text-text-primary border-transparent',
										)}
										onclick={() => selectItem(allItems[idx])}
										onmouseenter={() => { selectedIndex = idx; preloadData(ri.entity.route); }}
									>
										<Icon class="h-3.5 w-3.5 shrink-0 opacity-50" />
										<div class="min-w-0 flex-1">
											<div class="truncate uppercase tracking-wider">{ri.entity.name}</div>
										</div>
										<span class="machine-text shrink-0 text-[9px] text-text-muted">{ri.entity.type}</span>
									</button>
								{/if}
							{/each}
						{/if}

						<!-- Command results -->
						{#each filteredCommands as cmd, cmdIdx}
							{@const flatIdx = commandIndexInFlat(cmdIdx)}
							{@const Icon = cmd.icon}
							{#if isFirstInCategory(cmd, cmdIdx)}
								<div class="px-3 pt-2 pb-1">
									<span class="machine-text text-[9px] text-text-muted">{getCategoryLabel(cmd.category)}</span>
								</div>
							{/if}
							<button
								data-active={flatIdx === selectedIndex}
								class={cn(
									'flex w-full items-center gap-2.5 px-3 py-2 text-left text-xs transition-colors border-l-2',
									flatIdx === selectedIndex
										? 'bg-accent-amber/8 text-accent-amber border-accent-amber'
										: 'text-text-secondary hover:bg-accent-amber/5 hover:text-text-primary border-transparent',
								)}
								onclick={() => selectItem(allItems[flatIdx])}
								onmouseenter={() => { selectedIndex = flatIdx; preloadData(cmd.path); }}
							>
								<Icon class="h-3.5 w-3.5 shrink-0 opacity-50" />
								<div class="min-w-0 flex-1">
									<div class="truncate uppercase tracking-wider">{cmd.label}</div>
								</div>
								<ChevronRight class="h-3 w-3 shrink-0 opacity-30" />
							</button>
						{/each}
						{#if entityResults.length > 0}
							<div class="px-3 pt-2 pb-1">
								<span class="machine-text text-[9px] text-text-muted">SCAN RESULTS</span>
							</div>
							{#each entityResults as hit, hitIdx}
								{@const flatIdx = entityStartIndex + hitIdx}
								{@const Icon = getEntityIcon(hit.type)}
								<button
									data-active={flatIdx === selectedIndex}
									class={cn(
										'flex w-full items-center gap-2.5 px-3 py-2 text-left text-xs transition-colors border-l-2',
										flatIdx === selectedIndex
											? 'bg-accent-amber/8 text-accent-amber border-accent-amber'
											: 'text-text-secondary hover:bg-accent-amber/5 hover:text-text-primary border-transparent',
									)}
									onclick={() => selectItem(allItems[flatIdx])}
									onmouseenter={() => { selectedIndex = flatIdx; preloadData(getEntityRoute(hit)); }}
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
						{/if}
					{:else if query && !isCommandMode && !searching}
						<div class="px-3 py-6 text-center">
							<p class="machine-text text-text-muted">NO RECORDS MATCH QUERY</p>
						</div>
					{:else if query && isCommandMode}
						<div class="px-3 py-6 text-center">
							<p class="machine-text text-text-muted">NO MATCHING DIRECTIVES</p>
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
					<span class="machine-text text-[9px] text-text-muted ml-auto">
						<kbd class="border border-border-dim bg-void px-1 py-px text-[9px]">&gt;</kbd>
						DIRECTIVES
					</span>
				</div>
			</div>
		</Dialog.Content>
	</Dialog.Portal>
</Dialog.Root>
