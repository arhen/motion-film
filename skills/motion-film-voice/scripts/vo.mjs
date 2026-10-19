// Voice-over takes with word timings (ElevenLabs text to speech with timestamps): one mp3 and one timing JSON per line.
//   VO_SCRIPT=vo/film/script.json [VO_AUDIO_DIR=…] [VO_ALIGN_DIR=…] node vo.mjs [line ids…]
// Without ids, generates only lines whose mp3 is missing. Audio and timing dirs default to the script's folder.
import {readFileSync, writeFileSync, existsSync, mkdirSync} from 'node:fs';
import {dirname, join, resolve} from 'node:path';
import {elevenLabsKey} from './key.mjs';

const scriptPath = resolve(process.env.VO_SCRIPT ?? 'vo/script.json');
const audioDir = resolve(process.env.VO_AUDIO_DIR ?? dirname(scriptPath));
const alignDir = resolve(process.env.VO_ALIGN_DIR ?? dirname(scriptPath));
const {voiceId, modelId, settings = {}, lines} = JSON.parse(readFileSync(scriptPath, 'utf8'));
const only = process.argv.slice(2);
const key = elevenLabsKey();
mkdirSync(audioDir, {recursive: true});
mkdirSync(alignDir, {recursive: true});

/** Groups aligned characters into words, skipping [direction tag] characters and whitespace. */
const toWords = (a) => {
	const words = [];
	let cur = null;
	let inTag = false;
	a.characters.forEach((ch, k) => {
		if (ch === '[') inTag = true;
		if (inTag) {
			if (ch === ']') inTag = false;
			cur = null;
			return;
		}
		if (/\s/.test(ch)) {
			cur = null;
			return;
		}
		if (!cur) words.push((cur = {w: '', start: a.character_start_times_seconds[k], end: 0}));
		cur.w += ch;
		cur.end = a.character_end_times_seconds[k];
	});
	return words;
};

for (const [i, line] of lines.entries()) {
	if (only.length ? !only.includes(line.id) : existsSync(join(audioDir, `${line.id}.mp3`))) continue;
	const res = await fetch(
		`https://api.elevenlabs.io/v1/text-to-speech/${line.voiceId ?? voiceId}/with-timestamps?output_format=mp3_44100_128`,
		{
			method: 'POST',
			headers: {'xi-api-key': key, 'content-type': 'application/json'},
			body: JSON.stringify({
				text: (line.direction ?? '') + line.text,
				model_id: line.modelId ?? modelId,
				voice_settings: {...settings, ...line.settings},
				...(line.context === false ? {} : {previous_text: lines[i - 1]?.text, next_text: lines[i + 1]?.text}),
				seed: line.seed ?? 7,
			}),
		},
	);
	if (!res.ok) {
		console.error(`${line.id}: ${res.status} ${await res.text()}`);
		continue;
	}
	const body = await res.json();
	writeFileSync(join(audioDir, `${line.id}.mp3`), Buffer.from(body.audio_base64, 'base64'));
	const words = toWords(body.alignment);
	writeFileSync(join(alignDir, `${line.id}.json`), JSON.stringify({text: line.text, words}, null, 1));
	console.log(line.id, `${words.at(-1)?.end.toFixed(2)}s`, words.map((w) => `${w.w}@${w.start.toFixed(2)}`).join(' '));
}
