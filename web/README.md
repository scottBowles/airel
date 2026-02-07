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
