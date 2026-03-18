<script lang="ts">
	import { Box, ExternalLink, Shield, Sword } from 'lucide-svelte';
	import DOMPurify from 'isomorphic-dompurify';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import type { PageData } from './$houdini';
	import { UpdateItemImagesStore } from '$houdini';
	import AdminImageManager from '$lib/components/images/AdminImageManager.svelte';
	import {
		buildRelationGroups,
		detailPanelClass,
		detailRailCardClass,
		detailSectionTitleClass,
		getLogNodes
	} from '$lib/database-detail';

	type ItemTypeCard = {
		key: 'armor' | 'weapon' | 'equipment';
		label: string;
		description: string;
		icon: typeof Shield;
		tone: string;
	};

	let { data }: { data: PageData } = $props();
	let ItemDetail = $derived(data.ItemDetail);
	let item = $derived($ItemDetail.data?.node);
	let Me = $derived(data.Me);
	let me = $derived($Me?.data?.me);
	let isAdmin = $derived(me?.isStaff || me?.isSuperuser);
	let itemTypeCards = $derived.by((): ItemTypeCard[] => {
		if (!item || item.__typename !== 'Item') {
			return [];
		}

		const cards: ItemTypeCard[] = [];

		if (item.armor) {
			cards.push({
				key: 'armor',
				label: 'Armor',
				description: 'Built for protection and defensive utility.',
				icon: Shield,
				tone: 'border-sky-500/35 bg-sky-950/35 text-sky-200'
			});
		}

		if (item.weapon) {
			cards.push({
				key: 'weapon',
				label: 'Weapon',
				description: 'Designed for offense and combat application.',
				icon: Sword,
				tone: 'border-amber-500/35 bg-amber-950/35 text-amber-200'
			});
		}

		if (item.equipment) {
			cards.push({
				key: 'equipment',
				label: 'Equipment',
				description: item.equipment.briefDescription || 'General-purpose adventuring gear.',
				icon: Box,
				tone: 'border-emerald-500/35 bg-emerald-950/35 text-emerald-200'
			});
		}

		return cards;
	});
	let relationGroups = $derived.by(() => {
		if (!item || item.__typename !== 'Item') {
			return [];
		}

		return buildRelationGroups({
			relatedArtifacts: item.relatedArtifacts,
			relatedAssociations: item.relatedAssociations,
			relatedCharacters: item.relatedCharacters,
			relatedItems: item.relatedItems,
			relatedPlaces: item.relatedPlaces,
			relatedRaces: item.relatedRaces
		});
	});
	let logEntries = $derived.by(() => {
		if (!item || item.__typename !== 'Item') {
			return [];
		}

		return getLogNodes(item.logs);
	});
	let hasMarkdownNotes = $derived(
		!!(item && item.__typename === 'Item' && item.markdownNotes?.trim())
	);
	let sanitizedMarkdownNotes = $derived.by(() => {
		if (!item || item.__typename !== 'Item' || !item.markdownNotes) {
			return '';
		}

		return DOMPurify.sanitize(item.markdownNotes);
	});

	const updateStore = new UpdateItemImagesStore();

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

{#if item && item.__typename === 'Item'}
	<div class="db-detail">
		<div class="db-detail-header">
			<div class="space-y-2 sm:space-y-2.5">
				<h1 class="db-detail-title">{item.name}</h1>
			</div>
			<a href={resolve('/database/items')} class="db-back-link"> ← Back to Items </a>
		</div>

		<div class="db-detail-grid">
			<div class="db-detail-side order-1 lg:order-2">
				<AdminImageManager imageIds={item.imageIds || []} canEdit={isAdmin} onSave={saveImages} />

				<div class={detailRailCardClass}>
					<h3 class={detailSectionTitleClass}>Item Type</h3>

					{#if itemTypeCards.length > 0}
						<div class="grid gap-2">
							{#each itemTypeCards as typeCard (typeCard.key)}
								{@const Icon = typeCard.icon}
								<div class={'rounded-sm border p-3 ' + typeCard.tone}>
									<div class="flex items-start gap-3">
										<div
											class="flex h-10 w-10 shrink-0 items-center justify-center rounded-sm border border-current/20 bg-black/15"
										>
											<Icon class="h-4.5 w-4.5" aria-hidden="true" />
										</div>
										<div class="min-w-0">
											<div class="font-mono text-xs tracking-[0.18em] uppercase">
												{typeCard.label}
											</div>
											<p class="mt-1 text-sm leading-relaxed text-current/80">
												{typeCard.description}
											</p>
										</div>
									</div>
								</div>
							{/each}
						</div>
					{:else}
						<p class="text-sm text-zinc-500">No subtype metadata recorded for this item.</p>
					{/if}
				</div>

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
						{item.description || 'No description provided.'}
					</p>
				</div>

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
{:else if $ItemDetail.fetching}
	<div class="p-12 text-center font-mono text-zinc-500">Retrieving item record...</div>
{:else}
	<div class="p-8 text-center text-zinc-500">
		<p>Item not found or failed to load.</p>
	</div>
{/if}
