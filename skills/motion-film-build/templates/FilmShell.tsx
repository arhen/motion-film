import React from 'react';
import {AbsoluteFill, Audio, Freeze, staticFile} from 'remotion';
import {ease, prS, useSec} from './anim';
import {FontsGate} from './FontsGate';

/*
 * Shared shell for a video: scene → sign-off → captions → loop cross-fade into a frozen
 * copy of frame 0 → sample-data tag → grain → audio. With `loop` set, the last
 * `loop[1] - loop[0]` seconds fade into the opening still, so playback loops without a jump.
 *
 * Scene: a component that reads time itself (useSec) and draws its own ground.
 * Any SVG ids inside Scene must be per instance (useSvgId): the overlay renders a second copy.
 */
export const FilmShell: React.FC<{
	Scene: React.FC;
	ground: string;
	audio?: string;
	loop?: [number, number];
	signoff?: React.ReactNode;
	captions?: React.ReactNode;
	tag?: React.ReactNode;
	grain?: React.ReactNode;
}> = ({Scene, ground, audio, loop, signoff, captions, tag, grain}) => {
	const {t} = useSec();
	const loopP = loop ? prS(t, loop[0], loop[1] - loop[0], ease.inOutCubic) : 0;
	return (
		<AbsoluteFill style={{background: ground}}>
			<FontsGate>
				<Scene />
				{signoff}
				{captions}
				{loopP > 0 ? (
					<AbsoluteFill style={{opacity: loopP}}>
						<Freeze frame={0}>
							<AbsoluteFill style={{background: ground}}>
								<Scene />
							</AbsoluteFill>
						</Freeze>
					</AbsoluteFill>
				) : null}
				{tag}
				{grain}
			</FontsGate>
			{audio ? <Audio src={staticFile(audio)} /> : null}
		</AbsoluteFill>
	);
};
