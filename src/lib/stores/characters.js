import { browser } from '$app/env';
import { writable } from 'svelte/store';
import { makeRestStores } from '$lib/stores/utils/index.js';

console.log('characters file');

// need to drop the default stores, since loading state isn't the determiner
// we want anyway, as subscribers should access character(s) based on their
// presence, not based on loading state. optionally, we could have an isEmpty
// state or something of the store, or loading statuses.
const { getDetailStore, listStore } = browser
	? makeRestStores({
			listPath: 'characters',
			detailPath: (id) => `characters/${id}`
	  })
	: {
			listStore: writable({ loading: true }),
			getDetailStore: () => writable({ loading: true })
	  };

export { getDetailStore, listStore };
