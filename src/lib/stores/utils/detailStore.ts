import { derived } from 'svelte/store';

const makeDetailStore = (restStore, id, staleTime = 1000 * 5) => {
	let lastRefreshed = 0;

	// shape date for detail view with a derived store
	const detailStore = derived(restStore, ($restStore) => {
		// update lastRefreshed
		lastRefreshed = Date.now();
		// reshape the data for detail
		const data = $restStore.data?.[id];
		const loading = $restStore.loading?.[id] || $restStore.loading?.list;
		const errors = $restStore.errors?.[id];
		return { ...$restStore, loading, errors, data };
	});

	// on subscribe call, tell the rest store to fetch the detail
	const subscribe = (cb) => {
		if (Date.now() - lastRefreshed > staleTime) {
			restStore.getDetail(id);
		}
		return detailStore.subscribe(cb);
	};

	// return the derived store with methods for refreshing and mutating data
	const { getDetail, patchDetail, deleteDetail } = restStore;
	return { subscribe, get: getDetail, patch: patchDetail, delete: deleteDetail };
};

export default makeDetailStore;
