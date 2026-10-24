// Speech-to-text check (ElevenLabs Scribe): prints each file's transcript and word onsets.
//   node stt.mjs <audio or video files…> [--lang eng] [--json out/stt.json]
// --lang takes an ISO 639-3 code; omit it to let the model detect the language.
import {readFileSync, writeFileSync} from 'node:fs';
import {basename} from 'node:path';
import {elevenLabsKey} from './key.mjs';
import {SCRIBE_MODEL} from './models.mjs';

const args = process.argv.slice(2);
const take = (flag) => {
	const i = args.indexOf(flag);
	return i >= 0 ? args.splice(i, 2)[1] : null;
};
const jsonOut = take('--json');
const lang = take('--lang');
const key = elevenLabsKey();
const results = {};

for (const file of args) {
	const form = new FormData();
	form.append('model_id', SCRIBE_MODEL);
	if (lang) form.append('language_code', lang);
	form.append('timestamps_granularity', 'word');
	form.append('tag_audio_events', 'false');
	form.append('file', new Blob([readFileSync(file)]), basename(file));
	const res = await fetch('https://api.elevenlabs.io/v1/speech-to-text', {method: 'POST', headers: {'xi-api-key': key}, body: form});
	if (!res.ok) {
		console.error(`${file}: ${res.status} ${await res.text()}`);
		process.exitCode = 1;
		continue;
	}
	const body = await res.json();
	const words = (body.words ?? []).filter((w) => w.type === 'word').map((w) => ({w: w.text, start: w.start, end: w.end}));
	results[file] = {text: body.text, language: body.language_code, words};
	console.log(`\n${file} [${body.language_code}]\n${body.text}`);
	console.log(words.map((w) => `${w.w}@${w.start.toFixed(2)}`).join(' '));
}
if (jsonOut) writeFileSync(jsonOut, JSON.stringify(results, null, 1));
