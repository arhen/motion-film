// Renders review stills from a Remotion composition, bundling once.
//   COMP=<id> [ENTRY=src/index.ts] [OUT=out/qa] [SCALE=0.5] [PREFIX=<id>-] node stills.mjs <frames…>
//   COMP=<id> node stills.mjs --seconds 0 1.5 3.2
// Output names: <PREFIX>f<frame>.jpg (frame zero-padded to 4), so grid.py can label them.
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import {mkdirSync} from 'node:fs';
import {join, resolve} from 'node:path';

const args = process.argv.slice(2);
const seconds = args[0] === '--seconds';
const values = (seconds ? args.slice(1) : args).map(Number);
const id = process.env.COMP;
if (!id || !values.length) {
	console.error('usage: COMP=<id> node stills.mjs <frames…> | --seconds <s…>');
	process.exit(1);
}
const out = resolve(process.env.OUT ?? 'out/qa');
mkdirSync(out, {recursive: true});
const serveUrl = await bundle({entryPoint: resolve(process.env.ENTRY ?? 'src/index.ts')});
const composition = await selectComposition({serveUrl, id});
const prefix = process.env.PREFIX ?? `${id}-`;
for (const v of values) {
	const frame = Math.min(composition.durationInFrames - 1, Math.round(seconds ? v * composition.fps : v));
	const output = join(out, `${prefix}f${String(frame).padStart(4, '0')}.jpg`);
	await renderStill({composition, serveUrl, frame, output, imageFormat: 'jpeg', jpegQuality: 85, scale: Number(process.env.SCALE ?? 0.5)});
	console.log(output);
}
