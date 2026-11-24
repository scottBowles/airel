<script lang="ts">
	import { T, useTask } from '@threlte/core';
	import { onDestroy } from 'svelte';
	import { sunCoronaMaterial, sunSurfaceMaterial, type SunLook } from './sunShader';

	type Props = {
		look: SunLook;
		radius?: number;
		position?: [number, number, number];
		/** Strength of the light the sun casts on planets. */
		intensity?: number;
		/**
		 * How far the light reaches (0: everywhere, undimmed). It fades smoothly to nothing there,
		 * so with two suns each planet is lit mostly by its own, and a tidally locked world's dark
		 * side stays dark.
		 */
		reach?: number;
	};
	let { look, radius = 1, position = [0, 0, 0], intensity = 3, reach = 0 }: Props = $props();

	const CORONA = 2.6; // corona size, in sun radii
	// The look is fixed for a sun's lifetime, so the materials are built once.
	// svelte-ignore state_referenced_locally
	const surface = sunSurfaceMaterial(look);
	// svelte-ignore state_referenced_locally
	const corona = sunCoronaMaterial(look, CORONA);

	// Light falling on planets: the sun's hue, but mostly white, so it doesn't tint every surface.
	// svelte-ignore state_referenced_locally
	const light = look.glow.map((c) => 0.35 * c + 0.65) as [number, number, number];

	useTask((delta) => {
		surface.uniforms.uTime.value += delta;
		corona.uniforms.uTime.value += delta;
	});

	onDestroy(() => {
		surface.dispose();
		corona.dispose();
	});
</script>

<T.Group {position}>
	<T.Mesh scale={radius} material={surface}>
		<T.SphereGeometry args={[1, 96, 48]} />
	</T.Mesh>
	<T.Mesh scale={radius * CORONA} material={corona} renderOrder={1}>
		<T.PlaneGeometry args={[2, 2]} />
	</T.Mesh>
	<T.PointLight color={light} {intensity} decay={0} distance={reach} />
</T.Group>
