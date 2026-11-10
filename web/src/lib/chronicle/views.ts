// The Chronicle's selectable views. `classic` is the original list and stays the default.
export const CHRONICLE_VIEWS = [
	{
		id: 'classic',
		label: 'Classic',
		code: 'LST',
		tagline: 'The original log list',
		description: 'Newest first, one row per session with its date and brief. Unchanged.'
	},
	{
		id: 'control',
		label: 'Mission Control',
		code: 'CTL',
		tagline: 'Everything on one screen',
		description:
			'The latest session and the arc it belongs to, the course so far world by world, the crew, cargo, ports of call and who has gone quiet.'
	},
	{
		id: 'voyage',
		label: 'Flight Path',
		code: 'FLT',
		tagline: 'The journey, world to world',
		description:
			'A lane per world and a column per session: the whole voyage on one screen. Switch to every place for the detail within each world.'
	},
	{
		id: 'starchart',
		label: 'Star Chart',
		code: 'NAV',
		tagline: 'A navigable map of the route',
		description:
			'Each sun with its worlds in orbit and the routes the crew flew between them, thicker for the ones flown often. Scrub or play the voyage.'
	},
	{
		id: 'timeline',
		label: 'Timeline',
		code: 'TML',
		tagline: 'Sessions on a spine of time',
		description:
			'Each world the crew reaches opens an arc; moves, long breaks and new years are marked. Fold it down to the arcs alone.'
	},
	{
		id: 'saga',
		label: 'Saga',
		code: 'SGA',
		tagline: 'Read it as one story',
		description:
			'The campaign as a book: a part per world, a chapter per session, opening with the prologue.'
	},
	{
		id: 'replay',
		label: 'Holo-Replay',
		code: 'RPL',
		tagline: 'A viewscreen recap',
		description:
			'One session fills the screen at a time. Opens on the last few sessions for a recap before game night, or plays the arc or the whole voyage.'
	},
	{
		id: 'postcards',
		label: 'Postcards',
		code: 'PCD',
		tagline: 'An album of places visited',
		description:
			'A card per session with a small landscape drawn from where it is set, a section per arc. Filter to one world.'
	},
	{
		id: 'threads',
		label: 'Threads',
		code: 'THR',
		tagline: 'Who and what appears when',
		description:
			'Characters, places, items, artifacts and factions against sessions, most-seen first. Follow a thread through the story.'
	},
	{
		id: 'atlas',
		label: 'Atlas',
		code: 'ATL',
		tagline: 'The story by location',
		description:
			'Every place the crew has been, nested by world, with the sessions that happened there.'
	},
	{
		id: 'calendar',
		label: 'Calendar',
		code: 'CAL',
		tagline: 'Game nights at a glance',
		description:
			'A strip per year with each game night lit in the colour of its world, plus the usual gap and the longest break.'
	}
] as const;

export type ChronicleViewId = (typeof CHRONICLE_VIEWS)[number]['id'] | 'deck';

export function isChronicleView(value: string | null | undefined): value is ChronicleViewId {
	return value === 'deck' || CHRONICLE_VIEWS.some((view) => view.id === value);
}

/** A view's link. Every view, Classic included, names itself, so choosing it is remembered. */
export function viewHref(id: ChronicleViewId): string {
	return `/chronicle?view=${id}`;
}
