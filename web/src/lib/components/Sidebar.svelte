<script lang="ts">
	import { page } from '$app/state';
	import { cn } from '$lib/utils';
	import {
		Home,
		BookOpen,
		Database,
		MessageSquare,
		Search,
		LogIn,
		LogOut,
		Menu,
		X,
	} from 'lucide-svelte';

	let {
		user,
		onsearch,
	}: {
		user: { username: string; isStaff?: boolean } | null | undefined;
		onsearch: () => void;
	} = $props();

	let mobileOpen = $state(false);

	const navItems = [
		{ href: '/', label: 'BRIDGE', icon: Home, code: 'SYS-00' },
		{ href: '/chronicle', label: 'CHRONICLE', icon: BookOpen, code: 'LOG-01' },
		{ href: '/database', label: 'DATABASE', icon: Database, code: 'DAT-02' },
		{ href: '/kozmo', label: 'KOZMO', icon: MessageSquare, code: 'AI-03' },
	];

	function isActive(href: string) {
		if (href === '/') return page.url.pathname === '/';
		return page.url.pathname.startsWith(href);
	}

	function closeMobile() {
		mobileOpen = false;
	}

	async function logout() {
		await fetch('/auth/logout', { method: 'POST' });
		window.location.href = '/login';
	}
</script>

<!-- Mobile hamburger -->
<button
	class="fixed left-2 top-2 z-50 flex h-9 w-9 items-center justify-center border border-border-dim bg-hull text-accent-amber lg:hidden"
	onclick={() => (mobileOpen = !mobileOpen)}
	aria-label="Toggle navigation"
>
	{#if mobileOpen}
		<X class="h-4 w-4" />
	{:else}
		<Menu class="h-4 w-4" />
	{/if}
</button>

<!-- Mobile overlay -->
{#if mobileOpen}
	<button
		class="fixed inset-0 z-30 bg-black/70 lg:hidden"
		onclick={closeMobile}
		aria-label="Close navigation"
	></button>
{/if}

<!-- Sidebar -->
<nav
	class={cn(
		'fixed left-0 top-0 z-40 flex h-dvh w-56 flex-col border-r border-border-subtle bg-hull transition-transform duration-200 lg:translate-x-0',
		mobileOpen ? 'translate-x-0' : '-translate-x-full',
	)}
>
	<!-- Ship identity — top panel -->
	<div class="border-b border-border-subtle px-4 py-3">
		<a href="/" class="group block" onclick={closeMobile}>
			<div class="flex items-center gap-2 mb-1">
				<span class="status-dot text-accent-green animate-pulse-glow"></span>
				<span class="machine-text text-[9px] text-text-muted">ONLINE</span>
			</div>
			<h1 class="title-display text-sm text-accent-amber text-glow-amber">
				KSS KONTULARIEN
			</h1>
			<div class="trace-line mt-2"></div>
			<p class="machine-text mt-1.5 text-[9px] text-text-muted">
				SHIPBOARD COMPUTER v3.7.1
			</p>
		</a>
	</div>

	<!-- Search trigger -->
	<div class="border-b border-border-dim px-3 py-2">
		<button
			onclick={() => {
				closeMobile();
				onsearch();
			}}
			class="flex w-full items-center gap-2 border border-border-dim bg-void px-2.5 py-1.5 text-left text-text-muted transition-colors hover:border-accent-amber/30 hover:text-accent-amber"
		>
			<Search class="h-3.5 w-3.5" />
			<span class="text-[11px] uppercase tracking-widest flex-1">Search</span>
			<kbd class="hidden border border-border-dim bg-panel px-1 py-0.5 text-[9px] sm:inline">
				⌘K
			</kbd>
		</button>
	</div>

	<!-- Nav links -->
	<div class="flex-1 overflow-y-auto px-2 py-2">
		<p class="machine-text px-2 py-1 text-[9px] text-text-muted/60">NAVIGATION</p>
		<div class="space-y-px mt-1">
			{#each navItems as item}
				{@const active = isActive(item.href)}
				<a
					href={item.href}
					onclick={closeMobile}
					class={cn(
						'group flex items-center gap-2.5 px-2 py-2 text-xs uppercase tracking-wider transition-all',
						active
							? 'bg-accent-amber/8 text-accent-amber border-l-2 border-accent-amber'
							: 'text-text-secondary hover:bg-accent-amber/5 hover:text-accent-amber border-l-2 border-transparent',
					)}
				>
					<item.icon class={cn('h-3.5 w-3.5', active ? 'text-accent-amber' : 'text-text-muted group-hover:text-accent-amber/60')} />
					<span class="flex-1">{item.label}</span>
					<span class={cn('text-[9px] tracking-normal', active ? 'text-accent-amber/40' : 'text-text-muted/40')}>{item.code}</span>
				</a>
			{/each}
		</div>
	</div>

	<!-- System status -->
	<div class="border-t border-border-dim px-3 py-2">
		<div class="flex items-center justify-between px-1 mb-2">
			<span class="machine-text text-[9px] text-text-muted/60">SYS STATUS</span>
			<span class="machine-text text-[9px] text-accent-green">NOMINAL</span>
		</div>
		<div class="flex gap-1">
			<div class="h-1 flex-1 bg-accent-green/30"></div>
			<div class="h-1 flex-1 bg-accent-green/30"></div>
			<div class="h-1 flex-1 bg-accent-green/30"></div>
			<div class="h-1 flex-1 bg-accent-green/20"></div>
			<div class="h-1 flex-1 bg-accent-green/10"></div>
		</div>
	</div>

	<!-- User section -->
	<div class="border-t border-border-subtle px-3 py-2.5">
		{#if user}
			<div class="flex items-center gap-2.5">
				<div class="flex h-7 w-7 items-center justify-center border border-accent-amber/20 bg-accent-amber/5 text-[10px] font-bold text-accent-amber uppercase">
					{user.username.charAt(0)}
				</div>
				<div class="min-w-0 flex-1">
					<p class="truncate text-xs text-text-primary uppercase tracking-wider">{user.username}</p>
					<p class="machine-text text-[9px] text-text-muted">
						{user.isStaff ? 'CLEARANCE: ADMIN' : 'CLEARANCE: CREW'}
					</p>
				</div>
				<button
					onclick={logout}
					class="text-text-muted transition-colors hover:text-accent-red"
					title="Log out"
				>
					<LogOut class="h-3.5 w-3.5" />
				</button>
			</div>
		{:else}
			<a
				href="/login"
				onclick={closeMobile}
				class="flex items-center gap-2.5 text-xs text-text-secondary uppercase tracking-wider transition-colors hover:text-accent-amber"
			>
				<LogIn class="h-3.5 w-3.5 text-text-muted" />
				<span>System Access</span>
			</a>
		{/if}
	</div>
</nav>
