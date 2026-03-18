<script lang="ts">
	import { ExternalLink } from 'lucide-svelte';
	import DOMPurify from 'isomorphic-dompurify';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import type { PageData } from './$houdini';
	import { UpdateCharacterImagesStore } from '$houdini';
	import AdminImageManager from '$lib/components/images/AdminImageManager.svelte';
	import {
		buildRelationGroups,
		detailPanelClass,
		detailRailCardClass,
		detailSectionTitleClass,
		getLogNodes,
		getNamedNodes,
		type LogNode,
		type NamedNode,
		type RelationGroup
	} from '$lib/database-detail';

	function openExternalLog(url: string) {
		window.open(url, '_blank', 'noopener,noreferrer');
	}

	let { data }: { data: PageData } = $props();
	let CharacterDetail = $derived(data.CharacterDetail);
	let char = $derived($CharacterDetail.data?.node);
	let Me = $derived(data.Me);
	let me = $derived($Me?.data?.me);
	let isAdmin = $derived(me?.isStaff || me?.isSuperuser);
	let affiliationNodes = $derived.by((): NamedNode[] => {
		if (!char || char.__typename !== 'Character') {
			return [];
		}

		return getNamedNodes(char.associations);
	});
	let relationGroups = $derived.by((): RelationGroup[] => {
		if (!char || char.__typename !== 'Character') {
			return [];
		}

		return buildRelationGroups({
			relatedArtifacts: char.relatedArtifacts,
			relatedAssociations: char.relatedAssociations,
			relatedCharacters: char.relatedCharacters,
			relatedItems: char.relatedItems,
			relatedPlaces: char.relatedPlaces,
			relatedRaces: char.relatedRaces
		});
	});
	let logEntries = $derived.by((): LogNode[] => {
		if (!char || char.__typename !== 'Character') {
			return [];
		}

		return getLogNodes(char.logs);
	});
	let hasMarkdownNotes = $derived(
		!!(char && char.__typename === 'Character' && char.markdownNotes?.trim())
	);
	let sanitizedMarkdownNotes = $derived.by(() => {
		if (!char || char.__typename !== 'Character' || !char.markdownNotes) {
			return '';
		}

		return DOMPurify.sanitize(char.markdownNotes);
	});

	const updateStore = new UpdateCharacterImagesStore();

	async function saveImages(newIds: string[]) {
		await updateStore.mutate({
			id: page.params.id ?? '',
			imageIds: newIds
		});
	}
</script>

{#if char && char.__typename === 'Character'}
	<div class="db-detail">
		<div class="db-detail-header">
			<div class="space-y-2 sm:space-y-2.5">
				<h1 class="db-detail-title">{char.name}</h1>
				{#if char.race}
					<a
						href={resolve(`/database/races/${char.race.id}`)}
						class="inline-flex items-center text-base leading-none tracking-[0.14em] text-emerald-400 uppercase transition-colors hover:text-emerald-300 sm:text-lg"
					>
						<span class="font-display text-lg tracking-[0.14em] text-emerald-400 sm:text-xl">
							{char.race.name}
						</span>
					</a>
				{/if}
			</div>
			<a href={resolve('/database/characters')} class="db-back-link"> ← Back to Characters </a>
		</div>

		<div class="db-detail-grid">
			<div class="db-detail-side order-1 lg:order-2">
				<AdminImageManager imageIds={char.imageIds || []} canEdit={isAdmin} onSave={saveImages} />

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
						{char.description || 'No description provided.'}
					</p>
				</div>

				{#if affiliationNodes.length > 0}
					<div class={detailPanelClass}>
						<h3 class={detailSectionTitleClass}>Affiliations</h3>
						<div class="flex flex-wrap items-baseline gap-x-1.5 gap-y-1 text-sm leading-6">
							{#each affiliationNodes as node (node.id)}
								<a
									href={resolve('/database/associations/[id]', { id: node.id })}
									class="text-zinc-200 underline decoration-transparent underline-offset-3 transition-colors hover:text-emerald-300 hover:decoration-emerald-500/40"
								>
									{node.name}
								</a>
								{#if node !== affiliationNodes[affiliationNodes.length - 1]}
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
{:else if $CharacterDetail.fetching}
	<div class="p-12 text-center font-mono text-zinc-500">Retrieving character record...</div>
{:else}
	<div class="p-8 text-center text-zinc-500">
		<p>Character not found or failed to load.</p>
	</div>
{/if}
