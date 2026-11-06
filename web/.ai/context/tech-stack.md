# Tech Stack & Standards

## Core Framework

- **Framework**: `SvelteKit` (Svelte 5)
- **Language**: `TypeScript` (Strict mode)
- **Build Tool**: `Vite` (v5+)

## Data Layer

- **GraphQL Client**: `Houdini` (v2/Next)
  - **Pattern**: Colocated queries in `.svelte` files using `<script>` tags.
  - **Stores**: Use Houdini's generated stores for mutations and subscriptions.
  - **Config**: `houdini.config.js` points to `env:PUBLIC_GRAPHQL_ENDPOINT`.

## UI & Styling

- **Engine**: `Tailwind CSS` (v4)
- **Component Primitives**: `Bits UI` (Headless accessibility)
- **Icons**: `Lucide Svelte`
- **Theme**: "Sci-Fi" / "Spaceship's Console"

## AI Development Patterns

- **Context Awareness**: Always check `.ai/context/` before major architectural changes.
- **Data**: New entities must verify schema consistency via `schema.graphql`.
