<script lang="ts">
	import { T, useTask, useThrelte } from '@threlte/core';
	import { HTML } from '@threlte/extras';
	import { onDestroy } from 'svelte';
	import * as THREE from 'three';
	import { latLonToVector, type Pin } from './geo';

	type Props = {
		/** Folder under /system/ holding albedo, normal, roughness, emissive (from tools/planets). */
		slug: string;
		radius?: number;
		position?: [number, number, number];
		/** Multiplier for the emissive map (lava, city lights). */
		glow?: number;
		/** Turns per second about the planet's axis. */
		spin?: number;
		/** Longitude (degrees) that starts out facing +z, towards the default camera. */
		face?: number;
		pins?: Pin[];
		onpin?: (pin: Pin) => void;
	};
	let {
		slug,
		radius = 1,
		position = [0, 0, 0],
		glow = 1.5,
		spin = 0,
		face = -90,
		pins = [],
		onpin
	}: Props = $props();

	const loader = new THREE.TextureLoader();
	function load(file: string, srgb: boolean) {
		const tex = loader.load(`/system/${slug}/${file}`);
		tex.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
		tex.anisotropy = 8;
		return tex;
	}
	// The planet's textures don't change while it's shown, so they load once.
	// svelte-ignore state_referenced_locally
	const material = new THREE.MeshStandardMaterial({
		map: load('albedo.webp', true),
		normalMap: load('normal.webp', false),
		roughnessMap: load('roughness.webp', false),
		emissiveMap: load('emissive.webp', true),
		emissive: new THREE.Color(1, 1, 1),
		metalness: 0
	});
	$effect(() => {
		material.emissiveIntensity = glow;
	});

	let group = $state<THREE.Group>();
	const { camera } = useThrelte();

	// A pin shows only while it's on the side of the planet facing the camera.
	let facing = $state<boolean[]>([]);
	const world = new THREE.Vector3();
	const normal = new THREE.Vector3();
	const toCamera = new THREE.Vector3();
	useTask((delta) => {
		if (!group) return;
		group.rotation.y += spin * Math.PI * 2 * delta;
		const next = pins.map((pin) => {
			normal.set(...latLonToVector(pin.lat, pin.lon));
			world.copy(normal).multiplyScalar(radius);
			group!.localToWorld(world);
			normal.transformDirection(group!.matrixWorld);
			toCamera.copy(camera.current.position).sub(world).normalize();
			return normal.dot(toCamera) > 0.3;
		});
		if (next.some((v, i) => v !== facing[i])) facing = next;
	});

	onDestroy(() => {
		for (const t of [material.map, material.normalMap, material.roughnessMap, material.emissiveMap])
			t?.dispose();
		material.dispose();
	});
</script>

<T.Group bind:ref={group} {position} rotation.y={(-(face + 90) * Math.PI) / 180}>
	<T.Mesh scale={radius} {material}>
		<T.SphereGeometry args={[1, 128, 64]} />
	</T.Mesh>
	{#each pins as pin, i (pin.name)}
		{#if facing[i]}
			<HTML position={latLonToVector(pin.lat, pin.lon, radius * 1.01)} center zIndexRange={[10, 0]}>
				<button class="pin pin-{pin.confidence}" onclick={() => onpin?.(pin)}>
					<span class="dot"></span>{pin.name.split(' — ')[0].split(',')[0]}
				</button>
			</HTML>
		{/if}
	{/each}
</T.Group>

<style>
	.pin {
		display: flex;
		align-items: center;
		gap: 0.3rem;
		white-space: nowrap;
		font: 500 11px/1 var(--font-mono, ui-monospace, monospace);
		color: #ffe9c7;
		text-shadow: 0 0 3px #000, 0 0 6px #000;
		background: none;
		border: 0;
		padding: 0;
		cursor: pointer;
		transform: translateX(calc(50% - 4px));
	}
	.dot {
		width: 7px;
		height: 7px;
		border-radius: 50%;
		background: currentColor;
		box-shadow: 0 0 0 1.5px #000;
	}
	.pin-lore {
		color: #9dffb0;
	}
	.pin-layout {
		color: #ffe07a;
	}
	.pin-guess {
		color: #ff9ee0;
	}
	.pin:hover {
		color: #fff;
	}
</style>
