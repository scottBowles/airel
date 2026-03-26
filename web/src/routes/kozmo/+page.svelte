<script lang="ts">
	import { fromStore } from 'svelte/store';
	import { ChatSessionListStore, graphql } from '$houdini';
	import { page } from '$app/state';
	import { toast } from 'svelte-sonner';
	import { MessageSquare, Plus, Clock, LogIn, Trash2 } from 'lucide-svelte';
	import { getUserContext } from '$lib/auth';
	import Button from '$lib/components/Button.svelte';
	import ConfirmDialog from '$lib/components/ConfirmDialog.svelte';
	import type { PageData } from './$houdini';
	import { SvelteSet } from 'svelte/reactivity';

	let { data }: { data: PageData } = $props();
	let store = $derived(fromStore(data.ChatSessionList).current);
	let allSessions = $derived(store?.data?.chatSessions?.edges ?? []);
	let archivedIds = new SvelteSet();
	let sessions = $derived(allSessions.filter((edge) => !archivedIds.has(edge.node.id)));

	const getUser = getUserContext();
	let user = $derived(getUser());
	let isStaff = $derived(!!user?.isStaff);

	let confirmArchiveId = $state<string | null>(null);

	const archiveMutation = graphql(`
		mutation ArchiveChatSession($input: ArchiveChatSessionInput!) {
			archiveChatSession(input: $input) {
				id
				title
			}
		}
	`);

	async function archiveSession(sessionId: string) {
		try {
			await archiveMutation.mutate({ input: { sessionId } });
			archivedIds.add(sessionId);
			archivedIds = archivedIds;
			toast.success('Session archived');
		} catch {
			toast.error('Failed to archive session');
		}
	}

	function formatDate(date: Date | string | null) {
		if (!date) return '';
		const d = typeof date === 'string' ? new Date(date) : date;
		return d.toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit',
		});
	}
</script>

<svelte:head>
	<title>Kozmo — Kontularien</title>
</svelte:head>

<div class="content-pad db-page">
	<ConfirmDialog
		open={!!confirmArchiveId}
		title="Archive Session"
		message="Archive this chat session? It will no longer appear in your session list."
		confirmLabel="Archive"
		onconfirm={() => { if (confirmArchiveId) archiveSession(confirmArchiveId); confirmArchiveId = null; }}
		oncancel={() => { confirmArchiveId = null; }}
	/>
	<div class="border border-border-dim bg-hull">
		<div class="flex items-center justify-between border-b border-border-dim px-3 py-1.5">
			<div class="flex items-center gap-2">
				<MessageSquare class="h-3 w-3 text-accent-green/40" />
				<span class="machine-text text-[9px] text-text-muted">AI-03 // KOZMO INTERFACE</span>
			</div>
			<span class="machine-text text-[9px] text-accent-green/60">● ONLINE</span>
		</div>
		<div class="flex flex-col gap-2 px-3 py-3 sm:flex-row sm:items-center sm:justify-between">
			<div>
				<h1 class="title-display text-lg text-accent-green text-glow-green">KOZMO</h1>
				<p class="machine-text text-[10px] text-text-muted mt-0.5">
					Shipboard AI — conversational intelligence with full archive access
				</p>
			</div>
			{#if isStaff}
				<Button variant="primary" href="/kozmo/new">
					<Plus class="h-3 w-3" />
					NEW CHAT
				</Button>
			{/if}
		</div>
	</div>

	{#if !user}
		<div class="border border-border-dim bg-panel px-4 py-6 text-center">
			<div class="mx-auto mb-3 flex h-10 w-10 items-center justify-center border border-accent-amber/20 bg-accent-amber/5">
				<LogIn class="h-5 w-5 text-accent-amber" />
			</div>
			<p class="machine-text text-xs text-accent-amber/60 uppercase tracking-wider">
				Authentication Required
			</p>
			<p class="machine-text mt-2 text-[10px] text-text-muted max-w-md mx-auto">
				Log in with your crew credentials to access the Kozmo AI interface.
			</p>
			<div class="mt-4">
				<Button variant="primary" href="/login?redirect={encodeURIComponent(page.url.pathname + page.url.search)}">
					<LogIn class="h-3 w-3" />
					SYSTEM ACCESS
				</Button>
			</div>
		</div>
	{:else if !isStaff}
		<div class="border border-border-dim bg-panel px-4 py-6 text-center">
			<p class="machine-text text-xs text-accent-red/60 uppercase tracking-wider">
				Insufficient Clearance
			</p>
			<p class="machine-text mt-2 text-[10px] text-text-muted max-w-md mx-auto">
				Admin clearance is required to access the Kozmo AI interface.
			</p>
		</div>
	{:else}
		{#if sessions.length === 0}
			<div class="border border-border-dim bg-panel px-4 py-6 text-center">
				<div class="mx-auto mb-3 flex h-10 w-10 items-center justify-center border border-accent-green/20 bg-accent-green/5">
					<MessageSquare class="h-5 w-5 text-accent-green" />
				</div>
				<p class="machine-text text-xs text-accent-green/60 uppercase tracking-wider">
					No active sessions
				</p>
				<p class="machine-text mt-2 text-[10px] text-text-muted max-w-md mx-auto">
					I have access to all ship logs, crew profiles, and the complete entity database.
				</p>
				<div class="mt-4">
					<Button variant="primary" href="/kozmo/new">
						INITIALIZE SESSION
					</Button>
				</div>
			</div>
		{/if}

		{#if sessions.length > 0}
			<div>
				<h2 class="title-section mb-3">Session Archive</h2>
				<div class="stack-space">
					{#each sessions as edge, i}
						{@const session = edge.node}
						<div class="group flex items-center border border-border-dim bg-panel transition-all hover:border-accent-green/30 hover:bg-accent-green/5">
							<a
								href="/kozmo/{session.id}"
								class="flex min-w-0 flex-1 items-center gap-3 px-3 py-2.5"
							>
								<span class="machine-text text-[9px] text-text-faint w-8 shrink-0">#{String(sessions.length - i).padStart(3, '0')}</span>
								<MessageSquare class="h-3.5 w-3.5 shrink-0 text-accent-green/30 group-hover:text-accent-green" />
								<div class="min-w-0 flex-1">
									<p class="truncate text-xs text-text-primary group-hover:text-accent-green transition-colors">
										{session.title}
									</p>
								</div>
								<p class="machine-text flex items-center gap-1 text-[10px] text-text-muted">
									<Clock class="h-3 w-3" />
									{formatDate(session.updatedAt)}
								</p>
							</a>
							{#if isStaff}
								<button
									onclick={(e) => { e.preventDefault(); confirmArchiveId = session.id; }}
									class="shrink-0 cursor-pointer p-2 text-text-muted opacity-0 transition-opacity hover:text-accent-red group-hover:opacity-100"
								>
									<Trash2 class="h-3.5 w-3.5" />
								</button>
							{/if}
						</div>
					{/each}
				</div>
			</div>
		{/if}
	{/if}
</div>
