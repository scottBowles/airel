// Makes a planet's emissive map feel alive: glowing areas pulse and shimmer slowly, as lava
// does. Optionally the glow shows only on the night side, for city lights. Also casts the
// cloud layer's shadows onto the ground. Patches a MeshStandardMaterial's shader; advance
// `uniforms.uTime` every frame.

import * as THREE from 'three';

export type Flicker = {
	uniforms: {
		uTime: { value: number };
		uAmount: { value: number };
		/** 1: show the glow only on the side facing away from uSun. */
		uNightOnly: { value: number };
		uSun: { value: THREE.Vector3 };
		/** The cloud layer's alpha map; its shadow strength (0 for none). */
		uCloudMap: { value: THREE.Texture | null };
		uShadow: { value: number };
		/** The sun's position in the planet mesh's own space (unit sphere). */
		uSunLocal: { value: THREE.Vector3 };
		/** How far the cloud layer has turned relative to the ground, radians about +y. */
		uCloudTurn: { value: number };
		/** 0..1: break the glow into fine points of light as the camera comes close (cities). */
		uDetail: { value: number };
	};
};

export function addEmissiveFlicker(material: THREE.MeshStandardMaterial, amount: number): Flicker {
	const uniforms = {
		uTime: { value: 0 },
		uAmount: { value: amount },
		uNightOnly: { value: 0 },
		uSun: { value: new THREE.Vector3() },
		uCloudMap: { value: null as THREE.Texture | null },
		uShadow: { value: 0 },
		uSunLocal: { value: new THREE.Vector3(0, 0, 1) },
		uCloudTurn: { value: 0 },
		uDetail: { value: 0 }
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
				'#include <map_fragment>',
				/* glsl */ `#include <map_fragment>
if (uShadow > 0.0) diffuseColor.rgb *= 1.0 - uShadow * cloudShadow(normalize(vObjPos));`
			)
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
uniform sampler2D uCloudMap;
uniform float uShadow;
uniform vec3 uSunLocal;
uniform float uCloudTurn;
uniform float uDetail;
// Cloud cover between this point and the sun. The shadow is cast from a little higher than the
// cloud mesh really is, so the offset shows; a blurred mip makes its edges soft.
float cloudShadow(vec3 p) {
  vec3 l = normalize(uSunLocal - p);
  float r = 1.05;
  float b = dot(p, l);
  vec3 c = p + l * (-b + sqrt(b * b - (1.0 - r * r)));
  float s = sin(-uCloudTurn), co = cos(-uCloudTurn);
  c = vec3(co * c.x + s * c.z, c.y, -s * c.x + co * c.z);
  c = normalize(c);
  // three.js SphereGeometry's uv: u from atan(z, -x), v from y.
  float u = atan(c.z, -c.x) / (2.0 * PI);
  u = u < 0.0 ? u + 1.0 : u;
  float v = 1.0 - acos(clamp(c.y, -1.0, 1.0)) / PI;
  // Only thick cloud casts a shadow; a thin overcast everywhere would just dim the whole planet.
  return smoothstep(0.4, 0.85, textureLod(uCloudMap, vec2(u, v), 3.0).r);
}
float hash13(vec3 p) { p = fract(p * vec3(0.1031, 0.1030, 0.0973)); p += dot(p, p.yxz + 33.33); return fract((p.x + p.y) * p.z); }
// Points of light finer than the emissive map can hold: each cell of a grid laid on the cube
// faces (so nothing pinches at the poles) holds one jittered light, or none. Averages to about
// 1, so multiplying the map by it keeps the glow as bright overall. Fades out wherever a cell is
// smaller than a few pixels, where it would only shimmer.
float glitter(vec2 uv, float face, float s) {
  vec2 x = uv * s;
  vec2 cell = floor(x);
  vec3 i = vec3(cell, face * 7919.0 + s);
  float h = hash13(i);
  vec2 c = 0.2 + 0.6 * vec2(hash13(i + 11.1), hash13(i + 23.7));
  float r = 0.16 + 0.2 * hash13(i + 37.3);
  float dots = step(0.3, h) * smoothstep(r, r * 0.35, length(fract(x) - c)) * (0.4 + h);
  float lit = 0.5 + dots * 6.4;
  float px = s * length(fwidth(uv));
  return mix(1.0, lit, smoothstep(0.6, 0.3, px));
}
float cityDetail(vec3 q) {
  vec3 a = abs(q);
  vec2 uv; float face;
  if (a.x >= a.y && a.x >= a.z) { uv = q.yz / a.x; face = sign(q.x); }
  else if (a.y >= a.z) { uv = q.xz / a.y; face = 2.0 + sign(q.y); }
  else { uv = q.xy / a.z; face = 4.0 + sign(q.z); }
  return glitter(uv, face, 300.0) * glitter(uv, face, 900.0);
}
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
  if (uDetail > 0.0) totalEmissiveRadiance *= mix(1.0, cityDetail(q), uDetail);
  // City lights come on across dusk and are off in daylight.
  float sunward = dot(normalize(vWorldNormal), normalize(uSun - vWorldPos));
  totalEmissiveRadiance *= mix(1.0, smoothstep(0.12, -0.18, sunward), uNightOnly);
}`
			);
	};
	material.customProgramCacheKey = () => 'emissive-flicker';
	return { uniforms };
}
