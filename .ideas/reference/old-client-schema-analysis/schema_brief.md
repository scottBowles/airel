# Consolidated GraphQL Usage Report

This report summarizes the GraphQL API usage found in the codebase. It lists the active Operations (Queries/Mutations) and the Fields requested from definitions and fragments.

## 1. Active Operations

These are the root fields used in the `Query` and `Mutation` types.

### Generic / Shared

**Queries**

- `me` (User details)
- `node` (Used for by-ID lookups)

**Mutations**

- `lock`
- `unlock`
- `refreshToken` (`customApiCalls`)
- `googleLogin` (`customApiCalls`)

### Entities (Artifact, Association, Character, Item, Place, Race)

**Queries**

- `artifacts`
- `associations`
- `characters`
- `items`
- `places`
- `races`

**Mutations**

- `createArtifact`, `createAssociation`, `createCharacter`, `createItem`, `createPlace`, `createRace`
- `updateAssociation`, `updateCharacter`, `updateItem`, `updatePlace`, `updateRace`
- `*Lock` variants: `associationLock`, `characterLock`, `itemLock`, `placeLock`, `raceLock`
- `entityAddAlias`
- `entityAddImage`
- `addEntityLog`
- `removeEntityLog`

### Game Logs

**Queries**

- `gameLogs`
- `aiLogSuggestions`

**Mutations**

- `getOrCreateGameLog`
- `updateGamelog`
- `addAiLogSuggestion`

### Chat

**Queries**

- `chatSessions`

**Mutations**

- `startChatSession`
- `sendChatMessage`

---

## 2. Used Types & Fields

The following fields are requested across the application (including via Fragments like `EntityListFields`).

### `User`

- `id`, `username`, `email`
- `firstName`, `lastName`
- `isActive`, `isStaff`, `isSuperuser`
- `dateJoined`, `lastLogin`

### `Entity` Interface (and Implementations)

Common fields used by `Artifact`, `Association`, `Character`, `Item`, `Place`, `Race`:

- `id`
- `name`
- `description`
- `markdownNotes`
- `imageIds`, `thumbnailId` (via `EntityListFields`)
- `logs`
- `aliases`
- `lockedBySelf`, `lockTime`, `lockUser` (id, username)
- **Relationships:**
  - `relatedArtifacts`
  - `relatedAssociations`
  - `relatedCharacters`
  - `relatedItems`
  - `relatedPlaces`
  - `relatedRaces`

### Specific Entity Fields

- **Place**: `placeType`, `parent`, `children`
- **Character**: `race`
- **Item**: `armor`, `weapon`, `equipment`

### `GameLog`

- `id`, `url`, `title`, `googleId`
- `gameDate`
- `brief`, `synopsis`
- `placesSetIn`
- `aiSuggestions` (Complex object)

### `GameLogAiSummary` / `CombinedGameLogAiSummary` (under `aiSuggestions`)

- Scalars: `titles`, `briefs`, `synopses`
- Lists: `associations`, `characters`, `items`, `places`, `races`
- Found Objects: `foundArtifacts`, `foundAssociations`, `foundCharacters`, `foundItems`, `foundPlaces`, `foundRaces` (Note: nested queries often fetch `id`, `name`, `aliases` for these)

### `ChatSession` & `ChatMessage`

- `ChatSession`: `id`, `title`, `createdAt`, `updatedAt`, `messages`
- `ChatMessage`: `id`, `message`, `response`, `createdAt`
