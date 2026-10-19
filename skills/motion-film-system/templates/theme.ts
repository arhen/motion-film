/*
 * Video theme. Import the product's generated tokens; never paste hex values that the
 * product already defines. Add film-only shades below with a reason each.
 *
 * Replace the import with your token source, for example a generated TS module,
 * a JSON export, or CSS variables parsed at build time.
 */
import {tokens} from '../../path/to/your/design-tokens';

export const C = {
	// Brand roles (logo, grounds, ink)
	brand: tokens.color.brand.accent,
	paper: tokens.color.brand.paper,
	ink: tokens.color.brand.ink,
	graphite: tokens.color.brand.graphite,
	// Functional roles (product UI)
	action: tokens.color.ui.action,
	surface: tokens.color.ui.surface,
	inkSoft: tokens.color.ui.inkSoft,
	inkFaint: tokens.color.ui.inkFaint,
	positive: tokens.color.ui.positive,
	negative: tokens.color.ui.negative,
	warning: tokens.color.ui.warning,
	// Film-only shades: tuned for compression and large areas at 1080p
	hairline: '#e3dfd7', // 1 px lines survive h264 better a step darker than the UI token
	glow: '#ff7a3d', // soft radial glow behind the hero element
};

// Family names must match the FONTS list in FontsGate.tsx.
export const FONT = {
	display: '"Display Face", ui-rounded, sans-serif',
	ui: '"UI Face", system-ui, sans-serif',
	mono: '"Mono Face", ui-monospace, monospace', // only for the roles the brand allows
};

/** Minimum sizes for 1920×1080 seen in a ~900 px card (playback width ÷ 1920 ≈ 0.47). */
export const TYPE = {
	caption: 58,
	display: 84,
	ui: 28,
	label: 22,
};

/** Minimum sizes for 1080-wide vertical, square or 4:5 video seen full width on a phone (≈ 390 px ÷ 1080 ≈ 0.36). */
export const TYPE_PHONE = {
	caption: 72,
	display: 104,
	ui: 34,
	label: 28,
};

export const typeFor = (width: number, height: number) => (height >= width ? TYPE_PHONE : TYPE);

export const MOTION = {
	outExpo: [0.16, 1, 0.3, 1] as const,
	inOutCubic: [0.65, 0, 0.35, 1] as const,
	inQuint: [0.64, 0, 0.78, 0] as const,
	springCalm: {f: 2.2, z: 0.8},
	springPlayful: {f: 2.6, z: 0.55},
	springKinetic: {f: 3.2, z: 0.45},
	logoReveal: {seconds: 0.5},
	readingHold: 1.5,
};
