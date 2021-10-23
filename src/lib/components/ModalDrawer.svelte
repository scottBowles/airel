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
	import Drawer, { AppContent, Content, Header, Title, Subtitle, Scrim } from '@smui/drawer';
	import Button, { Label } from '@smui/button';
	import List, { Item, Text, Graphic, Separator, Subheader } from '@smui/list';
	import { H6 } from '@smui/common/elements';

	import { page } from '$app/stores';

	$: currentPage = '/' + $page.path.split('/')[1];

	export let open = false;
</script>

<div class="drawer-container">
	<!-- Don't include fixed={false} if this is a page wide drawer.
        It adds a style for absolute positioning. -->
	<Drawer variant="modal" fixed={false} bind:open>
		<Header>
			<Title>Super Mail</Title>
			<Subtitle>It's the best fake mail app drawer.</Subtitle>
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
				<!-- <Item
					href="javascript:void(0)"
					on:click={() => setActive('Inbox')}
					activated={active === 'Inbox'}
				>
					<Graphic class="material-icons" aria-hidden="true">inbox</Graphic>
					<Text>Inbox</Text>
				</Item>
				<Item
					href="javascript:void(0)"
					on:click={() => setActive('Star')}
					activated={active === 'Star'}
				>
					<Graphic class="material-icons" aria-hidden="true">star</Graphic>
					<Text>Star</Text>
				</Item>
				<Item
					href="javascript:void(0)"
					on:click={() => setActive('Sent Mail')}
					activated={active === 'Sent Mail'}
				>
					<Graphic class="material-icons" aria-hidden="true">send</Graphic>
					<Text>Sent Mail</Text>
				</Item>
				<Item
					href="javascript:void(0)"
					on:click={() => setActive('Drafts')}
					activated={active === 'Drafts'}
				>
					<Graphic class="material-icons" aria-hidden="true">drafts</Graphic>
					<Text>Drafts</Text>
				</Item>

				<Separator />
				<Subheader component={H6}>Labels</Subheader>
				<Item
					href="javascript:void(0)"
					on:click={() => setActive('Family')}
					activated={active === 'Family'}
				>
					<Graphic class="material-icons" aria-hidden="true">bookmark</Graphic>
					<Text>Family</Text>
				</Item>
				<Item
					href="javascript:void(0)"
					on:click={() => setActive('Friends')}
					activated={active === 'Friends'}
				>
					<Graphic class="material-icons" aria-hidden="true">bookmark</Graphic>
					<Text>Friends</Text>
				</Item>
				<Item
					href="javascript:void(0)"
					on:click={() => setActive('Work')}
					activated={active === 'Work'}
				>
					<Graphic class="material-icons" aria-hidden="true">bookmark</Graphic>
					<Text>Work</Text>
				</Item> -->
			</List>
		</Content>
	</Drawer>

	<!-- Don't include fixed={false} if this is a page wide drawer.
        It adds a style for absolute positioning. -->
	<Scrim />
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
		/* height: 350px; */
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
