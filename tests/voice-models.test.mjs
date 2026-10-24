import assert from 'node:assert/strict';
import {mkdtempSync, readFileSync, writeFileSync, existsSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import test from 'node:test';
import {selectLatestTtsModel, assertCurrentModel, currentTtsModel, SCRIBE_MODEL} from '../skills/motion-film-voice/scripts/models.mjs';
import {generateVoice, toWords} from '../skills/motion-film-voice/scripts/vo.mjs';

const models = [
	{model_id: 'eleven_multilingual_v2', can_do_text_to_speech: true},
	{model_id: 'eleven_flash_v2_5', can_do_text_to_speech: true},
	{model_id: 'eleven_v3', can_do_text_to_speech: true},
	{model_id: 'eleven_v3_conversational', can_do_text_to_speech: true},
];
const alignment = {characters: [...'Hello'], character_start_times_seconds: [0, .1, .2, .3, .4],
	character_end_times_seconds: [.1, .2, .3, .4, .5]};
const speech = {audio_base64: Buffer.from('ID3-fixture').toString('base64'), alignment};

function fixture(t, overrides = {}) {
	const directory = mkdtempSync(join(tmpdir(), 'motion-voice-test-'));
	t.after(() => rmSync(directory, {recursive: true, force: true}));
	const scriptPath = join(directory, 'script.json');
	writeFileSync(scriptPath, JSON.stringify({voiceId: 'voice-test', modelId: 'latest',
		lines: [{id: 'V1', text: 'Hello'}], ...overrides}));
	return {directory, scriptPath};
}

test('select current flagship, not old, flash, conversational or voice-conversion models', () => {
	assert.equal(selectLatestTtsModel(models).model_id, 'eleven_v3');
	assert.equal(SCRIBE_MODEL, 'scribe_v2');
	assert.throws(() => selectLatestTtsModel(models.filter((m) => m.model_id !== 'eleven_v3')), /refusing v2 fallback/);
	assert.throws(() => selectLatestTtsModel({models}), /not an array/);
});

test('discover a future flagship numerically, not by cached default or catalogue order', () => {
	const newer = [...models, {model_id: 'eleven_v4', can_do_text_to_speech: true},
		{model_id: 'eleven_v10', can_do_text_to_speech: true},
		{model_id: 'eleven_v99', can_do_text_to_speech: false}];
	assert.equal(selectLatestTtsModel(newer).model_id, 'eleven_v10');
	assert.throws(() => assertCurrentModel('eleven_v3', selectLatestTtsModel(newer)), /not the current flagship/);
});

test('accept latest, omitted or current explicit model; reject stale overrides', () => {
	const model = selectLatestTtsModel(models);
	for (const requested of [undefined, null, 'latest', 'eleven_v3']) {
		assert.equal(assertCurrentModel(requested, model), 'eleven_v3');
	}
	for (const stale of ['eleven_multilingual_v2', 'eleven_flash_v2_5', '']) {
		assert.throws(() => assertCurrentModel(stale, model), /no silent downgrade/);
	}
});

test('failed catalogue lookup stops instead of trusting an offline fallback', async () => {
	await assert.rejects(currentTtsModel({fetchImpl: async () => new Response('Unavailable', {status: 503})}), /preflight failed: 503/);
	await assert.rejects(currentTtsModel({fetchImpl: async () => {throw new Error('offline');}}), /offline/);
});

test('generation sends explicit current model and records provenance', async (t) => {
	const {directory, scriptPath} = fixture(t, {modelId: undefined});
	const calls = [];
	await generateVoice({scriptPath, key: 'test-key', fetchImpl: async (url, options) => {
		calls.push({url, options});
		return Response.json(url.endsWith('/models') ? models : speech);
	}});
	assert.equal(calls.length, 2);
	assert.equal(JSON.parse(calls[1].options.body).model_id, 'eleven_v3');
	const take = JSON.parse(readFileSync(join(directory, 'V1.json')));
	assert.equal(take.modelId, 'eleven_v3');
	assert.equal(take.voiceId, 'voice-test');
	assert.equal(take.words[0].w, 'Hello');
	assert.ok(take.generatedAt);
	assert.ok(existsSync(join(directory, 'V1.mp3')));
});

test('stale script or later line override fails before any paid request', async (t) => {
	for (const overrides of [
		{modelId: 'eleven_multilingual_v2'},
		{lines: [{id: 'V1', text: 'Hello'}, {id: 'V2', text: 'Old', modelId: 'eleven_multilingual_v2'}]},
	]) {
		const {directory, scriptPath} = fixture(t, overrides);
		let paid = 0;
		await assert.rejects(generateVoice({scriptPath, fetchImpl: async (url) => {
			if (!url.endsWith('/models')) paid++;
			return Response.json(models);
		}}), /not the current flagship/);
		assert.equal(paid, 0);
		assert.equal(existsSync(join(directory, 'V1.mp3')), false);
	}
});

test('provider error never retries another model or reports success', async (t) => {
	const {directory, scriptPath} = fixture(t);
	let paid = 0;
	await assert.rejects(generateVoice({scriptPath, fetchImpl: async (url) => {
		if (url.endsWith('/models')) return Response.json(models);
		paid++;
		return new Response('unsupported voice', {status: 400});
	}}), /400 unsupported voice.*no model fallback/);
	assert.equal(paid, 1);
	assert.equal(existsSync(join(directory, 'V1.mp3')), false);
});

test('untimed or empty response cannot leave audio that a rerun would skip', async (t) => {
	for (const response of [{...speech, alignment: null}, {...speech, audio_base64: ''}]) {
		const {directory, scriptPath} = fixture(t);
		await assert.rejects(generateVoice({scriptPath, fetchImpl: async (url) =>
			Response.json(url.endsWith('/models') ? models : response)}));
		assert.equal(existsSync(join(directory, 'V1.mp3')), false);
	}
});

test('existing takes remain untouched without explicit line selection', async (t) => {
	const {directory, scriptPath} = fixture(t);
	writeFileSync(join(directory, 'V1.mp3'), 'shipped');
	writeFileSync(join(directory, 'V1.json'), '{"modelId":"old-shipped-take"}');
	await generateVoice({scriptPath, fetchImpl: async () => {throw new Error('must not call API');}});
	assert.equal(readFileSync(join(directory, 'V1.mp3'), 'utf8'), 'shipped');
});

test('missing timing for existing audio is an error, never automatic regeneration', async (t) => {
	const {directory, scriptPath} = fixture(t);
	writeFileSync(join(directory, 'V1.mp3'), 'shipped');
	await assert.rejects(generateVoice({scriptPath, fetchImpl: async () => {throw new Error('must not call API');}}), /restore its alignment/);
});

test('unknown line selection is an error', async (t) => {
	const {scriptPath} = fixture(t);
	await assert.rejects(generateVoice({scriptPath, ids: ['missing']}), /Unknown voice line/);
});

test('alignment validation rejects missing or malformed timing arrays', () => {
	for (const invalid of [null, {}, {...alignment, character_end_times_seconds: []},
		{...alignment, character_end_times_seconds: [-1, .2, .3, .4, .5]}]) {
		assert.throws(() => toWords(invalid));
	}
});
