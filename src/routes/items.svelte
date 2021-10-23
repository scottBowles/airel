<script>
	import character from '$lib/stores/characters.js';

	$: console.log({ $character });
	const handleClick = () => character.get();
</script>

<svelte:head>
	<title>Items</title>
</svelte:head>

<h1>Items</h1>
<p>{character}</p>
<button on:click={handleClick}>Click me</button>
{#await character.get()}
	Loading...
{:then}
	<p>Name: {$character?.name}</p>
	<p>Player: {$character?.player_name}</p>
	<p>strength: {$character?.strength}</p>
	<p>dexterity: {$character?.dexterity}</p>
	<p>constitution: {$character?.constitution}</p>
	<p>intelligence: {$character?.intelligence}</p>
	<p>wisdom: {$character?.wisdom}</p>
	<p>charisma: {$character?.charisma}</p>
{/await}
<p>Items</p>
