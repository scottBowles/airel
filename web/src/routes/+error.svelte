<script lang="ts">
	import { page } from '$app/state';
</script>

<svelte:head>
	<title>Error {page.status} — Kontularien</title>
</svelte:head>

<div class="flex min-h-[60vh] flex-col items-center justify-center text-center content-pad">
	<div class="border border-accent-red/20 bg-hull px-8 py-10">
		<p class="title-display text-2xl text-accent-red text-glow-red mb-3">
			ERROR {page.status}
		</p>
		<div class="h-px w-full bg-gradient-to-r from-transparent via-accent-red/30 to-transparent mb-4"></div>
		<p class="machine-text text-xs text-text-muted tracking-wider">
			{#if page.status === 404}
				SIGNAL LOST // TARGET NOT FOUND
			{:else if page.status === 500}
				SYSTEM MALFUNCTION // INTERNAL ERROR
			{:else if page.status === 403}
				ACCESS DENIED // INSUFFICIENT CLEARANCE
			{:else}
				UNEXPECTED FAULT DETECTED
			{/if}
		</p>
		{#if page.error?.message}
			<p class="mt-3 text-xs text-text-secondary">{page.error.message}</p>
		{/if}
		<a
			href="/"
			class="mt-6 inline-block border border-accent-amber/30 px-4 py-2 machine-text text-xs text-accent-amber transition-colors hover:bg-accent-amber/10"
		>
			RETURN TO BRIDGE
		</a>
	</div>
</div>
