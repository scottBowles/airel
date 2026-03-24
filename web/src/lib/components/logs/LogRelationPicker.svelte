<script lang="ts">
	import { sortRelationOptions, type RelationOption } from './log-editor-types';

	function scoreFuzzyMatch(text: string, query: string) {
		if (!query) {
			return 0;
		}

		const normalizedText = text.toLowerCase();
		const normalizedQuery = query.toLowerCase();

		if (normalizedText.includes(normalizedQuery)) {
			const index = normalizedText.indexOf(normalizedQuery);
			const startsWord = index === 0 || /[\s([{_-]/.test(normalizedText[index - 1] ?? '');

			return 1000 - index * 4 + (startsWord ? 40 : 0);
		}

		let score = 0;
		let searchIndex = 0;
		let previousMatchIndex = -1;

		for (const character of normalizedQuery) {
			const matchIndex = normalizedText.indexOf(character, searchIndex);

			if (matchIndex === -1) {
				return null;
			}

			const isConsecutive = previousMatchIndex >= 0 && matchIndex === previousMatchIndex + 1;
			const startsWord = matchIndex === 0 || /[\s([{_-]/.test(normalizedText[matchIndex - 1] ?? '');
			const gap = previousMatchIndex >= 0 ? matchIndex - previousMatchIndex - 1 : matchIndex;

			score += 12;
			score += isConsecutive ? 18 : 0;
			score += startsWord ? 10 : 0;
			score -= gap;

			previousMatchIndex = matchIndex;
			searchIndex = matchIndex + 1;
		}

		return score;
	}

	function getOptionMatchScore(option: RelationOption, normalizedQuery: string) {
		if (!normalizedQuery) {
			return 0;
		}

		const nameScore = scoreFuzzyMatch(option.name, normalizedQuery);
		const secondaryScore = option.secondaryText
			? scoreFuzzyMatch(option.secondaryText, normalizedQuery)
			: null;

		if (nameScore === null && secondaryScore === null) {
			return null;
		}

		return Math.max(nameScore ?? Number.NEGATIVE_INFINITY, (secondaryScore ?? Number.NEGATIVE_INFINITY) - 25);
	}

	let {
		title,
		placeholder = 'Search records...',
		selected,
		options,
		disabled = false,
		onChange
	}: {
		title: string;
		placeholder?: string;
		selected: RelationOption[];
		options: RelationOption[];
		disabled?: boolean;
		onChange: (next: RelationOption[]) => void;
	} = $props();

	let query = $state('');
	let highlightedIndex = $state(-1);

	let selectedIds = $derived.by(() => new Set(selected.map((option) => option.id)));
	let sortedSelected = $derived.by(() => sortRelationOptions(selected));
	let filteredOptions = $derived.by(() => {
		const normalizedQuery = query.trim().toLowerCase();

		return sortRelationOptions(options)
			.filter((option) => !selectedIds.has(option.id))
			.map((option) => ({
				option,
				score: getOptionMatchScore(option, normalizedQuery)
			}))
			.filter(({ score }) => score !== null)
			.sort((left, right) => {
				if ((right.score ?? 0) !== (left.score ?? 0)) {
					return (right.score ?? 0) - (left.score ?? 0);
				}

				return left.option.name.localeCompare(right.option.name, undefined, { sensitivity: 'base' });
			})
			.map(({ option }) => option)
			.slice(0, 5);
	});
	let activeHighlightedIndex = $derived.by(() => {
		if (filteredOptions.length === 0) {
			return -1;
		}

		if (highlightedIndex < 0 || highlightedIndex >= filteredOptions.length) {
			return 0;
		}

		return highlightedIndex;
	});

	function addOption(option: RelationOption) {
		onChange([...selected, option]);
		query = '';
		highlightedIndex = -1;
	}

	function removeOption(optionId: string) {
		onChange(selected.filter((option) => option.id !== optionId));
	}

	function handleKeydown(event: KeyboardEvent) {
		if (disabled) {
			return;
		}

		if (event.key === 'ArrowDown') {
			event.preventDefault();
			if (filteredOptions.length === 0) return;
			highlightedIndex =
				activeHighlightedIndex < 0 ? 0 : (activeHighlightedIndex + 1) % filteredOptions.length;
			return;
		}

		if (event.key === 'ArrowUp') {
			event.preventDefault();
			if (filteredOptions.length === 0) return;
			highlightedIndex =
				activeHighlightedIndex < 0
					? filteredOptions.length - 1
					: (activeHighlightedIndex - 1 + filteredOptions.length) % filteredOptions.length;
			return;
		}

		if (event.key === 'Enter' && activeHighlightedIndex >= 0 && filteredOptions[activeHighlightedIndex]) {
			event.preventDefault();
			addOption(filteredOptions[activeHighlightedIndex]);
			return;
		}

		if (event.key === 'Escape' && query) {
			event.preventDefault();
			query = '';
			highlightedIndex = -1;
		}
	}

	function getOptionClasses(index: number) {
		const baseClasses =
			'flex w-full items-start justify-between gap-3 rounded-sm border px-3 py-2 text-left transition-colors';

		return index === activeHighlightedIndex
			? `${baseClasses} border-industrial-amber bg-slate-900`
			: `${baseClasses} border-slate-800 bg-slate-950/40`;
	}
</script>

<div class="space-y-3 rounded-sm border border-slate-800/80 bg-slate-950/60 p-3">
	<div class="font-mono text-[11px] tracking-[0.22em] text-slate-500 uppercase">{title}</div>

	{#if sortedSelected.length > 0}
		<div class="flex flex-wrap gap-2">
			{#each sortedSelected as option (option.id)}
				<div class="flex items-center gap-1.5 rounded-sm border border-slate-700 bg-slate-900 px-2 py-1 text-xs text-slate-200">
					<div class="min-w-0">
						{#if option.href}
							<a
								href={option.href}
								class="truncate underline decoration-transparent underline-offset-2 transition-colors hover:text-white hover:decoration-white/50"
							>
								{option.name}
							</a>
						{:else}
							<div class="truncate">{option.name}</div>
						{/if}
						{#if option.secondaryText}
							<div class="truncate text-[10px] leading-tight text-slate-500">{option.secondaryText}</div>
						{/if}
					</div>
					<button
						type="button"
						onclick={() => removeOption(option.id)}
						disabled={disabled}
						class="inline-flex h-5 w-5 shrink-0 cursor-pointer items-center justify-center rounded-sm text-base leading-none text-slate-500 transition-colors hover:text-rose-300 disabled:cursor-not-allowed disabled:opacity-50"
						aria-label={`Remove ${option.name}`}
					>
						<span aria-hidden="true">×</span>
					</button>
				</div>
			{/each}
		</div>
	{:else}
		<p class="text-sm text-slate-500">No records selected.</p>
	{/if}

	<div class="space-y-2">
		<input
			bind:value={query}
			onkeydown={handleKeydown}
			type="text"
			role="combobox"
			aria-expanded={filteredOptions.length > 0}
			aria-controls={`picker-options-${title}`}
			aria-autocomplete="list"
			placeholder={placeholder}
			class="industrial-input w-full bg-slate-950"
			disabled={disabled}
		/>

		{#if filteredOptions.length > 0}
			<ul
				id={`picker-options-${title}`}
				role="listbox"
				class="space-y-1 rounded-sm border border-slate-800 bg-slate-950/90 p-2"
			>
				{#each filteredOptions as option, index (option.id)}
					<li>
						<button
							type="button"
							role="option"
							aria-selected={index === activeHighlightedIndex}
							onclick={() => addOption(option)}
							onmouseenter={() => {
								highlightedIndex = index;
							}}
							class={getOptionClasses(index)}
						>
							<div class="min-w-0">
								<div class="truncate text-sm text-slate-200">{option.name}</div>
								{#if option.secondaryText}
									<div class="truncate text-xs text-slate-500">{option.secondaryText}</div>
								{/if}
							</div>
							<div class="font-mono text-[10px] tracking-[0.18em] text-slate-500 uppercase">
								Add
							</div>
						</button>
					</li>
				{/each}
			</ul>
		{:else if query.trim()}
			<p class="text-sm text-slate-500">No matching records.</p>
		{/if}
	</div>
</div>