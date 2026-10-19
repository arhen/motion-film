/*
 * Clock access for one video. The clock JSON is the single source of timing for picture,
 * voice-over and score. Voice entries:
 *   {id, at}                 line starts at `at` s
 *   {id, alignWord, at}      word `alignWord` starts at `at` s
 *   {id, alignWord, beat}    word `alignWord` lands on `beat` (needs bpm)
 * Beat b is at beatOffset + b × 60 / bpm seconds; beatOffset (default 0) is set by snap.py for a supplied track.
 * Word timing JSON per line: {text, words: [{w, start, end}]} (written by vo.mjs).
 */
import clock from '../../clock.json';
import V1 from '../../vo/film/V1.json';
import V2 from '../../vo/film/V2.json';
import V3 from '../../vo/film/V3.json';
import V4 from '../../vo/film/V4.json';

type Word = {w: string; start: number; end: number};
type Line = {text: string; words: Word[]};
type VoEntry = {id: string; at?: number; beat?: number; alignWord?: number};

const LINES: Record<string, Line> = {V1, V2, V3, V4};

export const FPS = clock.fps;
export const SECONDS = clock.seconds;
export const DURATION = Math.round(clock.seconds * clock.fps);
export const cue = clock.cues;
const grid = clock as {bpm?: number; beatOffset?: number};
export const beat = (b: number) => (grid.beatOffset ?? 0) + (b * 60) / grid.bpm!;

const start = (e: VoEntry, words: Word[]) => {
	const anchor = e.beat !== undefined ? beat(e.beat) : e.at ?? 0;
	return e.alignWord !== undefined ? anchor - words[e.alignWord].start : anchor;
};

/** Absolute word times per voice line, in clock order. */
export const VO = (clock.vo as VoEntry[]).map((e) => {
	const line = LINES[e.id];
	if (!line) throw new Error(`clock.json lists ${e.id}; import vo/film/${e.id}.json into LINES`);
	const s = start(e, line.words);
	return {id: e.id, text: line.text, words: line.words.map((w) => ({w: w.w, start: s + w.start, end: s + w.end}))};
});

/** Start time (s) of word `word` in voice line `line` (0-based). */
export const wordAt = (line: number, word: number) => VO[line].words[word].start;
