<script lang="ts">
	import { graphql } from '$houdini';
	import { toast } from 'svelte-sonner';
	import { formatGameDate } from '$lib/utils';
	import { getUserContext } from '$lib/auth';
	import BookOpen from '@lucide/svelte/icons/book-open';
	import Calendar from '@lucide/svelte/icons/calendar';
	import Plus from '@lucide/svelte/icons/plus';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import Panel from '$lib/components/Panel.svelte';
	import Button from '$lib/components/Button.svelte';
	import ConfirmDialog from '$lib/components/ConfirmDialog.svelte';

	type LogConnection = {
		edges: Array<{ node: { id: string; title: string | null; gameDate: Date | null } }>;
	} | null;

	let {
		entityId,
		logs,
	}: {
		entityId: string;
		logs: LogConnection;
	} = $props();

	const getUser = getUserContext();
	let isStaff = $derived(!!getUser()?.isStaff);

	let logUrl = $state('');
	let adding = $state(false);
	let showAddForm = $state(false);
	let confirmDeleteId = $state<string | null>(null);
	let inputEl = $state<HTMLInputElement | null>(null);

	const addLogMutation = graphql(`
		mutation AddEntityLogMutation($input: AddEntityLogInput!) {
			addEntityLog(input: $input) {
				... on Artifact { id logs(first: 50, order: { gameDate: DESC }) { edges { node { id title gameDate } } } }
				... on Association { id logs(first: 50, order: { gameDate: DESC }) { edges { node { id title gameDate } } } }
				... on Character { id logs(first: 50, order: { gameDate: DESC }) { edges { node { id title gameDate } } } }
				... on Item { id logs(first: 50, order: { gameDate: DESC }) { edges { node { id title gameDate } } } }
				... on Place { id logs(first: 50, order: { gameDate: DESC }) { edges { node { id title gameDate } } } }
				... on Race { id logs(first: 50, order: { gameDate: DESC }) { edges { node { id title gameDate } } } }
			}
		}
	`);

	const removeLogMutation = graphql(`
		mutation RemoveEntityLogMutation($input: RemoveEntityLogInput!) {
			removeEntityLog(input: $input) {
				... on Artifact { id logs(first: 50, order: { gameDate: DESC }) { edges { node { id title gameDate } } } }
				... on Association { id logs(first: 50, order: { gameDate: DESC }) { edges { node { id title gameDate } } } }
				... on Character { id logs(first: 50, order: { gameDate: DESC }) { edges { node { id title gameDate } } } }
				... on Item { id logs(first: 50, order: { gameDate: DESC }) { edges { node { id title gameDate } } } }
				... on Place { id logs(first: 50, order: { gameDate: DESC }) { edges { node { id title gameDate } } } }
				... on Race { id logs(first: 50, order: { gameDate: DESC }) { edges { node { id title gameDate } } } }
			}
		}
	`);

	async function addLog() {
		if (!logUrl.trim()) return;
		adding = true;
		try {
			await addLogMutation.mutate({
				input: { entityId, logUrl: logUrl.trim() },
			});
			logUrl = '';
			showAddForm = false;
			toast.success('Log added');
		} catch {
			toast.error('Failed to add log');
		} finally {
			adding = false;
		}
	}

	async function removeLog(logId: string) {
		try {
			await removeLogMutation.mutate({
				input: { entityId, logId },
			});
			toast.success('Log removed');
		} catch {
			toast.error('Failed to remove log');
		}
	}

	function openAddForm() {
		showAddForm = true;
		// Focus the input after it renders
		setTimeout(() => inputEl?.focus(), 0);
	}

	function handleInputKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			showAddForm = false;
			logUrl = '';
		}
	}
</script>

<ConfirmDialog
	open={!!confirmDeleteId}
	title="Remove Log"
	message="Remove this log from the entity?"
	confirmLabel="Remove"
	onconfirm={() => { if (confirmDeleteId) removeLog(confirmDeleteId); confirmDeleteId = null; }}
	oncancel={() => { confirmDeleteId = null; }}
/>

<Panel>
	<div class="mb-2 flex items-center justify-between">
		<h3 class="title-section flex items-center gap-2">
			<BookOpen class="h-3 w-3 text-text-muted" />
			Logs
		</h3>
	</div>

	{#if logs && logs.edges.length > 0}
		<div class="space-y-px">
			{#each logs.edges as edge}
				<div class="group flex items-center justify-between">
					<a
						href="/chronicle/{edge.node.id}"
						class="flex min-w-0 flex-1 items-center gap-2 px-2 py-1 text-xs text-text-secondary transition-colors hover:bg-accent-amber/5 hover:text-accent-amber"
					>
						<Calendar class="h-3 w-3 shrink-0 text-accent-amber/30" />
						<span class="truncate uppercase tracking-wider">
							{edge.node.title ?? formatGameDate(edge.node.gameDate)}
						</span>
					</a>
					{#if isStaff}
						<button
							onclick={() => { confirmDeleteId = edge.node.id; }}
							class="shrink-0 cursor-pointer p-1 text-text-muted opacity-0 transition-opacity hover:text-accent-red group-hover:opacity-100"
						>
							<Trash2 class="h-3 w-3" />
						</button>
					{/if}
				</div>
			{/each}
		</div>
	{:else}
		<p class="py-2 text-center text-[10px] text-text-muted">No logs</p>
	{/if}

	{#if isStaff && !showAddForm}
		<div class="mt-2 flex justify-start">
			<button
				onclick={openAddForm}
				class="cursor-pointer p-0.5 text-text-muted transition-colors hover:text-accent-amber"
			>
				<Plus class="h-3.5 w-3.5" />
			</button>
		</div>
	{/if}

	{#if showAddForm}
		<div class="mt-2 flex gap-1">
			<input
				bind:this={inputEl}
				bind:value={logUrl}
				onkeydown={handleInputKeydown}
				placeholder="Google Docs URL..."
				class="flex-1 border border-border-dim bg-bg-inset px-2 py-1 text-xs text-text-primary outline-none placeholder:text-text-faint focus:border-accent-amber"
			/>
			<Button size="sm" onclick={addLog} disabled={adding || !logUrl.trim()}>
				<Plus class="mr-1 h-3 w-3" />
				Add
			</Button>
		</div>
	{/if}
</Panel>
