// ElevenLabs API key lookup: ELEVENLABS_API_KEY, then ./.env in the working directory, then ~/.config/elevenlabs.key.
//   node key.mjs --check   says whether a key exists and where, without printing it (exit 0 found, 1 not found)
import {existsSync, readFileSync} from 'node:fs';
import {homedir} from 'node:os';
import {join, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

export function findKey() {
	if (process.env.ELEVENLABS_API_KEY) return {key: process.env.ELEVENLABS_API_KEY.trim(), from: 'ELEVENLABS_API_KEY'};
	const env = join(process.cwd(), '.env');
	if (existsSync(env)) {
		const m = readFileSync(env, 'utf8').match(/^\s*ELEVENLABS_API_KEY\s*=\s*["']?([^"'\s#]+)/m);
		if (m) return {key: m[1], from: env};
	}
	const file = join(homedir(), '.config/elevenlabs.key');
	if (existsSync(file)) return {key: readFileSync(file, 'utf8').trim(), from: file};
	return null;
}

export function elevenLabsKey() {
	const found = findKey();
	if (found) return found.key;
	console.error('No ElevenLabs key: set ELEVENLABS_API_KEY, add it to ./.env, or put it in ~/.config/elevenlabs.key.');
	process.exit(1);
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url) && process.argv.includes('--check')) {
	const found = findKey();
	console.log(found ? `ElevenLabs key found (${found.from})` : 'No ElevenLabs key found');
	process.exit(found ? 0 : 1);
}
