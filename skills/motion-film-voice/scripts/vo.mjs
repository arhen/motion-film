import {readFileSync, writeFileSync, existsSync, mkdirSync} from 'node:fs';
import {dirname, join, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {elevenLabsKey} from './key.mjs';
import {assertCurrentModel, currentTtsModel} from './models.mjs';

export function toWords(alignment) {
	if (!alignment || !Array.isArray(alignment.characters) ||
		!Array.isArray(alignment.character_start_times_seconds) ||
		!Array.isArray(alignment.character_end_times_seconds) ||
		alignment.characters.length !== alignment.character_start_times_seconds.length ||
		alignment.characters.length !== alignment.character_end_times_seconds.length) {
		throw new Error('ElevenLabs returned no valid character alignment; refusing an untimed take.');
	}
	const words = [];
	let current = null;
	let inTag = false;
	alignment.characters.forEach((character, index) => {
		const start = alignment.character_start_times_seconds[index];
		const end = alignment.character_end_times_seconds[index];
		if (!Number.isFinite(start) || !Number.isFinite(end) || start < 0 || end < start) {
			throw new Error('ElevenLabs returned invalid character timestamps.');
		}
		if (character === '[') inTag = true;
		if (inTag) {
			if (character === ']') inTag = false;
			current = null;
			return;
		}
		if (/\s/.test(character)) {
			current = null;
			return;
		}
		if (!current) words.push((current = {w: '', start, end}));
		current.w += character;
		current.end = end;
	});
	if (!words.length) throw new Error('ElevenLabs returned no timed words.');
	return words;
}

export async function generateVoice({scriptPath, audioDir = dirname(scriptPath),
	alignDir = dirname(scriptPath), ids = [], key, fetchImpl = fetch}) {
	const {voiceId, modelId, settings = {}, lines} = JSON.parse(readFileSync(scriptPath, 'utf8'));
	if (!Array.isArray(lines)) throw new Error('Voice script must contain a lines array.');
	for (const id of ids) {
		if (!lines.some((line) => line.id === id)) throw new Error(`Unknown voice line: ${id}`);
	}
	const selected = lines.filter((line) => {
		if (ids.length) return ids.includes(line.id);
		if (!existsSync(join(audioDir, `${line.id}.mp3`))) return true;
		if (!existsSync(join(alignDir, `${line.id}.json`))) {
			throw new Error(`${line.id}: audio exists without timing JSON; restore its alignment, do not regenerate a shipped take.`);
		}
		return false;
	});
	if (!selected.length) return [];
	const model = await currentTtsModel({key, fetchImpl});
	assertCurrentModel(modelId, model);
	for (const line of selected) {
		assertCurrentModel(line.modelId, model, line.id);
		if (!(line.voiceId ?? voiceId)) throw new Error(`${line.id}: voiceId is required.`);
		if (!/^[\w-]+$/.test(line.id)) throw new Error('Voice line ids must contain only letters, digits, underscores or hyphens.');
	}
	console.log(`Model: ${model.model_id} (live ElevenLabs catalogue; no older-model fallback)`);
	mkdirSync(audioDir, {recursive: true});
	mkdirSync(alignDir, {recursive: true});
	const completed = [];
	for (const line of selected) {
		const index = lines.indexOf(line);
		const selectedVoice = line.voiceId ?? voiceId;
		const response = await fetchImpl(
			`https://api.elevenlabs.io/v1/text-to-speech/${encodeURIComponent(selectedVoice)}/with-timestamps?output_format=mp3_44100_128`,
			{
				method: 'POST',
				headers: {'xi-api-key': key, 'content-type': 'application/json'},
				signal: AbortSignal.timeout(120_000),
				body: JSON.stringify({
					text: (line.direction ?? '') + line.text,
					model_id: model.model_id,
					voice_settings: {...settings, ...line.settings},
					...(line.context === false ? {} : {previous_text: lines[index - 1]?.text, next_text: lines[index + 1]?.text}),
					seed: line.seed ?? 7,
				}),
			},
		);
		if (!response.ok) throw new Error(`${line.id}: ${response.status} ${await response.text()} (no model fallback)`);
		const body = await response.json();
		const words = toWords(body.normalized_alignment ?? body.alignment);
		if (typeof body.audio_base64 !== 'string') throw new Error(`${line.id}: missing audio_base64.`);
		const audio = Buffer.from(body.audio_base64, 'base64');
		if (!audio.length) throw new Error(`${line.id}: empty audio.`);
		const take = {text: line.text, words, modelId: model.model_id, voiceId: selectedVoice,
			generatedAt: new Date().toISOString()};
		writeFileSync(join(audioDir, `${line.id}.mp3`), audio);
		writeFileSync(join(alignDir, `${line.id}.json`), JSON.stringify(take, null, 1));
		console.log(line.id, model.model_id, `${words.at(-1).end.toFixed(2)}s`,
			words.map((word) => `${word.w}@${word.start.toFixed(2)}`).join(' '));
		completed.push(take);
	}
	return completed;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
	try {
		const scriptPath = resolve(process.env.VO_SCRIPT ?? 'vo/script.json');
		await generateVoice({scriptPath,
			audioDir: resolve(process.env.VO_AUDIO_DIR ?? dirname(scriptPath)),
			alignDir: resolve(process.env.VO_ALIGN_DIR ?? dirname(scriptPath)),
			ids: process.argv.slice(2), key: elevenLabsKey()});
	} catch (error) {
		console.error(error.message);
		process.exitCode = 1;
	}
}
