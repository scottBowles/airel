<script lang="ts">
	import { page } from '$app/stores';
	import { getDetailStore } from '$lib/stores/characters.js';

	const { id } = $page.params;

	const character = getDetailStore(id);

	const handleClick = () => character.get(id);

	let char = {
		id: 3,
		hit_die: null,
		strength: 8,
		dexterity: 10,
		constitution: 11,
		intelligence: 12,
		wisdom: 14,
		charisma: 16,
		copper_pieces: 0,
		silver_pieces: 0,
		electrum_pieces: 0,
		gold_pieces: 0,
		platinum_pieces: 0,
		max_hit_points: 1,
		temporary_hit_points: 0,
		damage_taken: 0,
		name: 'Darwin',
		player_name: null,
		alignment: null,
		experience_points: 1,
		armor_class: 10,
		initiative: 0,
		speed: 0,
		num_hit_dice: 1,
		death_save_successes: 0,
		death_save_failures: 0,
		inspiration: false,
		passive_wisdom: 10,
		passive_intelligence: 10,
		size: null,
		background: null,
		race: null,
		user: null,
		features_and_traits: [],
		proficiencies: [],
		equipment: [],
		tool: [],
		feats: [],
		weapons: [],
		armor: []
	};
</script>

<svelte:head>
	<title>Character</title>
</svelte:head>

<h1 class="ml-4 pt-2">{$character?.data?.name}</h1>

<button on:click={handleClick}>Refresh Character Data</button>
{#if $character?.loading}
	Loading...
{:else}
	<p>Player: {$character?.data?.player_name}</p>
	<p>strength: {$character?.data?.strength}</p>
	<p>dexterity: {$character?.data?.dexterity}</p>
	<p>constitution: {$character?.data?.constitution}</p>
	<p>intelligence: {$character?.data?.intelligence}</p>
	<p>wisdom: {$character?.data?.wisdom}</p>
	<p>charisma: {$character?.data?.charisma}</p>
{/if}

<div class="ability-scores-container">
	<div class="ability-score-container">
		<span>STR</span><span>{char.strength}</span>
	</div>
	<div class="ability-score-container">
		<span>DEX</span><span>{char.dexterity}</span>
	</div>
	<div class="ability-score-container">
		<span>CON</span><span>{char.constitution}</span>
	</div>
	<div class="ability-score-container">
		<span>INT</span><span>{char.intelligence}</span>
	</div>
	<div class="ability-score-container">
		<span>WIS</span><span>{char.wisdom}</span>
	</div>
	<div class="ability-score-container mr-4 mt-4">
		<span class="pr-2">CHA</span><span>{char.charisma}</span>
	</div>
</div>

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
