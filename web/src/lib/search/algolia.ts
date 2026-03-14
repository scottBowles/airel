import { browser } from '$app/environment';
import { PUBLIC_ALGOLIA_APP_ID, PUBLIC_ALGOLIA_SEARCH_API_KEY } from '$env/static/public';
import { liteClient as createLiteClient } from 'algoliasearch/lite';

import {
	normalizeSearchHit,
	SEARCH_INDEX_CONFIGS,
	type AlgoliaSearchHit,
	type SearchResult
} from './types';

const SEARCH_HITS_PER_INDEX = 4;

export const algoliaConfigured = Boolean(PUBLIC_ALGOLIA_APP_ID && PUBLIC_ALGOLIA_SEARCH_API_KEY);

const searchClient = algoliaConfigured
	? createLiteClient(PUBLIC_ALGOLIA_APP_ID, PUBLIC_ALGOLIA_SEARCH_API_KEY)
	: null;

export async function searchGlobalRecords(query: string): Promise<SearchResult[]> {
	const normalizedQuery = query.trim();

	if (!browser || !searchClient || !normalizedQuery) {
		return [];
	}

	const { results } = await searchClient.searchForHits<AlgoliaSearchHit>(
		SEARCH_INDEX_CONFIGS.map((config) => ({
			indexName: config.indexName,
			query: normalizedQuery,
			hitsPerPage: SEARCH_HITS_PER_INDEX,
			attributesToRetrieve: ['objectID', 'name', 'global_id', 'description', 'thumbnail'],
			attributesToHighlight: [],
			attributesToSnippet: []
		}))
	);

	return results.flatMap((result, index) => {
		const config = SEARCH_INDEX_CONFIGS[index];

		return result.hits
			.filter((hit) => Boolean(hit.global_id) && Boolean(hit.name))
			.map((hit) => normalizeSearchHit(config.indexName, hit));
	});
}
