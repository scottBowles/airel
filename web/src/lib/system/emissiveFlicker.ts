// Makes a planet's emissive map feel alive: glowing areas pulse and shimmer slowly, as lava
// does. Optionally the glow shows only on the night side, for city lights. Patches a
// MeshStandardMaterial's shader; advance `uniforms.uTime` every frame.

import * as THREE from 'three';

export type Flicker = {
	uniforms: {
		uTime: { value: number };
		uAmount: { value: number };
		/** 1: show the glow only on the side facing away from uSun. */
		uNightOnly: { value: number };
		uSun: { value: THREE.Vector3 };
	};
};

export function addEmissiveFlicker(material: THREE.MeshStandardMaterial, amount: number): Flicker {
	const uniforms = {
		uTime: { value: 0 },
		uAmount: { value: amount },
		uNightOnly: { value: 0 },
		uSun: { value: new THREE.Vector3() }
	};
	material.onBeforeCompile = (shader) => {
		Object.assign(shader.uniforms, uniforms);
		shader.vertexShader = shader.vertexShader
			.replace(
				'#include <common>',
				'#include <common>\nvarying vec3 vObjPos;\nvarying vec3 vWorldNormal;\nvarying vec3 vWorldPos;'
			)
			.replace(
				'#include <begin_vertex>',
				`#include <begin_vertex>
vObjPos = position;
vWorldNormal = normalize(mat3(modelMatrix) * objectNormal);
vWorldPos = (modelMatrix * vec4(position, 1.0)).xyz;`
			);
		shader.fragmentShader = shader.fragmentShader
			.replace(
				'#include <common>',
				/* glsl */ `#include <common>
varying vec3 vObjPos;
varying vec3 vWorldNormal;
varying vec3 vWorldPos;
uniform float uTime;
uniform float uAmount;
uniform float uNightOnly;
uniform vec3 uSun;
float fhash(vec3 p) { p = fract(p * 0.3183099 + 0.1); p *= 17.0; return fract(p.x * p.y * p.z * (p.x + p.y + p.z)); }
float fnoise(vec3 x) {
  vec3 i = floor(x); vec3 f = fract(x); f = f * f * (3.0 - 2.0 * f);
  return mix(mix(mix(fhash(i), fhash(i + vec3(1,0,0)), f.x), mix(fhash(i + vec3(0,1,0)), fhash(i + vec3(1,1,0)), f.x), f.y),
             mix(mix(fhash(i + vec3(0,0,1)), fhash(i + vec3(1,0,1)), f.x), mix(fhash(i + vec3(0,1,1)), fhash(i + vec3(1,1,1)), f.x), f.y), f.z);
}`
			)
			.replace(
				'#include <emissivemap_fragment>',
				/* glsl */ `#include <emissivemap_fragment>
{
  vec3 q = normalize(vObjPos);
  // Slow surges across regions, quicker shimmer in the small cracks.
  float surge = fnoise(q * 5.0 + vec3(0.0, uTime * 0.05, uTime * 0.03));
  float shimmer = fnoise(q * 60.0 + vec3(uTime * 0.35, 0.0, -uTime * 0.25));
  float k = 0.65 + 0.55 * surge + 0.25 * (shimmer - 0.5);
  totalEmissiveRadiance *= mix(1.0, k, uAmount);
  // City lights come on across dusk and are off in daylight.
  float sunward = dot(normalize(vWorldNormal), normalize(uSun - vWorldPos));
  totalEmissiveRadiance *= mix(1.0, smoothstep(0.12, -0.18, sunward), uNightOnly);
}`
			);
	};
	material.customProgramCacheKey = () => 'emissive-flicker';
	return { uniforms };
}
