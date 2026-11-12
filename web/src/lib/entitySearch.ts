import { CachePolicy, SearchEntitiesStore, type EntityType$options } from '$houdini';

export type EntitySearchHit = {
	/** Relay global ID, the same one the /database/<type>/<id> routes take. */
	id: string;
	name: string;
	/** Lowercase entity type, e.g. 'character'. */
	type: string;
	description: string | null;
	thumbnail: string | null;
};

/**
 * Entity search by name and alias (the API's `search` query), for a debounced search input.
 * Each call to the returned function supersedes the previous one: a superseded call
 * resolves to null, so a slow response never overwrites a newer one.
 */
export function createEntitySearch() {
	const store = new SearchEntitiesStore();
	let latest = 0;

	return async (
		query: string,
		{ types, limit }: { types?: EntityType$options[]; limit: number }
	): Promise<EntitySearchHit[] | null> => {
		const call = ++latest;
		let hits: EntitySearchHit[] = [];
		try {
			const { data } = await store.fetch({
				variables: { query, types: types ?? null, limit },
				policy: CachePolicy.NetworkOnly
			});
			hits = (data?.search ?? []).map((hit) => ({ ...hit, type: hit.type.toLowerCase() }));
		} catch {
			hits = [];
		}
		return call === latest ? hits : null;
	};
}
