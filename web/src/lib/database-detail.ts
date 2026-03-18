export type NamedNode = {
	id: string;
	name: string;
};

export type NamedConnection =
	| {
			edges?: Array<{
				node: NamedNode;
			}>;
	  }
	| null
	| undefined;

export type LogNode = {
	id: string;
	title: string | null;
	url: string;
};

export type LogConnection =
	| {
			edges?: Array<{
				node: LogNode;
			}>;
	  }
	| null
	| undefined;

export type RelationKind =
	| 'artifacts'
	| 'associations'
	| 'characters'
	| 'items'
	| 'places'
	| 'races';

export type RelationRoute =
	| '/database/artifacts/[id]'
	| '/database/associations/[id]'
	| '/database/characters/[id]'
	| '/database/items/[id]'
	| '/database/places/[id]'
	| '/database/races/[id]';

export type RelationGroup = {
	key: RelationKind;
	label: string;
	route: RelationRoute;
	nodes: NamedNode[];
};

type RelatedEntityCollections = {
	relatedArtifacts?: NamedConnection;
	relatedAssociations?: NamedConnection;
	relatedCharacters?: NamedConnection;
	relatedItems?: NamedConnection;
	relatedPlaces?: NamedConnection;
	relatedRaces?: NamedConnection;
};

type BreadcrumbNode = NamedNode & {
	parent?: BreadcrumbNode | null;
};

const RELATION_GROUP_META: Array<{
	key: RelationKind;
	label: string;
	route: RelationRoute;
	field: keyof RelatedEntityCollections;
}> = [
	{
		key: 'artifacts',
		label: 'Artifacts',
		route: '/database/artifacts/[id]',
		field: 'relatedArtifacts'
	},
	{
		key: 'associations',
		label: 'Associations',
		route: '/database/associations/[id]',
		field: 'relatedAssociations'
	},
	{
		key: 'characters',
		label: 'Characters',
		route: '/database/characters/[id]',
		field: 'relatedCharacters'
	},
	{
		key: 'items',
		label: 'Items',
		route: '/database/items/[id]',
		field: 'relatedItems'
	},
	{
		key: 'places',
		label: 'Places',
		route: '/database/places/[id]',
		field: 'relatedPlaces'
	},
	{
		key: 'races',
		label: 'Races',
		route: '/database/races/[id]',
		field: 'relatedRaces'
	}
];

export const detailPanelClass =
	'rounded-sm isolate overflow-hidden border border-slate-700/55 bg-slate-900/72 p-4 shadow-[0_0_0_1px_rgba(255,255,255,0.02),0_8px_18px_rgba(0,0,0,0.16)]';

export const detailRailCardClass =
	'rounded-sm border border-slate-700/60 bg-slate-900/74 p-4 shadow-[0_0_0_1px_rgba(255,255,255,0.02),0_8px_18px_rgba(0,0,0,0.16)]';

export const detailSectionTitleClass =
	'mb-5 text-xs font-bold tracking-[0.18em] text-zinc-500 uppercase';

export function getNamedNodes(connection: NamedConnection): NamedNode[] {
	return connection?.edges?.map(({ node }) => node) ?? [];
}

export function getLogNodes(connection: LogConnection): LogNode[] {
	return connection?.edges?.map(({ node }) => node) ?? [];
}

export function buildRelationGroups(connections: RelatedEntityCollections): RelationGroup[] {
	return RELATION_GROUP_META.map((group) => ({
		key: group.key,
		label: group.label,
		route: group.route,
		nodes: getNamedNodes(connections[group.field])
	})).filter((group) => group.nodes.length > 0);
}

export function buildPlaceBreadcrumbs(
	place: BreadcrumbNode | null | undefined,
	maxDepth = 6
): NamedNode[] {
	const breadcrumbs: NamedNode[] = [];
	let cursor = place?.parent;
	let depth = 0;

	while (cursor && depth < maxDepth) {
		breadcrumbs.unshift({ id: cursor.id, name: cursor.name });
		cursor = cursor.parent;
		depth += 1;
	}

	return breadcrumbs;
}
