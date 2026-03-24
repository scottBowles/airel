<script lang="ts">
	import { toast } from 'svelte-sonner';

	import { getOperationInfoMessage } from '$lib/mutation-errors';
	import LogRelationPicker from './LogRelationPicker.svelte';
	import {
		LOG_RELATION_KEYS,
		type EditableLogData,
		type LogEditorOptions,
		type LogRelationKey,
		type RelationOption,
		sortRelationOptions
	} from './log-editor-types';

	let {
		log,
		relationOptions,
		onSave,
		onDiscard
	}: {
		log: EditableLogData;
		relationOptions: LogEditorOptions;
		onSave: (draft: EditableLogData) => Promise<{
			__typename?: string | null;
			messages?: Array<{ message?: string }> | null;
		} | undefined>;
		onDiscard: () => Promise<{
			__typename?: string | null;
			messages?: Array<{ message?: string }> | null;
		} | undefined>;
	} = $props();

	function cloneOptions(options: RelationOption[]) {
		return sortRelationOptions(options.map((option) => ({ ...option })));
	}

	const relatedEntityKeys: LogRelationKey[] = ['artifacts', 'associations', 'characters', 'items', 'places', 'races'];

	let title = $state('');
	let brief = $state('');
	let synopsis = $state('');
	let gameDate = $state('');
	let relationState = $state<Record<LogRelationKey, RelationOption[]>>({
		artifacts: [],
		associations: [],
		characters: [],
		items: [],
		places: [],
		placesSetIn: [],
		races: []
	});
	let savePending = $state(false);
	let discardPending = $state(false);
	let errorMessage = $state('');
	let initializedForLogId = $state('');

	const relationTitles: Record<LogRelationKey, string> = {
		artifacts: 'Artifacts',
		associations: 'Associations',
		characters: 'Characters',
		items: 'Items',
		places: 'Places',
		placesSetIn: 'Places Set In',
		races: 'Races'
	};

	$effect(() => {
		if (initializedForLogId === log.id) {
			return;
		}

		title = log.title;
		brief = log.brief;
		synopsis = log.synopsis;
		gameDate = log.gameDate;
		relationState = {
			artifacts: cloneOptions(log.artifacts),
			associations: cloneOptions(log.associations),
			characters: cloneOptions(log.characters),
			items: cloneOptions(log.items),
			places: cloneOptions(log.places),
			placesSetIn: cloneOptions(log.placesSetIn),
			races: cloneOptions(log.races)
		};
		errorMessage = '';
		initializedForLogId = log.id;
	});

	let busy = $derived(savePending || discardPending);
	let dirty = $derived.by(() => {
		if (
			title !== log.title ||
			brief !== log.brief ||
			synopsis !== log.synopsis ||
			gameDate !== log.gameDate
		) {
			return true;
		}

		return LOG_RELATION_KEYS.some((key) => {
			const currentIds = relationState[key].map((option) => option.id).join('|');
			const initialIds = log[key].map((option) => option.id).join('|');

			return currentIds !== initialIds;
		});
	});

	function updateRelation(key: LogRelationKey, next: RelationOption[]) {
		relationState = {
			...relationState,
			[key]: next
		};
	}

	function buildDraft(): EditableLogData {
		return {
			id: log.id,
			title,
			brief,
			synopsis,
			gameDate,
			artifacts: cloneOptions(relationState.artifacts),
			associations: cloneOptions(relationState.associations),
			characters: cloneOptions(relationState.characters),
			items: cloneOptions(relationState.items),
			places: cloneOptions(relationState.places),
			placesSetIn: cloneOptions(relationState.placesSetIn),
			races: cloneOptions(relationState.races)
		};
	}

	async function submitForm(event: SubmitEvent) {
		event.preventDefault();
		if (busy) {
			return;
		}

		errorMessage = '';
		savePending = true;

		try {
			const payload = await onSave(buildDraft());
			const operationInfoMessage = getOperationInfoMessage(payload, 'Failed to save log changes.');

			if (operationInfoMessage) {
				errorMessage = operationInfoMessage;
				toast.error(operationInfoMessage);
				return;
			}
		} catch (error) {
			console.error('Failed to save log changes:', error);
			errorMessage = 'Failed to save log changes.';
			toast.error(errorMessage);
		} finally {
			savePending = false;
		}
	}

	async function discardChanges() {
		if (busy) {
			return;
		}

		errorMessage = '';
		discardPending = true;

		try {
			const payload = await onDiscard();
			const operationInfoMessage = getOperationInfoMessage(payload, 'Failed to discard changes.');

			if (operationInfoMessage) {
				errorMessage = operationInfoMessage;
				toast.error(operationInfoMessage);
				return;
			}
		} catch (error) {
			console.error('Failed to discard log changes:', error);
			errorMessage = 'Failed to discard changes.';
			toast.error(errorMessage);
		} finally {
			discardPending = false;
		}
	}
</script>

<form class="space-y-6" onsubmit={submitForm}>
	<div class="rounded-sm border border-slate-700/55 bg-slate-900/72 p-4 shadow-[0_0_0_1px_rgba(255,255,255,0.02),0_8px_18px_rgba(0,0,0,0.16)]">
		<div class="flex flex-col gap-3 border-b border-white/5 pb-4 sm:flex-row sm:items-center sm:justify-between">
			<div>
				<h2 class="font-display text-industrial-amber text-lg tracking-[0.16em] uppercase">
					Log Editor
				</h2>
				<p class="mt-1 text-sm text-slate-400">Changes remain local until you save.</p>
			</div>
			<div class="flex flex-col gap-2 sm:flex-row">
				<button
					type="button"
					onclick={discardChanges}
					disabled={busy}
					class="inline-flex min-h-11 items-center justify-center rounded-sm border border-slate-700 px-4 font-mono text-xs tracking-[0.18em] text-slate-300 uppercase transition-colors hover:border-slate-500 hover:text-white disabled:opacity-50"
				>
					{discardPending ? 'DISCARDING...' : 'DISCARD CHANGES'}
				</button>
				<button
					type="submit"
					disabled={busy || !dirty}
					class="industrial-btn text-industrial-amber border-industrial-dim hover:border-industrial-amber hover:text-industrial-amber min-w-40 justify-center bg-slate-950 disabled:opacity-50"
				>
					{savePending ? 'SAVING...' : 'SAVE CHANGES'}
				</button>
			</div>
		</div>

		<div class="mt-4 grid gap-4 lg:grid-cols-2">
			<div class="space-y-2 lg:col-span-2">
				<label class="font-mono text-[11px] tracking-[0.22em] text-slate-500 uppercase" for="log-title-input">
					Title
				</label>
				<input id="log-title-input" bind:value={title} class="industrial-input w-full" disabled={busy} />
			</div>

			<div class="space-y-2">
				<label class="font-mono text-[11px] tracking-[0.22em] text-slate-500 uppercase" for="log-date-input">
					Game Date
				</label>
				<input
					id="log-date-input"
					bind:value={gameDate}
					type="date"
					class="industrial-input w-full"
					disabled={busy}
				/>
			</div>

			<div class="space-y-2 lg:col-span-2">
				<label class="font-mono text-[11px] tracking-[0.22em] text-slate-500 uppercase" for="log-brief-input">
					Brief
				</label>
				<textarea
					id="log-brief-input"
					bind:value={brief}
					rows="3"
					class="industrial-input w-full resize-y py-3"
					disabled={busy}
				></textarea>
			</div>

			<div class="space-y-2 lg:col-span-2">
				<label class="font-mono text-[11px] tracking-[0.22em] text-slate-500 uppercase" for="log-synopsis-input">
					Synopsis
				</label>
				<textarea
					id="log-synopsis-input"
					bind:value={synopsis}
					rows="8"
					class="industrial-input w-full resize-y py-3"
					disabled={busy}
				></textarea>
			</div>
		</div>
	</div>

	<div class="space-y-3 rounded-sm border border-slate-800/80 bg-slate-950/60 p-4">
		<div class="font-display text-industrial-amber text-sm tracking-[0.16em] uppercase">
			Places Set In
		</div>
		<LogRelationPicker
			title={relationTitles.placesSetIn}
			placeholder="Search places set in..."
			selected={relationState.placesSetIn}
			options={relationOptions.placesSetIn}
			disabled={busy}
			onChange={(next: RelationOption[]) => updateRelation('placesSetIn', next)}
		/>
	</div>

	<div class="space-y-3 rounded-sm border border-slate-800/80 bg-slate-950/60 p-4">
		<div class="font-display text-industrial-amber text-sm tracking-[0.16em] uppercase">
			Found In This Log
		</div>
		<div class="grid gap-4 xl:grid-cols-2">
			{#each relatedEntityKeys as relationKey (relationKey)}
				<LogRelationPicker
					title={relationTitles[relationKey]}
					placeholder={`Search ${relationTitles[relationKey].toLowerCase()}...`}
					selected={relationState[relationKey]}
					options={relationOptions[relationKey]}
					disabled={busy}
					onChange={(next: RelationOption[]) => updateRelation(relationKey, next)}
				/>
			{/each}
		</div>
	</div>

	{#if errorMessage}
		<p class="rounded-sm border border-rose-900/60 bg-rose-950/40 px-4 py-3 text-sm text-rose-300">
			{errorMessage}
		</p>
	{/if}
</form>