<script lang="ts">
	import { fromStore } from 'svelte/store';
	import { goto } from '$app/navigation';
	import { graphql } from '$houdini';
	import { toast } from 'svelte-sonner';
	import { MessageSquare, Plus, Clock } from 'lucide-svelte';
	import Button from '$lib/components/Button.svelte';
	import type { PageData } from './$houdini';

	let { data }: { data: PageData } = $props();
	let store = $derived(fromStore(data.ChatSessionList).current);
	let sessions = $derived(store?.data?.chatSessions?.edges ?? []);

	let startingChat = $state(false);

	const startChatMutation = graphql(`
		mutation StartNewChatSession($input: StartChatSessionInput!) {
			startChatSession(input: $input) {
				id
				title
			}
		}
	`);

	async function startNewChat() {
		startingChat = true;
		try {
			const result = await startChatMutation.mutate({
				input: { title: 'New Conversation' },
			});
			const session = result.data?.startChatSession;
			if (session) {
				goto(`/kozmo/${session.id}`);
			} else {
				toast.error('Failed to start chat');
			}
		} catch {
			toast.error('Failed to start chat');
		} finally {
			startingChat = false;
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
	<title>Kozmo — KSS Kontularien</title>
</svelte:head>

<div class="content-pad db-page">
	<div class="border border-border-dim bg-hull">
		<div class="flex items-center justify-between border-b border-border-dim px-3 py-1.5">
			<div class="flex items-center gap-2">
				<MessageSquare class="h-3 w-3 text-accent-green/40" />
				<span class="machine-text text-[9px] text-text-muted/60">AI-03 // KOZMO INTERFACE</span>
			</div>
			<span class="machine-text text-[9px] text-accent-green/60">● ONLINE</span>
		</div>
		<div class="flex items-center justify-between px-3 py-3">
			<div>
				<h1 class="title-display text-lg text-accent-green text-glow-green">KOZMO</h1>
				<p class="machine-text text-[10px] text-text-muted mt-0.5">
					Shipboard AI — conversational intelligence with full archive access
				</p>
			</div>
			<Button variant="primary" onclick={startNewChat} disabled={startingChat}>
				<Plus class="h-3 w-3" />
				{startingChat ? 'STARTING...' : 'NEW CHAT'}
			</Button>
		</div>
	</div>

	<!-- Chat splash -->
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
				<Button variant="primary" onclick={startNewChat} disabled={startingChat}>
					INITIALIZE SESSION
				</Button>
			</div>
		</div>
	{/if}

	<!-- Past sessions -->
	{#if sessions.length > 0}
		<div>
			<h2 class="title-section mb-3">Session Archive</h2>
			<div class="stack-space">
				{#each sessions as edge, i}
					{@const session = edge.node}
					<a
						href="/kozmo/{session.id}"
						class="group flex items-center gap-3 border border-border-dim bg-panel px-3 py-2.5 transition-all hover:border-accent-green/30 hover:bg-accent-green/5"
					>
						<span class="machine-text text-[9px] text-text-muted/40 w-8 shrink-0">#{String(sessions.length - i).padStart(3, '0')}</span>
						<MessageSquare class="h-3.5 w-3.5 shrink-0 text-accent-green/30 group-hover:text-accent-green" />
						<div class="min-w-0 flex-1">
							<p class="truncate text-xs text-text-primary group-hover:text-accent-green transition-colors">
								{session.title}
							</p>
						</div>
						<p class="machine-text flex items-center gap-1 text-[10px] text-text-muted/40">
							<Clock class="h-3 w-3" />
							{formatDate(session.updatedAt)}
						</p>
					</a>
				{/each}
			</div>
		</div>
	{/if}
</div>
