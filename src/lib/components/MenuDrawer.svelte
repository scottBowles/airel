<script context="module" lang="ts">
	const mainNavLinks = [
		{ label: 'Dashboard', href: '/' },
		{ label: 'NPCs', href: '/npcs' },
		{ label: 'Places', href: '/places' },
		{ label: 'Races', href: '/races' },
		{ label: 'Items', href: '/items' },
		{ label: 'Associations', href: '/associations' },
		{ label: 'Scientia', href: '/scientia' }
	];

	const profileNavLinks = [
		{ label: 'Profile', href: '/profile' },
		{ label: 'Settings', href: '/settings' },
		{ label: 'Logout', href: '/' }
	];
</script>

<script lang="ts">
	import Drawer, { AppContent, Content, Header, Title, Subtitle } from '@smui/drawer';
	import List, { Item, Text } from '@smui/list';

	import { page } from '$app/stores';

	$: currentPage = '/' + $page.path.split('/')[1];

	export let open;
</script>

<div class="drawer-container">
	<Drawer variant="dismissible" bind:open>
		<Header>
			<Title>Super Drawer</Title>
			<Subtitle>It's the best drawer.</Subtitle>
		</Header>

		<Content>
			<List>
				{#each mainNavLinks as { label, href }}
					<a {href} sveltekit:prefetch>
						<Item activated={href === currentPage}>
							<Text>{label}</Text>
						</Item>
					</a>
				{/each}
			</List>
		</Content>
	</Drawer>

	<AppContent class="app-content">
		<main class="main-content">
			<slot />
		</main>
	</AppContent>
</div>

<style>
	/* These classes are only needed because the
    drawer is in a container on the page. */
	.drawer-container {
		position: relative;
		display: flex;
		height: 350px;
		max-width: 600px;
		border: 1px solid var(--mdc-theme-text-hint-on-background, rgba(0, 0, 0, 0.1));
		overflow: hidden;
		z-index: 0;
	}

	* :global(.app-content) {
		flex: auto;
		overflow: auto;
		position: relative;
		flex-grow: 1;
	}

	.main-content {
		overflow: auto;
		padding: 16px;
		height: 100%;
		box-sizing: border-box;
	}

	a {
		text-decoration: none;
		color: inherit;
	}
</style>
