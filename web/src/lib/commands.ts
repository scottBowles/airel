import Home from '@lucide/svelte/icons/home';
import BookOpen from '@lucide/svelte/icons/book-open';
import Database from '@lucide/svelte/icons/database';
import MessageSquare from '@lucide/svelte/icons/message-square';
import Users from '@lucide/svelte/icons/users';
import MapPin from '@lucide/svelte/icons/map-pin';
import Globe from '@lucide/svelte/icons/globe';
import Swords from '@lucide/svelte/icons/swords';
import Gem from '@lucide/svelte/icons/gem';
import Dna from '@lucide/svelte/icons/dna';
import UserPlus from '@lucide/svelte/icons/user-plus';
import MapPinPlus from '@lucide/svelte/icons/map-pin-plus';
import GlobeLock from '@lucide/svelte/icons/globe-lock';
import SwordsIcon from '@lucide/svelte/icons/sword';
import GemIcon from '@lucide/svelte/icons/gem';
import DnaIcon from '@lucide/svelte/icons/dna';
import FilePlus from '@lucide/svelte/icons/file-plus';
import MessageSquarePlus from '@lucide/svelte/icons/message-square-plus';

import type { Component } from 'svelte';

export type CommandCategory = 'navigation' | 'create';

export interface Command {
	id: string;
	label: string;
	keywords: string[];
	category: CommandCategory;
	icon: Component<{ class?: string }>;
	path: string;
	staffOnly?: boolean;
}

export const commands: Command[] = [
	// ── Navigation ──
	{
		id: 'nav-bridge',
		label: 'BRIDGE',
		keywords: [
			'home',
			'dashboard',
			'bridge',
			'ship',
			'status',
			'landing',
			'access bridge',
			'go to bridge',
			'access  bridge',
			'command deck'
		],
		category: 'navigation',
		icon: Home,
		path: '/'
	},
	{
		id: 'nav-chronicle',
		label: 'SHIP LOG',
		keywords: [
			'chronicle',
			'logs',
			'mission',
			'sessions',
			'game',
			'history',
			'ship log',
			'mission log',
			'go to chronicle',
			'access  chronicle'
		],
		category: 'navigation',
		icon: BookOpen,
		path: '/chronicle'
	},
	{
		id: 'nav-database',
		label: 'DATA CORE',
		keywords: [
			'database',
			'archive',
			'records',
			'data',
			'entities',
			'data core',
			'go to database',
			'access  database',
			'access database'
		],
		category: 'navigation',
		icon: Database,
		path: '/database'
	},
	{
		id: 'nav-kozmo',
		label: 'KOZMO CHAT',
		keywords: [
			'ai',
			'chat',
			'assistant',
			'talk',
			'ask',
			'conversation',
			'computer',
			'open kozmo',
			'kozmo hub',
			'go to kozmo',
			'access  kozmo'
		],
		category: 'navigation',
		icon: MessageSquare,
		path: '/kozmo'
	},
	{
		id: 'nav-characters',
		label: 'KNOWN PERSONS',
		keywords: [
			'characters',
			'people',
			'crew',
			'npcs',
			'known persons',
			'individuals',
			'go to characters',
			'access  characters',
			'character index'
		],
		category: 'navigation',
		icon: Users,
		path: '/database/characters'
	},
	{
		id: 'nav-places',
		label: 'LOCATION INDEX',
		keywords: [
			'places',
			'locations',
			'planets',
			'maps',
			'geography',
			'location index',
			'stations',
			'go to places',
			'access  places'
		],
		category: 'navigation',
		icon: MapPin,
		path: '/database/places'
	},
	{
		id: 'nav-associations',
		label: 'AFFILIATION INDEX',
		keywords: [
			'associations',
			'orgs',
			'factions',
			'groups',
			'organizations',
			'affiliation index',
			'alliances',
			'families',
			'go to associations',
			'access  associations'
		],
		category: 'navigation',
		icon: Globe,
		path: '/database/associations'
	},
	{
		id: 'nav-items',
		label: 'ITEM INDEX',
		keywords: [
			'items',
			'weapons',
			'equipment',
			'gear',
			'loot',
			'item index',
			'ships',
			'objects',
			'go to items',
			'access  items'
		],
		category: 'navigation',
		icon: Swords,
		path: '/database/items'
	},
	{
		id: 'nav-artifacts',
		label: 'ARTIFACT INDEX',
		keywords: [
			'artifacts',
			'relics',
			'treasures',
			'rare',
			'artifact index',
			'artifact archive',
			'go to artifacts',
			'access  artifacts'
		],
		category: 'navigation',
		icon: Gem,
		path: '/database/artifacts'
	},
	{
		id: 'nav-races',
		label: 'SPECIES INDEX',
		keywords: [
			'races',
			'species',
			'ancestry',
			'lineage',
			'species index',
			'xenology',
			'go to races',
			'access  races'
		],
		category: 'navigation',
		icon: Dna,
		path: '/database/races'
	},

	// ── Creation (staff only) ──
	{
		id: 'create-character',
		label: 'REGISTER KNOWN PERSON',
		keywords: [
			'new character',
			'add character',
			'create person',
			'register known person',
			'known person'
		],
		category: 'create',
		icon: UserPlus,
		path: '/database/characters/new',
		staffOnly: true
	},
	{
		id: 'create-place',
		label: 'REGISTER LOCATION',
		keywords: [
			'new place',
			'add location',
			'create planet',
			'create location',
			'register location'
		],
		category: 'create',
		icon: MapPinPlus,
		path: '/database/places/new',
		staffOnly: true
	},
	{
		id: 'create-association',
		label: 'REGISTER AFFILIATION',
		keywords: [
			'new association',
			'add org',
			'create faction',
			'create group',
			'register affiliation',
			'affiliation'
		],
		category: 'create',
		icon: GlobeLock,
		path: '/database/associations/new',
		staffOnly: true
	},
	{
		id: 'create-item',
		label: 'REGISTER ITEM',
		keywords: [
			'new item',
			'add weapon',
			'create equipment',
			'create gear',
			'register item',
			'add item'
		],
		category: 'create',
		icon: SwordsIcon,
		path: '/database/items/new',
		staffOnly: true
	},
	{
		id: 'create-artifact',
		label: 'REGISTER ARTIFACT',
		keywords: ['new artifact', 'add artifact', 'create treasure', 'register artifact', 'add relic'],
		category: 'create',
		icon: GemIcon,
		path: '/database/artifacts/new',
		staffOnly: true
	},
	{
		id: 'create-race',
		label: 'REGISTER SPECIES',
		keywords: ['new race', 'add species', 'create ancestry', 'register species'],
		category: 'create',
		icon: DnaIcon,
		path: '/database/races/new',
		staffOnly: true
	},
	{
		id: 'create-chronicle',
		label: 'LOG MISSION RECORD',
		keywords: [
			'new log',
			'add session',
			'create chronicle',
			'import log',
			'mission record',
			'ship log entry',
			'register session'
		],
		category: 'create',
		icon: FilePlus,
		path: '/chronicle/new',
		staffOnly: true
	},
	{
		id: 'create-kozmo-chat',
		label: 'OPEN KOZMO CHANNEL',
		keywords: [
			'kozmo',
			'new chat',
			'start conversation',
			'ask kozmo',
			'new session',
			'kozmo channel',
			'open channel',
			'create chat'
		],
		category: 'create',
		icon: MessageSquarePlus,
		path: '/kozmo/new'
	}
];

const categoryLabels: Record<CommandCategory, string> = {
	navigation: 'ACCESS',
	create: 'INITIATE'
};

export function getCategoryLabel(category: CommandCategory): string {
	return categoryLabels[category];
}

/**
 * Score a command against a query string. Returns 0 for no match.
 * Higher scores = better match.
 */
function scoreCommand(command: Command, query: string): number {
	const q = query.toLowerCase();
	const label = command.label.toLowerCase();

	// Exact label prefix match — highest priority
	if (label.startsWith(q)) return 100;

	// Label contains query as a word boundary match
	if (label.includes(q)) return 80;

	// Keyword exact prefix match
	for (const kw of command.keywords) {
		if (kw.startsWith(q)) return 70;
	}

	// Keyword contains query
	for (const kw of command.keywords) {
		if (kw.includes(q)) return 60;
	}

	// All query words appear somewhere in label + keywords
	const searchable = `${label} ${command.keywords.join(' ')}`;
	const words = q.split(/\s+/).filter(Boolean);
	if (words.length > 1 && words.every((w) => searchable.includes(w))) {
		return 50;
	}

	// Single-word partial match anywhere in searchable text
	if (searchable.includes(q)) return 40;

	return 0;
}

export function filterCommands(
	query: string,
	options?: { isStaff?: boolean }
): Array<Command & { score: number }> {
	const isStaff = options?.isStaff ?? false;
	const available = commands.filter((c) => !c.staffOnly || isStaff);

	if (!query.trim()) {
		// Return all available commands, scored 0 (used for empty-state display)
		return available.map((c) => ({ ...c, score: 0 }));
	}

	return available
		.map((c) => ({ ...c, score: scoreCommand(c, query) }))
		.filter((c) => c.score > 0)
		.sort((a, b) => b.score - a.score);
}

// ── Frecency tracking ──

const FRECENCY_KEY = 'command-palette-frecency';
const DECAY_DAYS = 14;
const MAX_RECENT_TOTAL = 6;

interface FrecencyEntry {
	id: string;
	count: number;
	lastUsed: number; // timestamp
}

function loadFrecency(): FrecencyEntry[] {
	try {
		const raw = localStorage.getItem(FRECENCY_KEY);
		if (!raw) return [];
		return JSON.parse(raw) as FrecencyEntry[];
	} catch {
		return [];
	}
}

function saveFrecency(entries: FrecencyEntry[]) {
	try {
		localStorage.setItem(FRECENCY_KEY, JSON.stringify(entries));
	} catch {
		// SSR or storage full
	}
}

function frecencyScore(entry: FrecencyEntry): number {
	const ageMs = Date.now() - entry.lastUsed;
	const ageDays = ageMs / (1000 * 60 * 60 * 24);
	const decay = Math.max(0, 1 - ageDays / DECAY_DAYS);
	return entry.count * decay;
}

export function recordCommandUsage(commandId: string) {
	const entries = loadFrecency();
	const existing = entries.find((e) => e.id === commandId);
	if (existing) {
		existing.count += 1;
		existing.lastUsed = Date.now();
	} else {
		entries.push({ id: commandId, count: 1, lastUsed: Date.now() });
	}
	saveFrecency(entries);
}

export function getRecentCommands(options?: { isStaff?: boolean; limit?: number }): Command[] {
	const isStaff = options?.isStaff ?? false;
	const limit = options?.limit ?? MAX_RECENT_TOTAL;
	const entries = loadFrecency();
	if (entries.length === 0) return [];

	const available = commands.filter((c) => !c.staffOnly || isStaff);
	const availableIds = new Set(available.map((c) => c.id));

	return entries
		.filter((e) => availableIds.has(e.id) && frecencyScore(e) > 0)
		.sort((a, b) => frecencyScore(b) - frecencyScore(a))
		.slice(0, limit)
		.map((e) => available.find((c) => c.id === e.id)!)
		.filter(Boolean);
}

// ── Recent entity tracking ──

const ENTITY_FRECENCY_KEY = 'command-palette-entity-frecency';

export interface RecentEntity {
	id: string;
	name: string;
	type: string;
	route: string;
	lastUsed: number;
	count: number;
}

function loadEntityFrecency(): RecentEntity[] {
	try {
		const raw = localStorage.getItem(ENTITY_FRECENCY_KEY);
		if (!raw) return [];
		return JSON.parse(raw) as RecentEntity[];
	} catch {
		return [];
	}
}

function saveEntityFrecency(entries: RecentEntity[]) {
	try {
		localStorage.setItem(ENTITY_FRECENCY_KEY, JSON.stringify(entries));
	} catch {
		// SSR or storage full
	}
}

function entityFrecencyScore(entry: RecentEntity): number {
	const ageMs = Date.now() - entry.lastUsed;
	const ageDays = ageMs / (1000 * 60 * 60 * 24);
	const decay = Math.max(0, 1 - ageDays / DECAY_DAYS);
	return entry.count * decay;
}

export function recordEntityVisit(entity: {
	id: string;
	name: string;
	type: string;
	route: string;
}) {
	const entries = loadEntityFrecency();
	const existing = entries.find((e) => e.id === entity.id);
	if (existing) {
		existing.count += 1;
		existing.lastUsed = Date.now();
		existing.name = entity.name;
		existing.route = entity.route;
	} else {
		entries.push({ ...entity, count: 1, lastUsed: Date.now() });
	}
	saveEntityFrecency(entries);
}

export function getRecentEntities(options?: { limit?: number }): RecentEntity[] {
	const limit = options?.limit ?? MAX_RECENT_TOTAL;
	const entries = loadEntityFrecency();
	if (entries.length === 0) return [];

	return entries
		.filter((e) => entityFrecencyScore(e) > 0)
		.sort((a, b) => entityFrecencyScore(b) - entityFrecencyScore(a))
		.slice(0, limit);
}

// ── Combined recents (balanced allocation, sorted by frecency) ──

export type RecentItem =
	| { kind: 'command'; command: Command; score: number }
	| { kind: 'entity'; entity: RecentEntity; score: number };

export function getCombinedRecents(options?: { isStaff?: boolean }): RecentItem[] {
	const isStaff = options?.isStaff ?? false;

	const cmdEntries = loadFrecency();
	const available = commands.filter((c) => !c.staffOnly || isStaff);
	const availableIds = new Set(available.map((c) => c.id));

	const scoredCmds = cmdEntries
		.filter((e) => availableIds.has(e.id) && frecencyScore(e) > 0)
		.sort((a, b) => frecencyScore(b) - frecencyScore(a))
		.map((e) => ({
			kind: 'command' as const,
			command: available.find((c) => c.id === e.id)!,
			score: frecencyScore(e)
		}))
		.filter((item) => item.command);

	const entEntries = loadEntityFrecency();
	const scoredEnts = entEntries
		.filter((e) => entityFrecencyScore(e) > 0)
		.sort((a, b) => entityFrecencyScore(b) - entityFrecencyScore(a))
		.map((e) => ({
			kind: 'entity' as const,
			entity: e,
			score: entityFrecencyScore(e)
		}));

	let cmdLimit: number;
	let entLimit: number;

	if (scoredCmds.length >= 3 && scoredEnts.length >= 3) {
		cmdLimit = 3;
		entLimit = 3;
	} else if (scoredCmds.length < 3) {
		cmdLimit = scoredCmds.length;
		entLimit = Math.min(scoredEnts.length, MAX_RECENT_TOTAL - cmdLimit);
	} else {
		entLimit = scoredEnts.length;
		cmdLimit = Math.min(scoredCmds.length, MAX_RECENT_TOTAL - entLimit);
	}

	const items: RecentItem[] = [...scoredCmds.slice(0, cmdLimit), ...scoredEnts.slice(0, entLimit)];

	return items.sort((a, b) => b.score - a.score);
}
