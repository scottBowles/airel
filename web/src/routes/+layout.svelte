<script lang="ts">
	import '../app.css';
	import { fromStore } from 'svelte/store';
	import { Toaster } from 'svelte-sonner';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import CommandPalette from '$lib/components/CommandPalette.svelte';

	let { data, children } = $props();
	let meResult = $derived.by(() => fromStore(data.Me).current);
	let user = $derived(meResult?.data?.me);

	let searchOpen = $state(false);
</script>

<Toaster theme="dark" position="top-right" richColors />
<CommandPalette bind:open={searchOpen} />

<div class="flex min-h-dvh">
	<Sidebar {user} onsearch={() => (searchOpen = true)} />

	<!-- Main content area -->
	<main class="min-h-dvh flex-1 lg:pl-56">
		{@render children()}
	</main>
</div>