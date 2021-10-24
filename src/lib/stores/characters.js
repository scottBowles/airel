import { browser} from "$app/env";
import { writable } from "svelte/store";
import { makeRestStores } from '$lib/stores/utils/index.js'

console.log('characters file')

const { getDetailStore, listStore } = browser 
? makeRestStores({listPath: 'characters', detailPath: (id) => `characters/${id}`}) 
: {listStore: writable({loading: true}), getDetailStore: () => writable({loading: true})};

export { getDetailStore, listStore};