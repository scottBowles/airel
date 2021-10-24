import makeHttpStore from './httpStore';
import makeRestStore from './restStore';
import makeDetailStore from './detailStore';
import makeListStore from './listStore';

const makeRestStores = (config) => {
	'MAKING REST STORE';
	const restStore = makeRestStore(config);
	const listStore = makeListStore(restStore);
	let detailStores = {};
	const getDetailStore = (id) => {
		if (!detailStores[id]) {
			detailStores[id] = makeDetailStore(restStore, id);
		}
		return detailStores[id];
	};
	return { getDetailStore, listStore, restStore };
};

export { makeRestStores, makeHttpStore, makeRestStore, makeDetailStore, makeListStore };
