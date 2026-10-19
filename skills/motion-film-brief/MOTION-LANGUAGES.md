# Motion languages

A motion language is the physics of one video: how things enter, move, collide and leave, and how that sounds. Pick one per video from the subject's world, then keep every scene inside it. The first five have been built and shipped; the last four serve the content and footage kinds. Add your own in the same shape.

Spring notation: `f` is natural frequency (Hz), `z` is damping ratio (`z < 1` overshoots, `z ≥ 1` does not).

## Liquid and pour

- **Fits:** food and drink, hospitality, wellness, slow mornings, anything poured, filled or brewed.
- **Signature moves:** posts or messages that fall as drops; a vessel that fills to a level with a sloshing surface; steam that rises and carries the next element up; ripples on impact.
- **Timing:** soft and heavy. Ease in-out cubic over 0.8-1.6 s. Springs about `f 1.5, z 0.85-1.0`. Gravity drops ease in (quint).
- **Camera:** slow push-in (3-4 % over the video); rack focus to a foreground device.
- **Sound:** warm electric-piano chords, plucked arpeggios, a light shaker; drips (falling sine pitch), pour (band-passed noise rising), steam hiss, a register or bell ding.
- **Avoid:** snappy overshoot, hard cuts.

## Kinetic vertical feed

- **Fits:** creators, social media, community, anything that scrolls.
- **Signature moves:** a 9:16 device inside the 16:9 frame; comments that flick out, fan, snap into stacks and flip over; a stack that grows tall; a record ring that fills.
- **Timing:** snappy. Springs about `f 3.0-3.4, z 0.42-0.55`. Moves of 0.15-0.25 s, staggered 70-150 ms. Cuts on the beat.
- **Camera:** locked; the energy comes from the elements.
- **Sound:** upbeat (110-125 BPM), soft kick and clap, short plucks; swish per flick, stamp per landing, record beep, chime on success.
- **Avoid:** long glides, more than three stacks.

## Atmospheric constellation

- **Fits:** music and live events, the arts, the night, community and fandom.
- **Signature moves:** stage lights fade over a crowd drawn as a field of dots; individual dots glow as messages; colour waves sweep through on spoken words; the lit dots drift up into a word or shape (sampled from the brand display font); chosen dots turn the accent colour one by one on the beat.
- **Timing:** slow light, 1-2 s fades; drift with low-frequency noise; per-dot events on 16th notes.
- **Camera:** still; depth from glow and haze.
- **Sound:** ambient pads, felt-piano plucks, soft sub; twinkles in a pentatonic scale; one ascending chime per highlighted dot.
- **Avoid:** bright full-frame backgrounds, busy labels.

## Cartographic

- **Fits:** civic and public sector, logistics, delivery, real estate, field operations, anything with a place.
- **Signature moves:** a top-down map built as vector blocks and streets; pins that drop with a small bounce and ripple; a water or heat mask that rises and recedes; a route drawn with a stroke-dash reveal; a cluster marker that absorbs nearby pins; a reply bubble that rises from the map.
- **Timing:** calm. Ease in-out cubic; a tracking camera at 5-7 % zoom over the video; route draws over 1.5-2 s.
- **Camera:** slow track toward the hotspot, a gentle pull-out for the sign-off.
- **Sound:** rain or ambience bed, soft pad and piano pulse; pin thock, cluster whoosh, a scratching pencil while the route draws, a pump or engine hum, water draining.
- **Avoid:** party, team or ideological colours in civic work; dramatic shakes.

## Beat-locked showreel

- **Fits:** launch films, brand showreels, "what it is" videos.
- **Signature moves:** kinetic type revealed word by word on the voice; a field of cards collapsing into a dot (iris close); a silent beat before the drop; the logo revealed on the drop; a camera fly-through into the product; interface assembling in 3D; a tagline hit.
- **Timing:** every structural change sits on a bar or beat; transitions 0.25-0.5 s with motion blur; springs `f 2.4-2.6, z 0.38-0.6` for interface elements (never for the logo).
- **Camera:** pushes, whips and fly-throughs, with motion blur on fast moves only.
- **Sound:** a full arrangement (intro → build → riser → silence → drop → breakdown → final hit); pitched UI pops in key.
- **Avoid:** blurring static text; shaking during reading.

## Kinetic explainer

- **Fits:** a term, a concept, an article's argument, a number that needs context.
- **Signature moves:** the key word set large, then broken apart and rebuilt into a diagram; arrows that draw themselves from cause to effect; boxes that stack, split or merge as the idea develops; an underline or highlight that lands on the spoken keyword; a source card at the end.
- **Timing:** each build lands on its spoken keyword (a cue from `alignWord`), 0.08-0.12 s before the word. Builds of 0.4-0.7 s, ease out quint; then hold. At most two ideas on screen; the old one dims before the new one arrives. Springs about `f 2.2, z 0.8`.
- **Camera:** still, or a slow push toward the part being explained; a pan only to follow an arrow.
- **Sound:** a soft bed; a light tick or pop on each build, pitched upward as the idea completes; silence under the definition.
- **Avoid:** decorative motion, more than one moving element while a line is read, clip art.

## Screen tutorial

- **Fits:** how-tos, feature walkthroughs from a screen recording, onboarding, support videos.
- **Signature moves:** a camera that zooms to the region where the action happens and back out between steps; a ring on the cursor at each click and a soft ripple; the rest of the screen dimmed while one control is in focus; a step chip ("Step 2 of 4"); keyboard shortcuts as key caps.
- **Timing:** zoom in 0.5-0.7 s ease in-out cubic, hold through the action, zoom out before the next step. Never zoom while the person types or drags. Speed up dead time (loading, scrolling) with a visible marker rather than cutting it silently.
- **Camera:** shots from `motion-film-footage` (`scale`, `x`, `y`); the full screen at least once per step so the viewer keeps the map.
- **Sound:** the narration carries it; a quiet click on clicks, nothing else.
- **Avoid:** constant zooming, zooming to text too small to read even when enlarged, hiding the cursor.

## Talking head with overlays

- **Fits:** a person explaining something to camera, cut into short clips for Reels, TikTok and Shorts.
- **Signature moves:** jump cuts that remove pauses, alternating between two framings (1.0 and about 1.12) so each cut reads as deliberate; a split layout with the explanation above the speaker; a round bubble of the speaker while a full-screen explanation plays; captions with the spoken word highlighted; one keyword popping beside the face; a cutaway to a diagram while the voice continues.
- **Timing:** layout changes take 0.35-0.45 s, ease in-out cubic; callouts arrive 0.1 s before the spoken keyword and leave before the next one; punch-ins on cuts are instant, punch-ins within a shot ease over 0.3-0.6 s.
- **Camera:** the framing follows the face (the `x`, `y` of each shot); the eyes stay in the upper third; never crop the chin and forehead at once.
- **Sound:** the speaker's voice cleaned and up front; a light bed ducked well under it; a subtle whoosh on layout changes only.
- **Avoid:** covering the face or the mouth with captions or overlays, more than one overlay at once, captions in the platform's safe zones, cuts that change what the speaker meant.

## Mechanism explainer

- **Fits:** a technical idea that is really a system with parts: a queue, a cache, a pipeline, an index, an engine, how a product works inside. Developer tools and infrastructure.
- **Signature moves:** the idea drawn as a machine of solid isometric parts; parts assemble along the axis they mount on, base first; the machine runs (inputs enter, travel along pipes or belts, get changed, leave as the result); an exploded view pulls the assemblies apart so each can be named; one part at a time lights up in the accent while the voice names it; a gauge or counter shows the outcome.
- **Timing:** solid things do not wobble: assembly springs at `z 0.8-1.0`, staggered 60-120 ms in mounting order. Flows run at a constant, readable pace (linear), with eased starts and stops. One named part per spoken sentence, lit 0.1 s before its word. Hold the exploded view long enough to read every label (`holdFor()` on the label count).
- **Camera:** a fixed isometric angle (orbiting breaks the projection); push in 1.5-3× onto the part being named; pan only along the isometric axes.
- **Sound:** soft and mechanical: a seat "thock" as each assembly lands, a low hum while the machine runs, a tick per readout step, all on contact frames.
- **Avoid:** parts floating with nothing under them, lines that end in mid-air, more than one lit part at a time, spinning the whole machine, glows and particles standing in for "energy".
- **Built with:** the optional `anatomy` skill for the parts and geometry, animated from the clock (`motion-film-build` §7a).

## Writing a new one

Fill in the same six fields: fits, signature moves, timing (curves, springs, durations, stagger), camera, sound, avoid. Then add its motion and sound tokens to the video design system.
