// Places labels beside their pins on screen so that no two overlap. Each label tries a few
// spots around its dot in turn and takes the first that is clear of every label and dot placed
// so far; when none is clear, it is hidden (its dot stays, and hovering shows the name).

export type LabelInput = {
	/** Screen position of the pin's dot, px. */
	x: number;
	y: number;
	/** Label size, px. */
	w: number;
	h: number;
};

/** Offset of the label's top-left corner from its dot, px; null when it can't be placed. */
export type Placement = { dx: number; dy: number } | null;

type Box = { x0: number; y0: number; x1: number; y1: number };

const DOT = 4; // half the dot's size, plus a hair
const GAP = 5;

/** Spots around the dot, in order of preference. */
function spots(w: number, h: number): { dx: number; dy: number }[] {
	// Nudging above or below on the same side keeps a label by its own dot; flipping to the
	// other side can put it nearer a neighbour's.
	return [
		{ dx: DOT + GAP, dy: -h / 2 }, // right
		{ dx: DOT, dy: DOT }, // below right
		{ dx: DOT, dy: -h - DOT }, // above right
		{ dx: -DOT - GAP - w, dy: -h / 2 }, // left
		{ dx: -DOT - w, dy: DOT }, // below left
		{ dx: -DOT - w, dy: -h - DOT } // above left
	];
}

const overlaps = (a: Box, b: Box) => a.x0 < b.x1 && b.x0 < a.x1 && a.y0 < b.y1 && b.y0 < a.y1;

/** Earlier labels get first choice, so put the most important first. */
export function layoutLabels(labels: LabelInput[]): Placement[] {
	const taken: Box[] = labels.map((l) => ({
		x0: l.x - DOT,
		y0: l.y - DOT,
		x1: l.x + DOT,
		y1: l.y + DOT
	}));
	return labels.map((l, i) => {
		for (const s of spots(l.w, l.h)) {
			const box = { x0: l.x + s.dx, y0: l.y + s.dy, x1: l.x + s.dx + l.w, y1: l.y + s.dy + l.h };
			// Its own dot can't be in the way: every spot sits clear of it.
			if (!taken.some((t, j) => j !== i && overlaps(box, t))) {
				taken.push(box);
				return s;
			}
		}
		return null;
	});
}
