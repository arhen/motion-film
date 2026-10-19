import React from 'react';
import {AbsoluteFill, Freeze, useCurrentFrame} from 'remotion';

/*
 * Accumulation motion blur: renders `samples` copies of the children at sub-frame times
 * centred on the current frame, added with plus-lighter at 1/N opacity.
 *
 * - The children must read the frame themselves (useCurrentFrame / useSec). Props computed
 *   outside are frozen, so every sample would be identical.
 * - Children need an opaque ground, or use it on a subtree drawn over one.
 * - Any SVG ids inside must be per instance (useSvgId): each sample is another copy.
 * - Pass samples={1} outside blur windows; render cost scales with samples.
 */
export const MotionBlur: React.FC<{children: React.ReactNode; samples: number; shutter?: number}> = ({children, samples, shutter = 0.75}) => {
	const frame = useCurrentFrame();
	if (samples <= 1) return <>{children}</>;
	return (
		<AbsoluteFill style={{isolation: 'isolate'}}>
			{Array.from({length: samples}, (_, i) => (
				<AbsoluteFill key={i} style={{mixBlendMode: 'plus-lighter', filter: `opacity(${1 / samples})`}}>
					<Freeze frame={frame + ((i + 0.5) / samples - 0.5) * shutter}>{children}</Freeze>
				</AbsoluteFill>
			))}
		</AbsoluteFill>
	);
};

/** True when `t` (seconds) falls in any [from, to] window. */
export const inWindows = (t: number, windows: [number, number][]) => windows.some(([a, b]) => t >= a && t < b);
