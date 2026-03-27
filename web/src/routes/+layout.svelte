<script lang="ts">
	import '../app.css';
	import { fromStore } from 'svelte/store';
	import { afterNavigate } from '$app/navigation';
	import { navigating } from '$app/state';
	import { graphql } from '$houdini';
	import { Toaster } from 'svelte-sonner';
	import { setUserContext } from '$lib/auth';
	import { Tooltip } from 'bits-ui';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import CommandPalette from '$lib/components/CommandPalette.svelte';

	let { data, children } = $props();
	let isNavigating = $derived(!!navigating.to);
	let meResult = $derived.by(() => fromStore(data.Me).current);
	let user = $derived(meResult?.data?.me);

	setUserContext(() => user);

	const recordPageView = graphql(`
		mutation RecordPageView($path: String!) {
			recordPageView(path: $path)
		}
	`);

	afterNavigate((navigation) => {
		const path = navigation.to?.url.pathname;
		if (path) {
			recordPageView.mutate({ path }).catch(() => {});
		}
	});

	let searchOpen = $state(false);
</script>

<Tooltip.Provider>
<Toaster theme="dark" position="top-right" richColors />
<CommandPalette bind:open={searchOpen} />

{#if isNavigating}
	<div class="fixed top-0 left-0 right-0 z-[10000] h-0.5 bg-accent-amber/20">
		<div class="h-full w-1/3 bg-accent-amber shadow-[0_0_8px_rgba(255,176,0,0.6)] animate-[nav-progress_1.5s_ease-in-out_infinite]"></div>
	</div>
{/if}

<div class="flex h-dvh">
	<Sidebar {user} onsearch={() => (searchOpen = true)} />

	<!-- Main content area -->
	<main class="flex h-dvh flex-1 flex-col overflow-y-auto pt-9 pb-14 lg:pl-56 lg:pt-0 lg:pb-0">
		{@render children()}
	</main>
</div>
</Tooltip.Provider>