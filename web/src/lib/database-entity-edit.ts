import { resolve } from '$app/paths';
import type { RelationOption } from '$lib/components/logs/log-editor-types';
import { sortRelationOptions } from '$lib/components/logs/log-editor-types';
import type { RelationKind } from '$lib/database-detail';

type EntityUser = {
	username: string;
	firstName?: string | null;
	lastName?: string | null;
};

type NamedConnection =
	| {
			edges?: Array<{ node: { id: string; name: string } }> | null;
	  }
	| null
	| undefined;

type PlaceConnection =
	| {
			edges?: Array<{
				node: {
					id: string;
					name: string;
					placeType?: string | null;
					parent?: { name: string } | null;
				};
			}> | null;
	  }
	| null
	| undefined;

type EntityEditorOptionsShape = {
	artifacts?: NamedConnection;
	associations?: NamedConnection;
	characters?: NamedConnection;
	items?: NamedConnection;
	places?: PlaceConnection;
	races?: NamedConnection;
};

export function buildEntityHref(entityType: RelationKind, id: string) {
	switch (entityType) {
		case 'artifacts':
			return resolve('/database/artifacts/[id]', { id });
		case 'associations':
			return resolve('/database/associations/[id]', { id });
		case 'characters':
			return resolve('/database/characters/[id]', { id });
		case 'items':
			return resolve('/database/items/[id]', { id });
		case 'places':
			return resolve('/database/places/[id]', { id });
		case 'races':
			return resolve('/database/races/[id]', { id });
	}
}

export function getLockUserDisplayName(user: EntityUser) {
	const firstName = user.firstName?.trim();
	const lastName = user.lastName?.trim();

	if (firstName && lastName) {
		return `${firstName} ${lastName}`;
	}

	if (firstName) {
		return firstName;
	}

	if (lastName) {
		return lastName;
	}

	return user.username;
}

export function buildNodeInputList(options: RelationOption[]) {
	return options.map((option) => ({ id: option.id }));
}

export function normalizeTextValue(value: string, trim = false) {
	const normalizedValue = trim ? value.trim() : value;
	return normalizedValue ? normalizedValue : null;
}

export function mapNamedRelationOptions(
	entityType: RelationKind,
	connection: NamedConnection
): RelationOption[] {
	return sortRelationOptions(
		connection?.edges?.map(({ node }) => ({
			id: node.id,
			name: node.name,
			href: buildEntityHref(entityType, node.id)
		})) ?? []
	);
}

export function mapPlaceRelationOptions(connection: PlaceConnection): RelationOption[] {
	return sortRelationOptions(
		connection?.edges?.map(({ node }) => ({
			id: node.id,
			name: node.name,
			href: buildEntityHref('places', node.id),
			secondaryText: [node.placeType, node.parent?.name].filter(Boolean).join(' · ') || undefined
		})) ?? []
	);
}

export function buildEntityEditorRelationOptions(
	editorOptions: EntityEditorOptionsShape | undefined
) {
	return {
		artifacts: mapNamedRelationOptions('artifacts', editorOptions?.artifacts),
		associations: mapNamedRelationOptions('associations', editorOptions?.associations),
		characters: mapNamedRelationOptions('characters', editorOptions?.characters),
		items: mapNamedRelationOptions('items', editorOptions?.items),
		places: mapPlaceRelationOptions(editorOptions?.places),
		placesSetIn: mapPlaceRelationOptions(editorOptions?.places),
		races: mapNamedRelationOptions('races', editorOptions?.races)
	};
}
