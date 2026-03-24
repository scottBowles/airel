<script lang="ts">
	import { formatGameDate } from '$lib/utils';
	import { cn } from '$lib/utils';
	import {
		ArrowLeft,
		Calendar,
		Users,
		MapPin,
		Globe,
		Swords,
		Gem,
		Dna,
		BookOpen,
		ImageIcon,
		Save,
		X,
	} from 'lucide-svelte';
	import Panel from '$lib/components/Panel.svelte';
	import LockIndicator from '$lib/components/LockIndicator.svelte';
	import CloudinaryImage from '$lib/components/CloudinaryImage.svelte';
	import Button from '$lib/components/Button.svelte';

	type RelatedConnection = {
		edges: Array<{ node: { id: string; name: string; thumbnailId?: string | null; imageIds?: string[] | null } }>;
	} | null;

	type LogConnection = {
		edges: Array<{ node: { id: string; title: string | null; gameDate: Date | null } }>;
	} | null;

	let {
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
		relatedCharacters,
		relatedPlaces,
		relatedAssociations,
		relatedItems,
		relatedArtifacts,
		relatedRaces,
		logs,
		headerActions,
	}: {
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
		onsave?: (fields: { name: string; description: string; markdownNotes: string }) => Promise<boolean>;
		onstartediting?: () => void;
		extraInfo?: import('svelte').Snippet;
		editExtraInfo?: import('svelte').Snippet;
		relatedCharacters?: RelatedConnection;
		relatedPlaces?: RelatedConnection;
		relatedAssociations?: RelatedConnection;
		relatedItems?: RelatedConnection;
		relatedArtifacts?: RelatedConnection;
		relatedRaces?: RelatedConnection;
		logs?: LogConnection;
		headerActions?: import('svelte').Snippet;
	} = $props();

	let editing = $derived(lockedBySelf);
	let saving = $state(false);
	let editName = $state('');
	let editDescription = $state('');
	let editMarkdownNotes = $state('');

	$effect(() => {
		if (lockedBySelf) {
			editName = name;
			editDescription = description ?? '';
			editMarkdownNotes = markdownNotes ?? '';
			onstartediting?.();
		}
	});

	function discardEdits() {
		onunlock();
	}

	async function saveEdits() {
		if (!onsave) return;
		saving = true;
		const ok = await onsave({
			name: editName,
			description: editDescription,
			markdownNotes: editMarkdownNotes,
		});
		saving = false;
		if (ok) onunlock();
	}

	const relatedSections = $derived(
		[
			{ label: 'Characters', icon: Users, data: relatedCharacters, route: '/database/characters' },
			{ label: 'Places', icon: MapPin, data: relatedPlaces, route: '/database/places' },
			{
				label: 'Associations',
				icon: Globe,
				data: relatedAssociations,
				route: '/database/associations',
			},
			{ label: 'Items', icon: Swords, data: relatedItems, route: '/database/items' },
			{ label: 'Artifacts', icon: Gem, data: relatedArtifacts, route: '/database/artifacts' },
			{ label: 'Races', icon: Dna, data: relatedRaces, route: '/database/races' },
		].filter((s) => s.data && s.data.edges.length > 0),
	);
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
				{#if headerActions}
					{@render headerActions()}
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

			{#if imageIds.length > 1}
				<Panel>
					<h2 class="title-section mb-2 flex items-center gap-2">
						<ImageIcon class="h-3 w-3 text-text-muted" />
						Gallery
					</h2>
					<div class="grid grid-cols-2 gap-1 sm:grid-cols-3">
						{#each imageIds as imgId}
							<CloudinaryImage
								imageId={imgId}
								alt={name}
								width={400}
								crop="fit"
								class="w-full"
							/>
						{/each}
					</div>
				</Panel>
			{/if}
		</div>

		<!-- Sidebar -->
		<aside class="stack-space">
			{#each relatedSections as section}
				<Panel>
					<h3 class="title-section mb-2 flex items-center gap-2">
						<section.icon class="h-3 w-3 text-text-muted" />
						{section.label}
					</h3>
					<div class="space-y-px">
						{#each section.data?.edges ?? [] as edge}
							<a
								href="{section.route}/{edge.node.id}"
								class="block px-2 py-1 text-[11px] text-text-secondary uppercase tracking-wider transition-colors hover:bg-accent-amber/5 hover:text-accent-amber"
							>
								{edge.node.name}
							</a>
						{/each}
					</div>
				</Panel>
			{/each}

			{#if logs && logs.edges.length > 0}
				<Panel>
					<h3 class="title-section mb-2 flex items-center gap-2">
						<BookOpen class="h-3 w-3 text-text-muted" />
						Appears In
					</h3>
					<div class="space-y-px">
						{#each logs.edges as edge}
							<a
								href="/chronicle/{edge.node.id}"
								class="flex items-center gap-2 px-2 py-1 text-[11px] text-text-secondary transition-colors hover:bg-accent-amber/5 hover:text-accent-amber"
							>
								<Calendar class="h-3 w-3 shrink-0 text-accent-amber/30" />
								<span class="truncate uppercase tracking-wider">{edge.node.title ?? formatGameDate(edge.node.gameDate)}</span>
							</a>
						{/each}
					</div>
				</Panel>
			{/if}
		</aside>
	</div>
</div>
