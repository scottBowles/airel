import { isChronicleView, type ChronicleViewId } from '$lib/chronicle/views';
import type { PageServerLoad } from './$types';

const COOKIE = 'chronicle_view';
const ONE_YEAR = 60 * 60 * 24 * 365;

// The Chronicle opens on the view chosen last. Opening one by its link (?view=...) remembers
// it; the "all views" chooser is never remembered.
export const load: PageServerLoad = ({ url, cookies }) => {
	const chosen = url.searchParams.get('view');
	if (isChronicleView(chosen)) {
		if (chosen !== 'deck') {
			cookies.set(COOKIE, chosen, {
				path: '/chronicle',
				maxAge: ONE_YEAR,
				sameSite: 'lax',
				httpOnly: true
			});
		}
		return { savedView: null };
	}
	const saved = cookies.get(COOKIE);
	return {
		savedView: (isChronicleView(saved) && saved !== 'deck' ? saved : null) as ChronicleViewId | null
	};
};
