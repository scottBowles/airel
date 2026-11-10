<script lang="ts">
	// Postcards: a wall of cards, one per session, each with a small landscape drawn from the
	// place it is set in. A place keeps its skyline across visits; a system keeps its colour.
	import {
		buildPlaceTree,
		worldColours,
		pad,
		primaryStop,
		shortDate,
		type Session
	} from '$lib/chronicle/model';
	import { CARD_H, CARD_W, postcard } from '$lib/chronicle/postcard';

	let { sessions }: { sessions: Session[] } = $props();

	let tree = $derived(buildPlaceTree(sessions));
	let colours = $derived(worldColours(sessions));
	let systemId = $state<string | null>(null);

	let cards = $derived(
		sessions.map((session) => {
			const stop = primaryStop(session);
			const system = stop?.path[0] ?? null;
			return {
				session,
				stop,
				system,
				tone: system ? (colours.get(system.id) ?? '#8a7e60') : '#8a7e60',
				art: postcard(stop?.id ?? session.id, stop?.type ?? null, session.n)
			};
		})
	);
	let shown = $derived(systemId ? cards.filter((card) => card.system?.id === systemId) : cards);
</script>

<div class="flex flex-wrap items-center gap-1.5 border border-border-dim bg-hull px-3 py-2">
	<span class="mr-1 machine-text text-[9px] text-text-muted">WORLD</span>
	<button type="button" class="chip {systemId === null ? 'chip-on' : ''}" onclick={() => (systemId = null)}>All · {cards.length}</button>
	{#each tree.roots as root (root.id)}
		<button
			type="button"
			class="chip {systemId === root.id ? 'chip-on' : ''}"
			style:--tone={colours.get(root.id)}
			onclick={() => (systemId = systemId === root.id ? null : root.id)}
		>
			<span class="status-dot" style:color={colours.get(root.id)}></span>
			{root.name} · {root.allSessions.length}
		</button>
	{/each}
</div>

<div class="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-4">
	{#each shown as card (card.session.id)}
		{@const session = card.session}
		<a href="/chronicle/{session.id}" class="card group relative block overflow-hidden border border-border-dim bg-panel" style:--tone={card.tone}>
			<svg viewBox="0 0 {CARD_W} {CARD_H}" class="block w-full" aria-hidden="true">
				<defs>
					<linearGradient id="sky-{session.n}" x1="0" y1="0" x2="0" y2="1">
						<stop offset="0%" stop-color="#040407" />
						<stop offset="100%" stop-color={card.tone} stop-opacity="0.35" />
					</linearGradient>
				</defs>
				<rect width={CARD_W} height={CARD_H} fill="#040407" />
				<rect width={CARD_W} height={CARD_H} fill="url(#sky-{session.n})" />
				{#each card.art.stars as star, i (i)}
					<circle cx={star.x} cy={star.y} r={star.r} fill="#d4c5a0" opacity={star.o} />
				{/each}
				<circle cx={card.art.orb.x} cy={card.art.orb.y} r={card.art.orb.r} fill={card.tone} opacity="0.85" />
				<circle cx={card.art.orb.x + card.art.orb.r * 0.35} cy={card.art.orb.y - card.art.orb.r * 0.2} r={card.art.orb.r} fill="#040407" opacity="0.45" />
				{#if card.art.orb.ringed}
					<ellipse cx={card.art.orb.x} cy={card.art.orb.y} rx={card.art.orb.r * 1.7} ry={card.art.orb.r * 0.35} fill="none" stroke={card.tone} stroke-opacity="0.7" />
				{/if}
				<path d={card.art.far} fill={card.tone} opacity="0.28" />
				<path d={card.art.near} fill="#0c0c0f" stroke={card.tone} stroke-opacity="0.55" />
				<text x={CARD_W - 8} y="26" text-anchor="end" font-family="var(--font-display)" font-size="22" fill="#fff" opacity="0.2">{pad(session.n)}</text>
			</svg>
			<div class="border-t border-border-dim p-3">
				<p class="flex items-baseline justify-between gap-2 text-[10px] uppercase tracking-wider">
					<span class="truncate" style:color={card.tone}>{card.stop?.name ?? 'Location not recorded'}</span>
					<span class="shrink-0 machine-text text-[9px] text-text-muted">{shortDate(session.date)}</span>
				</p>
				<h2 class="mt-1 text-xs font-bold uppercase tracking-wider text-text-primary transition-colors group-hover:text-accent-amber">{session.title}</h2>
				<p class="mt-1 line-clamp-3 text-[11px] leading-relaxed text-text-secondary">{session.brief}</p>
			</div>
		</a>
	{/each}
</div>

<style>
	.card {
		transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
	}
	.card:hover {
		border-color: var(--tone);
		transform: translateY(-2px);
		box-shadow: 0 0 18px color-mix(in srgb, var(--tone) 25%, transparent);
	}
	.chip {
		display: inline-flex;
		align-items: center;
		gap: 0.375rem;
		border: 1px solid var(--color-border-subtle);
		padding: 0.125rem 0.5rem;
		font-size: 10px;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--color-text-muted);
	}
	.chip:hover {
		color: var(--color-text-primary);
	}
	.chip-on {
		border-color: var(--tone, var(--color-accent-amber));
		color: var(--tone, var(--color-accent-amber));
		background: color-mix(in srgb, var(--tone, var(--color-accent-amber)) 10%, transparent);
	}
	@media (prefers-reduced-motion: reduce) {
		.card:hover {
			transform: none;
		}
	}
</style>
