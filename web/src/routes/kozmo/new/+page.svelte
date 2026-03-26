<script lang="ts">
	import { tick } from 'svelte';
	import { goto, replaceState } from '$app/navigation';
	import { graphql } from '$houdini';
	import { toast } from 'svelte-sonner';
	import { getUserContext } from '$lib/auth';
	import { streamChat } from '$lib/streamChat';
	import {
		ArrowLeft,
		Send,
		User,
		Bot,
		Loader2,
	} from 'lucide-svelte';

	const getUser = getUserContext();
	let isStaff = $derived(!!getUser()?.isStaff);

	$effect(() => {
		if (!isStaff) goto('/kozmo');
	});

	let messages = $state<Array<{ id: string; message: string; response: string; createdAt: string }>>([]);
	let inputValue = $state('');
	let sending = $state(false);
	let streaming = $state(false);
	let messagesEnd = $state<HTMLDivElement | null>(null);
	// Once a session is created, store its ID for follow-up messages
	let sessionId = $state<string | null>(null);
	let sessionTitle = $state<string | null>(null);

	const startChatMutation = graphql(`
		mutation StartNewChatSessionWithMessage($input: StartChatSessionInput!) {
			startChatSession(input: $input) {
				id
				title
			}
		}
	`);

	async function scrollToBottom() {
		await tick();
		messagesEnd?.scrollIntoView({ behavior: 'smooth' });
	}

	async function sendMessage() {
		if (!inputValue.trim() || sending) return;

		const userMessage = inputValue.trim();
		inputValue = '';
		sending = true;
		streaming = false;

		const tempId = `temp-${Date.now()}`;
		messages = [
			...messages,
			{ id: tempId, message: userMessage, response: '', createdAt: new Date().toISOString() },
		];
		await scrollToBottom();

		try {
			// Create the session on first message, reuse for follow-ups
			let currentSessionId = sessionId;
			if (!currentSessionId) {
				const sessionResult = await startChatMutation.mutate({
					input: { title: userMessage.slice(0, 80) },
				});
				const session = sessionResult.data?.startChatSession;
				if (!session) {
					messages = messages.filter((m) => m.id !== tempId);
					toast.error('Failed to start chat');
					return;
				}
				currentSessionId = session.id;
				sessionId = session.id;
				sessionTitle = session.title;

				// Update URL without triggering navigation — no flash
				replaceState(`/kozmo/${session.id}`, {});
			}

			await streamChat({
				sessionId: currentSessionId,
				message: userMessage,
				onToken(token) {
					streaming = true;
					messages = messages.map((m) =>
						m.id === tempId ? { ...m, response: m.response + token } : m,
					);
					scrollToBottom();
				},
				onDone() {
					// Already on the right URL — nothing to do
				},
				onError(error) {
					if (!messages.find((m) => m.id === tempId)?.response) {
						messages = messages.filter((m) => m.id !== tempId);
					}
					toast.error(error || 'Kozmo failed to respond');
				},
			});
		} catch {
			messages = messages.filter((m) => m.id !== tempId);
			toast.error('Communication error');
		} finally {
			sending = false;
			streaming = false;
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			sendMessage();
		}
	}
</script>

<svelte:head>
	<title>{sessionTitle ? `${sessionTitle} — ` : ''}New Chat — Kozmo — Kontularien</title>
</svelte:head>

<div class="flex min-h-0 flex-1 flex-col">
	<!-- Header -->
	<header class="flex shrink-0 items-center gap-3 border-b border-border-dim bg-hull px-3 py-2">
		<a
			href="/kozmo"
			class="flex h-7 w-7 items-center justify-center text-text-muted transition-colors hover:bg-accent-amber/10 hover:text-accent-amber"
		>
			<ArrowLeft class="h-3.5 w-3.5" />
		</a>
		<div class="flex items-center gap-2">
			<Bot class="h-4 w-4 text-accent-green" />
			<h1 class="machine-text text-xs text-text-primary uppercase tracking-wider">
				{sessionTitle ?? 'New Session'}
			</h1>
		</div>
		<div class="ml-auto">
			<span class="machine-text text-accent-green/60 text-[9px]">● ONLINE</span>
		</div>
	</header>

	<!-- Messages -->
	<div class="flex-1 overflow-y-auto p-4">
		<div class="mx-auto max-w-3xl space-y-5">
			{#if messages.length === 0}
				<div class="flex flex-col items-center justify-center py-16 text-center">
					<Bot class="h-8 w-8 text-accent-green/20 mb-3" />
					<p class="machine-text text-xs text-accent-green/50 uppercase tracking-wider">
						Kozmo Ready
					</p>
					<p class="machine-text mt-2 max-w-sm text-xs text-text-secondary">
						Ask me about past missions, crew members, places we've visited, or anything from the ship's archives.
					</p>
				</div>
			{/if}

			{#each messages as msg}
				<div class="flex items-start gap-3">
					<div class="flex h-7 w-7 shrink-0 items-center justify-center border border-accent-cyan/20 bg-accent-cyan/5">
						<User class="h-3.5 w-3.5 text-accent-cyan" />
					</div>
					<div class="min-w-0 flex-1">
						<p class="machine-text mb-1 text-accent-cyan/50 text-[9px]">CREW</p>
						<div class="text-xs text-text-primary">{msg.message}</div>
					</div>
				</div>

				{#if msg.response}
					<div class="flex items-start gap-3">
						<div class="flex h-7 w-7 shrink-0 items-center justify-center border border-accent-green/20 bg-accent-green/5">
							<Bot class="h-3.5 w-3.5 text-accent-green" />
						</div>
						<div class="min-w-0 flex-1">
							<p class="machine-text mb-1 text-accent-green/50 text-[9px]">KOZMO</p>
							<div class="whitespace-pre-wrap text-xs text-text-secondary leading-relaxed">
								{msg.response}{#if streaming && msg.id.startsWith('temp-')}<span class="inline-block w-1.5 h-3 bg-accent-green/70 animate-pulse ml-0.5 align-middle"></span>{/if}
							</div>
						</div>
					</div>
				{:else if sending}
					<div class="flex items-start gap-3">
						<div class="flex h-7 w-7 shrink-0 items-center justify-center border border-accent-green/20 bg-accent-green/5">
							<Bot class="h-3.5 w-3.5 text-accent-green" />
						</div>
						<div>
							<p class="machine-text mb-1 text-accent-green/50 text-[9px]">KOZMO</p>
							<div class="flex items-center gap-2 text-xs text-text-muted">
								<Loader2 class="h-3.5 w-3.5 animate-spin text-accent-green" />
								<span class="machine-text">Searching ship's archives...</span>
							</div>
						</div>
					</div>
				{/if}
			{/each}

			<div bind:this={messagesEnd}></div>
		</div>
	</div>

	<!-- Input -->
	<div class="shrink-0 border-t border-border-dim bg-hull px-3 py-3">
		<div class="mx-auto flex max-w-3xl items-end gap-2">
			<textarea
				bind:value={inputValue}
				onkeydown={handleKeydown}
				placeholder="Ask Kozmo anything..."
				rows="1"
				class="flex-1 resize-none border border-border-dim bg-void px-3 py-2 text-xs text-text-primary placeholder:text-text-faint focus:border-accent-green focus:outline-none"
			></textarea>
			<button
				onclick={sendMessage}
				disabled={sending || !inputValue.trim()}
				class="flex h-9 w-9 shrink-0 items-center justify-center border border-accent-green/30 bg-accent-green/10 text-accent-green transition-all hover:bg-accent-green/20 disabled:opacity-30 disabled:cursor-not-allowed"
			>
				{#if sending}
					<Loader2 class="h-3.5 w-3.5 animate-spin" />
				{:else}
					<Send class="h-3.5 w-3.5" />
				{/if}
			</button>
		</div>
	</div>
</div>
