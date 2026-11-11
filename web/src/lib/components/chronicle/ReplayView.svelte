<script lang="ts">
	// Holo-Replay: one session fills the viewscreen at a time, like a recap before game night.
	// It opens on the last few sessions ("previously on…"); it can also start from the top of
	// the current arc or from the very beginning. Arrow keys step and space plays or pauses.
	import Play from '@lucide/svelte/icons/play';
	import Pause from '@lucide/svelte/icons/pause';
	import SkipBack from '@lucide/svelte/icons/skip-back';
	import SkipForward from '@lucide/svelte/icons/skip-forward';
	import ArrowRight from '@lucide/svelte/icons/arrow-right';
	import {
		arcBySession,
		buildArcs,
		roman,
		worldColours,
		pad,
		primaryStop,
		shortDate,
		wherePath,
		type Session
	} from '$lib/chronicle/model';

	let { sessions }: { sessions: Session[] } = $props();

	const DWELL_MS = 8000;
	/** How many sessions "previously on…" covers. */
	const RECAP = 8;

	let colours = $derived(worldColours(sessions));
	let arcs = $derived(buildArcs(sessions, colours));
	let arcOf = $derived(arcBySession(arcs));
	let recapStart = $derived(Math.max(0, sessions.length - RECAP));
	let index = $state<number | null>(null);
	let at = $derived(Math.min(index ?? recapStart, sessions.length - 1));
	let session = $derived(sessions[at]);
	let stop = $derived(session ? primaryStop(session) : null);
	let colour = $derived(stop ? (colours.get(stop.path[0].id) ?? '#ffb000') : '#ffb000');
	let arc = $derived(session ? arcOf.get(session.id) : undefined);
	let currentArcStart = $derived(arcs.at(-1)?.start ?? 0);

	/** Start points for a replay: the recap, the top of the current arc, the beginning. */
	let starts = $derived([
		{ label: 'Previously on…', from: recapStart },
		{ label: `This arc: ${arcs.at(-1)?.world?.name ?? '—'}`, from: currentArcStart },
		{ label: 'From the beginning', from: 0 }
	]);

	function startFrom(from: number) {
		index = from;
		playing = true;
	}

	let playing = $state(false);
	$effect(() => {
		if (!playing) return;
		// Reading `at` restarts the timer whenever the session changes by hand.
		const from = at;
		const timer = setTimeout(() => {
			if (from >= sessions.length - 1) playing = false;
			else index = from + 1;
		}, DWELL_MS);
		return () => clearTimeout(timer);
	});

	function go(to: number) {
		index = Math.max(0, Math.min(sessions.length - 1, to));
	}

	function onKey(event: KeyboardEvent) {
		const target = event.target as HTMLElement | null;
		if (target?.closest('input, textarea, select, [contenteditable]')) return;
		if (event.key === 'ArrowRight') go(at + 1);
		else if (event.key === 'ArrowLeft') go(at - 1);
		else if (event.key === ' ' && !target?.closest('button, a')) {
			event.preventDefault();
			playing = !playing;
		}
	}

	const stars = Array.from({ length: 90 }, (_, i) => {
		const a = Math.sin(i * 91.7) * 43758.5453;
		const b = Math.sin(i * 47.3) * 24634.6345;
		return { x: (a - Math.floor(a)) * 100, y: (b - Math.floor(b)) * 100, big: i % 6 === 0 };
	});
</script>

<svelte:window onkeydown={onKey} />

{#if session}
	<div class="border border-border-dim bg-hull">
		<div class="flex flex-wrap items-center justify-between gap-2 border-b border-border-dim px-3 py-1.5">
			<span class="machine-text text-[9px] text-text-muted">VIS-05 // HOLO-REPLAY</span>
			<div class="flex flex-wrap items-center gap-1.5">
				{#each starts as start (start.label)}
					<button
						type="button"
						class="border px-2 py-0.5 text-[10px] uppercase tracking-wider transition-colors {index === start.from || (index === null && start.from === recapStart)
							? 'border-accent-amber/60 text-accent-amber'
							: 'border-border-subtle text-text-muted hover:text-text-primary'}"
						onclick={() => startFrom(start.from)}
					>
						▶ {start.label}
					</button>
				{/each}
				<span class="ml-2 hidden machine-text text-[9px] text-text-faint sm:inline">← → STEP · SPACE {playing ? 'PAUSE' : 'PLAY'}</span>
			</div>
		</div>

		<div class="screen relative overflow-hidden" style:--tone={colour}>
			{#each stars as star, i (i)}
				<span class="absolute bg-text-primary" style:left="{star.x}%" style:top="{star.y}%"
					style:width={star.big ? '2px' : '1px'} style:height={star.big ? '2px' : '1px'} style:opacity={0.15 + (i % 5) * 0.1}></span>
			{/each}
			<div class="world" aria-hidden="true"></div>

			{#key session.id}
				<div class="relative flex min-h-[26rem] animate-fade-in flex-col justify-between gap-8 p-5 sm:min-h-[30rem] sm:p-10">
					<div class="flex flex-wrap items-baseline justify-between gap-2">
						<p class="font-display text-xs tracking-[0.3em] text-text-secondary">
							SESSION <span class="text-accent-amber">{pad(session.n)}</span> / {pad(sessions.length)}
							{#if arc}
								<span class="ml-3 text-[10px] tracking-[0.2em]" style:color={arc.colour}>
									PART {roman(arc.n)} · {arc.sessions.indexOf(session) + 1} OF {arc.sessions.length} ON {(arc.world?.name ?? 'UNRECORDED').toUpperCase()}
								</span>
							{/if}
						</p>
						<p class="machine-text text-[11px] text-text-secondary">{shortDate(session.date)}</p>
					</div>

					<div class="max-w-3xl">
						{#if stop}
							<p class="text-xs uppercase tracking-[0.25em]" style:color={colour}>▸ {wherePath(stop)}</p>
						{/if}
						<h2 class="title mt-3 font-display text-3xl uppercase leading-tight text-text-primary sm:text-5xl">{session.title}</h2>
						{#if session.brief}
							<p class="mt-4 max-w-2xl text-base leading-relaxed text-text-primary/90 sm:text-lg">{session.brief}</p>
						{/if}
					</div>

					<div class="flex flex-wrap items-end justify-between gap-3">
						<div class="flex max-w-2xl flex-wrap gap-1.5">
							{#each session.characters as character (character.id)}
								<span class="border border-border-subtle bg-void/60 px-2 py-0.5 text-[10px] uppercase tracking-wider text-text-secondary">{character.name}</span>
							{/each}
							{#each [...session.artifacts, ...session.items] as thing (thing.id)}
								<span class="border border-accent-purple/40 bg-void/60 px-2 py-0.5 text-[10px] uppercase tracking-wider text-accent-purple">{thing.name}</span>
							{/each}
						</div>
						<a href="/chronicle/{session.id}" class="flex items-center gap-1 machine-text text-[11px] text-accent-amber hover:underline">
							OPEN LOG <ArrowRight class="h-3 w-3" />
						</a>
					</div>
				</div>
			{/key}
		</div>

		<!-- One segment per session, tinted by the world of its arc -->
		<div class="flex gap-px border-t border-border-dim px-3 pt-2.5">
			{#each sessions as item, i (item.id)}
				{@const tone = arcOf.get(item.id)?.colour ?? '#ffb000'}
				<button type="button" class="group h-4 min-w-0 flex-1" aria-label="Session {item.n}: {item.title}" title="{pad(item.n)} · {item.title}" onclick={() => go(i)}>
					<span class="block h-1 overflow-hidden group-hover:brightness-150" style:background="color-mix(in srgb, {tone} 22%, var(--color-panel-light))">
						{#if i < at}
							<span class="block h-full" style:background={tone} style:opacity="0.75"></span>
						{:else if i === at}
							{#key `${item.id}-${playing}`}
								<span class="block h-full bg-accent-amber {playing ? 'fill' : ''}" style:--dwell="{DWELL_MS}ms"></span>
							{/key}
						{/if}
					</span>
				</button>
			{/each}
		</div>
		<div class="flex items-center gap-2 px-3 pb-2.5">
			<button type="button" class="ctl" aria-label="Previous session" disabled={at === 0} onclick={() => go(at - 1)}><SkipBack class="h-3.5 w-3.5" /></button>
			<button type="button" class="ctl ctl-main" aria-label={playing ? 'Pause' : 'Play'} onclick={() => { if (!playing && at >= sessions.length - 1) index = recapStart; playing = !playing; }}>
				{#if playing}<Pause class="h-3.5 w-3.5" />{:else}<Play class="h-3.5 w-3.5" />{/if}
			</button>
			<button type="button" class="ctl" aria-label="Next session" disabled={at >= sessions.length - 1} onclick={() => go(at + 1)}><SkipForward class="h-3.5 w-3.5" /></button>
			<span class="ml-2 min-w-0 truncate machine-text text-[10px] text-text-muted">
				{playing ? 'REPLAYING THE VOYAGE' : 'PAUSED'}{sessions[at + 1] ? ` · NEXT: ${sessions[at + 1].title}` : ' · END OF RECORD'}
			</span>
		</div>
	</div>
{/if}

<style>
	.screen {
		background:
			radial-gradient(ellipse at 20% 0%, color-mix(in srgb, var(--tone) 10%, transparent), transparent 60%),
			#040407;
	}
	.world {
		position: absolute;
		right: -9rem;
		bottom: -13rem;
		height: 30rem;
		width: 30rem;
		border-radius: 9999px;
		background: radial-gradient(circle at 32% 28%, color-mix(in srgb, var(--tone) 55%, #000), #06060a 68%);
		box-shadow:
			0 0 80px color-mix(in srgb, var(--tone) 22%, transparent),
			inset -30px -30px 80px #000;
		opacity: 0.75;
		transition: background 0.8s, box-shadow 0.8s;
	}
	.title {
		text-shadow: 0 0 24px color-mix(in srgb, var(--tone) 35%, transparent);
	}
	.fill {
		animation: fill var(--dwell) linear forwards;
	}
	@keyframes fill {
		from { width: 0; }
		to { width: 100%; }
	}
	.ctl {
		display: flex;
		height: 2rem;
		width: 2rem;
		flex-shrink: 0;
		align-items: center;
		justify-content: center;
		border: 1px solid var(--color-border-subtle);
		color: var(--color-text-secondary);
	}
	.ctl:hover:not(:disabled) {
		border-color: var(--color-accent-amber);
		color: var(--color-accent-amber);
	}
	.ctl:disabled {
		opacity: 0.35;
	}
	.ctl-main {
		background: var(--color-accent-amber-dim);
		color: var(--color-accent-amber);
	}
</style>
