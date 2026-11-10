import { load_ChronicleJourney, load_GameLogList } from '$houdini';
import { isChronicleView } from '$lib/chronicle/views';
import type { PageLoad } from './$types';

export const load: PageLoad = async (event) => {
	const param = event.url.searchParams.get('view');
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
