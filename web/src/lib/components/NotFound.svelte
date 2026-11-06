<script lang="ts">
	let { entityName = 'Record' }: { entityName?: string } = $props();
</script>

<div class="content-pad animate-fade-in">
	<div class="panel-border panel-bg panel-pad text-center">
		<p class="machine-text text-text-muted">{entityName.toUpperCase()} NOT FOUND</p>
	</div>
</div>
