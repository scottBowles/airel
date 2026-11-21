// A thin glow around a planet's rim, lit by its sun: brightest on the day side's edge, fading
// across the terminator to nothing on the night side. Put it on a sphere a little larger than
// the planet.

import * as THREE from 'three';

export type AtmosphereLook = {
	/** Rim colour (linear RGB, 0..1). */
	color: [number, number, number];
	/** Overall brightness; 1 is a clear blue-sky world, lower for thin air. */
	strength?: number;
};

export function atmosphereMaterial(look: AtmosphereLook, sun: THREE.Vector3) {
	return new THREE.ShaderMaterial({
		uniforms: {
			uColor: { value: new THREE.Color(...look.color) },
			uStrength: { value: look.strength ?? 1 },
			uSun: { value: sun }
		},
		vertexShader: /* glsl */ `
			varying vec3 vNormal;
			varying vec3 vPos;
			void main() {
				vec4 world = modelMatrix * vec4(position, 1.0);
				vPos = world.xyz;
				vNormal = normalize(mat3(modelMatrix) * normal);
				gl_Position = projectionMatrix * viewMatrix * world;
			}`,
		fragmentShader: /* glsl */ `
			uniform vec3 uColor;
			uniform float uStrength;
			uniform vec3 uSun;
			varying vec3 vNormal;
			varying vec3 vPos;
			void main() {
				vec3 n = normalize(vNormal);
				vec3 v = normalize(cameraPosition - vPos);
				vec3 l = normalize(uSun - vPos);
				float rim = pow(1.0 - max(dot(n, v), 0.0), 3.0);
				float lit = smoothstep(-0.3, 0.45, dot(n, l));
				gl_FragColor = vec4(uColor * rim * lit * uStrength, 1.0);
			}`,
		transparent: true,
		depthWrite: false,
		blending: THREE.AdditiveBlending
	});
}
