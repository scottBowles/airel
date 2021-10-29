<script lang="ts">
	import { useQuery } from '@sveltestack/svelte-query';
	import { page } from '$app/stores';
	import { getAccessJwt, getDefaultHeaders } from '$lib/auth.js';

	const { id } = $page.params;

	const ROOT_URL = 'http://localhost:3000';
	const API_ROOT = 'http://127.0.0.1:8000';

	const characterQuery = useQuery(['characters', id], async () => {
		const accessJwt = await getAccessJwt();
		const headers = getDefaultHeaders(accessJwt);
		return fetch(`${API_ROOT}/characters/${id}`, { headers }).then((res) =>
			res.json()
		);
	});

	let character;
	$: character = $characterQuery.data || {};
</script>

<svelte:head>
	<title>Character</title>
</svelte:head>

{#if character?.loading}
	Loading...
{/if}
{#if character}
	<h1 class="ml-4 pt-2">{character.name}</h1>
	<div class="ability-scores-container">
		<div class="ability-score-container">
			<span>STR</span><span>{character.strength}</span>
		</div>
		<div class="ability-score-container">
			<span>DEX</span><span>{character.dexterity}</span>
		</div>
		<div class="ability-score-container">
			<span>CON</span><span>{character.constitution}</span>
		</div>
		<div class="ability-score-container">
			<span>INT</span><span>{character.intelligence}</span>
		</div>
		<div class="ability-score-container">
			<span>WIS</span><span>{character.wisdom}</span>
		</div>
		<div class="ability-score-container mr-4 mt-4">
			<span class="pr-2">CHA</span><span>{character.charisma}</span>
		</div>
	</div>
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
