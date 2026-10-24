import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

export const SCRIBE_MODEL = 'scribe_v2';

export function selectLatestTtsModel(models) {
	if (!Array.isArray(models)) throw new Error('ElevenLabs model catalogue is not an array; refusing to guess a model.');
	const candidates = models.flatMap((model) => {
		const version = /^eleven_v(\d+)(?:_(\d+))?$/.exec(model.model_id);
		return version && Number(version[1]) >= 3 && model.can_do_text_to_speech === true
			? [{...model, version: [Number(version[1]), Number(version[2] ?? 0)]}]
			: [];
	});
	candidates.sort((a, b) => b.version[0] - a.version[0] || b.version[1] - a.version[1]);
	if (!candidates.length) throw new Error('No current ElevenLabs flagship TTS model (v3 or newer) available; refusing v2 fallback.');
	return candidates[0];
}

export async function currentTtsModel({key, fetchImpl = fetch} = {}) {
	const response = await fetchImpl('https://api.elevenlabs.io/v1/models', {
		headers: key ? {'xi-api-key': key} : {},
		signal: AbortSignal.timeout(30_000),
	});
	if (!response.ok) throw new Error(`ElevenLabs model preflight failed: ${response.status} ${await response.text()}`);
	return selectLatestTtsModel(await response.json());
}

export function assertCurrentModel(requested, current, label = 'script') {
	if (requested != null && requested !== 'latest' && requested !== current.model_id) {
		throw new Error(`${label}: modelId "${requested}" is not the current flagship "${current.model_id}". Set modelId to "latest"; no silent downgrade or take regeneration.`);
	}
	return current.model_id;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
	try {
		const {elevenLabsKey} = await import('./key.mjs');
		const model = await currentTtsModel({key: elevenLabsKey()});
		console.log(JSON.stringify({modelId: model.model_id, name: model.name,
			source: 'https://api.elevenlabs.io/v1/models', checkedAt: new Date().toISOString()}, null, 2));
	} catch (error) {
		console.error(error.message);
		process.exitCode = 1;
	}
}
