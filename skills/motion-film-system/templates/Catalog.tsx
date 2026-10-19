/*
 * Catalogue board: one still that shows the whole video design system, for review
 * before any video is built. Register it as a composition (1920×1080, 1 frame) and
 * render it with `npx remotion still Catalog out/catalog.png`. If you ship vertical, register
 * a 1080×1920 copy too: type sizes switch to the phone minimums.
 *
 * Replace the placeholder imports with your theme and components.
 */
import React from 'react';
import {AbsoluteFill, useVideoConfig} from 'remotion';
import {C, FONT, typeFor} from './theme';
import {FontsGate} from './FontsGate';
// import {Logo, Lockup, Caption, SampleTag, Card, Chip, Button, Notification, Phone} from './components';

const Section: React.FC<{title: string; children?: React.ReactNode}> = ({title, children}) => (
	<div style={{marginBottom: 36}}>
		<div style={{fontFamily: FONT.ui, fontWeight: 700, fontSize: 20, color: C.inkFaint, marginBottom: 12}}>{title}</div>
		<div style={{display: 'flex', flexWrap: 'wrap', gap: 24, alignItems: 'flex-end'}}>{children}</div>
	</div>
);

const Swatch: React.FC<{name: string; value: string}> = ({name, value}) => (
	<div style={{width: 150}}>
		<div style={{height: 80, borderRadius: 14, background: value, border: `1px solid ${C.hairline}`}} />
		<div style={{fontFamily: FONT.ui, fontSize: 18, color: C.ink, marginTop: 6}}>{name}</div>
		<div style={{fontFamily: FONT.mono, fontSize: 16, color: C.inkFaint}}>{value}</div>
	</div>
);

export const Catalog: React.FC = () => {
	const {width, height} = useVideoConfig();
	const TYPE = typeFor(width, height);
	return (
		<AbsoluteFill style={{background: C.paper, padding: 64}}>
			<FontsGate>
				<Section title="Type">
					<span style={{fontFamily: FONT.display, fontSize: TYPE.display, fontWeight: 500, color: C.ink}}>Display sign-off</span>
					<span style={{fontFamily: FONT.display, fontSize: TYPE.caption, fontWeight: 500, color: C.ink}}>Caption at minimum size</span>
					<span style={{fontFamily: FONT.ui, fontSize: TYPE.ui, color: C.ink}}>Interface text at minimum size</span>
					<span style={{fontFamily: FONT.ui, fontSize: TYPE.label, color: C.inkSoft}}>Label text</span>
				</Section>
				<Section title="Colour roles">
					{Object.entries(C).map(([k, v]) => (
						<Swatch key={k} name={k} value={v} />
					))}
				</Section>
				<Section title="Logo on each ground">
					{/* <Logo ground="paper" size={96} /> <Logo ground="dark" size={96} /> <Logo micro size={24} /> */}
				</Section>
				<Section title="Components and states">
					{/* <Card …/> <Chip tone="positive"/> <Button state="rest"/> <Button state="pressed"/> <Notification …/> <Phone …/> */}
				</Section>
				<Section title="Fixed pieces">
					{/* <Caption text="Captions are the voice-over" /> <SampleTag /> <Lockup /> */}
				</Section>
			</FontsGate>
		</AbsoluteFill>
	);
};
