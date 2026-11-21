// Makes a planet's emissive map feel alive: glowing areas pulse and shimmer slowly, as lava
// does. Patches a MeshStandardMaterial's shader; advance `uniforms.uTime` every frame.

import type * as THREE from 'three';

export type Flicker = { uniforms: { uTime: { value: number }; uAmount: { value: number } } };

export function addEmissiveFlicker(material: THREE.MeshStandardMaterial, amount: number): Flicker {
	const uniforms = { uTime: { value: 0 }, uAmount: { value: amount } };
	material.onBeforeCompile = (shader) => {
		Object.assign(shader.uniforms, uniforms);
		shader.vertexShader = shader.vertexShader
			.replace('#include <common>', '#include <common>\nvarying vec3 vObjPos;')
			.replace('#include <begin_vertex>', '#include <begin_vertex>\nvObjPos = position;');
		shader.fragmentShader = shader.fragmentShader
			.replace(
				'#include <common>',
				/* glsl */ `#include <common>
varying vec3 vObjPos;
uniform float uTime;
uniform float uAmount;
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
}`
			);
	};
	material.customProgramCacheKey = () => 'emissive-flicker';
	return { uniforms };
}
