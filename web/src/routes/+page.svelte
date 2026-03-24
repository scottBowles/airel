<script lang="ts">
	import {
		BookOpen,
		Database,
		MessageSquare,
		Shield,
		Activity,
		Radio,
		Cpu,
		Crosshair,
		Gauge,
		Zap,
	} from 'lucide-svelte';

	const systems = [
		{
			href: '/chronicle',
			label: 'CHRONICLE',
			code: 'LOG-01',
			description: 'Mission logs and session records',
			icon: BookOpen,
			status: 'ACTIVE',
			statusColor: 'text-accent-green',
		},
		{
			href: '/database',
			label: 'DATABASE',
			code: 'DAT-02',
			description: 'Crew, locations, items, artifacts',
			icon: Database,
			status: 'ACTIVE',
			statusColor: 'text-accent-green',
		},
		{
			href: '/kozmo',
			label: 'KOZMO AI',
			code: 'AI-03',
			description: 'Conversational intelligence system',
			icon: MessageSquare,
			status: 'ONLINE',
			statusColor: 'text-accent-green',
		},
	];

	const armament = [
		{ mount: 'FORE', name: 'Ion Cannon', type: 'Energy', note: 'Forward arc' },
		{ mount: 'TURRET', name: 'Plasma Turret', type: 'Fire / EMP', note: 'Mid-range, EMP capable' },
		{ mount: 'AFT', name: 'StoneFish MDS', type: 'Kinetic (Mines)', note: '27 mines loaded — life-support threat on impact' },
		{ mount: 'AFT', name: 'Vortex Flechette Needler', type: 'Gravity', note: 'Mid-range — gravity well on impact, reduces speed & maneuverability' },
	];

	const shipSpecs = [
		{ label: 'SPEED CLASS', value: '8' },
		{ label: 'MANEUVERABILITY', value: 'GOOD' },
		{ label: 'POWER CORE', value: 'GRIFTR — 200 PCU' },
		{ label: 'SHIELDS', value: '36 SP (9/QUAD)' },
	];

	const sensorSuite = [
		{ label: 'SENSORY ARRAY', value: 'MID-RANGE', status: 'ACTIVE' },
		{ label: 'SCANNER JAMMERS', value: 'EQUIPPED', status: 'STANDBY' },
		{ label: 'GATE CLEARANCE', value: 'CONFED G:9', status: 'VERIFIED' },
	];
</script>

<svelte:head>
	<title>KSS Kontularien — Bridge</title>
</svelte:head>

<div class="content-pad flex min-h-dvh flex-col">
	<div class="mx-auto flex w-full max-w-4xl flex-1 flex-col justify-center py-8 lg:py-0">

		<!-- System header bar -->
		<div class="border border-border-dim bg-hull px-4 py-2 mb-4">
			<div class="flex items-center justify-between">
				<div class="flex items-center gap-3">
					<span class="status-dot text-accent-green animate-pulse-glow"></span>
					<span class="machine-text text-[10px] text-accent-green">ALL SYSTEMS OPERATIONAL</span>
				</div>
				<span class="machine-text text-[9px] text-text-muted/50">STARDATE 2847.3</span>
			</div>
		</div>

		<!-- Ship identity -->
		<header class="border border-border-subtle bg-panel px-4 py-6 text-center console-frame mb-6">
			<p class="machine-text text-[10px] text-accent-amber/40 mb-2">
				FEDERAL STARSHIP REGISTRY // KSS-7742
			</p>
			<h1 class="title-display text-2xl text-accent-amber text-glow-amber sm:text-3xl lg:text-4xl tracking-[0.15em]">
				KONTULARIEN
			</h1>
			<div class="trace-line mx-auto mt-3 max-w-xs"></div>
			<p class="machine-text mt-3 text-[11px] text-text-muted">
				SHIPBOARD COMPUTER — NAVIGATION & INTELLIGENCE SYSTEMS
			</p>
		</header>

		<!-- System access panels -->
		<div class="grid gap-px sm:grid-cols-3 border border-border-dim mb-4">
			{#each systems as sys}
				<a
					href={sys.href}
					class="group relative flex flex-col gap-3 bg-panel px-4 py-4 transition-all hover:bg-panel-hover"
				>
					<!-- Status line -->
					<div class="flex items-center justify-between">
						<span class="machine-text text-[9px] text-text-muted/50">{sys.code}</span>
						<span class="machine-text text-[9px] {sys.statusColor}">
							<span class="status-dot {sys.statusColor} mr-1"></span>
							{sys.status}
						</span>
					</div>

					<!-- Icon + title -->
					<div class="flex items-center gap-2.5">
						<sys.icon class="h-4 w-4 text-accent-amber/50 group-hover:text-accent-amber transition-colors" />
						<h2 class="text-xs font-bold text-text-primary uppercase tracking-widest group-hover:text-accent-amber transition-colors">
							{sys.label}
						</h2>
					</div>

					<p class="text-[11px] text-text-muted leading-relaxed">{sys.description}</p>

					<!-- Access prompt -->
					<div class="border-t border-border-dim pt-2 mt-auto">
						<span class="machine-text text-[10px] text-text-muted/50 group-hover:text-accent-amber transition-colors">
							ACCESS &gt;
						</span>
					</div>

					<!-- Hover indicator bar -->
					<div class="absolute bottom-0 left-0 h-px w-0 bg-accent-amber transition-all duration-300 group-hover:w-full"></div>
				</a>
			{/each}
		</div>

		<!-- Ship Specifications -->
		<div class="border border-border-dim bg-hull mb-4">
			<div class="border-b border-border-dim px-3 py-1.5 flex items-center gap-2">
				<Gauge class="h-3 w-3 text-accent-amber/40" />
				<span class="machine-text text-[9px] text-text-muted/60">ENGINEERING // SHIP SPECIFICATIONS</span>
				<span class="ml-auto machine-text text-[9px] text-text-muted/30">GRIFTR: Gallium Retrofit Isolating Free Turbine Rig</span>
			</div>
			<div class="grid grid-cols-2 sm:grid-cols-4 gap-px">
				{#each shipSpecs as spec}
					<div class="bg-panel px-3 py-2.5">
						<p class="machine-text text-[9px] text-text-muted/50 mb-1">{spec.label}</p>
						<p class="text-sm font-bold tracking-wider text-accent-amber">{spec.value}</p>
					</div>
				{/each}
			</div>
		</div>

		<!-- Armament Readout -->
		<div class="border border-border-dim bg-hull mb-4">
			<div class="border-b border-border-dim px-3 py-1.5 flex items-center gap-2">
				<Crosshair class="h-3 w-3 text-accent-red/40" />
				<span class="machine-text text-[9px] text-text-muted/60">TACTICAL // ARMAMENT STATUS</span>
			</div>
			<div class="divide-y divide-border-dim">
				{#each armament as wep}
					<div class="flex items-start gap-3 bg-panel px-3 py-2.5">
						<span class="machine-text text-[9px] text-text-muted/40 w-12 shrink-0 pt-0.5">{wep.mount}</span>
						<div class="min-w-0 flex-1">
							<div class="flex items-baseline gap-2">
								<span class="text-xs font-bold text-text-primary tracking-wider">{wep.name}</span>
								<span class="machine-text text-[9px] text-accent-amber/50">{wep.type}</span>
							</div>
							<p class="machine-text text-[9px] text-text-muted/50 mt-0.5">{wep.note}</p>
						</div>
						<span class="machine-text text-[9px] text-accent-green shrink-0">ONLINE</span>
					</div>
				{/each}
			</div>
		</div>

		<!-- Sensors & Clearance -->
		<div class="border border-border-dim bg-hull">
			<div class="border-b border-border-dim px-3 py-1.5 flex items-center gap-2">
				<Activity class="h-3 w-3 text-accent-cyan/40" />
				<span class="machine-text text-[9px] text-text-muted/60">SENSORS & AUTHORIZATION</span>
			</div>
			<div class="grid sm:grid-cols-3 gap-px">
				{#each sensorSuite as sensor}
					<div class="bg-panel px-3 py-2.5 flex items-center justify-between">
						<div>
							<p class="machine-text text-[9px] text-text-muted/50 mb-1">{sensor.label}</p>
							<p class="text-xs font-bold tracking-wider text-text-primary">{sensor.value}</p>
						</div>
						<span class="machine-text text-[9px] text-accent-green">{sensor.status}</span>
					</div>
				{/each}
			</div>
		</div>

		<!-- Footer -->
		<footer class="mt-6 flex items-center justify-between px-1">
			<div class="flex items-center gap-3">
				<Radio class="h-3 w-3 text-text-muted/30" />
				<p class="machine-text text-[9px] text-text-muted/30">
					KOZMO INTEGRATION // ACTIVE
				</p>
			</div>
			<div class="flex items-center gap-3">
				<Cpu class="h-3 w-3 text-text-muted/30" />
				<p class="machine-text text-[9px] text-text-muted/30">
					CORE v3.7.1
				</p>
			</div>
		</footer>
	</div>
</div>
