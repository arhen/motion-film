import React from 'react';
import {Easing, useCurrentFrame, useVideoConfig} from 'remotion';
import {noise2D} from '@remotion/noise';

export const clamp = (v: number, a = 0, b = 1) => Math.min(b, Math.max(a, v));
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

export const ease = {
	outExpo: Easing.bezier(0.16, 1, 0.3, 1),
	outQuint: Easing.bezier(0.22, 1, 0.36, 1),
	outCubic: Easing.bezier(0.33, 1, 0.68, 1),
	inQuint: Easing.bezier(0.64, 0, 0.78, 0),
	inExpo: Easing.bezier(0.7, 0, 0.84, 0),
	inOutCubic: Easing.bezier(0.65, 0, 0.35, 1),
	inOutQuart: Easing.bezier(0.76, 0, 0.24, 1),
	inOutSine: Easing.bezier(0.37, 0, 0.63, 1),
	outBack: Easing.bezier(0.34, 1.56, 0.64, 1), // playful pop on objects; never on text, the logo, opacity or colour
	linear: (x: number) => x,
};

/** Current time in seconds (works at any fps and at sub-frame times under Freeze). */
export const useSec = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	return {t: frame / fps, frame, fps};
};

/** Analytic damped spring 0 → 1 at time `s` seconds. f = natural frequency (Hz), z = damping ratio (z ≥ 1: no overshoot). */
export const springT = (s: number, f = 2.2, z = 0.75) => {
	if (s <= 0) return 0;
	const w = 2 * Math.PI * f;
	if (z < 1) {
		const wd = w * Math.sqrt(1 - z * z);
		return 1 - Math.exp(-z * w * s) * (Math.cos(wd * s) + ((z * w) / wd) * Math.sin(wd * s));
	}
	return 1 - Math.exp(-w * s) * (1 + w * s);
};

/** Spring starting at `start` seconds. */
export const spS = (t: number, start: number, f = 2.2, z = 0.75) => springT(t - start, f, z);

/** A Remotion spring config as natural frequency and damping ratio. Remotion's default (1, 10, 100) is z 0.5: playful, not calm. */
export const fromRemotionSpring = ({mass = 1, damping = 10, stiffness = 100}) => ({f: Math.sqrt(stiffness / mass) / (2 * Math.PI), z: damping / (2 * Math.sqrt(stiffness * mass))});

/** Seconds until the spring stays within `within` of 1: put the settle sound or the next move here. */
export const springSettle = (f = 2.2, z = 0.75, within = 0.03) => {
	let last = 0;
	for (let s = 0; s < 10; s += 0.001) if (Math.abs(1 - springT(s, f, z)) > within) last = s;
	return last;
};

/** Seconds at which the spring moves fastest: put a whoosh peak here. */
export const springPeakSpeed = (f = 2.2, z = 0.75) => {
	let best = 0;
	let top = 0;
	for (let s = 0.001; s < 5; s += 0.001) {
		const v = springT(s, f, z) - springT(s - 0.001, f, z);
		if (v > top) [top, best] = [v, s];
	}
	return best;
};

/** Eased 0 → 1 progress from `start` over `dur` seconds. */
export const prS = (t: number, start: number, dur: number, fn: (x: number) => number = ease.outExpo) => fn(clamp((t - start) / dur));

/** Hit envelope: a short raised-cosine attack (so it never pops in one frame), then an exponential decay of `tau` seconds. */
export const hit = (t: number, start: number, tau = 0.12, attack = 0.03) => {
	const s = t - start;
	if (s < 0) return 0;
	if (s < attack) return 0.5 - 0.5 * Math.cos((Math.PI * s) / attack);
	return Math.exp(-(s - attack) / tau);
};

/** Scale and zoom interpolate in log space, so a zoom feels even from start to end. */
export const logLerp = (a: number, b: number, t: number) => a * Math.pow(b / a, t);

/** How long a line of on-screen text must hold still to be read: about 0.5 s plus 0.28 s per word, at least 1 s. */
export const holdFor = (words: number) => Math.max(1, 0.5 + 0.28 * words);

/** 0 → 1 phase that repeats every `period` seconds; use whole cycles per loop so the seam is invisible. */
export const loopPhase = (t: number, period: number) => (((t % period) + period) % period) / period;

/** Drift that returns to its start every `period` seconds (noise sampled on a circle), for seamless loops. */
export const loopNoise = (seed: string, t: number, period: number, amp = 4, radius = 0.6) => {
	const a = 2 * Math.PI * loopPhase(t, period);
	return noise2D(seed, Math.cos(a) * radius, Math.sin(a) * radius) * amp;
};

/** Squash/stretch pair for a landing at `start` seconds. */
export const squash = (t: number, start: number, amount = 0.25) => {
	const s = t - start;
	if (s < 0) return {sx: 1, sy: 1};
	const k = Math.exp(-s * 9) * Math.cos(s * 2 * Math.PI * 4.2) * amount;
	return {sx: 1 + k, sy: 1 - k};
};

/** Low-amplitude deterministic drift in px. */
export const drift = (t: number, seed: string, amp = 4, speed = 0.25) => ({
	x: noise2D(seed + 'x', t * speed, 0) * amp,
	y: noise2D(seed + 'y', 0, t * speed) * amp,
});

/** Quadratic Bézier point for cursor paths and arcs. */
export const qbez = (p0: number[], p1: number[], p2: number[], k: number) => {
	const u = 1 - k;
	return [u * u * p0[0] + 2 * u * k * p1[0] + k * k * p2[0], u * u * p0[1] + 2 * u * k * p1[1] + k * k * p2[1]];
};

/** Per-instance SVG id: loop overlays and motion-blur samples render extra copies of a scene. */
export const useSvgId = (name: string) => `${name}-${React.useId().replace(/[^a-zA-Z0-9]/g, '')}`;
