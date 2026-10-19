# Motion languages

A motion language is the physics of one video: how things enter, move, collide and leave, and how that sounds. Pick one per video from the subject's world, then keep every scene inside it. These five have been built and shipped; add your own in the same shape.

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

## Writing a new one

Fill in the same six fields: fits, signature moves, timing (curves, springs, durations, stagger), camera, sound, avoid. Then add its motion and sound tokens to the video design system.
