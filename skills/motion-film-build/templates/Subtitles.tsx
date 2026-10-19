import React from 'react';
import {useVideoConfig} from 'remotion';
import {clamp, ease, prS, spS, useSec} from './anim';

type Word = {w: string; start: number; end: number};

/*
 * Captions = the voice-over, revealed word by word. Lines are split into chunks of at most `max`
 * characters, at punctuation where possible; short chunks merge back; chunks play strictly in sequence.
 * `lines` holds absolute word times in seconds (see clock.ts VO).
 * highlight: a colour for the word being spoken (short-video caption style); omit it for calm captions.
 * Size, position and chunk length follow the format: landscape sits low in the frame; vertical sits
 * above the band that short-video apps cover with their own interface (see motion-film-system §6).
 */
export const chunk = (lines: Word[][], max = 44) => {
	const out: Word[][] = [];
	const len = (ws: Word[]) => ws.map((w) => w.w).join(' ').length;
	for (const words of lines) {
		let cur: Word[] = [];
		for (const w of words) {
			if (cur.length && len([...cur, w]) > max) {
				out.push(cur);
				cur = [];
			}
			cur.push(w);
			if (/[,.:;?!]$/.test(w.w) && len(cur) >= max * 0.4) {
				out.push(cur);
				cur = [];
			}
		}
		if (cur.length) out.push(cur);
	}
	for (let i = out.length - 1; i > 0; i--) {
		const c = out[i];
		if (c[c.length - 1].end - c[0].start < 0.9 && len(out[i - 1]) + 1 + len(c) <= max) {
			out[i - 1] = [...out[i - 1], ...c];
			out.splice(i, 1);
		}
	}
	return out;
};

const Word: React.FC<{at: number; t: number; color?: string; children: string}> = ({at, t, color, children}) => {
	const s = spS(t, at, 2.8, 0.75);
	const lin = clamp((t - at) / 0.16);
	return (
		<span style={{display: 'inline-block', overflow: 'hidden', padding: '0.08em 0.04em 0.16em', margin: '-0.08em -0.04em -0.16em', verticalAlign: 'top'}}>
			<span style={{display: 'inline-block', transform: `translateY(${(1 - s) * 105}%)`, filter: lin < 1 ? `blur(${(1 - lin) * 5}px)` : undefined, opacity: t < at ? 0 : clamp(lin * 2), color}}>{children}</span>
		</span>
	);
};

export const Subtitles: React.FC<{
	lines: Word[][];
	font: string;
	ink: string;
	pill: string;
	border?: string;
	size?: number;
	y?: number;
	until?: number;
	highlight?: string;
}> = ({lines, font, ink, pill, border = 'transparent', size, y, until = Infinity, highlight}) => {
	const {t} = useSec();
	const {width, height} = useVideoConfig();
	const tall = height > width * 1.2;
	const px = size ?? (height >= width ? 72 : 58);
	const top = y ?? height * (tall ? 0.7 : height >= width ? 0.88 : 0.937);
	// Tall frames keep the pill left of the app's button column (x ≥ 87 % of the width).
	const cs = chunk(lines, Math.min(44, Math.floor((width * (tall ? 0.72 : 0.84)) / (px * 0.55))));
	const begin = (k: number) => cs[k][0].start - 0.12;
	const finish = (k: number) => Math.min(k < cs.length - 1 ? begin(k + 1) - 0.08 : Infinity, cs[k][cs[k].length - 1].end + 0.7, until);
	return (
		<>
			{cs.map((c, i) => {
				const start = i > 0 ? Math.max(begin(i), finish(i - 1) + 0.16) : begin(i);
				const end = finish(i);
				if (t < start || t > end + 0.15) return null;
				const inP = prS(t, start, 0.18, ease.outQuint);
				const outP = prS(t, end, 0.15, ease.inOutCubic);
				return (
					<div key={i} style={{position: 'absolute', left: 0, right: 0, top, display: 'flex', justifyContent: 'center', transform: 'translateY(-50%)', opacity: inP * (1 - outP)}}>
						<div style={{fontFamily: font, fontWeight: 500, fontSize: px, letterSpacing: '-0.01em', lineHeight: 1.15, color: ink, background: pill, border: `1px solid ${border}`, borderRadius: 22, padding: '12px 30px 16px', whiteSpace: 'nowrap'}}>
							{c.map((w, k) => (
								<React.Fragment key={k}>
									<Word at={w.start - 0.08} t={t} color={highlight && t >= w.start - 0.04 && t < w.end + 0.06 ? highlight : undefined}>
										{w.w}
									</Word>
									{k < c.length - 1 ? ' ' : ''}
								</React.Fragment>
							))}
						</div>
					</div>
				);
			})}
		</>
	);
};
