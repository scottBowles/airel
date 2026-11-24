<script lang="ts">
	import type { Snippet } from 'svelte';

	let { children }: { children: Snippet } = $props();

	// The solar-system pages are a window onto space, not a ship's screen: switch off the
	// app-wide scanlines and grain while one is open (see `body.clear-view` in app.css).
	$effect(() => {
		document.body.classList.add('clear-view');
		return () => document.body.classList.remove('clear-view');
	});
</script>

{@render children()}
