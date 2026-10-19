#!/usr/bin/env bash
# Brand drift audit over the video sources. Configure with environment variables; every hit needs a fix or a reason.
#   WORDMARK='acme' BANNED_FONTS='Inter|Roboto' MONO='JetBrains Mono' OLD_DOMAINS='acme\.io' THEME=src/theme.ts \
#   bash brand-audit.sh src
#
# WORDMARK      the brand name as it would appear if someone retyped the logo in a font (case-insensitive)
# BANNED_FONTS  font families that must not appear (regex alternation)
# MONO          the monospace family; every use is listed so you can check it is a timecode or a key hint
# OLD_DOMAINS   retired domains or handles (regex alternation)
# THEME         the theme file allowed to hold raw colour values
# Also flags time-based CSS animation (transition, @keyframes, animation:) and will-change: in a frame-rendered
# video every value must be a function of the frame, or renders flicker and differ between runs.
set -uo pipefail
src=${1:-src}
theme=${THEME:-src/theme.ts}
hits=0

section() { printf "\n== %s\n" "$1"; }
report() {
	if [ -n "$1" ]; then
		echo "$1"
		hits=$((hits + $(printf "%s\n" "$1" | wc -l)))
	else
		echo "ok"
	fi
}

if [ -n "${WORDMARK:-}" ]; then
	section "Wordmark typed as text (should be artwork)"
	report "$(grep -rniE ">[[:space:]]*${WORDMARK}[[:space:]]*<|['\"]${WORDMARK}['\"]" "$src" --include='*.tsx' --include='*.ts' 2>/dev/null)"
fi
if [ -n "${BANNED_FONTS:-}" ]; then
	section "Banned font families"
	report "$(grep -rnE "${BANNED_FONTS}" "$src" --include='*.tsx' --include='*.ts' --include='*.css' 2>/dev/null)"
fi
if [ -n "${MONO:-}" ]; then
	section "Monospace uses (check each is a timecode or key hint)"
	grep -rn "MONO\|${MONO}" "$src" --include='*.tsx' 2>/dev/null | grep -v "^${theme}:" || echo "none"
fi
if [ -n "${OLD_DOMAINS:-}" ]; then
	section "Retired domains or handles"
	report "$(grep -rnE "${OLD_DOMAINS}" "$src" 2>/dev/null)"
fi
section "Raw hex colours outside the theme"
report "$(grep -rnE "#[0-9a-fA-F]{6}\b" "$src" --include='*.tsx' 2>/dev/null | grep -v "^${theme}:" | head -50)"
section "Non-deterministic sources"
report "$(grep -rnE "Math\.random|Date\.now|new Date\(" "$src" --include='*.tsx' --include='*.ts' 2>/dev/null)"

section "Time-based CSS animation (must be frame-driven)"
report "$(grep -rnE "transition:|@keyframes|animation:|will-change" "$src" --include='*.tsx' --include='*.ts' --include='*.css' 2>/dev/null)"

printf "\n%d hit(s)\n" "$hits"
[ "$hits" -eq 0 ]
