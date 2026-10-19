import React from 'react';
import {AbsoluteFill, OffthreadVideo, Sequence, staticFile, useVideoConfig} from 'remotion';
import {clamp, ease, lerp, prS, useSec} from './anim';

/*
 * Existing footage (a talking head or a screen recording) placed on the clock.
 * segments: the edit in source seconds, played back to back (clock.footage.segments).
 * shots:    camera keyframes in output seconds. scale 1 shows the whole frame; x and y (0 to 1) are the point of
 *           the source kept centred. Use them to reframe 16:9 footage for 9:16, to punch in on a key line, to
 *           zoom to a region of a screen recording, and on alternate sides of a jump cut. ease = 0 cuts.
 * layouts:  where the footage sits: full, split (footage below or right, the explanation in the rest), bubble
 *           (a round inset while the explanation fills the frame), cutaway (footage hidden, its audio continues).
 * The video is muted: its audio reaches the mix through retime.py, so voice, music and SFX share one master.
 */
export type Segment = {in: number; out: number};
export type Shot = {at: number; scale?: number; x?: number; y?: number; ease?: number};
export type Mode = 'full' | 'split' | 'bubble' | 'cutaway';
export type Layout = {at: number; mode: Mode};
type Rect = {x: number; y: number; w: number; h: number; r: number; o: number};

const SWITCH = 0.4;

export const rectFor = (mode: Mode, W: number, H: number): Rect => {
	const tall = H > W;
	if (mode === 'split') return tall ? {x: 0, y: H * 0.45, w: W, h: H * 0.55, r: 0, o: 1} : {x: W * 0.5, y: 0, w: W * 0.5, h: H, r: 0, o: 1};
	if (mode === 'bubble' || mode === 'cutaway') {
		const d = Math.min(W, H) * (tall ? 0.34 : 0.26);
		// Tall frames: top left, under the app's status bar and clear of the right-hand buttons.
		const p = tall ? {x: W * 0.06, y: H * 0.13} : {x: W - d - W * 0.04, y: H - d - H * 0.2};
		return {...p, w: d, h: d, r: d / 2, o: mode === 'cutaway' ? 0 : 1};
	}
	return {x: 0, y: 0, w: W, h: H, r: 0, o: 1};
};

/** The area the explanation may use while a layout is on screen (null: the footage fills the frame). */
export const explainRegion = (mode: Mode, W: number, H: number) => {
	if (mode === 'split') return H > W ? {x: 0, y: 0, w: W, h: H * 0.45} : {x: 0, y: 0, w: W * 0.5, h: H};
	if (mode === 'full') return null;
	return {x: 0, y: 0, w: W, h: H};
};

export const modeAt = (layouts: Layout[], t: number) => [...layouts].reverse().find((l) => t >= l.at)?.mode ?? 'full';

const layoutRect = (layouts: Layout[], t: number, W: number, H: number): Rect => {
	const sorted = [...layouts].sort((a, b) => a.at - b.at);
	const k = sorted.findIndex((l, i) => t >= l.at && (i === sorted.length - 1 || t < sorted[i + 1].at));
	if (k < 0) return rectFor('full', W, H);
	const cur = rectFor(sorted[k].mode, W, H);
	const prev = rectFor(k > 0 ? sorted[k - 1].mode : 'full', W, H);
	const p = k === 0 && sorted[0].at === 0 ? 1 : prS(t, sorted[k].at, SWITCH, ease.inOutCubic);
	return {x: lerp(prev.x, cur.x, p), y: lerp(prev.y, cur.y, p), w: lerp(prev.w, cur.w, p), h: lerp(prev.h, cur.h, p), r: lerp(prev.r, cur.r, p), o: lerp(prev.o, cur.o, p)};
};

const cameraAt = (shots: Shot[], t: number) => {
	const sorted = [...shots].sort((a, b) => a.at - b.at);
	const val = (s?: Shot) => ({scale: s?.scale ?? 1, x: s?.x ?? 0.5, y: s?.y ?? 0.5});
	const k = sorted.findIndex((s, i) => t >= s.at && (i === sorted.length - 1 || t < sorted[i + 1].at));
	if (k < 0) return val(sorted[0]);
	const cur = val(sorted[k]);
	const dur = sorted[k].ease ?? 0;
	if (k === 0 || dur <= 0) return cur;
	const prev = val(sorted[k - 1]);
	const p = prS(t, sorted[k].at, dur, ease.inOutCubic);
	return {scale: lerp(prev.scale, cur.scale, p), x: lerp(prev.x, cur.x, p), y: lerp(prev.y, cur.y, p)};
};

export const Footage: React.FC<{
	src: string;
	segments: Segment[];
	shots?: Shot[];
	layouts?: Layout[];
	source?: {width: number; height: number};
	border?: string;
}> = ({src, segments, shots = [], layouts = [], source = {width: 1920, height: 1080}, border}) => {
	const {t} = useSec();
	const {fps, width: W, height: H} = useVideoConfig();
	const box = layoutRect(layouts, t, W, H);
	const cam = cameraAt(shots, t);
	const cover = Math.max(box.w / source.width, box.h / source.height) * cam.scale;
	const dw = source.width * cover;
	const dh = source.height * cover;
	const left = clamp(box.w / 2 - cam.x * dw, box.w - dw, 0);
	const top = clamp(box.h / 2 - cam.y * dh, box.h - dh, 0);
	let acc = 0;
	const placed = segments.map((s) => {
		const from = Math.round(acc * fps);
		acc += s.out - s.in;
		return {s, from, frames: Math.round(acc * fps) - from};
	});
	if (box.o <= 0.001) return null;
	return (
		<AbsoluteFill style={{pointerEvents: 'none'}}>
			<div style={{position: 'absolute', left: box.x, top: box.y, width: box.w, height: box.h, borderRadius: box.r, overflow: 'hidden', opacity: box.o, boxShadow: border ? `0 0 0 4px ${border}` : undefined}}>
				{placed.map(({s, from, frames}, i) => (
					<Sequence key={i} from={from} durationInFrames={frames}>
						<OffthreadVideo src={staticFile(src)} trimBefore={Math.round(s.in * fps)} muted style={{position: 'absolute', left, top, width: dw, height: dh}} />
					</Sequence>
				))}
			</div>
		</AbsoluteFill>
	);
};
