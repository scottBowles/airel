<script lang="ts">
	import { createEntitySearch, type EntitySearchHit } from '$lib/entitySearch';
	import Search from '@lucide/svelte/icons/search';
	import X from '@lucide/svelte/icons/x';

	let {
		entityType,
		onselect,
		exclude = [],
		placeholder,
	}: {
		entityType: 'Association' | 'Artifact' | 'Character' | 'Item' | 'Place' | 'Race';
		onselect: (entity: { id: string; name: string }) => void;
		exclude?: string[];
		placeholder?: string;
	} = $props();

	let query = $state('');
	let results = $state<EntitySearchHit[]>([]);
	let showDropdown = $state(false);
	let searching = $state(false);
	let inputEl = $state<HTMLInputElement | null>(null);
	let activeIndex = $state(-1);
	let listboxId = $state(`ep-listbox-${Math.random().toString(36).slice(2, 8)}`);

	const runSearch = createEntitySearch();

	async function search(q: string) {
		if (!q.trim()) {
			results = [];
			return;
		}
		searching = true;
		// Ask for extra hits so up to 10 remain after dropping the excluded ones.
		const hits = await runSearch(q, {
			types: [entityType.toUpperCase() as Uppercase<typeof entityType>],
			limit: 10 + exclude.length,
		});
		if (hits === null) return; // superseded by a newer search
		results = hits.filter((h) => !exclude.includes(h.id)).slice(0, 10);
		searching = false;
	}

	let debounceTimer: ReturnType<typeof setTimeout>;
	function handleInput() {
		clearTimeout(debounceTimer);
		debounceTimer = setTimeout(() => search(query), 200);
		showDropdown = true;
		activeIndex = -1;
	}

	function select(hit: (typeof results)[number]) {
		onselect({ id: hit.id, name: hit.name });
		query = '';
		results = [];
		showDropdown = false;
		activeIndex = -1;
		inputEl?.focus();
	}

	function handleKeydown(e: KeyboardEvent) {
		if (!showDropdown || results.length === 0) return;
		if (e.key === 'ArrowDown') {
			e.preventDefault();
			activeIndex = activeIndex < results.length - 1 ? activeIndex + 1 : 0;
		} else if (e.key === 'ArrowUp') {
			e.preventDefault();
			activeIndex = activeIndex > 0 ? activeIndex - 1 : results.length - 1;
		} else if (e.key === 'Enter' && activeIndex >= 0) {
			e.preventDefault();
			select(results[activeIndex]);
		} else if (e.key === 'Escape') {
			showDropdown = false;
			activeIndex = -1;
		}
	}

	function handleBlur() {
		// Delay to allow click on dropdown item
		setTimeout(() => { showDropdown = false; }, 150);
	}
</script>

<div class="relative" role="group">
	<div class="flex items-center border border-border-dim bg-bg-inset">
		<Search class="ml-2 h-3 w-3 shrink-0 text-text-muted" />
		<input
			bind:this={inputEl}
			bind:value={query}
			oninput={handleInput}
			onfocus={() => { if (results.length) showDropdown = true; }}
			onblur={handleBlur}
			onkeydown={handleKeydown}
			placeholder={placeholder ?? `Search ${entityType.toLowerCase()}s...`}
			class="w-full bg-transparent px-2 py-1 text-xs text-text-primary outline-none placeholder:text-text-faint"
			role="combobox"
			aria-expanded={showDropdown && results.length > 0}
			aria-activedescendant={activeIndex >= 0 ? `${listboxId}-option-${activeIndex}` : undefined}
			aria-autocomplete="list"
			aria-controls={listboxId}
		/>
		{#if query}
			<button
				onclick={() => { query = ''; results = []; showDropdown = false; }}
				class="mr-1 cursor-pointer p-0.5 text-text-muted hover:text-accent-amber"
				aria-label="Clear search"
			>
				<X class="h-3 w-3" />
			</button>
		{/if}
	</div>

	{#if showDropdown && results.length > 0}
		<div id={listboxId} role="listbox" class="absolute z-50 mt-0.5 max-h-48 w-full overflow-y-auto border border-border-dim bg-hull shadow-lg">
			{#each results as hit, i}
				<button
					id="{listboxId}-option-{i}"
					role="option"
					aria-selected={i === activeIndex}
					onmousedown={(e) => { e.preventDefault(); select(hit); }}
					onmouseenter={() => { activeIndex = i; }}
					class="block w-full cursor-pointer px-2 py-1.5 text-left text-xs text-text-secondary transition-colors hover:bg-accent-amber/10 hover:text-accent-amber {i === activeIndex ? 'bg-accent-amber/10 text-accent-amber' : ''}"
				>
					{hit.name}
				</button>
			{/each}
		</div>
	{:else if showDropdown && query.trim() && !searching}
		<div class="absolute z-50 mt-0.5 w-full border border-border-dim bg-hull px-2 py-2 shadow-lg">
			<p class="text-[10px] text-text-muted">No results</p>
		</div>
	{/if}
</div>
