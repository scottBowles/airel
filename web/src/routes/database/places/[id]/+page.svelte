<script lang="ts">
	import DOMPurify from 'isomorphic-dompurify';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import type { PageData } from './$houdini';
	import { UpdatePlaceImagesStore } from '$houdini';
	import AdminImageManager from '$lib/components/images/AdminImageManager.svelte';
	import EntityLogManager from '$lib/components/logs/EntityLogManager.svelte';
	import {
		buildPlaceBreadcrumbs,
		buildRelationGroups,
		detailPanelClass,
		detailRailCardClass,
		detailSectionTitleClass,
		getLogNodes,
		getNamedNodes
	} from '$lib/database-detail';

	let { data }: { data: PageData } = $props();
	let PlaceDetail = $derived(data.PlaceDetail);
	let place = $derived($PlaceDetail.data?.node);
	let Me = $derived(data.Me);
	let me = $derived($Me?.data?.me);
	let isAdmin = $derived(me?.isStaff || me?.isSuperuser);
	let breadcrumbs = $derived.by(() => {
		if (!place || place.__typename !== 'Place') {
			return [];
		}

		return buildPlaceBreadcrumbs(place);
	});
	let childPlaces = $derived.by(() => {
		if (!place || place.__typename !== 'Place') {
			return [];
		}

		return getNamedNodes(place.children);
	});
	let relationGroups = $derived.by(() => {
		if (!place || place.__typename !== 'Place') {
			return [];
		}

		return buildRelationGroups({
			relatedArtifacts: place.relatedArtifacts,
			relatedAssociations: place.relatedAssociations,
			relatedCharacters: place.relatedCharacters,
			relatedItems: place.relatedItems,
			relatedPlaces: place.relatedPlaces,
			relatedRaces: place.relatedRaces
		});
	});
	let logEntries = $derived.by(() => {
		if (!place || place.__typename !== 'Place') {
			return [];
		}

		return getLogNodes(place.logs);
	});
	let hasMarkdownNotes = $derived(
		!!(place && place.__typename === 'Place' && place.markdownNotes?.trim())
	);
	let sanitizedMarkdownNotes = $derived.by(() => {
		if (!place || place.__typename !== 'Place' || !place.markdownNotes) {
			return '';
		}

		return DOMPurify.sanitize(place.markdownNotes);
	});

	const updateStore = new UpdatePlaceImagesStore();

	async function saveImages(newIds: string[]) {
		await updateStore.mutate({
			id: page.params.id ?? '',
			imageIds: newIds
		});
	}
</script>

{#if place && place.__typename === 'Place'}
	<div class="db-detail">
		<div class="db-detail-header">
			<div class="space-y-2 sm:space-y-2.5">
				{#if breadcrumbs.length > 0}
					<nav
						aria-label="Place hierarchy"
						class="flex flex-wrap items-center gap-x-2 gap-y-1 font-mono text-[0.68rem] tracking-[0.18em] text-zinc-500 uppercase"
					>
						{#each breadcrumbs as crumb (crumb.id)}
							<a
								href={resolve('/database/places/[id]', { id: crumb.id })}
								class="transition-colors hover:text-emerald-300"
							>
								{crumb.name}
							</a>
							<span class="text-zinc-700" aria-hidden="true">/</span>
						{/each}
						<span class="text-zinc-300">{place.name}</span>
					</nav>
				{/if}
				<h1 class="db-detail-title">{place.name}</h1>
				{#if place.placeType}
					<div
						class="inline-flex items-center text-base leading-none tracking-[0.14em] text-emerald-400 uppercase sm:text-lg"
					>
						<span class="font-display text-lg tracking-[0.14em] text-emerald-400 sm:text-xl">
							{place.placeType}
						</span>
					</div>
				{/if}
			</div>
			<a href={resolve('/database/places')} class="db-back-link"> ← Back to Places </a>
		</div>

		<div class="db-detail-grid">
			<div class="db-detail-side order-1 lg:order-2">
				<AdminImageManager imageIds={place.imageIds || []} canEdit={isAdmin} onSave={saveImages} />

				<div class={detailRailCardClass + ' hidden lg:block'}>
					<EntityLogManager entityId={page.params.id ?? ''} logs={logEntries} canEdit={isAdmin} />
				</div>
			</div>

			<div class="db-detail-main order-2 lg:order-1">
				<div class={detailPanelClass}>
					<p class="text-sm leading-relaxed whitespace-pre-wrap text-zinc-300 sm:text-base">
						{place.description || 'No description provided.'}
					</p>
				</div>

				{#if childPlaces.length > 0}
					<div class={detailPanelClass}>
						<h3 class={detailSectionTitleClass}>Locations Within</h3>
						<div class="flex flex-wrap items-baseline gap-x-1.5 gap-y-1 text-sm leading-6">
							{#each childPlaces as node (node.id)}
								<a
									href={resolve('/database/places/[id]', { id: node.id })}
									class="text-zinc-200 underline decoration-transparent underline-offset-3 transition-colors hover:text-emerald-300 hover:decoration-emerald-500/40"
								>
									{node.name}
								</a>
								{#if node !== childPlaces[childPlaces.length - 1]}
									<span class="text-zinc-700" aria-hidden="true">•</span>
								{/if}
							{/each}
						</div>
					</div>
				{/if}

				{#if hasMarkdownNotes}
					<div class={detailPanelClass}>
						<div class="text-sm leading-relaxed whitespace-pre-wrap text-zinc-300">
							<!-- eslint-disable-next-line svelte/no-at-html-tags -->
							{@html sanitizedMarkdownNotes}
						</div>
					</div>
				{/if}

				<div class={detailPanelClass}>
					<h3 class={detailSectionTitleClass}>Related Entities</h3>

					{#if relationGroups.length > 0}
						<div class="space-y-3.5">
							{#each relationGroups as group (group.key)}
								<div class="border-b border-slate-700/90 pb-3 last:border-0 last:pb-0">
									<div class="space-y-1.5 sm:flex sm:items-baseline sm:gap-3 sm:space-y-0">
										<h4
											class="shrink-0 font-mono text-xs leading-6 tracking-[0.18em] text-zinc-500 uppercase sm:w-34"
										>
											{group.label}
										</h4>
										<div class="flex flex-wrap items-baseline gap-x-1.5 gap-y-1 text-sm leading-6">
											{#each group.nodes as node (node.id)}
												<a
													href={resolve(group.route, { id: node.id })}
													class="text-zinc-200 underline decoration-transparent underline-offset-3 transition-colors hover:text-emerald-300 hover:decoration-emerald-500/40"
												>
													{node.name}
												</a>
												{#if node !== group.nodes[group.nodes.length - 1]}
													<span class="text-zinc-700" aria-hidden="true">•</span>
												{/if}
											{/each}
										</div>
									</div>
								</div>
							{/each}
						</div>
					{:else}
						<p class="text-sm text-zinc-500">No linked entities recorded.</p>
					{/if}
				</div>

				<div class={detailPanelClass + ' lg:hidden'}>
					<EntityLogManager entityId={page.params.id ?? ''} logs={logEntries} canEdit={isAdmin} />
				</div>
			</div>
		</div>
	</div>
{:else if $PlaceDetail.fetching}
	<div class="p-12 text-center font-mono text-zinc-500">Retrieving place record...</div>
{:else}
	<div class="p-8 text-center text-zinc-500">
		<p>Place not found or failed to load.</p>
	</div>
{/if}
