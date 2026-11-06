<script lang="ts">
	import { cn } from '$lib/utils';
	import { getUserContext } from '$lib/auth';
	import Lock from '@lucide/svelte/icons/lock';
	import Unlock from '@lucide/svelte/icons/unlock';

	let {
		locked,
		lockedBySelf,
		lockUser,
		onlock,
		class: className,
	}: {
		locked: boolean;
		lockedBySelf: boolean;
		lockUser?: { username: string } | null;
		onlock: () => void;
		class?: string;
	} = $props();

	const getUser = getUserContext();
	let isStaff = $derived(!!getUser()?.isStaff);
</script>

{#if isStaff}
	<div class={cn('flex items-center gap-2', className)}>
		{#if locked && !lockedBySelf}
			<span class="machine-text flex items-center gap-1.5 text-accent-red text-[10px]">
				<span class="status-dot text-accent-red"></span>
				<Lock class="h-3 w-3" />
				LOCKED BY {lockUser?.username ?? 'UNKNOWN'}
			</span>
		{:else if lockedBySelf}
			<span
				class="machine-text flex items-center gap-1.5 text-accent-green text-[10px]"
			>
				<span class="status-dot text-accent-green animate-pulse-glow"></span>
				<Unlock class="h-3 w-3" />
				EDITING
			</span>
		{:else}
			<button
				onclick={onlock}
				class="machine-text flex items-center gap-1.5 text-text-muted text-[10px] transition-colors hover:text-accent-amber cursor-pointer"
			>
				<Lock class="h-3 w-3" />
				UPDATE RECORD
			</button>
		{/if}
	</div>
{/if}
