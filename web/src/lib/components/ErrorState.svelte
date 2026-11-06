<script lang="ts">
	type GraphQLError = { message: string };

	let { errors = [] }: { errors?: GraphQLError[] | null } = $props();
</script>

<div class="content-pad animate-fade-in">
	<div class="border border-accent-red/20 bg-accent-red/5 px-4 py-6 text-center">
		<p class="machine-text text-xs text-accent-red mb-2">SYSTEM ERROR</p>
		{#if errors && errors.length > 0}
			{#each errors as error}
				<p class="text-xs text-text-secondary">{error.message}</p>
			{/each}
		{:else}
			<p class="text-xs text-text-secondary">An unexpected error occurred</p>
		{/if}
	</div>
</div>
