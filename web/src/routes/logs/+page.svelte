<script lang="ts">
	import type { PageData } from './$houdini';
	import { browser } from '$app/environment';
	import { resolve } from '$app/paths';
	import { formatGameDate } from '$lib/utils';
	import { ExternalLink } from 'lucide-svelte';
	import { SvelteMap } from 'svelte/reactivity';
	import { fromStore } from 'svelte/store';

	type LogPlace = {
		id: string;
		name: string;
		placeType: string | null;
	};

	type LogEntry = {
		id: string;
		title: string | null;
		brief: string | null;
		gameDate: string | Date | null;
		url: string | null;
		synopsis: string | null;
		placesSetIn?: {
			edges?: Array<{
				node: LogPlace;
			}> | null;
		} | null;
	};

	type LogGroup = {
		key: string;
		placeName: string;
		logs: LogEntry[];
	};

	type HeadingAction = {
		update: (groupKey: string) => void;
		destroy: () => void;
	};

	let { data }: { data: PageData } = $props();

	let LogList = $derived.by(() => fromStore(data.LogList).current);
	let activeStickyGroup = $state<string | null>(null);

	const headingElements = new SvelteMap<string, HTMLElement>();
	let scrollContainer: HTMLElement | null = null;

	function resolveLogPlace(log: LogEntry | undefined): LogPlace | null {
		const places = log?.placesSetIn?.edges?.map(({ node }) => node) ?? [];

		return (
			places.find((place) => place.placeType === 'PLANET') ??
			places.find((place) => place.name === 'Space') ??
			places.find((place) => place.name === 'In the ReDream') ??
			null
		);
	}

	function openExternalSource(url: string) {
		window.open(url, '_blank', 'noopener,noreferrer');
	}

	function handleExternalLinkKeydown(event: KeyboardEvent, url: string) {
		if (event.key !== 'Enter' && event.key !== ' ') return;

		event.preventDefault();
		openExternalSource(url);
	}

	function getGroupId(group: LogGroup): string {
		return `${group.key}-${group.logs[0]?.id ?? group.placeName}`;
	}

	function findScrollContainer(node: HTMLElement | null): HTMLElement | null {
		let parent = node?.parentElement ?? null;

		while (parent) {
			const styles = getComputedStyle(parent);
			if (styles.overflowY === 'auto' || styles.overflowY === 'scroll') {
				return parent;
			}

			parent = parent.parentElement;
		}

		return null;
	}

	function updateActiveStickyGroup() {
		if (!browser || !scrollContainer) return;

		const stickyTop = scrollContainer.getBoundingClientRect().top + 1;
		let nextActiveGroup: string | null = null;

		for (const group of groupedLogs) {
			const groupId = getGroupId(group);
			const heading = headingElements.get(groupId);

			if (!heading) continue;

			const rect = heading.getBoundingClientRect();
			if (rect.top <= stickyTop && rect.bottom > stickyTop) {
				nextActiveGroup = groupId;
			}
		}

		activeStickyGroup = nextActiveGroup;
	}

	function trackGroupHeading(node: HTMLElement, groupKey: string): HeadingAction {
		let currentGroupKey = groupKey;

		headingElements.set(currentGroupKey, node);
		scrollContainer ??= findScrollContainer(node);
		queueMicrotask(updateActiveStickyGroup);

		return {
			update(nextGroupKey) {
				if (nextGroupKey === currentGroupKey) return;

				headingElements.delete(currentGroupKey);
				currentGroupKey = nextGroupKey;
				headingElements.set(currentGroupKey, node);
				queueMicrotask(updateActiveStickyGroup);
			},
			destroy() {
				headingElements.delete(currentGroupKey);
				queueMicrotask(updateActiveStickyGroup);
			}
		};
	}

	let recordCount = $derived(LogList?.data?.gameLogs?.edges?.length ?? 0);

	let groupedLogs = $derived.by(() => {
		const logs = (LogList?.data?.gameLogs?.edges?.map(({ node }) => node) ?? []) as LogEntry[];
		const groups: LogGroup[] = [];

		for (const log of logs) {
			const place = resolveLogPlace(log);
			const key = place?.id ?? 'unknown';
			const placeName = place?.name ?? 'Unknown';
			const currentGroup = groups.at(-1);

			if (currentGroup && currentGroup.key === key) {
				currentGroup.logs.push(log);
				continue;
			}

			groups.push({
				key,
				placeName,
				logs: [log]
			});
		}

		return groups;
	});

	$effect(() => {
		if (!browser || !scrollContainer) return;

		const handleScroll = () => updateActiveStickyGroup();

		scrollContainer.addEventListener('scroll', handleScroll, { passive: true });
		window.addEventListener('resize', handleScroll);
		requestAnimationFrame(handleScroll);

		return () => {
			scrollContainer?.removeEventListener('scroll', handleScroll);
			window.removeEventListener('resize', handleScroll);
		};
	});
</script>

<div class="log-page">
	<div class="log-header">
		<h2 class="log-title">Chronicle</h2>
		<div class="text-industrial-amber font-mono text-xs">
			Records Found: {recordCount}
		</div>
	</div>

	<div class="log-group-stack">
		{#if LogList?.fetching}
			<div class="log-panel text-industrial-dim animate-pulse text-center font-mono">
				INITIALIZING DATALINK...
			</div>
		{:else if LogList?.errors}
			<div class="border border-red-900/50 bg-red-900/10 p-4 font-mono text-red-500">
				DATA CORRUPTION DETECTED.
				<pre class="mt-2 text-xs">{JSON.stringify(LogList.errors, null, 2)}</pre>
			</div>
		{:else if LogList?.data}
			{#if groupedLogs.length}
				{#each groupedLogs as group (getGroupId(group))}
					{@const groupId = getGroupId(group)}
					<section class="log-group" aria-label={`Logs set in ${group.placeName}`}>
						<div
							use:trackGroupHeading={groupId}
							class="log-group-heading"
							class:log-group-heading-active={activeStickyGroup === groupId}
						>
							<p
								class="log-group-title"
								class:log-group-title-active={activeStickyGroup === groupId}
							>
								{group.placeName}
							</p>
						</div>

						<div class="grid gap-4">
							{#each group.logs as log (log.id)}
								<div class="log-card">
									<div class="absolute top-0 bottom-0 left-0 w-1.5 bg-slate-700"></div>

									<div class="log-card-body relative z-10">
										<div
											class="mb-2 flex flex-col gap-2 sm:flex-row sm:items-baseline sm:justify-between"
										>
											<div class="min-w-0 flex-1">
												<h3 class="font-display min-w-0 text-xl font-medium text-slate-100">
													<a
														href={resolve(`/logs/${log.id}`)}
														class="decoration-industrial-amber/80 hover:text-industrial-amber underline-offset-4 transition-[color,text-decoration-color] hover:underline"
													>
														{log.title}
													</a>
													{#if log.url}
														{@const sourceUrl = log.url}
														<span
															role="link"
															tabindex="0"
															onclick={() => openExternalSource(sourceUrl)}
															onkeydown={(event) => handleExternalLinkKeydown(event, sourceUrl)}
															class="text-industrial-amber inline-flex cursor-pointer items-center justify-center rounded-sm px-1.5 py-0.5 transition-colors hover:text-slate-50"
															aria-label={`Open source for ${log.title ?? 'Untitled log'}`}
															title="Open source"
														>
															<ExternalLink class="h-3.5 w-3.5" aria-hidden="true" />
														</span>
													{/if}
												</h3>
											</div>
											<div class="relative z-20 flex shrink-0 items-center gap-2">
												<span class="font-mono text-xs text-slate-500"
													>{formatGameDate(log.gameDate)}</span
												>
											</div>
										</div>

										<p
											class="font-body line-clamp-2 text-sm leading-relaxed text-slate-300 sm:text-[15px]"
										>
											{log.brief || log.synopsis}
										</p>
									</div>
								</div>
							{/each}
						</div>
					</section>
				{/each}
			{:else}
				<div class="log-panel text-center font-mono text-slate-500">NO LOG RECORDS FOUND.</div>
			{/if}
		{/if}
	</div>
</div>
