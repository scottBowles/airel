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
- **Icons**: `Lucide Svelte` (Recommended, install if needed) or `Phosphor`
- **Theme**: "Industrial Sci-Fi" / "Nostromo"
    - **Fonts**: `Space Mono` (Mono), `Rajdhani` (Headers), `Inter` (Body).
    - **Colors**: Slate/Charcoal background, Amber/Green for data.
    - **Class Utility**: `clsx` + `tailwind-merge` for class overrides.

## AI Development Patterns
- **Context Awareness**: Always check `.ai/context/` before major architectural changes.
- **Routing**: Domain-driven naming (`/logs`, `/database/characters`, `/comms`).
- **Data**: New entities must verify schema consistency via `schema.graphql` or `schema-summary.md`.
