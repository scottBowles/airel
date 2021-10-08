<script>
	import { base, assets } from '$app/paths';
	console.log({ base });
	console.log({ assets });
	let meepo = 'meepo.jpeg';
	const npcs = [
		{
			name: 'Meepo',
			image: meepo,
			race: 'Kobold',
			status: 'Alive',
			partyRelation: 'Friendly',
			location: 'Genussa',
			affiliations: []
		},
		{
			name: 'Visparo',
			race: 'Shadowvar',
			status: 'Alive',
			partyRelation: 'Friendly',
			location: 'Janus',
			affiliations: []
		},
		{
			name: 'Charles Whidmore',
			race: 'Human',
			status: 'Alive',
			partyRelation: 'Strained',
			location: 'Unknown',
			affiliations: ['Whidmore Corp']
		},
		{
			name: 'Kozmo',
			race: 'Artificial Intelligence',
			status: 'Alive',
			partyRelation: 'Cautious',
			location: 'Desconnegut',
			affiliations: []
		},
		{
			name: 'Bruno',
			race: 'Elf',
			status: 'Unknown',
			partyRelation: 'Friendly',
			location: 'Unknown',
			affiliations: []
		},
		{
			name: 'Dhund Hal Kal',
			race: 'Griffin',
			status: 'Alive',
			partyRelation: 'Cautious',
			location: 'Unknown',
			affilitions: ['Griffin Cavalry']
		},
		{
			name: 'Daryo',
			race: 'Human',
			status: 'Dead',
			partyRelation: 'Friendly',
			location: 'None',
			affiliations: []
		}
	];
</script>

<svelte:head>
	<title>NPCs</title>
</svelte:head>

<h1 class="text-4xl mt-4 mb-5">NPCs</h1>
{#each npcs as { name, image, race }}
	<div>
		<img src={meepo} alt={`${name} image`} height="75" width="75" loading="lazy" />
		<div>{name}</div>
		<div>{race}</div>
	</div>
{/each}
