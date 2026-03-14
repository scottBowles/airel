<script lang="ts">
	import { goto } from '$app/navigation';
	import { tick } from 'svelte';
	import { CornerDownLeft, LoaderCircle, Search } from 'lucide-svelte';

	import CldImage from '$lib/components/images/CldImage.svelte';
	import ScifiPlaceholder from '$lib/components/ui/ScifiPlaceholder.svelte';
	import { algoliaConfigured, searchGlobalRecords } from '$lib/search/algolia';
	import { SEARCH_INDEX_CONFIGS, type SearchResult } from '$lib/search/types';

	let {
		open = false,
		onClose = () => {}
	}: {
		open?: boolean;
		onClose?: () => void;
	} = $props();

	let inputRef = $state<HTMLInputElement | null>(null);
	let query = $state('');
	let results = $state<SearchResult[]>([]);
	let highlightedIndex = $state(-1);
	let loading = $state(false);
	let errorMessage = $state('');
	let requestSequence = 0;
	let debounceTimer: ReturnType<typeof setTimeout> | null = null;

	const searchableTypes = SEARCH_INDEX_CONFIGS.map((config) => config.label).join(', ');
	const hasQuery = $derived(query.trim().length > 0);

	function clearDebounceTimer() {
		if (debounceTimer) {
			clearTimeout(debounceTimer);
			debounceTimer = null;
		}
	}

	function resetSearchState() {
		clearDebounceTimer();
		requestSequence += 1;
		query = '';
		results = [];
		highlightedIndex = -1;
		loading = false;
		errorMessage = '';
	}

	function closeSearch() {
		resetSearchState();
		onClose();
	}

	function moveHighlight(step: number) {
		if (results.length === 0) return;

		if (highlightedIndex < 0) {
			highlightedIndex = step > 0 ? 0 : results.length - 1;
			return;
		}

		highlightedIndex = (highlightedIndex + step + results.length) % results.length;
	}

	async function selectResult(result: SearchResult) {
		await goto(result.href as Parameters<typeof goto>[0]);
		closeSearch();
	}

	function getResultDomId(index: number) {
		return `global-search-result-${index}`;
	}

	function getResultClasses(index: number) {
		const baseClasses =
			'group flex w-full items-start gap-3 border px-3 py-3 text-left transition-colors sm:px-4';

		if (index === highlightedIndex) {
			return `${baseClasses} border-industrial-amber bg-slate-900`;
		}

		return `${baseClasses} border-slate-800 bg-slate-950/40`;
	}

	function handleInputKeydown(event: KeyboardEvent) {
		if (event.key === 'ArrowDown') {
			event.preventDefault();
			moveHighlight(1);
			return;
		}

		if (event.key === 'ArrowUp') {
			event.preventDefault();
			moveHighlight(-1);
			return;
		}

		if (event.key === 'Enter' && highlightedIndex >= 0) {
			event.preventDefault();
			void selectResult(results[highlightedIndex]);
			return;
		}

		if (event.key === 'Escape') {
			event.preventDefault();
			closeSearch();
		}
	}

	$effect(() => {
		if (!open) {
			resetSearchState();
			return;
		}

		void tick().then(() => {
			inputRef?.focus();
			inputRef?.select();
		});
	});

	$effect(() => {
		if (!open || !algoliaConfigured) {
			clearDebounceTimer();
			return;
		}

		const normalizedQuery = query.trim();

		if (!normalizedQuery) {
			clearDebounceTimer();
			results = [];
			highlightedIndex = -1;
			loading = false;
			errorMessage = '';
			return;
		}

		const currentRequest = ++requestSequence;
		clearDebounceTimer();
		loading = true;
		errorMessage = '';

		debounceTimer = setTimeout(async () => {
			try {
				const nextResults = await searchGlobalRecords(normalizedQuery);

				if (currentRequest !== requestSequence || !open) {
					return;
				}

				results = nextResults;
				highlightedIndex = nextResults.length > 0 ? 0 : -1;
			} catch (error) {
				if (currentRequest !== requestSequence || !open) {
					return;
				}

				console.error('Global search failed', error);
				results = [];
				highlightedIndex = -1;
				errorMessage = 'Search is temporarily unavailable.';
			} finally {
				if (currentRequest === requestSequence && open) {
					loading = false;
				}
			}
		}, 180);

		return () => {
			clearDebounceTimer();
		};
	});
</script>

{#if open}
	<button
		type="button"
		class="fixed inset-0 z-60 bg-slate-950/80 backdrop-blur-sm"
		tabindex="-1"
		onclick={closeSearch}
		aria-label="Close global search"
	></button>

	<div
		role="dialog"
		aria-modal="true"
		aria-label="Global search"
		class="fixed inset-x-3 top-3 z-70 overflow-hidden border border-slate-700 bg-slate-950/96 shadow-[0_20px_60px_rgba(0,0,0,0.45)] md:top-6 md:left-1/2 md:right-auto md:w-[min(64rem,calc(100vw-4rem))] md:-translate-x-1/2"
	>
		<div class="border-b border-slate-800 bg-slate-900/90 px-4 py-4">
			<div class="flex items-center gap-3">
				<div
					class="flex h-10 w-10 shrink-0 items-center justify-center border border-slate-800 bg-slate-950 text-slate-400"
				>
					<Search size={16} strokeWidth={1.75} />
				</div>
				<input
					bind:this={inputRef}
					bind:value={query}
					onkeydown={handleInputKeydown}
					type="text"
					placeholder="Search Database"
					class="industrial-input min-w-0 flex-1 bg-slate-950"
					spellcheck="false"
					autocomplete="off"
					autocorrect="off"
					aria-label="Search database"
					aria-controls="global-search-results"
					aria-activedescendant={highlightedIndex >= 0 ? getResultDomId(highlightedIndex) : undefined}
				/>
				<button
					type="button"
					onclick={closeSearch}
					class="machine-text hidden min-h-11 shrink-0 items-center border border-slate-700 px-3 text-[11px] sm:inline-flex"
				>
					Esc
				</button>
			</div>

			<div class="mt-3 flex flex-wrap items-center justify-between gap-2 text-[11px] tracking-[0.18em] text-slate-500 uppercase">
				<div>{searchableTypes}</div>
				<div class="flex items-center gap-2">
					{#if loading}
						<LoaderCircle class="animate-spin" size={12} />
						<span>Scanning</span>
					{:else if results.length > 0}
						<span>{results.length} result{results.length === 1 ? '' : 's'}</span>
					{/if}
				</div>
			</div>
		</div>

		<div class="max-h-[min(70dvh,34rem)] overflow-y-auto p-2 sm:p-3">
			{#if !algoliaConfigured}
				<div class="border border-slate-800 bg-slate-900/60 px-4 py-6 text-sm text-slate-400">
					Set <span class="font-mono text-slate-200">PUBLIC_ALGOLIA_APP_ID</span> and
					<span class="font-mono text-slate-200">PUBLIC_ALGOLIA_SEARCH_API_KEY</span> to enable
					global search.
				</div>
			{:else if errorMessage}
				<div class="border border-red-500/30 bg-red-500/10 px-4 py-6 text-sm text-red-200">
					{errorMessage}
				</div>
			{:else if !hasQuery}
				<div class="border border-slate-800 bg-slate-900/50 px-4 py-6 text-sm text-slate-400">
					Type to search database. Use the arrow keys to move, then press Enter to open the
					selected record.
				</div>
			{:else if !loading && results.length === 0}
				<div class="border border-slate-800 bg-slate-900/50 px-4 py-6 text-sm text-slate-400">
					No results found.
				</div>
			{:else}
				<ul id="global-search-results" class="space-y-2" role="listbox">
					{#each results as result, index (result.indexName + '-' + result.objectID)}
						<li>
							<button
								id={getResultDomId(index)}
								type="button"
								role="option"
								aria-selected={index === highlightedIndex}
								onclick={() => selectResult(result)}
								onmouseenter={() => (highlightedIndex = index)}
								class={getResultClasses(index)}
							>
								{#if result.thumbnail}
									<div class="db-card-thumb h-12 w-12 sm:h-14 sm:w-14">
										<CldImage
											id={result.thumbnail}
											alt={result.name}
											width={56}
											height={56}
											class="h-full w-full object-cover"
										/>
									</div>
								{:else}
									<ScifiPlaceholder type={result.placeholderType} />
								{/if}

								<div class="min-w-0 flex-1">
									<div class="flex items-start justify-between gap-3">
										<div class="min-w-0">
											<h3 class="font-display truncate text-base text-slate-100 uppercase sm:text-lg">
												{result.name}
											</h3>
											<div class="mt-1 font-mono text-[11px] tracking-[0.2em] text-slate-500 uppercase">
												{result.indexLabel}
											</div>
										</div>

										<div class="hidden items-center gap-2 font-mono text-[11px] text-slate-500 sm:flex">
											<CornerDownLeft size={12} />
											<span>Open</span>
										</div>
									</div>

									<p class="mt-2 line-clamp-2 text-sm leading-relaxed text-slate-400">
										{result.description || 'No description available.'}
									</p>
								</div>
							</button>
						</li>
					{/each}
				</ul>
			{/if}
		</div>
	</div>
{/if}
