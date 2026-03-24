<script lang="ts">
	import { toast } from 'svelte-sonner';

	import LogRelationPicker from '$lib/components/logs/LogRelationPicker.svelte';
	import { getOperationInfoMessage } from '$lib/mutation-errors';
	import { sortRelationOptions, type RelationOption } from '$lib/components/logs/log-editor-types';
	import {
		DATABASE_RELATION_TITLES,
		DATABASE_RELATED_RELATION_KEYS,
		DEFAULT_DATABASE_ENTITY_DRAFT,
		PLACE_TYPE_OPTIONS,
		type DatabaseEntityDraft,
		type DatabaseEntityEditorConfig,
		type DatabaseEntityEditorOptions,
		type DatabasePrimaryRelationKey,
		type DatabaseRelatedRelationKey
	} from './database-entity-editor-types';

	const relatedRelationToOptionKey: Record<DatabaseRelatedRelationKey, keyof DatabaseEntityEditorOptions> = {
		relatedArtifacts: 'artifacts',
		relatedAssociations: 'associations',
		relatedCharacters: 'characters',
		relatedItems: 'items',
		relatedPlaces: 'places',
		relatedRaces: 'races'
	};

	let {
		entity,
		config,
		relationOptions,
		onSave,
		onDiscard
	}: {
		entity: DatabaseEntityDraft;
		config: DatabaseEntityEditorConfig;
		relationOptions: DatabaseEntityEditorOptions;
		onSave: (draft: DatabaseEntityDraft) => Promise<{
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

	function getSelectLabel(option: RelationOption) {
		return option.secondaryText ? `${option.name} - ${option.secondaryText}` : option.name;
	}

	let name = $state('');
	let description = $state('');
	let markdownNotes = $state('');
	let notes = $state('');
	let size = $state('');
	let placeType = $state('');
	let raceId = $state('');
	let parentPlaceId = $state('');
	let armorAcBonus = $state('');
	let equipmentBriefDescription = $state('');
	let weaponAttackBonus = $state('');
	let primaryRelationState = $state<Record<DatabasePrimaryRelationKey, RelationOption[]>>({
		artifacts: [],
		associations: [],
		characters: [],
		items: []
	});
	let relatedRelationState = $state<Record<DatabaseRelatedRelationKey, RelationOption[]>>({
		relatedArtifacts: [],
		relatedAssociations: [],
		relatedCharacters: [],
		relatedItems: [],
		relatedPlaces: [],
		relatedRaces: []
	});
	let savePending = $state(false);
	let discardPending = $state(false);
	let errorMessage = $state('');
	let initializedForEntityId = $state('');

	$effect(() => {
		if (initializedForEntityId === entity.id) {
			return;
		}

		name = entity.name;
		description = entity.description;
		markdownNotes = entity.markdownNotes;
		notes = entity.notes;
		size = entity.size;
		placeType = entity.placeType;
		raceId = entity.raceId;
		parentPlaceId = entity.parentPlaceId;
		armorAcBonus = entity.armorAcBonus;
		equipmentBriefDescription = entity.equipmentBriefDescription;
		weaponAttackBonus = entity.weaponAttackBonus;
		primaryRelationState = {
			artifacts: cloneOptions(entity.artifacts),
			associations: cloneOptions(entity.associations),
			characters: cloneOptions(entity.characters),
			items: cloneOptions(entity.items)
		};
		relatedRelationState = {
			relatedArtifacts: cloneOptions(entity.relatedArtifacts),
			relatedAssociations: cloneOptions(entity.relatedAssociations),
			relatedCharacters: cloneOptions(entity.relatedCharacters),
			relatedItems: cloneOptions(entity.relatedItems),
			relatedPlaces: cloneOptions(entity.relatedPlaces),
			relatedRaces: cloneOptions(entity.relatedRaces)
		};
		errorMessage = '';
		initializedForEntityId = entity.id;
	});

	let busy = $derived(savePending || discardPending);
	let relatedRelations = $derived(config.relatedRelations ?? DATABASE_RELATED_RELATION_KEYS);
	let primaryRelations = $derived(config.primaryRelations ?? []);
	let hasSinglePrimaryRelation = $derived(primaryRelations.length === 1);
	let dirty = $derived.by(() => {
		if (
			name !== entity.name ||
			description !== entity.description ||
			markdownNotes !== entity.markdownNotes ||
			notes !== entity.notes ||
			size !== entity.size ||
			placeType !== entity.placeType ||
			raceId !== entity.raceId ||
			parentPlaceId !== entity.parentPlaceId ||
			armorAcBonus !== entity.armorAcBonus ||
			equipmentBriefDescription !== entity.equipmentBriefDescription ||
			weaponAttackBonus !== entity.weaponAttackBonus
		) {
			return true;
		}

		for (const relation of primaryRelations) {
			const currentIds = primaryRelationState[relation.key].map((option) => option.id).join('|');
			const initialIds = entity[relation.key].map((option) => option.id).join('|');

			if (currentIds !== initialIds) {
				return true;
			}
		}

		for (const relationKey of relatedRelations) {
			const currentIds = relatedRelationState[relationKey].map((option) => option.id).join('|');
			const initialIds = entity[relationKey].map((option) => option.id).join('|');

			if (currentIds !== initialIds) {
				return true;
			}
		}

		return false;
	});

	function updatePrimaryRelation(key: DatabasePrimaryRelationKey, next: RelationOption[]) {
		primaryRelationState = {
			...primaryRelationState,
			[key]: next
		};
	}

	function updateRelatedRelation(key: DatabaseRelatedRelationKey, next: RelationOption[]) {
		relatedRelationState = {
			...relatedRelationState,
			[key]: next
		};
	}

	function buildDraft(): DatabaseEntityDraft {
		return {
			...DEFAULT_DATABASE_ENTITY_DRAFT,
			id: entity.id,
			name,
			description,
			markdownNotes,
			notes,
			size,
			placeType,
			raceId,
			parentPlaceId,
			armorAcBonus,
			equipmentBriefDescription,
			weaponAttackBonus,
			artifacts: cloneOptions(primaryRelationState.artifacts),
			associations: cloneOptions(primaryRelationState.associations),
			characters: cloneOptions(primaryRelationState.characters),
			items: cloneOptions(primaryRelationState.items),
			relatedArtifacts: cloneOptions(relatedRelationState.relatedArtifacts),
			relatedAssociations: cloneOptions(relatedRelationState.relatedAssociations),
			relatedCharacters: cloneOptions(relatedRelationState.relatedCharacters),
			relatedItems: cloneOptions(relatedRelationState.relatedItems),
			relatedPlaces: cloneOptions(relatedRelationState.relatedPlaces),
			relatedRaces: cloneOptions(relatedRelationState.relatedRaces)
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
			const operationInfoMessage = getOperationInfoMessage(
				payload,
				`Failed to save ${config.entityLabel.toLowerCase()} changes.`
			);

			if (operationInfoMessage) {
				errorMessage = operationInfoMessage;
				toast.error(operationInfoMessage);
				return;
			}
		} catch (error) {
			console.error(`Failed to save ${config.entityLabel.toLowerCase()} changes:`, error);
			errorMessage = `Failed to save ${config.entityLabel.toLowerCase()} changes.`;
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
			const operationInfoMessage = getOperationInfoMessage(
				payload,
				`Failed to discard ${config.entityLabel.toLowerCase()} changes.`
			);

			if (operationInfoMessage) {
				errorMessage = operationInfoMessage;
				toast.error(operationInfoMessage);
				return;
			}
		} catch (error) {
			console.error(`Failed to discard ${config.entityLabel.toLowerCase()} changes:`, error);
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
					{config.entityLabel} Editor
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
				<label class="font-mono text-[11px] tracking-[0.22em] text-slate-500 uppercase" for="entity-name-input">
					Name
				</label>
				<input id="entity-name-input" bind:value={name} class="industrial-input w-full" disabled={busy} />
			</div>

			{#if config.showSize}
				<div class="space-y-2">
					<label class="font-mono text-[11px] tracking-[0.22em] text-slate-500 uppercase" for="entity-size-input">
						Size
					</label>
					<input id="entity-size-input" bind:value={size} class="industrial-input w-full" disabled={busy} />
				</div>
			{/if}

			{#if config.showPlaceType}
				<div class="space-y-2">
					<label class="font-mono text-[11px] tracking-[0.22em] text-slate-500 uppercase" for="entity-place-type-select">
						Place Type
					</label>
					<select id="entity-place-type-select" bind:value={placeType} class="industrial-input w-full" disabled={busy}>
						<option value="">No place type</option>
						{#each PLACE_TYPE_OPTIONS as option (option)}
							<option value={option}>{option}</option>
						{/each}
					</select>
				</div>
			{/if}

			{#if config.showRace}
				<div class="space-y-2">
					<label class="font-mono text-[11px] tracking-[0.22em] text-slate-500 uppercase" for="entity-race-select">
						Race
					</label>
					<select id="entity-race-select" bind:value={raceId} class="industrial-input w-full" disabled={busy}>
						<option value="">No race</option>
						{#each relationOptions.races as option (option.id)}
							<option value={option.id}>{getSelectLabel(option)}</option>
						{/each}
					</select>
				</div>
			{/if}

			{#if config.showParentPlace}
				<div class="space-y-2">
					<label class="font-mono text-[11px] tracking-[0.22em] text-slate-500 uppercase" for="entity-parent-place-select">
						Parent Place
					</label>
					<select id="entity-parent-place-select" bind:value={parentPlaceId} class="industrial-input w-full" disabled={busy}>
						<option value="">No parent place</option>
						{#each relationOptions.places as option (option.id)}
							<option value={option.id}>{getSelectLabel(option)}</option>
						{/each}
					</select>
				</div>
			{/if}

			<div class="space-y-2 lg:col-span-2">
				<label class="font-mono text-[11px] tracking-[0.22em] text-slate-500 uppercase" for="entity-description-input">
					Description
				</label>
				<textarea
					id="entity-description-input"
					bind:value={description}
					rows="4"
					class="industrial-input w-full resize-y py-3"
					disabled={busy}
				></textarea>
			</div>

			{#if config.showNotes}
				<div class="space-y-2 lg:col-span-2">
					<label class="font-mono text-[11px] tracking-[0.22em] text-slate-500 uppercase" for="entity-notes-input">
						Notes
					</label>
					<textarea
						id="entity-notes-input"
						bind:value={notes}
						rows="4"
						class="industrial-input w-full resize-y py-3"
						disabled={busy}
					></textarea>
				</div>
			{/if}

			<div class="space-y-2 lg:col-span-2">
				<label class="font-mono text-[11px] tracking-[0.22em] text-slate-500 uppercase" for="entity-markdown-notes-input">
					Markdown Notes
				</label>
				<textarea
					id="entity-markdown-notes-input"
					bind:value={markdownNotes}
					rows="8"
					class="industrial-input w-full resize-y py-3"
					disabled={busy}
				></textarea>
			</div>

			{#if config.showArmorAcBonus}
				<div class="space-y-2">
					<label class="font-mono text-[11px] tracking-[0.22em] text-slate-500 uppercase" for="entity-armor-ac-input">
						Armor AC Bonus
					</label>
					<input id="entity-armor-ac-input" bind:value={armorAcBonus} type="number" class="industrial-input w-full" disabled={busy} />
				</div>
			{/if}

			{#if config.showWeaponAttackBonus}
				<div class="space-y-2">
					<label class="font-mono text-[11px] tracking-[0.22em] text-slate-500 uppercase" for="entity-weapon-attack-input">
						Weapon Attack Bonus
					</label>
					<input id="entity-weapon-attack-input" bind:value={weaponAttackBonus} type="number" class="industrial-input w-full" disabled={busy} />
				</div>
			{/if}

			{#if config.showEquipmentBriefDescription}
				<div class="space-y-2 lg:col-span-2">
					<label class="font-mono text-[11px] tracking-[0.22em] text-slate-500 uppercase" for="entity-equipment-description-input">
						Equipment Brief Description
					</label>
					<textarea
						id="entity-equipment-description-input"
						bind:value={equipmentBriefDescription}
						rows="3"
						class="industrial-input w-full resize-y py-3"
						disabled={busy}
					></textarea>
				</div>
			{/if}
		</div>
	</div>

	{#if hasSinglePrimaryRelation}
		{@const relation = primaryRelations[0]}
		<LogRelationPicker
			title={relation.title}
			placeholder={relation.placeholder ?? `Search ${relation.title.toLowerCase()}...`}
			selected={primaryRelationState[relation.key]}
			options={relationOptions[relation.key]}
			disabled={busy}
			onChange={(next: RelationOption[]) => updatePrimaryRelation(relation.key, next)}
		/>
	{:else if primaryRelations.length > 0}
		<div class="space-y-3 rounded-sm border border-slate-800/80 bg-slate-950/60 p-4">
			<div class="font-display text-industrial-amber text-sm tracking-[0.16em] uppercase">
				Entity Links
			</div>
			<div class="grid gap-4 xl:grid-cols-2">
				{#each primaryRelations as relation (relation.key)}
					<LogRelationPicker
						title={relation.title}
						placeholder={relation.placeholder ?? `Search ${relation.title.toLowerCase()}...`}
						selected={primaryRelationState[relation.key]}
						options={relationOptions[relation.key]}
						disabled={busy}
						onChange={(next: RelationOption[]) => updatePrimaryRelation(relation.key, next)}
					/>
				{/each}
			</div>
		</div>
	{/if}

	{#if relatedRelations.length > 0}
		<div class="space-y-3 rounded-sm border border-slate-800/80 bg-slate-950/60 p-4">
			<div class="font-display text-industrial-amber text-sm tracking-[0.16em] uppercase">
				Related Entities
			</div>
			<div class="grid gap-4 xl:grid-cols-2">
				{#each relatedRelations as relationKey (relationKey)}
					<LogRelationPicker
						title={DATABASE_RELATION_TITLES[relatedRelationToOptionKey[relationKey] as keyof typeof DATABASE_RELATION_TITLES]}
						placeholder={`Search ${DATABASE_RELATION_TITLES[relatedRelationToOptionKey[relationKey] as keyof typeof DATABASE_RELATION_TITLES].toLowerCase()}...`}
						selected={relatedRelationState[relationKey]}
						options={relationOptions[relatedRelationToOptionKey[relationKey]]}
						disabled={busy}
						onChange={(next: RelationOption[]) => updateRelatedRelation(relationKey, next)}
					/>
				{/each}
			</div>
		</div>
	{/if}

	{#if errorMessage}
		<p class="rounded-sm border border-rose-900/60 bg-rose-950/40 px-4 py-3 text-sm text-rose-300">
			{errorMessage}
		</p>
	{/if}
</form>
