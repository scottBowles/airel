export const SEARCH_INDEX_CONFIGS = [
	{
		indexName: 'Association',
		label: 'Association',
		routeSegment: 'associations',
		placeholderType: 'association'
	},
	{
		indexName: 'Artifact',
		label: 'Artifact',
		routeSegment: 'artifacts',
		placeholderType: 'artifact'
	},
	{
		indexName: 'Character',
		label: 'Character',
		routeSegment: 'characters',
		placeholderType: 'character'
	},
	{
		indexName: 'Item',
		label: 'Item',
		routeSegment: 'items',
		placeholderType: 'item'
	},
	{
		indexName: 'Place',
		label: 'Place',
		routeSegment: 'places',
		placeholderType: 'place'
	},
	{
		indexName: 'Race',
		label: 'Race',
		routeSegment: 'races',
		placeholderType: 'race'
	}
] as const;

export type SearchIndexConfig = (typeof SEARCH_INDEX_CONFIGS)[number];
export type SearchIndexName = SearchIndexConfig['indexName'];
export type SearchPlaceholderType = SearchIndexConfig['placeholderType'];

export interface AlgoliaSearchHit {
	objectID: string;
	name: string;
	global_id: string;
	description?: string | null;
	thumbnail?: string | null;
}

export interface SearchResult extends AlgoliaSearchHit {
	indexName: SearchIndexName;
	indexLabel: string;
	href: string;
	placeholderType: SearchPlaceholderType;
}

const SEARCH_INDEX_BY_NAME = new Map<SearchIndexName, SearchIndexConfig>(
	SEARCH_INDEX_CONFIGS.map((config) => [config.indexName, config])
);

export function getSearchIndexConfig(indexName: SearchIndexName): SearchIndexConfig {
	const config = SEARCH_INDEX_BY_NAME.get(indexName);

	if (!config) {
		throw new Error(`Unknown search index: ${indexName}`);
	}

	return config;
}

export function getSearchResultHref(indexName: SearchIndexName, globalId: string): string {
	const config = getSearchIndexConfig(indexName);
	return `/database/${config.routeSegment}/${globalId}`;
}

export function normalizeSearchHit(
	indexName: SearchIndexName,
	hit: AlgoliaSearchHit
): SearchResult {
	const config = getSearchIndexConfig(indexName);

	return {
		...hit,
		indexName,
		indexLabel: config.label,
		href: getSearchResultHref(indexName, hit.global_id),
		placeholderType: config.placeholderType,
		description: hit.description ?? '',
		thumbnail: hit.thumbnail ?? null
	};
}
