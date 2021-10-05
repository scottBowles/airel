<script lang="ts">
	import '$lib/styles/normalize.css';

	import TopAppBar, {
		Row,
		Section,
		Title,
		AutoAdjust,
		TopAppBarComponentDev
	} from '@smui/top-app-bar';
	import IconButton from '@smui/icon-button';

	import MenuDrawer from '$lib/components/MenuDrawer.svelte';

	let topAppBar: TopAppBarComponentDev;
	let isMenuDrawerOpen: boolean = false;
</script>

<TopAppBar bind:this={topAppBar} variant="standard">
	<Row>
		<Section>
			<IconButton class="material-icons" on:click={() => (isMenuDrawerOpen = !isMenuDrawerOpen)}
				>menu</IconButton
			>
			<Title>Standard</Title>
		</Section>
		<Section align="end" toolbar>
			<IconButton class="material-icons" aria-label="Download">file_download</IconButton>
			<IconButton class="material-icons" aria-label="Print this page">print</IconButton>
			<IconButton class="material-icons" aria-label="Bookmark this page">bookmark</IconButton>
		</Section>
	</Row>
</TopAppBar>
<AutoAdjust {topAppBar}>
	<MenuDrawer open={isMenuDrawerOpen} />
	<slot />
</AutoAdjust>

<style>
	/* Hide everything above this component. */
	:global(app),
	:global(body),
	:global(html) {
		display: block !important;
		height: auto !important;
		width: auto !important;
		position: static !important;
	}
</style>
