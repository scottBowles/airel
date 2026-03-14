# Airel - Frontend (Kontularien)

A SvelteKit application for the Kontularien spaceship interface.

## Tech Stack & Patterns

### 1. Data Fetching (Houdini + SSR)

We utilize **Houdini 2.0** with SvelteKit. To ensure Server-Side Rendering (SSR) works correctly, follow this pattern for all data-fetching routes:

**A. Define the Query**
Create a named `.gql` file in the route folder (do not use `+page.gql` for page queries to avoid auto-route conflicts).
_Example:_ `src/routes/logs/LogList.gql`

```graphql
query LogList {
  ...
}
```

**B. Create the Load Function**
Use the `_houdini_load` pattern in `+page.ts`.

```typescript
import { load_LogList } from '$houdini';
import type { PageLoad } from './$types';

export const load: PageLoad = async (event) => {
	return {
		...(await load_LogList({ event }))
	};
};
```

**C. Consume in Component**
In `+page.svelte`, access the store via `data` props and derived state.

```svelte
<script lang="ts">
	import type { PageData } from './$houdini';

	let { data }: { data: PageData } = $props();
	let LogList = $derived(data.LogList);
</script>

{#if $LogList.data} ... {/if}
```

### 2. Styling (TailwindCSS v4)

- Theme configuration is in `src/app.css` under the `@theme` block.
- Import order in `app.css` is strict: `@import` -> `@plugin` -> `@theme`.

### 3. Responsive Scale Rules

To keep responsive styling maintainable, use shared utility classes from `src/app.css` instead of ad hoc spacing/type combinations.

- App shell/content spacing: `content-pad`, `panel-pad`, `stack-space`
- Shared typography: `title-display`, `copy-readable`, `machine-text`
- Database list pages: `db-page`, `db-header`, `db-title`, `db-toolbar`, `db-grid`, `db-card`, `db-card-thumb`, `db-card-title`, `db-card-copy`
- Database detail pages: `db-detail`, `db-detail-header`, `db-detail-title`, `db-back-link`, `db-detail-grid`, `db-detail-main`, `db-detail-side`, `db-detail-panel`, `db-detail-panel-title`

When adding a new screen:

1. Start with existing utility classes.
2. If you need a new spacing/type pattern in more than one place, add a named utility in `src/app.css`.
3. Avoid copying large class strings between route files.

### 4. Mobile Follow-Up

Current state:

- App shell, database routes, logs, image-management controls, and login now have a mobile-first baseline.
- Shared responsive utilities in `src/app.css` are the default way to keep spacing and type decisions consistent.

Next pass should focus on QA and the remaining product gaps, not another broad styling rewrite:

1. Test key screens at 320px, 375px, 390px, 768px, and short landscape heights.
2. Verify keyboard flow, focus visibility, and comfortable tap targets on navigation, login, logs, and image management.
3. Review reduced-motion behavior and any hover-only affordances that need a touch fallback.
4. Replace the placeholder bridge screen at `src/routes/+page.svelte` with a real mobile-ready landing page.
5. Only add new shared utility classes when a responsive pattern repeats in more than one place.

Viewport QA notes completed so far:

- Mobile navigation now scrolls on short-height screens instead of clipping below the fold.
- The main content viewport uses `min-h-0` so nested scroll areas behave correctly inside the fixed shell.
- Login aligns from the top on shorter screens and re-centers on larger ones to reduce vertical clipping.
- Logs allow safer title and metadata wrapping at narrow widths.
- The image carousel now uses a smaller default mobile height and scales up at larger breakpoints.

Accessibility pass notes completed so far:

- Reduced-motion mode now suppresses long transitions, smooth scrolling, and pulsing animation globally.
- The image carousel supports keyboard navigation with left/right arrows plus Home/End.
- Reorderable image grids now expose visible drag guidance for touch users instead of relying only on hover.
- The mobile navigation close control now matches the 44px touch-target baseline used elsewhere.

---

## Standard Development

# sv

Everything you need to build a Svelte project, powered by [`sv`](https://github.com/sveltejs/cli).

## Creating a project

If you're seeing this, you've probably already done this step. Congrats!

```sh
# create a new project
npx sv create my-app
```

To recreate this project with the same configuration:

```sh
# recreate this project
pnpm dlx sv create --template minimal --types ts --add prettier eslint tailwindcss="plugins:typography,forms" --install pnpm .
```

## Developing

Once you've created a project and installed dependencies with `npm install` (or `pnpm install` or `yarn`), start a development server:

```sh
npm run dev

# or start the server and open the app in a new browser tab
npm run dev -- --open
```

## Building

To create a production version of your app:

```sh
npm run build
```

You can preview the production build with `npm run preview`.

> To deploy your app, you may need to install an [adapter](https://svelte.dev/docs/kit/adapters) for your target environment.
