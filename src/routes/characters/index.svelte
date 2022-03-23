<script context="module" lang="ts">
	// import { useQueryClient } from '@sveltestack/svelte-query';

	import api from '$lib/api';

	export async function load({ fetch, session }) {
		// const queryClient = useQueryClient();

		/**
		 * check env. if browser, use useQuery. if not, fetch then
		 * queryClient.setQueryData OUTSIDE of the load function.
		 * or maybe useQuery outside of the load function with initial value?
		 * extra call, but does queryClient.setQueryData risk overwriting changed data?
		 */
		const token = session.token;
		const res = await api.get(`/characters`, token, fetch);
		const json = await res.json();
		return {
			props: {
				characters: json
			}
		};
	}
</script>

<script>
	// import { getAccessJwt, getDefaultHeaders } from '$lib/auth.js';
	// import { useQuery } from '@sveltestack/svelte-query';
	import { ROOT_URL } from '$lib/constants';
	import { onMount } from 'svelte';
	import { session } from '$app/stores';

	export let characters = [];

	onMount(async () => {
		const token = $session.token;
		const res = await api.get(`/characters`, token);
		const json = await res.json();
	});
	// import { listStore as characters } from '$lib/stores/characters.js';

	// const characterQuery = useQuery('characters', async () => {
	// 	const accessJwt = await getAccessJwt();
	// 	const headers = getDefaultHeaders(accessJwt);
	// 	console.log({ API_ROOT });
	// 	return fetch(`${API_ROOT}/characters`, { headers }).then((res) =>
	// 		res.json()
	// 	);
	// });
	// let characters;
	// $: characters = $characterQuery.data || [];
</script>

<svelte:head>
	<title>Character</title>
</svelte:head>

<h1 class="ml-4 pt-2">Characters</h1>

{#if characters?.loading}
	Loading...
{/if}
{#if characters}
	{#each characters as character}
		<a sveltekit:prefetch href={`${ROOT_URL}/characters/${character?.id}`}
			><p>Name: {character?.name}</p></a
		>
		<p>Player: {character?.player_name}</p>
		<div class="ability-scores-container">
			<div class="ability-score-container">
				<span>STR</span><span>{character?.strength}</span>
			</div>
			<div class="ability-score-container">
				<span>DEX</span><span>{character?.dexterity}</span>
			</div>
			<div class="ability-score-container">
				<span>CON</span><span>{character?.constitution}</span>
			</div>
			<div class="ability-score-container">
				<span>INT</span><span>{character?.intelligence}</span>
			</div>
			<div class="ability-score-container">
				<span>WIS</span><span>{character?.wisdom}</span>
			</div>
			<div class="ability-score-container mr-4 mt-4">
				<span class="pr-2">CHA</span><span>{character?.charisma}</span>
			</div>
		</div>
	{/each}
{/if}

<style>
	.ability-scores-container {
		display: flex;
		flex-direction: column;
	}

	.ability-score-container {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		border: 1px solid black;
		border-radius: 4px;
		width: 3rem;
		height: 3rem;
	}

	.ability-score-container span:first-child {
		font-weight: bold;
	}
</style>
