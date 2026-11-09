/// <reference types="node" />
// Open a page of the running web app in headless Chromium, signed in as a dev user, and
// report what loaded: status, title, visible text, console errors and warnings, page errors,
// failed requests, and a screenshot. For agents without a browser pane (cloud sessions); see the
// verify-ui skill. Needs the api and web dev servers, `manage.py seed_dev`, and Chromium
// (`vp exec playwright install chromium --only-shell`, or --with-deps on a bare Linux box).
// When Playwright's own browser isn't installed (cloud sessions, where its download host is
// blocked), it uses $BROWSE_CHROMIUM_PATH or a Chromium preinstalled under
// $PLAYWRIGHT_BROWSERS_PATH (default /opt/pw-browsers).
//
//   node scripts/browse.ts /database/characters
//   node scripts/browse.ts /chronicle --as player --out /tmp/chronicle.png --width 390
//   node scripts/browse.ts / --as anon
//   node scripts/browse.ts --check-browser   # launch Chromium, print its path, exit
import { execFileSync } from 'node:child_process';
import { existsSync, readdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { resolve } from 'node:path';
import { parseArgs } from 'node:util';
import { chromium, type Browser } from 'playwright';

const { values, positionals } = parseArgs({
	allowPositionals: true,
	options: {
		as: { type: 'string', default: 'dm' },
		out: { type: 'string', default: resolve(tmpdir(), 'browse.png') },
		width: { type: 'string', default: '1280' },
		height: { type: 'string', default: '800' },
		'full-page': { type: 'boolean', default: false },
		'max-text': { type: 'string', default: '4000' },
		'check-browser': { type: 'boolean', default: false }
	}
});

const baseUrl = process.env.WEB_URL ?? 'http://localhost:5173';
const url = new URL(positionals[0] ?? '/', baseUrl);
const repoRoot = resolve(import.meta.dirname, '../..');

function devLoginTokens(username: string): { access_token: string; refresh_token: string } {
	const output = execFileSync(
		resolve(repoRoot, 'api/.venv/bin/python'),
		[resolve(repoRoot, 'api/manage.py'), 'dev_login', username, '--json'],
		{ encoding: 'utf8' }
	);
	return JSON.parse(output.trim().split('\n').at(-1) ?? '');
}

// Preinstalled Chromium builds, newest first: headless shells, then full Chromium.
function preinstalledChromium(): string[] {
	const root = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
	if (!existsSync(root)) return [];
	const builds = (prefix: string, binary: string) =>
		readdirSync(root)
			.filter((name) => new RegExp(`^${prefix}-\\d+$`).test(name))
			.sort((a, b) => Number(b.split('-').at(-1)) - Number(a.split('-').at(-1)))
			.map((name) => resolve(root, name, binary))
			.filter((path) => existsSync(path));
	return [
		...builds('chromium_headless_shell', 'chrome-headless-shell-linux64/chrome-headless-shell'),
		...builds('chromium', 'chrome-linux64/chrome')
	];
}

// $BROWSE_CHROMIUM_PATH, else Playwright's own browser, else a preinstalled one.
async function launchChromium(): Promise<{ browser: Browser; executable: string }> {
	const override = process.env.BROWSE_CHROMIUM_PATH;
	if (override)
		return { browser: await chromium.launch({ executablePath: override }), executable: override };
	try {
		return { browser: await chromium.launch(), executable: 'playwright default' };
	} catch (error) {
		if (!String(error).includes("Executable doesn't exist")) throw error;
		const executable = preinstalledChromium()[0];
		if (!executable) throw error;
		return { browser: await chromium.launch({ executablePath: executable }), executable };
	}
}

const { browser, executable } = await launchChromium();
if (values['check-browser']) {
	console.log(`chromium: ${executable} (${browser.version()})`);
	await browser.close();
	process.exit(0);
}
const context = await browser.newContext({
	viewport: { width: Number(values.width), height: Number(values.height) }
});

if (values.as !== 'anon') {
	const tokens = devLoginTokens(values.as);
	await context.addCookies(
		Object.entries(tokens).map(([name, value]) => ({
			name,
			value,
			url: url.origin,
			httpOnly: true,
			sameSite: 'Strict' as const
		}))
	);
}

const page = await context.newPage();
const consoleErrors: string[] = [];
const consoleWarnings: string[] = [];
const failedRequests: string[] = [];
page.on('console', (message) => {
	if (message.type() === 'error') consoleErrors.push(message.text());
	if (message.type() === 'warning') consoleWarnings.push(message.text());
});
page.on('pageerror', (error) => consoleErrors.push(`pageerror: ${error.message}`));
page.on('requestfailed', (request) =>
	failedRequests.push(`${request.method()} ${request.url()}: ${request.failure()?.errorText}`)
);
page.on('response', (response) => {
	if (response.status() >= 400)
		failedRequests.push(`${response.status()} ${response.request().method()} ${response.url()}`);
});

const response = await page.goto(url.href, { waitUntil: 'networkidle' });
const out = resolve(values.out);
await page.screenshot({ path: out, fullPage: values['full-page'] });
const text = (await page.locator('body').innerText()).replace(/\n{3,}/g, '\n\n');
const maxText = Number(values['max-text']);

console.log(
	[
		`url: ${page.url()}`,
		`status: ${response?.status() ?? 'none'}`,
		`title: ${await page.title()}`,
		`signed in as: ${values.as}`,
		`screenshot: ${out}`,
		`console errors (${consoleErrors.length}):`,
		...consoleErrors.map((line) => `  ${line}`),
		`console warnings (${consoleWarnings.length}):`,
		...consoleWarnings.map((line) => `  ${line}`),
		`failed requests (${failedRequests.length}):`,
		...failedRequests.map((line) => `  ${line}`),
		`text${text.length > maxText ? ` (first ${maxText} of ${text.length} chars)` : ''}:`,
		text.slice(0, maxText)
	].join('\n')
);

await browser.close();
