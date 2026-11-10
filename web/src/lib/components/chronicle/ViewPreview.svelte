<script lang="ts">
	// A small schematic of what each Chronicle view looks like, for the "All views" deck.
	import type { ChronicleViewId } from '$lib/chronicle/views';

	let { view }: { view: ChronicleViewId } = $props();

	const A = 'var(--color-accent-amber)';
	const C = 'var(--color-accent-cyan)';
	const P = 'var(--color-accent-purple)';
	const DIM = 'rgba(212, 197, 160, 0.22)';
</script>

<svg viewBox="0 0 160 64" class="block w-full border border-border-dim bg-void" aria-hidden="true">
	{#if view === 'classic'}
		{#each [8, 22, 36, 50] as y (y)}
			<rect x="8" {y} width="144" height="10" fill="none" stroke={DIM} />
			<rect x="12" y={y + 3} width="18" height="4" fill={A} />
			<rect x="36" y={y + 3} width={60 + (y % 3) * 14} height="4" fill={DIM} />
		{/each}
	{:else if view === 'control'}
		<rect x="8" y="6" width="92" height="22" fill="none" stroke={A} />
		<rect x="14" y="12" width="50" height="5" fill={A} />
		<rect x="14" y="20" width="70" height="3" fill={DIM} />
		<rect x="104" y="6" width="48" height="22" fill="none" stroke={DIM} />
		<polyline points="8,36 40,36 56,42 100,42 116,36 152,36" fill="none" stroke={A} />
		{#each [8, 57, 106] as x (x)}
			<rect {x} y="46" width="46" height="13" fill="none" stroke={DIM} />
			<rect x={x + 4} y="50" width="30" height="2" fill={C} />
			<rect x={x + 4} y="54" width="20" height="2" fill={DIM} />
		{/each}
	{:else if view === 'voyage'}
		{#each [10, 22, 34, 46, 58] as y (y)}<line x1="34" x2="156" y1={y} y2={y} stroke={DIM} />{/each}
		{#each [10, 22, 34, 46, 58] as y, i (y)}<rect x="6" y={y - 2} width={14 + (i % 2) * 8} height="4" fill={DIM} />{/each}
		<path d="M40,10 C50,10 50,22 60,22 S70,34 80,34 S90,46 100,46 S110,58 120,58 S130,22 150,22" fill="none" stroke={A} stroke-width="1.5" />
		{#each [[40, 10], [60, 22], [80, 34]] as [x, y] (x)}<circle cx={x} cy={y} r="3" fill={A} />{/each}
		{#each [[100, 46], [120, 58]] as [x, y] (x)}<circle cx={x} cy={y} r="3" fill={C} />{/each}
		<circle cx="150" cy="22" r="3" fill={A} />
	{:else if view === 'starchart'}
		<circle cx="38" cy="32" r="20" fill="none" stroke={DIM} stroke-dasharray="2 3" />
		<circle cx="112" cy="30" r="24" fill="none" stroke={DIM} stroke-dasharray="2 3" />
		<circle cx="38" cy="32" r="4" fill={A} />
		<circle cx="112" cy="30" r="4" fill={C} />
		<path d="M24,18 Q70,-4 130,16 T96,50 Q60,66 52,46" fill="none" stroke={A} stroke-width="1.2" />
		{#each [[24, 18], [52, 46]] as [x, y] (x)}<rect x={x - 3} y={y - 3} width="6" height="6" fill={A} transform="rotate(45 {x} {y})" />{/each}
		{#each [[130, 16], [96, 50]] as [x, y] (x)}<rect x={x - 3} y={y - 3} width="6" height="6" fill={C} transform="rotate(45 {x} {y})" />{/each}
		<circle cx="52" cy="46" r="7" fill="none" stroke={A} />
	{:else if view === 'timeline'}
		<line x1="80" x2="80" y1="2" y2="62" stroke={A} stroke-opacity="0.5" />
		{#each [6, 26, 46] as y, i (y)}
			<rect x={i % 2 ? 90 : 14} {y} width="56" height="14" fill="none" stroke={DIM} />
			<rect x={i % 2 ? 94 : 18} y={y + 3} width="30" height="3" fill={A} />
			<rect x={i % 2 ? 94 : 18} y={y + 8} width="44" height="2" fill={DIM} />
			<rect x="76" y={y + 3} width="8" height="8" fill="var(--color-void)" stroke={i === 1 ? C : A} />
		{/each}
	{:else if view === 'saga'}
		<rect x="8" y="8" width="34" height="48" fill="none" stroke={DIM} />
		{#each [14, 21, 28, 35, 42] as y, i (y)}<rect x="12" {y} width={i === 1 ? 26 : 20} height="2" fill={i === 1 ? A : DIM} />{/each}
		<rect x="56" y="8" width="60" height="5" fill={A} />
		<rect x="56" y="20" width="10" height="12" fill={A} />
		{#each [20, 26, 32, 38, 44, 50] as y, i (y)}<rect x={i < 2 ? 70 : 56} {y} width={i < 2 ? 78 : 92 - (i % 3) * 8} height="2" fill={DIM} />{/each}
	{:else if view === 'replay'}
		<circle cx="134" cy="56" r="30" fill={A} opacity="0.3" />
		<rect x="12" y="14" width="34" height="3" fill={C} />
		<rect x="12" y="22" width="86" height="8" fill="#d4c5a0" />
		<rect x="12" y="36" width="70" height="3" fill={DIM} />
		{#each [0, 1, 2, 3, 4, 5, 6, 7] as i (i)}<rect x={12 + i * 17} y="54" width="15" height="3" fill={i < 3 ? A : DIM} />{/each}
	{:else if view === 'postcards'}
		{#each [8, 59, 110] as x, i (x)}
			{@const tone = [A, C, P][i]}
			<rect {x} y="8" width="42" height="48" fill="none" stroke={DIM} />
			<rect {x} y="8" width="42" height="26" fill={tone} opacity="0.2" />
			<circle cx={x + 28 - i * 6} cy="18" r="5" fill={tone} />
			<path d="M{x},34 l8,-6 l9,4 l10,-7 l15,9 z" fill={tone} opacity="0.6" />
			<rect x={x + 4} y="40" width="26" height="3" fill="#d4c5a0" />
			<rect x={x + 4} y="47" width="34" height="2" fill={DIM} />
		{/each}
	{:else if view === 'threads'}
		{#each [12, 24, 36, 48] as y, row (y)}
			<rect x="6" y={y - 2} width={22 + (row % 2) * 8} height="4" fill={DIM} />
			<line x1={46 + row * 12} x2={150 - row * 10} y1={y} y2={y} stroke={A} stroke-opacity="0.4" />
			{#each [0, 1, 2, 3, 4, 5, 6, 7, 8] as i (i)}
				{#if (i + row * 2) % 3 !== 1 && i >= row && i <= 8 - (row % 3)}
					<rect x={43 + i * 12} y={y - 3} width="6" height="6" fill={A} />
				{/if}
			{/each}
		{/each}
	{:else if view === 'atlas'}
		{#each [[8, A], [84, C]] as [x, tone] (x)}
			<rect {x} y="6" width="68" height="52" fill="none" stroke={DIM} />
			<line x1={x} x2={Number(x) + 68} y1="6" y2="6" stroke={tone} stroke-width="2" />
			<rect x={Number(x) + 5} y="12" width="26" height="4" fill={tone} />
			{#each [24, 34, 44] as y, i (y)}
				<rect x={Number(x) + 5 + i * 5} {y} width="22" height="3" fill="#d4c5a0" opacity="0.7" />
				<rect x={Number(x) + 44} {y} width={20 - i * 6} height="3" fill={tone} />
			{/each}
		{/each}
	{:else if view === 'calendar'}
		{#each [0, 1, 2] as m (m)}
			{#each [0, 1, 2, 3] as row (row)}
				{#each [0, 1, 2, 3, 4, 5] as col (col)}
					{@const lit = (m * 7 + row * 5 + col) % 9 === 0}
					<rect x={8 + m * 50 + col * 7} y={12 + row * 11} width="5.5" height="8" fill={lit ? [A, C, P][m] : DIM} opacity={lit ? 1 : 0.5} />
				{/each}
			{/each}
		{/each}
	{/if}
</svg>
