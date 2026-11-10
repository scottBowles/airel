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
			'Several views combined: the last session, the course so far, crew, cargo, ports of call and who has gone quiet.'
	},
	{
		id: 'voyage',
		label: 'Flight Path',
		code: 'FLT',
		tagline: 'The journey, place to place',
		description:
			'Every place gets a lane and every session a column. One line traces where the crew went, session by session.'
	},
	{
		id: 'starchart',
		label: 'Star Chart',
		code: 'NAV',
		tagline: 'A navigable map of the route',
		description:
			'Systems, worlds and ports drawn as a chart, with the route plotted across them. Scrub or play the voyage.'
	},
	{
		id: 'timeline',
		label: 'Timeline',
		code: 'TML',
		tagline: 'Sessions on a spine of time',
		description:
			'A vertical timeline with course changes called out between sessions and the gaps between game nights.'
	},
	{
		id: 'saga',
		label: 'Saga',
		code: 'SGA',
		tagline: 'Read it as one story',
		description:
			'The whole campaign as a book: one chapter per session, a contents rail and a reading-progress bar.'
	},
	{
		id: 'replay',
		label: 'Holo-Replay',
		code: 'RPL',
		tagline: 'A viewscreen recap',
		description:
			'One session fills the screen at a time. Auto-plays like a recap before game night; arrow keys step through.'
	},
	{
		id: 'postcards',
		label: 'Postcards',
		code: 'PCD',
		tagline: 'A wall of places visited',
		description:
			'One card per session with a small landscape drawn from where it is set. Filter by star system.'
	},
	{
		id: 'threads',
		label: 'Threads',
		code: 'THR',
		tagline: 'Who and what appears when',
		description:
			'A matrix of characters, places, items and factions against sessions. Follow a thread through the story.'
	},
	{
		id: 'atlas',
		label: 'Atlas',
		code: 'ATL',
		tagline: 'The story by location',
		description:
			'Every place the crew has been, nested by system and world, with the sessions that happened there.'
	},
	{
		id: 'calendar',
		label: 'Calendar',
		code: 'CAL',
		tagline: 'Game nights at a glance',
		description:
			'A month-by-month record of when the group played, with the usual and longest gaps.'
	}
] as const;

export type ChronicleViewId = (typeof CHRONICLE_VIEWS)[number]['id'] | 'deck';

export function isChronicleView(value: string | null | undefined): value is ChronicleViewId {
	return value === 'deck' || CHRONICLE_VIEWS.some((view) => view.id === value);
}

export function viewHref(id: ChronicleViewId): string {
	return id === 'classic' ? '/chronicle' : `/chronicle?view=${id}`;
}
