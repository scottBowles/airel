/** Themed loading messages shown while waiting for Kozmo's response. */
const KOZMO_STATUS_MESSAGES = [
	"Searching ship's archives...",
	'Scanning long-range databanks...',
	'Cross-referencing star charts...',
	'Consulting the navigation logs...',
	'Parsing old transmissions...',
	'Decrypting crew journals...',
	'Querying the astral index...',
	'Sifting through cargo manifests...',
	'Analyzing sensor telemetry...',
	'Reviewing mission briefings...',
	"Checking the captain's log...",
	'Correlating subspace frequencies...',
	'Indexing planetary surveys...',
	'Digging through comm transcripts...',
	'Calibrating memory banks...',
	'Compiling incident reports...',
	'Tracing flight path records...',
	'Accessing restricted archives...',
	'Running deep-scan query...',
	'Reassembling fragmented data...',
	'Probing the knowledge core...',
	'Sorting temporal metadata...',
	'Decoding encrypted field notes...',
	'Fetching xenobiology records...',
	'Verifying source integrity...'
];

/** Fisher-Yates shuffle (returns a new array). */
function shuffle<T>(arr: readonly T[]): T[] {
	const copy = [...arr];
	for (let i = copy.length - 1; i > 0; i--) {
		const j = Math.floor(Math.random() * (i + 1));
		[copy[i], copy[j]] = [copy[j], copy[i]];
	}
	return copy;
}

/**
 * Returns a shuffled copy of the status messages.
 * Call once per request, then cycle through the array on a timer.
 */
export function getShuffledStatusMessages(): string[] {
	return shuffle(KOZMO_STATUS_MESSAGES);
}
