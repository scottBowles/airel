export const ENTITY_TYPES = [
	{ slug: 'characters', label: 'Characters', singular: 'Character' },
	{ slug: 'places', label: 'Places', singular: 'Place' },
	{ slug: 'associations', label: 'Associations', singular: 'Association' },
	{ slug: 'items', label: 'Items', singular: 'Item' },
	{ slug: 'artifacts', label: 'Artifacts', singular: 'Artifact' },
	{ slug: 'races', label: 'Races', singular: 'Race' }
] as const;

export type EntitySlug = (typeof ENTITY_TYPES)[number]['slug'];
