<script lang="ts">
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import { graphql } from '$houdini';
	import { ArrowLeft, Plus } from 'lucide-svelte';
	import Button from '$lib/components/Button.svelte';
	import Panel from '$lib/components/Panel.svelte';

	let name = $state('');
	let description = $state('');
	let markdownNotes = $state('');
	let loading = $state(false);

	const createMutation = graphql(`
		mutation CreateAssociation($input: AssociationInput!) {
			createAssociation(input: $input) {
				... on Association { id name }
				... on OperationInfo { messages { field kind message } }
			}
		}
	`);

	async function handleSubmit() {
		if (!name.trim()) { toast.error('Name is required'); return; }
		loading = true;
		try {
			const result = await createMutation.mutate({
				input: { name: name.trim(), description: description.trim() || undefined, markdownNotes: markdownNotes.trim() || undefined },
			});
			const payload = result.data?.createAssociation;
			if (payload?.__typename === 'Association') {
				toast.success('Association created');
				goto(`/database/associations/${payload.id}`);
			} else if (payload?.__typename === 'OperationInfo') {
				toast.error(payload.messages?.[0]?.message ?? 'Failed to create');
			}
		} catch { toast.error('An error occurred'); }
		finally { loading = false; }
	}
</script>

<svelte:head><title>New Association — Database — KSS Kontularien</title></svelte:head>

<div class="content-pad db-page">
	<a href="/database/associations" class="inline-flex items-center gap-2 text-xs text-text-muted uppercase tracking-wider transition-colors hover:text-accent-amber">
		<ArrowLeft class="h-3.5 w-3.5" /><span>Back to Associations</span>
	</a>

	<div class="border border-border-dim bg-hull px-3 py-3">
		<span class="machine-text text-[9px] text-text-muted block mb-1">ASC // NEW ENTRY</span>
		<h1 class="title-display text-lg text-accent-amber text-glow-amber">NEW ASSOCIATION</h1>
	</div>

	<Panel class="max-w-2xl">
		<form onsubmit={handleSubmit} class="stack-space">
			<div>
				<label for="name" class="title-section mb-2 block">Name *</label>
				<input id="name" bind:value={name} class="w-full bg-void border border-border-dim px-2.5 py-2 text-text-primary placeholder:text-text-faint focus:border-accent-amber focus:outline-none" placeholder="Association name" />
			</div>
			<div>
				<label for="desc" class="title-section mb-2 block">Description</label>
				<textarea id="desc" bind:value={description} rows="3" class="w-full resize-y bg-void border border-border-dim px-2.5 py-2 text-text-primary placeholder:text-text-faint focus:border-accent-amber focus:outline-none" placeholder="Brief description"></textarea>
			</div>
			<div>
				<label for="notes" class="title-section mb-2 block">Notes</label>
				<textarea id="notes" bind:value={markdownNotes} rows="6" class="w-full resize-y bg-void border border-border-dim px-2.5 py-2 font-mono text-sm text-text-primary placeholder:text-text-faint focus:border-accent-amber focus:outline-none" placeholder="Detailed notes..."></textarea>
			</div>
			<Button type="submit" variant="primary" disabled={loading}>
				<Plus class="h-3 w-3" />
				{loading ? 'CREATING...' : 'CREATE'}
			</Button>
		</form>
	</Panel>
</div>
