<script lang="ts">
	import { T, useTask } from '@threlte/core';
	import type { Snippet } from 'svelte';
	import type * as THREE from 'three';

	type Props = {
		/** Seconds per turn. */
		period: number;
		/** Starting angle, radians. */
		phase?: number;
		/** Tilt of the orbital plane, degrees. */
		tilt?: number;
		position?: [number, number, number];
		/** How fast time runs: 1 is normal, 0 paused. */
		rate?: number;
		children: Snippet;
	};
	let { period, phase = 0, tilt = 0, position = [0, 0, 0], rate = 1, children }: Props = $props();

	// Anything placed on the +x axis inside circles the centre; because it turns with the
	// group, it keeps one face to the centre (tidal lock).
	let spinner = $state<THREE.Group>();
	useTask((delta) => {
		if (spinner) spinner.rotation.y += ((Math.PI * 2) / period) * delta * rate;
	});
</script>

<T.Group {position} rotation.z={(tilt * Math.PI) / 180}>
	<!-- svelte-ignore state_referenced_locally -->
	<T.Group bind:ref={spinner} rotation.y={phase}>
		{@render children()}
	</T.Group>
</T.Group>
