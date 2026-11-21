// Shaders for the two suns: an animated, granulated surface and a soft corona around it.
// Each sun's character (lore: the Yellow Sun is "refining fire, with the heat of purity", the
// Red Sun "wild fire, burning with the heat of passion") is a set of SunLook values.

import * as THREE from 'three';

export type SunLook = {
	/** Hottest, brightest surface colour. */
	core: [number, number, number];
	/** Typical surface colour. */
	mid: [number, number, number];
	/** Darkest colour: cool lanes between cells, and the darkened limb. */
	dark: [number, number, number];
	/** Glow colour of the corona. */
	glow: [number, number, number];
	/** How restless the surface is: contrast and size of the churning, 0 calm … 2 wild. */
	turbulence: number;
	/** How fast the surface churns. */
	speed: number;
	/** Strength of flares and streamers in the corona, 0 … 1. */
	flares: number;
};

export const YELLOW_SUN: SunLook = {
	core: [1.0, 0.98, 0.88],
	mid: [1.0, 0.83, 0.42],
	dark: [0.92, 0.52, 0.16],
	glow: [1.0, 0.82, 0.45],
	turbulence: 0.55,
	speed: 0.025,
	flares: 0.25
};

export const RED_SUN: SunLook = {
	core: [1.0, 0.62, 0.3],
	mid: [0.95, 0.24, 0.06],
	dark: [0.42, 0.04, 0.02],
	glow: [1.0, 0.28, 0.08],
	turbulence: 1.5,
	speed: 0.07,
	flares: 0.9
};

// 3D simplex noise (Ashima Arts / Stefan Gustavson, MIT licence).
const NOISE = /* glsl */ `
vec3 mod289(vec3 x){return x-floor(x*(1.0/289.0))*289.0;}
vec4 mod289(vec4 x){return x-floor(x*(1.0/289.0))*289.0;}
vec4 permute(vec4 x){return mod289(((x*34.0)+10.0)*x);}
vec4 taylorInvSqrt(vec4 r){return 1.79284291400159-0.85373472095314*r;}
float snoise(vec3 v){
  const vec2 C=vec2(1.0/6.0,1.0/3.0); const vec4 D=vec4(0.0,0.5,1.0,2.0);
  vec3 i=floor(v+dot(v,C.yyy)); vec3 x0=v-i+dot(i,C.xxx);
  vec3 g=step(x0.yzx,x0.xyz); vec3 l=1.0-g; vec3 i1=min(g.xyz,l.zxy); vec3 i2=max(g.xyz,l.zxy);
  vec3 x1=x0-i1+C.xxx; vec3 x2=x0-i2+C.yyy; vec3 x3=x0-D.yyy;
  i=mod289(i);
  vec4 p=permute(permute(permute(i.z+vec4(0.0,i1.z,i2.z,1.0))+i.y+vec4(0.0,i1.y,i2.y,1.0))+i.x+vec4(0.0,i1.x,i2.x,1.0));
  float n_=0.142857142857; vec3 ns=n_*D.wyz-D.xzx;
  vec4 j=p-49.0*floor(p*ns.z*ns.z); vec4 x_=floor(j*ns.z); vec4 y_=floor(j-7.0*x_);
  vec4 x=x_*ns.x+ns.yyyy; vec4 y=y_*ns.x+ns.yyyy; vec4 h=1.0-abs(x)-abs(y);
  vec4 b0=vec4(x.xy,y.xy); vec4 b1=vec4(x.zw,y.zw);
  vec4 s0=floor(b0)*2.0+1.0; vec4 s1=floor(b1)*2.0+1.0; vec4 sh=-step(h,vec4(0.0));
  vec4 a0=b0.xzyw+s0.xzyw*sh.xxyy; vec4 a1=b1.xzyw+s1.xzyw*sh.zzww;
  vec3 p0=vec3(a0.xy,h.x); vec3 p1=vec3(a0.zw,h.y); vec3 p2=vec3(a1.xy,h.z); vec3 p3=vec3(a1.zw,h.w);
  vec4 norm=taylorInvSqrt(vec4(dot(p0,p0),dot(p1,p1),dot(p2,p2),dot(p3,p3)));
  p0*=norm.x; p1*=norm.y; p2*=norm.z; p3*=norm.w;
  vec4 m=max(0.5-vec4(dot(x0,x0),dot(x1,x1),dot(x2,x2),dot(x3,x3)),0.0); m=m*m;
  return 105.0*dot(m*m,vec4(dot(p0,x0),dot(p1,x1),dot(p2,x2),dot(p3,x3)));
}
float fbm(vec3 p){float s=0.0,a=0.5;for(int i=0;i<5;i++){s+=a*snoise(p);p*=2.03;a*=0.5;}return s;}
`;

const surfaceVertex = /* glsl */ `
varying vec3 vPos;
varying vec3 vNormal;
varying vec3 vView;
void main(){
  vPos = position;
  vec4 mv = modelViewMatrix * vec4(position, 1.0);
  vNormal = normalize(normalMatrix * normal);
  vView = normalize(-mv.xyz);
  gl_Position = projectionMatrix * mv;
}`;

const surfaceFragment = /* glsl */ `
uniform float uTime; uniform float uTurb; uniform float uSpeed;
uniform vec3 uCore; uniform vec3 uMid; uniform vec3 uDark;
varying vec3 vPos; varying vec3 vNormal; varying vec3 vView;
${NOISE}
void main(){
  vec3 p = normalize(vPos);
  float t = uTime * uSpeed;
  // Large slow convection, warped; small granules riding on it.
  vec3 warp = vec3(fbm(p*2.0+t), fbm(p*2.0-t+3.1), fbm(p*2.0+t*0.7+7.4));
  float big = fbm(p*3.0 + warp*(0.6+0.5*uTurb) + t*0.5);
  float gran = 1.0 - abs(snoise(p*28.0 + warp*2.0 + t*3.0));
  float v = 0.5 + 0.5*big*(0.6+0.4*uTurb) + 0.18*(gran-0.5)*(1.0+uTurb*0.5);
  v = clamp(v, 0.0, 1.0);
  vec3 col = v < 0.5 ? mix(uDark, uMid, v*2.0) : mix(uMid, uCore, (v-0.5)*2.0);
  // Limb darkening: the edge of the disc is cooler and dimmer.
  float mu = clamp(dot(normalize(vNormal), normalize(vView)), 0.0, 1.0);
  col = mix(uDark*0.8, col, pow(mu, 0.35));
  col *= 0.75 + 0.45*pow(mu, 0.6);
  gl_FragColor = vec4(col, 1.0);
}`;

const coronaVertex = /* glsl */ `
varying vec2 vUv;
void main(){
  vUv = uv*2.0-1.0;
  // Billboard: keep the quad facing the camera.
  vec4 mv = modelViewMatrix * vec4(0.0,0.0,0.0,1.0);
  vec3 scale = vec3(length(modelMatrix[0].xyz), length(modelMatrix[1].xyz), 1.0);
  mv.xy += position.xy * scale.xy;
  gl_Position = projectionMatrix * mv;
}`;

const coronaFragment = /* glsl */ `
uniform float uTime; uniform float uSpeed; uniform float uFlares; uniform float uInner;
uniform vec3 uGlow;
varying vec2 vUv;
${NOISE}
void main(){
  float r = length(vUv);
  if (r > 1.0) discard;
  float a = atan(vUv.y, vUv.x);
  float t = uTime * uSpeed;
  // Radial falloff from the sun's edge (uInner, in quad units) outwards.
  float d = max(r - uInner, 0.0) / (1.0 - uInner);
  float glow = exp(-d*7.0) * 0.9 + exp(-d*2.5) * 0.25;
  // Streamers and flares: noise around the rim, stretched outwards.
  vec3 q = vec3(cos(a)*2.0, sin(a)*2.0, d*1.5 - t*2.0);
  float streak = smoothstep(0.1, 0.8, fbm(q*1.7 + t)) * exp(-d*3.5);
  float flare = pow(max(snoise(vec3(cos(a)*3.0, sin(a)*3.0, t*1.5)), 0.0), 3.0) * exp(-d*4.0);
  float k = glow + uFlares*(0.8*streak + 1.6*flare);
  k *= smoothstep(1.0, 0.85, r);
  gl_FragColor = vec4(uGlow * k, k);
}`;

export function sunSurfaceMaterial(look: SunLook): THREE.ShaderMaterial {
	return new THREE.ShaderMaterial({
		vertexShader: surfaceVertex,
		fragmentShader: surfaceFragment,
		uniforms: {
			uTime: { value: 0 },
			uTurb: { value: look.turbulence },
			uSpeed: { value: look.speed },
			uCore: { value: new THREE.Color(...look.core) },
			uMid: { value: new THREE.Color(...look.mid) },
			uDark: { value: new THREE.Color(...look.dark) }
		}
	});
}

/** Corona drawn on a camera-facing quad `size` times the sun's radius across. */
export function sunCoronaMaterial(look: SunLook, size: number): THREE.ShaderMaterial {
	return new THREE.ShaderMaterial({
		vertexShader: coronaVertex,
		fragmentShader: coronaFragment,
		transparent: true,
		depthWrite: false,
		blending: THREE.AdditiveBlending,
		uniforms: {
			uTime: { value: 0 },
			uSpeed: { value: look.speed },
			uFlares: { value: look.flares },
			uInner: { value: 1 / size },
			uGlow: { value: new THREE.Color(...look.glow) }
		}
	});
}
