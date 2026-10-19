# Build patterns

Compact recipes that have shipped. All take `t` in seconds and read cue times from the clock. Helpers (`prS`, `spS`, `ease`, `clamp`, `lerp`, `qbez`) are in `templates/anim.ts`.

## Word-by-word reveal (kinetic type, captions)

A masked word that rises from below its baseline and de-blurs as it lands, starting slightly before its spoken onset.

```tsx
const Rise = ({at, children}: {at: number; children: React.ReactNode}) => {
	const {t} = useSec();
	const s = spS(t, at, 2.6, 0.75);
	const lin = clamp((t - at) / 0.16);
	return (
		<span style={{display: 'inline-block', overflow: 'hidden', padding: '0.08em 0.04em 0.16em', margin: '-0.08em -0.04em -0.16em', verticalAlign: 'top'}}>
			<span style={{display: 'inline-block', transform: `translateY(${(1 - s) * 105}%)`, filter: lin < 1 ? `blur(${(1 - lin) * 6}px)` : undefined, opacity: t < at ? 0 : clamp(lin * 2)}}>{children}</span>
		</span>
	);
};
// usage: words.map((w) => <Rise at={w.start - 0.08}>{w.w}</Rise>)
```

## Bouncing lead (a dot that lands on each spoken word)

Measure the word positions with the loaded font. Between word onsets, move along a parabola `y = lerp(a, b, k) - h·4k(1-k)` with `h = max(100, distance × 0.4)`. On each landing, apply a squash `sx = 1 + s, sy = 1 - s` where `s = e^(-9τ)·cos(2π·4.2τ)·amount`. The last landing becomes the full stop: a strong close.

## Card → node morph (posts become a map or graph)

Fly the card from its spot to the node over 0.4 s with ease in-out. Scale it toward `nodeDiameter / cardWidth` and fade it out over the last 35 %. The node pops in (`spS(…, 2.4, 0.6)`) when the card arrives, its edge drawing 0.28 s before.

## Iris close or open

Use a full-frame overlay with `radial-gradient(circle at 50% 50%, transparent R px, ground R+1 px)`, where `R` eases in from the frame diagonal to 0. Open with a ground-coloured circle growing from the focus point. Hold a beat of silence in the score at the closed moment.

## Stroke-dash trace reveal (logo or route)

To reveal filled artwork without deforming it, mask it with a wide stroke along its centre line, dashed by progress.

```tsx
<mask id={id} maskUnits="userSpaceOnUse">
	<path d={centreLine} fill="none" stroke="#fff" strokeWidth={traceWidth} pathLength={1} strokeDasharray={`${p} 1`} />
</mask>
<g mask={`url(#${id})`}>{/* the untouched artwork paths */}</g>
```

Routes and lines use the same `pathLength={1}` with `strokeDasharray={`${p} 1`}`. A flowing dash on top (`strokeDasharray="5 22"`, `strokeDashoffset={-t * 90}`) shows the line is live.

## Conic sweep reveal (logo, small sizes)

Use a pie-slice clip path that grows from the mark's starting terminal around its centre: `p × 360°`, eased out, about 0.5 s.

## Text → particles (a word made of dots)

Draw the word on an offscreen canvas in the display font (after fonts load), sample alpha on a staggered grid (step 14-18 px), and cache the points. Map existing particles to points sorted by x so their paths do not cross. Fly them with ease in-out plus a sine lift, and give each particle its own delay. Draw thin lines only between neighbouring samples (distance < 20 px), at low opacity.

## Counting numbers

`Math.round(n × prS(t, at, 0.7, outQuint))`, formatted in the audience's locale. Count only to numbers from the shared dataset.

## 3D assembly (interface builds itself)

Use a container with `perspective: 2400px` and `transform: rotateX(20-28deg) rotateY(-18…-10deg) rotateZ(4-6deg)` plus `preserve-3d`. Each piece enters from `translateZ(+600-700px)` with a spring (`z 0.6-0.8`), staggered on 16ths. Afterwards, drift `rotateY` slowly. When a foreground device arrives, rack-focus the assembly (blur 2-5 px, dim 20-35 %).

## Notification stack

New items drop from the top (`translateY(-150px → 0)`, spring `z 0.6-0.8`); older items move down by `height + gap` with their own spring. Each arrival is pitched one note higher. Land the arrival on the spoken word for that channel.

## Button press and result

- Cursor travel: a quadratic Bézier with ease in-out, arriving 0.15 s before the press.
- Press: scale the button to 0.96 (cursor 0.88) for 0.12 s.
- Ripple: a white circle at 35 % opacity that expands and fades.
- Result: the colour shifts toward the positive colour, the label swaps (old rises out, new rises in), and a check draws (`pathLength=1`, dash by progress). No confetti, no bounce.

## Typed draft

Characters appear at `cps` (90-140 per second, computed with `fps`). Draw the caret between the typed and untyped text, never after the hidden remainder.

## Loop shell

Copy `templates/FilmShell.tsx`. It layers: scene → sign-off lockup → captions → a loop cross-fade into `<Freeze frame={0}>` of the scene → sample tag → grain → audio.
