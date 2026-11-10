<script lang="ts">
	// Atlas: the story by location. Every place the crew has been, nested by system and world,
	// with how often they were there and which sessions happened there.
	import {
		buildPlaceTree,
		worldColours,
		pad,
		shortDate,
		type PlaceNode,
		type Session
	} from '$lib/chronicle/model';

	let { sessions }: { sessions: Session[] } = $props();

	let tree = $derived(buildPlaceTree(sessions));
	let colours = $derived(worldColours(sessions));
	let uncharted = $derived(sessions.filter((s) => !s.stops.length));

	type Row = { node: PlaceNode; rootId: string };
	const flatten = (root: PlaceNode): Row[] => {
		const out: Row[] = [];
		const walk = (node: PlaceNode) => {
			out.push({ node, rootId: root.id });
			node.children.forEach(walk);
		};
		root.children.forEach(walk);
		return out;
	};

	let most = $derived(Math.max(1, ...[...tree.byId.values()].map((n) => n.sessions.length)));
	let ports = $derived(
		[...tree.byId.values()]
			.filter((n) => n.sessions.length)
			.sort((a, b) => b.sessions.length - a.sessions.length)
			.slice(0, 4)
	);
	const typeLabel = (type: string | null) => (type ?? 'PLACE').toUpperCase();
</script>

<div class="grid grid-cols-2 gap-px border border-border-dim bg-border-dim lg:grid-cols-4">
	{#each ports as port, i (port.id)}
		<a href="/database/places/{port.id}" class="group bg-hull px-3 py-2.5 hover:bg-panel-hover">
			<p class="machine-text text-[9px] text-text-muted">{i === 0 ? 'HOME PORT' : `MOST VISITED #${i + 1}`}</p>
			<p class="mt-0.5 truncate font-display text-xs uppercase tracking-wider text-accent-amber">{port.name}</p>
			<p class="machine-text text-[9px] text-text-faint">{port.sessions.length} SESSIONS</p>
		</a>
	{/each}
</div>

<div class="grid grid-cols-1 gap-3 xl:grid-cols-2">
	{#each tree.roots as root (root.id)}
		{@const colour = colours.get(root.id) ?? '#8a7e60'}
		{@const span = root.allSessions}
		<section class="border border-border-dim bg-hull" style:border-top-color={colour} style:border-top-width="2px">
			<header class="flex flex-wrap items-baseline justify-between gap-2 border-b border-border-dim px-3 py-2.5">
				<div>
					<p class="machine-text text-[9px] text-text-muted">{typeLabel(root.type)}</p>
					<a href="/database/places/{root.id}" class="font-display text-base uppercase tracking-widest hover:underline" style:color={colour}>{root.name}</a>
				</div>
				<p class="text-right machine-text text-[9px] text-text-muted">
					{span.length} SESSIONS<br />
					{shortDate(span[0]?.date ?? null)} → {shortDate(span.at(-1)?.date ?? null)}
				</p>
			</header>

			{#each [{ node: root, rootId: root.id }, ...flatten(root)] as row (row.node.id)}
				{@const node = row.node}
				{#if node.depth > 0 || node.sessions.length}
					<div class="border-b border-border-dim/60 px-3 py-2 last:border-b-0" style:padding-left="{12 + Math.max(0, node.depth - 1) * 18}px">
						<div class="flex items-center gap-2">
							{#if node.depth > 1}<span class="text-text-faint">└</span>{/if}
							<a href="/database/places/{node.id}" class="truncate text-xs font-bold uppercase tracking-wider hover:text-accent-amber {node.sessions.length ? 'text-text-primary' : 'text-text-muted'}">
								{node.depth === 0 ? `${node.name} (general)` : node.name}
							</a>
							<span class="machine-text text-[9px] text-text-faint">{typeLabel(node.type)}</span>
							<span class="ml-auto h-1.5 w-24 shrink-0 bg-void">
								<span class="block h-full" style:background={colour} style:width="{(node.sessions.length / most) * 100}%"></span>
							</span>
							<span class="w-6 text-right machine-text text-[10px]" style:color={node.sessions.length ? colour : undefined}>{node.sessions.length ? `×${node.sessions.length}` : '—'}</span>
						</div>
						{#if node.sessions.length}
							<ul class="mt-1.5 space-y-0.5" style:padding-left="{node.depth > 1 ? 18 : 0}px">
								{#each node.sessions as session (session.id)}
									<li>
										<a href="/chronicle/{session.id}" class="group flex items-baseline gap-2 text-[11px] text-text-secondary hover:text-accent-amber">
											<span class="machine-text shrink-0 text-[10px]" style:color={colour}>{pad(session.n)}</span>
											<span class="truncate">{session.title}</span>
											<span class="ml-auto shrink-0 machine-text text-[9px] text-text-faint">{shortDate(session.date)}</span>
										</a>
									</li>
								{/each}
							</ul>
						{/if}
					</div>
				{/if}
			{/each}
		</section>
	{/each}
</div>

{#if uncharted.length}
	<section class="border border-border-dim bg-hull px-3 py-2.5">
		<p class="machine-text text-[9px] text-text-muted">LOCATION NOT RECORDED · {uncharted.length} SESSIONS</p>
		<div class="mt-1.5 flex flex-wrap gap-1.5">
			{#each uncharted as session (session.id)}
				<a href="/chronicle/{session.id}" class="border border-border-subtle px-1.5 py-0.5 text-[10px] uppercase tracking-wider text-text-muted hover:border-accent-amber hover:text-accent-amber" title={session.title}>
					{pad(session.n)} · {session.title}
				</a>
			{/each}
		</div>
	</section>
{/if}
