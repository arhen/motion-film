// Word-timed transcript of a recording or a video, in the clock's line format {text, words: [{w, start, end}]},
// the same format vo.mjs writes, so captions, cues, the mixer and sync.py read it unchanged.
//   node transcribe.mjs <media> <out.json> [--engine whisper|scribe] [--model base] [--lang en] [--no-align]
// whisper (default): local and free. Needs `npx remotion add @remotion/install-whisper-cpp` in the video project;
//   the first run builds whisper.cpp into ./whisper.cpp (or $WHISPER_DIR) and downloads the model.
//   Models: tiny, base, small, medium, large-v3-turbo; the .en variants are English only and more accurate for it.
// scribe: ElevenLabs speech-to-text. Paid, needs a key; often better for names and non-English speech.
// --lang: a code or a name (en, id, English, Indonesian); omit it to detect the language.
import {execFileSync} from 'node:child_process';
import {mkdtempSync, readFileSync, rmSync, writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {basename, join, resolve} from 'node:path';

const args = process.argv.slice(2);
const take = (flag, fallback) => {
	const i = args.indexOf(flag);
	return i >= 0 ? args.splice(i, 2)[1] : fallback;
};
const engine = take('--engine', 'whisper');
const model = take('--model', 'base');
const lang = take('--lang', null);
const [media, out] = args;
if (!media || !out) {
	console.error('usage: node transcribe.mjs <media> <out.json> [--engine whisper|scribe] [--model base] [--lang en]');
	process.exit(1);
}

const tmp = mkdtempSync(join(tmpdir(), 'transcribe-'));
const wav = join(tmp, 'audio.wav');
execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', media, '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', wav]);

let words = [];
if (engine === 'scribe') {
	const {elevenLabsKey} = await import('./key.mjs');
	const form = new FormData();
	form.append('model_id', 'scribe_v1');
	if (lang) form.append('language_code', lang);
	form.append('timestamps_granularity', 'word');
	form.append('tag_audio_events', 'false');
	form.append('file', new Blob([readFileSync(wav)]), basename(wav));
	const res = await fetch('https://api.elevenlabs.io/v1/speech-to-text', {method: 'POST', headers: {'xi-api-key': elevenLabsKey()}, body: form});
	if (!res.ok) {
		console.error(`${res.status} ${await res.text()}`);
		process.exit(1);
	}
	const body = await res.json();
	words = (body.words ?? []).filter((w) => w.type === 'word').map((w) => ({w: w.text, start: w.start, end: w.end}));
} else {
	const whisper = await import('@remotion/install-whisper-cpp');
	const to = resolve(process.env.WHISPER_DIR ?? 'whisper.cpp');
	const version = '1.5.5';
	await whisper.installWhisperCpp({to, version, printOutput: false});
	await whisper.downloadWhisperModel({model, folder: to, printOutput: false});
	const output = await whisper.transcribe({model, whisperPath: to, whisperCppVersion: version, inputPath: wav, tokenLevelTimestamps: true, language: lang, printOutput: false});
	// Tokens can be parts of a word; a token that starts with a space begins a new word.
	for (const c of whisper.toCaptions({whisperCppOutput: output}).captions) {
		const text = c.text;
		if (!text.trim()) continue;
		if (/^\s/.test(text) || !words.length) words.push({w: text.trim(), start: c.startMs / 1000, end: c.endMs / 1000});
		else {
			const last = words[words.length - 1];
			last.w += text;
			last.end = c.endMs / 1000;
		}
	}
}
if (engine === 'whisper' && !process.argv.includes('--no-align')) words = alignToAudio(words, wav);
rmSync(tmp, {recursive: true, force: true});

// Whisper's word times are spread evenly and ignore pauses. Re-time them against the audio: find the speech
// stretches, put each pause at the nearest word boundary (preferring one after punctuation), then spread each
// stretch's words by their length. Good for captions and cut lists; use scribe when word-exact timing matters.
function alignToAudio(ws, wavPath) {
	if (ws.length < 2) return ws;
	const raw = join(tmp, 'audio.s16');
	execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', wavPath, '-f', 's16le', '-ac', '1', '-ar', '16000', raw]);
	const buf = readFileSync(raw);
	const pcm = new Int16Array(buf.buffer, buf.byteOffset, Math.floor(buf.length / 2));
	const hop = 160;
	const db = [];
	for (let i = 0; i + hop <= pcm.length; i += hop) {
		let s = 0;
		for (let k = i; k < i + hop; k++) s += (pcm[k] / 32768) ** 2;
		db.push(10 * Math.log10(s / hop + 1e-12));
	}
	const sorted = [...db].sort((a, b) => a - b);
	const th = Math.min(-35, Math.max(-70, sorted[Math.floor(sorted.length * 0.9)] - 30));
	const total = (db.length * hop) / 16000;
	const quiet = [];
	let q0 = null;
	db.concat([0]).forEach((v, i) => {
		if (v < th && q0 === null) q0 = i;
		else if (v >= th && q0 !== null) {
			if (((i - q0) * hop) / 16000 >= 0.3) quiet.push([(q0 * hop) / 16000, (i * hop) / 16000]);
			q0 = null;
		}
	});
	const regions = [];
	let t0 = 0;
	for (const [a, b] of quiet) {
		if (a - t0 > 0.1) regions.push([t0, a]);
		t0 = b;
	}
	if (total - t0 > 0.1) regions.push([t0, total]);
	if (!regions.length) return ws;
	// Boundary k sits between word k-1 and word k; choose one per pause between regions, in order.
	const bonus = (w) => (/[.?!]$/.test(w) ? 0.5 : /[,;:]$/.test(w) ? 0.25 : 0);
	const cuts = [];
	let prev = 0;
	for (let r = 1; r < regions.length; r++) {
		const mid = (regions[r - 1][1] + regions[r][0]) / 2;
		let best = null;
		for (let k = prev + 1; k <= ws.length - (regions.length - r); k++) {
			const cost = Math.abs(ws[k].start - mid) - bonus(ws[k - 1].w);
			if (best === null || cost < best.cost) best = {k, cost};
		}
		if (!best) break;
		cuts.push(best.k);
		prev = best.k;
	}
	const bounds = [0, ...cuts, ws.length];
	const outWords = [];
	regions.slice(0, bounds.length - 1).forEach(([a, b], r) => {
		const group = ws.slice(bounds[r], bounds[r + 1]);
		const chars = group.reduce((n, w) => n + w.w.length + 1, 0);
		let t = a;
		for (const w of group) {
			const d = ((b - a) * (w.w.length + 1)) / chars;
			outWords.push({w: w.w, start: t, end: t + d * 0.92});
			t += d;
		}
	});
	return outWords;
}

const round = (v) => Math.round(v * 1000) / 1000;
words = words.map((w) => ({w: w.w, start: round(w.start), end: round(Math.max(w.end, w.start))}));
const text = words.map((w) => w.w).join(' ');
writeFileSync(out, JSON.stringify({text, words, source: basename(media), engine}, null, 1));
const last = words.at(-1);
console.log(`${out}: ${words.length} words, ${last ? last.end.toFixed(2) : 0} s (${engine}${engine === 'whisper' ? ' ' + model : ''})`);
console.log(text.slice(0, 240) + (text.length > 240 ? ' ...' : ''));
