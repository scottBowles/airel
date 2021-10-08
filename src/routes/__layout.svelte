<script lang="ts">
	import '$lib/styles/normalize.css';
	import TopAppBar from '$lib/components/TopAppBar.svelte';
	import MenuDrawer from '$lib/components/MenuDrawer.svelte';
	import ModalDrawer from '$lib/components/ModalDrawer.svelte';
	import MediaQuery from '$lib/components/MediaQuery.svelte';

	let isMenuDrawerOpen: boolean = false;
	let toggleMenuDrawer = () => {
		isMenuDrawerOpen = !isMenuDrawerOpen;
	};
</script>

<TopAppBar {toggleMenuDrawer}>
	<MediaQuery query="(max-width: 480px)" let:matches>
		{#if matches}
			<ModalDrawer bind:open={isMenuDrawerOpen}><slot /></ModalDrawer>
		{:else}
			<MenuDrawer bind:open={isMenuDrawerOpen}><slot /></MenuDrawer>
		{/if}
	</MediaQuery>
</TopAppBar>
