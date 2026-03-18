<script lang="ts">
	import { ExternalLink } from 'lucide-svelte';
	import DOMPurify from 'isomorphic-dompurify';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import type { PageData } from './$houdini';
	import { UpdateAssociationImagesStore } from '$houdini';
	import AdminImageManager from '$lib/components/images/AdminImageManager.svelte';
	import {
		buildRelationGroups,
		detailPanelClass,
		detailRailCardClass,
		detailSectionTitleClass,
		getLogNodes,
		getNamedNodes
	} from '$lib/database-detail';

	let { data }: { data: PageData } = $props();
	let AssociationDetail = $derived(data.AssociationDetail);
	let association = $derived($AssociationDetail.data?.node);
	let Me = $derived(data.Me);
	let me = $derived($Me?.data?.me);
	let isAdmin = $derived(me?.isStaff || me?.isSuperuser);
	let memberNodes = $derived.by(() => {
		if (!association || association.__typename !== 'Association') {
			return [];
		}

		return getNamedNodes(association.characters);
	});
	let relationGroups = $derived.by(() => {
		if (!association || association.__typename !== 'Association') {
			return [];
		}

		return buildRelationGroups({
			relatedArtifacts: association.relatedArtifacts,
			relatedAssociations: association.relatedAssociations,
			relatedCharacters: association.relatedCharacters,
			relatedItems: association.relatedItems,
			relatedPlaces: association.relatedPlaces,
			relatedRaces: association.relatedRaces
		});
	});
	let logEntries = $derived.by(() => {
		if (!association || association.__typename !== 'Association') {
			return [];
		}

		return getLogNodes(association.logs);
	});
	let hasMarkdownNotes = $derived(
		!!(association && association.__typename === 'Association' && association.markdownNotes?.trim())
	);
	let sanitizedMarkdownNotes = $derived.by(() => {
		if (!association || association.__typename !== 'Association' || !association.markdownNotes) {
			return '';
		}

		return DOMPurify.sanitize(association.markdownNotes);
	});

	const updateStore = new UpdateAssociationImagesStore();

	function openExternalLog(url: string) {
		window.open(url, '_blank', 'noopener,noreferrer');
	}

	async function saveImages(newIds: string[]) {
		await updateStore.mutate({
			id: page.params.id ?? '',
			imageIds: newIds
		});
	}
</script>

{#if association && association.__typename === 'Association'}
	<div class="db-detail">
		<div class="db-detail-header">
			<div class="space-y-2 sm:space-y-2.5">
				<h1 class="db-detail-title">{association.name}</h1>
			</div>
			<a href={resolve('/database/associations')} class="db-back-link"> ← Back to Associations </a>
		</div>

		<div class="db-detail-grid">
			<div class="db-detail-side order-1 lg:order-2">
				<AdminImageManager
					imageIds={association.imageIds || []}
					canEdit={isAdmin}
					onSave={saveImages}
				/>

				<div class={detailRailCardClass + ' hidden lg:block'}>
					<h3 class={detailSectionTitleClass}>Logs</h3>

					{#if logEntries.length > 0}
						<ul class="max-h-80 space-y-1.5 overflow-y-auto pr-1">
							{#each logEntries as log (log.id)}
								<li
									class="flex items-center justify-between gap-2 rounded-sm border border-slate-800 bg-slate-950 px-2 py-1.5"
								>
									<a
										href={resolve(`/logs/${log.id}`)}
										class="min-w-0 truncate text-sm text-zinc-200 transition-colors hover:text-emerald-300"
									>
										{log.title || 'Untitled log'}
									</a>
									<button
										type="button"
										onclick={() => openExternalLog(log.url)}
										class="inline-flex h-7 w-7 shrink-0 cursor-pointer items-center justify-center rounded-sm text-zinc-400 transition-colors hover:text-emerald-300"
										aria-label={`Open source document for ${log.title || 'this log'}`}
									>
										<ExternalLink class="h-3.5 w-3.5" aria-hidden="true" />
									</button>
								</li>
							{/each}
						</ul>
					{:else}
						<p class="text-sm text-zinc-500">No linked logs recorded.</p>
					{/if}
				</div>
			</div>

			<div class="db-detail-main order-2 lg:order-1">
				<div class={detailPanelClass}>
					<p class="text-sm leading-relaxed whitespace-pre-wrap text-zinc-300 sm:text-base">
						{association.description || 'No description provided.'}
					</p>
				</div>

				{#if memberNodes.length > 0}
					<div class={detailPanelClass}>
						<h3 class={detailSectionTitleClass}>Members</h3>
						<div class="flex flex-wrap items-baseline gap-x-1.5 gap-y-1 text-sm leading-6">
							{#each memberNodes as node (node.id)}
								<a
									href={resolve('/database/characters/[id]', { id: node.id })}
									class="text-zinc-200 underline decoration-transparent underline-offset-3 transition-colors hover:text-emerald-300 hover:decoration-emerald-500/40"
								>
									{node.name}
								</a>
								{#if node !== memberNodes[memberNodes.length - 1]}
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
					<h3 class={detailSectionTitleClass}>Logs</h3>

					{#if logEntries.length > 0}
						<ul class="space-y-1.5">
							{#each logEntries as log (log.id)}
								<li
									class="flex items-center justify-between gap-2 rounded-sm border border-slate-800 bg-slate-950 px-2 py-1.5"
								>
									<div class="min-w-0">
										<a
											href={resolve(`/logs/${log.id}`)}
											class="block truncate text-sm text-zinc-200 transition-colors hover:text-emerald-300"
										>
											{log.title || 'Untitled log'}
										</a>
									</div>
									<button
										type="button"
										onclick={() => openExternalLog(log.url)}
										class="inline-flex h-7 w-7 shrink-0 cursor-pointer items-center justify-center rounded-sm text-zinc-400 transition-colors hover:text-emerald-300"
										aria-label={`Open source document for ${log.title || 'this log'}`}
									>
										<ExternalLink class="h-3.5 w-3.5" aria-hidden="true" />
									</button>
								</li>
							{/each}
						</ul>
					{:else}
						<p class="text-sm text-zinc-500">No linked logs recorded.</p>
					{/if}
				</div>
			</div>
		</div>
	</div>
{:else if $AssociationDetail.fetching}
	<div class="p-12 text-center font-mono text-zinc-500">Retrieving association record...</div>
{:else}
	<div class="p-8 text-center text-zinc-500">
		<p>Association not found or failed to load.</p>
	</div>
{/if}
