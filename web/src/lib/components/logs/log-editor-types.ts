export const LOG_RELATION_KEYS = [
	'artifacts',
	'associations',
	'characters',
	'items',
	'places',
	'placesSetIn',
	'races'
] as const;

export type LogRelationKey = (typeof LOG_RELATION_KEYS)[number];

export type RelationOption = {
	id: string;
	name: string;
	secondaryText?: string;
	href?: string;
};

export function sortRelationOptions(options: RelationOption[]) {
	return [...options].sort((left, right) =>
		left.name.localeCompare(right.name, undefined, { sensitivity: 'base' })
	);
}

export type EditableLogData = {
	id: string;
	title: string;
	brief: string;
	synopsis: string;
	gameDate: string;
	artifacts: RelationOption[];
	associations: RelationOption[];
	characters: RelationOption[];
	items: RelationOption[];
	places: RelationOption[];
	placesSetIn: RelationOption[];
	races: RelationOption[];
};

export type LogEditorOptions = Record<LogRelationKey, RelationOption[]>;
