<script lang="ts">
	import type { Session } from '$lib/chronicle/model';
	let { sessions }: { sessions: Session[] } = $props();
</script>

<p class="machine-text text-text-muted">{sessions.length} sessions</p>
