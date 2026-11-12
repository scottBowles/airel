import { load_ChronicleJourney, load_GameLogList } from '$houdini';
import { isChronicleView } from '$lib/chronicle/views';
import type { PageLoad } from './$types';

export const load: PageLoad = async (event) => {
	// The view named in the link, else the one chosen last (see +page.server.ts), else Classic.
	const param = event.url.searchParams.get('view') ?? event.data.savedView;
	const view = isChronicleView(param) ? param : 'classic';

	// The classic list keeps its light query. Every other view reads the journey query,
	// which also carries the places, cast and items each session touches.
	if (view === 'classic') {
		return {
			view,
			...(await load_GameLogList({ event, variables: { order: { gameDate: 'DESC' } } }))
		};
	}
	return {
		view,
		...(await load_ChronicleJourney({ event, variables: { order: { gameDate: 'ASC' } } }))
	};
};
