import { derived } from 'svelte/store';

const makeListStore = (restStore, staleTime = 1000 * 5) => {
	const lastRefreshed = 0;

	// shape data for list view with a derived store
	const listStore = derived(restStore, ($restStore) => {
		return {
			errors: $restStore.errors?.list,
			loading: $restStore.loading?.list,
			data: $restStore?.data && Object.values($restStore?.data)
		};
	});

	// on subscribe call, tell the rest store to fetch the list
	const subscribe = (cb) => {
		if (Date.now() - lastRefreshed > staleTime) {
			restStore.getList();
		}
		const unsubscribe = listStore.subscribe(cb);
		return unsubscribe;
	};

	// return the derived store with methods for refreshing and creating data
	return { subscribe, get: restStore.getList, post: restStore.postToList };
};

export default makeListStore;
