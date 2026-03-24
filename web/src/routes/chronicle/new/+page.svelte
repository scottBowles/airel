<script lang="ts">
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import { graphql } from '$houdini';
	import { ArrowLeft, Plus } from 'lucide-svelte';
	import Button from '$lib/components/Button.svelte';
	import Panel from '$lib/components/Panel.svelte';

	let url = $state('');
	let loading = $state(false);

	const getOrCreateGameLog = graphql(`
		mutation CreateNewGameLog($input: GetOrCreateGameLogInput!) {
			getOrCreateGameLog(input: $input) {
				... on GameLog {
					id
					title
					url
				}
				... on OperationInfo {
					messages { field kind message }
				}
			}
		}
	`);

	async function handleSubmit() {
		if (!url.trim()) {
			toast.error('Please enter a Google Docs URL');
			return;
		}
		loading = true;
		try {
			const result = await getOrCreateGameLog.mutate({
				input: { url: url.trim(), lock: false },
			});
			const payload = result.data?.getOrCreateGameLog;
			if (payload?.__typename === 'GameLog') {
				toast.success('Log created');
				goto(`/chronicle/${payload.id}`);
			} else if (payload?.__typename === 'OperationInfo') {
				toast.error(payload.messages?.[0]?.message ?? 'Failed to create log');
			}
		} catch (err) {
			toast.error('An error occurred');
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>New Log — Chronicle — KSS Kontularien</title>
</svelte:head>

<div class="content-pad db-page">
	<a
		href="/chronicle"
		class="inline-flex items-center gap-2 text-xs text-text-muted uppercase tracking-wider transition-colors hover:text-accent-amber"
	>
		<ArrowLeft class="h-3.5 w-3.5" />
		<span>Back to Chronicle</span>
	</a>

	<div class="border border-border-dim bg-hull px-3 py-3">
		<span class="machine-text text-[9px] text-text-muted/60 block mb-1">NEW ENTRY</span>
		<h1 class="title-display text-lg text-accent-amber text-glow-amber">ADD SESSION LOG</h1>
		<p class="machine-text text-[10px] text-text-muted mt-1">
			Import a session log from Google Docs
		</p>
	</div>

	<Panel class="max-w-xl">
		<form onsubmit={handleSubmit} class="stack-space">
			<div>
				<label for="doc-url" class="title-section mb-2 block">Document URL</label>
				<input
					id="doc-url"
					type="url"
					bind:value={url}
					placeholder="https://docs.google.com/document/d/..."
					class="w-full bg-void border border-border-dim px-2.5 py-2 text-xs text-text-primary placeholder:text-text-muted focus:border-accent-amber focus:outline-none"
				/>
			</div>
			<Button type="submit" variant="primary" disabled={loading}>
				<Plus class="h-3 w-3" />
				{loading ? 'PROCESSING...' : 'IMPORT LOG'}
			</Button>
		</form>
	</Panel>
</div>
