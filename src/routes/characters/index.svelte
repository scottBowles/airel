<script>
	import { getAccessJwt, getDefaultHeaders } from '$lib/auth.js';
	import { ROOT_URL, API_ROOT } from '$lib/constants';
	import { useQuery } from '@sveltestack/svelte-query';
	// import { listStore as characters } from '$lib/stores/characters.js';

	const characterQuery = useQuery('characters', async () => {
		const accessJwt = await getAccessJwt();
		const headers = getDefaultHeaders(accessJwt);
		console.log({ API_ROOT });
		return fetch(`${API_ROOT}/characters`, { headers }).then((res) =>
			res.json()
		);
	});
	let characters;
	$: characters = $characterQuery.data || [];
</script>

<svelte:head>
	<title>Character</title>
</svelte:head>

<h1 class="ml-4 pt-2">Characters</h1>

{#if characters?.loading}
	Loading...
{/if}
{#each characters as character}
	<a href={`${ROOT_URL}/characters/${character?.id}`}
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
