import React, {useEffect, useState} from 'react';
import {cancelRender, continueRender, delayRender, staticFile} from 'remotion';

/*
 * Holds rendering until the brand fonts are loaded and the image assets are decoded, so the
 * first frame and every text measurement use real metrics. Edit FONTS and PRELOAD per project.
 */
const FONTS: {family: string; file: string; weight: string}[] = [
	{family: 'Display Face', file: 'fonts/Display-Variable.woff2', weight: '300 700'},
	{family: 'UI Face', file: 'fonts/UI-Variable.woff2', weight: '200 1000'},
	{family: 'Mono Face', file: 'fonts/Mono-Variable.woff2', weight: '100 900'},
];
const PRELOAD: string[] = [
	// staticFile('logos/partner.svg'), imported SVG/PNG module URLs, …
];

let loaded: Promise<void> | null = null;

const load = () => {
	const face = (f: (typeof FONTS)[number]) =>
		new FontFace(f.family, `url(${staticFile(f.file)}) format('woff2')`, {weight: f.weight}).load().catch(() => {
			throw new Error(`font failed to load: public/${f.file}`);
		});
	loaded ??= Promise.all(FONTS.map(face)).then(async (faces) => {
		faces.forEach((face) => document.fonts.add(face));
		await Promise.all(
			PRELOAD.map(
				(src) =>
					new Promise<void>((done) => {
						const img = new Image();
						img.onload = () => img.decode().then(done, done);
						img.onerror = () => done();
						img.src = src;
					}),
			),
		);
	});
	return loaded;
};

export const FontsGate: React.FC<{children: React.ReactNode}> = ({children}) => {
	const [handle] = useState(() => delayRender('fonts'));
	const [ready, setReady] = useState(false);
	useEffect(() => {
		load().then(() => setReady(true), cancelRender);
	}, []);
	useEffect(() => {
		if (ready) continueRender(handle);
	}, [ready, handle]);
	return ready ? <>{children}</> : null;
};

let ctx: CanvasRenderingContext2D | null = null;
const cache = new Map<string, number>();

/** Text width in px with the loaded font; tracking in em. Call only inside the gate. */
export const measure = (text: string, size: number, weight: number, family: string, tracking = 0) => {
	const key = `${text}|${size}|${weight}|${family}|${tracking}`;
	const hit = cache.get(key);
	if (hit !== undefined) return hit;
	ctx ??= document.createElement('canvas').getContext('2d')!;
	ctx.font = `${weight} ${size}px "${family}"`;
	const w = ctx.measureText(text).width + tracking * size * text.length;
	cache.set(key, w);
	return w;
};
