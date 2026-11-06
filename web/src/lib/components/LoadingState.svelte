<script lang="ts">
	let { message = 'ACCESSING DATABASE' }: { message?: string } = $props();
</script>

<div class="flex flex-col items-center justify-center py-16 text-center animate-fade-in">
	<div class="mb-4 flex items-center gap-2">
		<span class="inline-block h-2 w-2 bg-accent-amber animate-pulse-glow"></span>
		<span class="machine-text text-xs text-accent-amber tracking-wider">{message}</span>
		<span class="machine-text text-xs text-accent-amber animate-blink">_</span>
	</div>
	<div class="h-px w-32 bg-gradient-to-r from-transparent via-accent-amber/30 to-transparent"></div>
</div>
