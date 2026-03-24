import type { LogEditorOptions, RelationOption } from '$lib/components/logs/log-editor-types';
import type { RelationKind } from '$lib/database-detail';

export const DATABASE_PRIMARY_RELATION_KEYS = [
	'artifacts',
	'associations',
	'characters',
	'items'
] as const;
export const DATABASE_RELATED_RELATION_KEYS = [
	'relatedArtifacts',
	'relatedAssociations',
	'relatedCharacters',
	'relatedItems',
	'relatedPlaces',
	'relatedRaces'
] as const;

export const DATABASE_RELATION_TITLES: Record<RelationKind, string> = {
	artifacts: 'Artifacts',
	associations: 'Associations',
	characters: 'Characters',
	items: 'Items',
	places: 'Places',
	races: 'Races'
};

export const PLACE_TYPE_OPTIONS = [
	'DISTRICT',
	'LOCATION',
	'MOON',
	'PLANET',
	'REGION',
	'STAR',
	'TOWN'
] as const;

export type DatabasePrimaryRelationKey = (typeof DATABASE_PRIMARY_RELATION_KEYS)[number];
export type DatabaseRelatedRelationKey = (typeof DATABASE_RELATED_RELATION_KEYS)[number];
export type DatabasePlaceType = (typeof PLACE_TYPE_OPTIONS)[number];

export type DatabaseEntityDraft = {
	id: string;
	name: string;
	description: string;
	markdownNotes: string;
	notes: string;
	size: string;
	placeType: string;
	raceId: string;
	parentPlaceId: string;
	armorAcBonus: string;
	equipmentBriefDescription: string;
	weaponAttackBonus: string;
	artifacts: RelationOption[];
	associations: RelationOption[];
	characters: RelationOption[];
	items: RelationOption[];
	relatedArtifacts: RelationOption[];
	relatedAssociations: RelationOption[];
	relatedCharacters: RelationOption[];
	relatedItems: RelationOption[];
	relatedPlaces: RelationOption[];
	relatedRaces: RelationOption[];
};

export type DatabaseEntityEditorOptions = LogEditorOptions;

export type DatabaseEntityRelationFieldConfig = {
	key: DatabasePrimaryRelationKey;
	title: string;
	placeholder?: string;
	sectionTitle?: string;
};

export type DatabaseEntityEditorConfig = {
	entityLabel: string;
	showNotes?: boolean;
	showSize?: boolean;
	showPlaceType?: boolean;
	showRace?: boolean;
	showParentPlace?: boolean;
	showArmorAcBonus?: boolean;
	showEquipmentBriefDescription?: boolean;
	showWeaponAttackBonus?: boolean;
	primaryRelations?: DatabaseEntityRelationFieldConfig[];
	relatedRelations?: DatabaseRelatedRelationKey[];
};

export const DEFAULT_DATABASE_ENTITY_DRAFT: DatabaseEntityDraft = {
	id: '',
	name: '',
	description: '',
	markdownNotes: '',
	notes: '',
	size: '',
	placeType: '',
	raceId: '',
	parentPlaceId: '',
	armorAcBonus: '',
	equipmentBriefDescription: '',
	weaponAttackBonus: '',
	artifacts: [],
	associations: [],
	characters: [],
	items: [],
	relatedArtifacts: [],
	relatedAssociations: [],
	relatedCharacters: [],
	relatedItems: [],
	relatedPlaces: [],
	relatedRaces: []
};
