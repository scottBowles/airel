<script lang="ts">
	import type { Component, Snippet } from 'svelte';
	import { toast } from 'svelte-sonner';
	import {
		ArrowLeft,
		Users,
		MapPin,
		Globe,
		Swords,
		Gem,
		Dna,
		Save,
		X,
	} from 'lucide-svelte';
	import Panel from '$lib/components/Panel.svelte';
	import LockIndicator from '$lib/components/LockIndicator.svelte';
	import CloudinaryImage from '$lib/components/CloudinaryImage.svelte';
	import Button from '$lib/components/Button.svelte';
	import ImageGallery from '$lib/components/ImageGallery.svelte';
	import EntityLogsBlock from '$lib/components/EntityLogsBlock.svelte';
	import RelatedEntitiesBlock from '$lib/components/RelatedEntitiesBlock.svelte';
	import EntityPicker from '$lib/components/EntityPicker.svelte';

	type RelatedConnection = {
		edges: Array<{ node: { id: string; name: string } }>;
	} | null;

	type LogConnection = {
		edges: Array<{ node: { id: string; title: string | null; gameDate: Date | null } }>;
	} | null;

	type NodeInputList = { add?: Array<{ id: string }>; remove?: Array<{ id: string }> };

	type SaveFields = {
		name: string;
		description: string;
		markdownNotes: string;
		relatedCharacters?: NodeInputList;
		relatedPlaces?: NodeInputList;
		relatedAssociations?: NodeInputList;
		relatedItems?: NodeInputList;
		relatedArtifacts?: NodeInputList;
		relatedRaces?: NodeInputList;
	};

	type SectionDef = {
		key: string;
		label: string;
		icon: Component;
		data: RelatedConnection;
		route: string;
		entityType: 'Character' | 'Place' | 'Association' | 'Item' | 'Artifact' | 'Race';
	};

	let {
		entityId,
		name,
		description,
		thumbnailId,
		imageIds = [],
		markdownNotes,
		backHref,
		backLabel,
		locked,
		lockedBySelf,
		lockUser,
		onlock,
		onunlock,
		onsave,
		onstartediting,
		extraInfo,
		editExtraInfo,
		breadcrumbs,
		relatedCharacters,
		relatedPlaces,
		relatedAssociations,
		relatedItems,
		relatedArtifacts,
		relatedRaces,
		logs,
	}: {
		entityId: string;
		name: string;
		description?: string | null;
		thumbnailId?: string | null;
		imageIds?: string[];
		markdownNotes?: string | null;
		backHref: string;
		backLabel: string;
		locked: boolean;
		lockedBySelf: boolean;
		lockUser?: { username: string } | null;
		onlock: () => void;
		onunlock: () => void;
		onsave?: (fields: SaveFields) => Promise<boolean>;
		onstartediting?: () => void;
		extraInfo?: Snippet;
		editExtraInfo?: Snippet;
		breadcrumbs?: Snippet;
		relatedCharacters?: RelatedConnection;
		relatedPlaces?: RelatedConnection;
		relatedAssociations?: RelatedConnection;
		relatedItems?: RelatedConnection;
		relatedArtifacts?: RelatedConnection;
		relatedRaces?: RelatedConnection;
		logs?: LogConnection;
	} = $props();

	let editing = $derived(lockedBySelf);
	let saving = $state(false);
	let editName = $state('');
	let editDescription = $state('');
	let editMarkdownNotes = $state('');

	// Related entity editing state
	let relatedAdds = $state<Record<string, Array<{ id: string; name: string }>>>({});
	let relatedRemoves = $state<Record<string, string[]>>({});

	const allSections: SectionDef[] = $derived([
		{ key: 'relatedCharacters', label: 'Characters', icon: Users, data: relatedCharacters, route: '/database/characters', entityType: 'Character' },
		{ key: 'relatedPlaces', label: 'Places', icon: MapPin, data: relatedPlaces, route: '/database/places', entityType: 'Place' },
		{ key: 'relatedAssociations', label: 'Associations', icon: Globe, data: relatedAssociations, route: '/database/associations', entityType: 'Association' },
		{ key: 'relatedItems', label: 'Items', icon: Swords, data: relatedItems, route: '/database/items', entityType: 'Item' },
		{ key: 'relatedArtifacts', label: 'Artifacts', icon: Gem, data: relatedArtifacts, route: '/database/artifacts', entityType: 'Artifact' },
		{ key: 'relatedRaces', label: 'Races', icon: Dna, data: relatedRaces, route: '/database/races', entityType: 'Race' },
	]);

	// Read-only view: only non-empty sections
	const relatedSections = $derived(
		allSections.filter((s) => s.data && s.data.edges.length > 0),
	);

	$effect(() => {
		if (lockedBySelf) {
			editName = name;
			editDescription = description ?? '';
			editMarkdownNotes = markdownNotes ?? '';
			relatedAdds = {};
			relatedRemoves = {};
			onstartediting?.();
		}
	});

	function discardEdits() {
		relatedAdds = {};
		relatedRemoves = {};
		onunlock();
	}

	function addRelated(key: string, entity: { id: string; name: string }) {
		relatedAdds[key] = [...(relatedAdds[key] ?? []), entity];
	}

	function removeRelated(key: string, id: string) {
		const current = relatedRemoves[key] ?? [];
		if (!current.includes(id)) {
			relatedRemoves[key] = [...current, id];
		}
	}

	function undoAdd(key: string, id: string) {
		relatedAdds[key] = (relatedAdds[key] ?? []).filter((e) => e.id !== id);
	}

	function undoRemove(key: string, id: string) {
		relatedRemoves[key] = (relatedRemoves[key] ?? []).filter((x) => x !== id);
	}

	function getEffectiveItems(section: SectionDef) {
		const existing = section.data?.edges.map((e) => e.node) ?? [];
		const removes = relatedRemoves[section.key] ?? [];
		const adds = relatedAdds[section.key] ?? [];
		return {
			kept: existing.filter((e) => !removes.includes(e.id)),
			removed: existing.filter((e) => removes.includes(e.id)),
			added: adds,
		};
	}

	function getExcludeIds(section: SectionDef): string[] {
		const existing = section.data?.edges.map((e) => e.node.id) ?? [];
		const addedIds = (relatedAdds[section.key] ?? []).map((e) => e.id);
		const removedIds = relatedRemoves[section.key] ?? [];
		// Exclude all that would appear in the list (existing - removed + added) + self
		const inList = [...existing, ...addedIds].filter((id) => !removedIds.includes(id));
		return [entityId, ...inList];
	}

	async function saveEdits() {
		if (!onsave) return;
		if (!editName.trim()) {
			toast.error('Name is required');
			return;
		}
		saving = true;
		const relatedFields: Record<string, NodeInputList> = {};
		for (const section of allSections) {
			const adds = relatedAdds[section.key] ?? [];
			const removes = [...(relatedRemoves[section.key] ?? [])];
			if (adds.length || removes.length) {
				relatedFields[section.key] = {
					...(adds.length ? { add: adds.map((e) => ({ id: e.id })) } : {}),
					...(removes.length ? { remove: removes.map((id) => ({ id })) } : {}),
				};
			}
		}

		const ok = await onsave({
			name: editName,
			description: editDescription,
			markdownNotes: editMarkdownNotes,
			...relatedFields,
		});
		saving = false;
		if (ok) {
			relatedAdds = {};
			relatedRemoves = {};
			onunlock();
		}
	}
</script>

<div class="content-pad db-page">
	<!-- Back link -->
	<a
		href={backHref}
		class="inline-flex items-center gap-2 text-xs text-text-muted uppercase tracking-wider transition-colors hover:text-accent-amber"
	>
		<ArrowLeft class="h-3.5 w-3.5" />
		<span>{backLabel}</span>
	</a>

	{#if breadcrumbs}
		{@render breadcrumbs()}
	{/if}

	<!-- Header panel -->
	<div class="panel-border panel-bg panel-pad console-frame">
		<div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
			<div class="flex items-start gap-3">
				{#if thumbnailId || imageIds?.length}
					<CloudinaryImage
						imageId={thumbnailId ?? imageIds?.[0]}
						alt={name}
						width={120}
						height={120}
						class="hidden h-16 w-16 shrink-0 border border-border-dim sm:block"
					/>
				{/if}
				<div>
					{#if editing}
						<input
							bind:value={editName}
							class="w-full border border-border-dim bg-bg-inset px-2 py-1 font-[family-name:var(--font-display)] text-lg text-accent-amber outline-none focus:border-accent-amber"
						/>
					{:else}
						<h1 class="title-display text-lg text-accent-amber text-glow-amber sm:text-xl">{name}</h1>
					{/if}
					{#if editing}
						<textarea
							bind:value={editDescription}
							rows="2"
							placeholder="Description..."
							class="mt-1.5 w-full border border-border-dim bg-bg-inset px-2 py-1 text-xs text-text-secondary outline-none focus:border-accent-amber"
						></textarea>
					{:else if description}
						<p class="mt-1.5 max-w-2xl text-xs text-text-secondary leading-relaxed">{description}</p>
					{/if}
				</div>
			</div>
			<div class="flex flex-wrap items-center gap-2">
				<LockIndicator {locked} {lockedBySelf} {lockUser} {onlock} {onunlock} />
				{#if editing}
					<Button size="sm" onclick={saveEdits} disabled={saving}>
						<Save class="mr-1 h-3 w-3" />
						{saving ? 'Saving...' : 'Commit'}
					</Button>
					<Button size="sm" variant="ghost" onclick={discardEdits} disabled={saving}>
						<X class="mr-1 h-3 w-3" />
						Discard
					</Button>
				{/if}
			</div>
		</div>
	</div>

	<div class="grid gap-3 lg:grid-cols-[1fr_260px]">
		<!-- Main content -->
		<div class="stack-space">
			{#if editing && editExtraInfo}
				{@render editExtraInfo()}
			{:else if extraInfo}
				{@render extraInfo()}
			{/if}

			{#if editing}
				<Panel>
					<h2 class="title-section mb-2">Notes</h2>
					<textarea
						bind:value={editMarkdownNotes}
						rows="12"
						placeholder="Notes (markdown)..."
						class="w-full border border-border-dim bg-bg-inset px-2 py-1 text-xs text-text-secondary leading-relaxed outline-none focus:border-accent-amber"
					></textarea>
				</Panel>
			{:else if markdownNotes}
				<Panel>
					<h2 class="title-section mb-2">Notes</h2>
					<div class="whitespace-pre-wrap text-xs text-text-secondary leading-relaxed">
						{markdownNotes}
					</div>
				</Panel>
			{/if}

			<ImageGallery {entityId} {imageIds} {name} />
		</div>

		<!-- Sidebar -->
		<aside class="stack-space">
			{#if editing}
				{#each allSections as section}
					{@const effective = getEffectiveItems(section)}
					{@const hasContent = effective.kept.length > 0 || effective.added.length > 0}
					<Panel>
						<h3 class="title-section mb-2 flex items-center gap-2">
							<section.icon class="h-3 w-3 text-text-muted" />
							{section.label}
						</h3>
						{#if hasContent}
							<div class="space-y-px">
								{#each effective.kept as item}
									<div class="group flex items-center justify-between">
										<a
											href="{section.route}/{item.id}"
											class="flex-1 truncate px-2 py-1 text-[11px] text-text-secondary uppercase tracking-wider transition-colors hover:text-accent-amber"
										>
											{item.name}
										</a>
										<button
											onclick={() => removeRelated(section.key, item.id)}
										class="shrink-0 cursor-pointer p-0.5 text-text-muted opacity-0 transition-opacity hover:text-accent-red group-hover:opacity-100 focus-visible:opacity-100"
										aria-label="Remove {item.name}"
										>
											<X class="h-3 w-3" />
										</button>
									</div>
								{/each}
								{#each effective.added as item}
									<div class="group flex items-center justify-between">
										<span class="flex-1 truncate px-2 py-1 text-[11px] text-accent-green uppercase tracking-wider">
											+ {item.name}
										</span>
										<button
											onclick={() => undoAdd(section.key, item.id)}
										class="shrink-0 cursor-pointer p-0.5 text-text-muted opacity-0 transition-opacity hover:text-accent-red group-hover:opacity-100 focus-visible:opacity-100"
										aria-label="Undo add {item.name}"
										>
											<X class="h-3 w-3" />
										</button>
									</div>
								{/each}
							</div>
						{/if}
						{#if effective.removed.length > 0}
							<div class="mt-1 space-y-px border-t border-border-dim pt-1">
								{#each effective.removed as item}
									<div class="group flex items-center justify-between opacity-50">
										<span class="flex-1 truncate px-2 py-1 text-[11px] text-text-muted line-through uppercase tracking-wider">
											{item.name}
										</span>
										<button
											onclick={() => undoRemove(section.key, item.id)}
											class="shrink-0 cursor-pointer p-0.5 text-text-muted opacity-0 transition-opacity hover:text-accent-green group-hover:opacity-100"
											title="Undo remove"
										>
											↩
										</button>
									</div>
								{/each}
							</div>
						{/if}
						<div class="mt-1.5">
							<EntityPicker
								entityType={section.entityType}
								onselect={(e) => addRelated(section.key, e)}
								exclude={getExcludeIds(section)}
								placeholder="Add {section.label.toLowerCase()}..."
							/>
						</div>
					</Panel>
				{/each}
			{:else}
				<RelatedEntitiesBlock sections={relatedSections} />
			{/if}
			<EntityLogsBlock {entityId} {logs} />
		</aside>
	</div>
</div>
