<script lang="ts">
	import { resolve } from '$app/paths';
	import { fade } from 'svelte/transition';
	import { Check, ExternalLink, Plus, X } from 'lucide-svelte';
	import { AddEntityLogStore, RemoveEntityLogStore } from '$houdini';
	import { detailSectionTitleClass, type LogNode } from '$lib/database-detail';
	import { toast } from 'svelte-sonner';

	let {
		entityId,
		logs,
		canEdit = false
	}: {
		entityId: string;
		logs: LogNode[];
		canEdit?: boolean;
	} = $props();

	let addFormOpen = $state(false);
	let addInput = $state('');
	let addPending = $state(false);
	let removePending = $state(false);
	let pendingRemoval = $state<LogNode | null>(null);

	const addStore = new AddEntityLogStore();
	const removeStore = new RemoveEntityLogStore();

	const focusOnAttach = ((element: HTMLElement) => {
		element.focus();
	}) satisfies import('svelte/attachments').Attachment<HTMLElement>;

	function openExternalLog(url: string) {
		window.open(url, '_blank', 'noopener,noreferrer');
	}

	function toggleAddForm() {
		addFormOpen = !addFormOpen;

		if (!addFormOpen) {
			addInput = '';
		}
	}

	function closeAddForm() {
		if (addPending) {
			return;
		}

		addFormOpen = false;
		addInput = '';
	}

	function requestRemoval(log: LogNode) {
		pendingRemoval = log;
	}

	function closeRemovalModal() {
		if (removePending) {
			return;
		}

		pendingRemoval = null;
	}

	function normalizeLogUrl(rawUrl: string) {
		try {
			const url = new URL(rawUrl.trim());

			if (!['http:', 'https:'].includes(url.protocol)) {
				return null;
			}

			return url.toString();
		} catch {
			return null;
		}
	}

	async function addLog() {
		const normalizedUrl = normalizeLogUrl(addInput);

		if (!normalizedUrl) {
			toast.error('Enter a valid log URL.');
			return;
		}

		addPending = true;

		try {
			await addStore.mutate({
				entityId,
				logUrl: normalizedUrl
			});

			addInput = '';
			addFormOpen = false;
			toast.success('Log linked.');
		} catch (error) {
			console.error('Failed to add log:', error);
			toast.error('Failed to link log.');
		} finally {
			addPending = false;
		}
	}

	async function confirmRemoval() {
		if (!pendingRemoval) {
			return;
		}

		removePending = true;

		try {
			await removeStore.mutate({
				entityId,
				logId: pendingRemoval.id
			});

			pendingRemoval = null;
			toast.success('Log removed.');
		} catch (error) {
			console.error('Failed to remove log:', error);
			toast.error('Failed to remove log.');
		} finally {
			removePending = false;
		}
	}

	function handleModalKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape') {
			event.preventDefault();
			closeRemovalModal();
		}
	}
</script>

<div class="space-y-4">
	<div class="border-b border-white/5 pb-3">
		<div>
			<h3 class={detailSectionTitleClass + ' mb-1'}>Logs</h3>
			<p class="text-xs leading-5 text-zinc-500">Chronicles connected to this record.</p>
		</div>
	</div>

	{#if logs.length > 0 || canEdit}
		<ul class="space-y-1.5">
			{#each logs as log (log.id)}
				<li
					class="flex items-center gap-2 rounded-sm border border-slate-800 bg-slate-950 px-2 py-1.5"
				>
					<a
						href={resolve(`/logs/${log.id}`)}
						class="min-w-0 flex-1 truncate text-sm text-zinc-200 transition-colors hover:text-emerald-300"
					>
						{log.title || 'Untitled log'}
					</a>
					<div class="flex shrink-0 items-center gap-1">
						<button
							type="button"
							onclick={() => openExternalLog(log.url)}
							class="inline-flex h-8 w-8 cursor-pointer items-center justify-center rounded-sm text-zinc-400 transition-colors hover:text-emerald-300"
							aria-label={`Open source document for ${log.title || 'this log'}`}
						>
							<ExternalLink class="h-3.5 w-3.5" aria-hidden="true" />
						</button>
						{#if canEdit}
							<button
								type="button"
								onclick={() => requestRemoval(log)}
								class="inline-flex h-8 w-8 cursor-pointer items-center justify-center rounded-sm text-zinc-500 transition-colors hover:text-rose-300"
								aria-label={`Remove ${log.title || 'this log'} from this record`}
							>
								<X class="h-3.5 w-3.5" aria-hidden="true" />
							</button>
						{/if}
					</div>
				</li>
			{/each}

			{#if canEdit && addFormOpen}
				<li
					in:fade={{ duration: 160 }}
					out:fade={{ duration: 100 }}
					class="flex items-center gap-2 rounded-sm border border-slate-700/70 bg-slate-950/70 px-2 py-1.5"
				>
					<input
						bind:value={addInput}
						type="url"
						{@attach focusOnAttach}
						placeholder="https://..."
						aria-label="Log URL"
						class="industrial-input h-10 min-w-0 flex-1 border-0 bg-transparent px-2 py-0 text-sm shadow-none outline-none"
						disabled={addPending}
						onkeydown={(event) => {
							if (event.key === 'Enter') {
								event.preventDefault();
								addLog();
							}

							if (event.key === 'Escape') {
								event.preventDefault();
								closeAddForm();
							}
						}}
					/>
					<div class="flex shrink-0 items-center gap-1">
						<button
							type="button"
							onclick={addLog}
							disabled={addPending}
							class="text-industrial-amber inline-flex h-8 w-8 items-center justify-center rounded-sm transition-colors hover:text-white disabled:opacity-50"
							aria-label="Confirm add log"
						>
							<Check class="h-3.5 w-3.5" aria-hidden="true" />
						</button>
						<button
							type="button"
							onclick={closeAddForm}
							disabled={addPending}
							class="inline-flex h-8 w-8 items-center justify-center rounded-sm text-zinc-500 transition-colors hover:text-white disabled:opacity-50"
							aria-label="Close add log form"
						>
							<X class="h-3.5 w-3.5" aria-hidden="true" />
						</button>
					</div>
				</li>
			{:else if canEdit}
				<li>
					<button
						type="button"
						onclick={toggleAddForm}
						class="text-industrial-amber flex h-11 w-full items-center gap-2 rounded-sm border border-slate-800/80 bg-slate-950/50 px-2 py-1.5 transition-colors hover:border-slate-700 hover:text-white"
						aria-label="Add log"
					>
						<span class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-sm">
							<Plus class="h-4 w-4" aria-hidden="true" />
						</span>
					</button>
				</li>
			{/if}
		</ul>
	{:else}
		<p class="text-sm text-zinc-500">
			{canEdit ? 'No linked logs yet.' : 'No linked logs recorded.'}
		</p>
	{/if}
</div>

{#if pendingRemoval}
	<button
		type="button"
		class="fixed inset-0 z-60 bg-slate-950/80 backdrop-blur-sm"
		tabindex="-1"
		onclick={closeRemovalModal}
		aria-label="Close remove log confirmation"
	></button>

	<div
		role="dialog"
		aria-modal="true"
		aria-labelledby="remove-log-title"
		aria-describedby="remove-log-description"
		tabindex="-1"
		class="fixed inset-x-3 top-1/2 z-70 -translate-y-1/2 rounded-sm border border-slate-700 bg-slate-950/96 shadow-[0_20px_60px_rgba(0,0,0,0.45)] sm:right-auto sm:left-1/2 sm:w-[min(22rem,calc(100vw-2rem))] sm:-translate-x-1/2"
		onkeydown={handleModalKeydown}
	>
		<div class="border-b border-slate-800 bg-slate-900/90 px-4 py-4">
			<p class="font-mono text-[11px] tracking-[0.18em] text-rose-300 uppercase">Confirm removal</p>
			<h4 id="remove-log-title" class="font-display mt-2 text-xl text-zinc-100">
				Remove linked log?
			</h4>
		</div>

		<div class="space-y-4 px-4 py-4 sm:px-5">
			<p id="remove-log-description" class="text-sm leading-6 text-zinc-300">
				Remove <span class="text-zinc-100">{pendingRemoval.title || 'Untitled log'}</span>?
			</p>

			<div class="flex flex-col gap-2 sm:flex-row sm:justify-end">
				<button
					type="button"
					{@attach focusOnAttach}
					onclick={closeRemovalModal}
					disabled={removePending}
					class="inline-flex min-h-11 items-center justify-center rounded border border-transparent px-3 py-2 text-xs text-slate-400 transition-colors hover:border-slate-600 hover:text-white"
				>
					Cancel
				</button>
				<button
					type="button"
					onclick={confirmRemoval}
					disabled={removePending}
					class="inline-flex min-h-11 items-center justify-center rounded border border-rose-500/40 bg-rose-500/12 px-3 py-2 text-xs font-bold text-rose-200 transition-colors hover:border-rose-400/70 hover:bg-rose-500/18 disabled:opacity-50"
				>
					{removePending ? 'REMOVING...' : 'REMOVE LOG'}
				</button>
			</div>
		</div>
	</div>
{/if}
