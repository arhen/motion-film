// ElevenLabs API key lookup: ELEVENLABS_API_KEY, then ./.env in the working directory, then ~/.config/elevenlabs.key.
import {existsSync, readFileSync} from 'node:fs';
import {homedir} from 'node:os';
import {join} from 'node:path';

export function elevenLabsKey() {
	if (process.env.ELEVENLABS_API_KEY) return process.env.ELEVENLABS_API_KEY.trim();
	const env = join(process.cwd(), '.env');
	if (existsSync(env)) {
		const m = readFileSync(env, 'utf8').match(/^\s*ELEVENLABS_API_KEY\s*=\s*["']?([^"'\s#]+)/m);
		if (m) return m[1];
	}
	const file = join(homedir(), '.config/elevenlabs.key');
	if (existsSync(file)) return readFileSync(file, 'utf8').trim();
	console.error('No ElevenLabs key: set ELEVENLABS_API_KEY, add it to ./.env, or put it in ~/.config/elevenlabs.key.');
	process.exit(1);
}
