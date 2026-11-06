# Candidates for Removal (Round 2)

This report compares the active usage defined in `schema_brief.md` against the latest `schema.graphql`. Items listed here appear to be unused by the client application.

## 1. Unused Queries

### Filtered Connections

These specific filtered connection queries appear unused. The application likely uses the standard collections (`artifacts`, `places`, etc.) or Algolia for search.

<!-- - `ArtifactsConnectionFiltered`
- `CharactersConnectionFiltered`
- `ItemsConnectionFiltered`
- `PlacesConnectionFiltered`
- `RacesConnectionFiltered`
- `associationsConnectionFiltered` -->

### RAG / Content Processing

These queries related to the RAG (Retrieval-Augmented Generation) system internals seem unused by the client directly.

- `availableContentTypes`
- `contentChunks`
- `contentStats`
- `queryCache`
- `searchContent` (Note: Ensure this isn't used dynamically in search bars)

### Chat

- `chatMessages` (The client likely loads messages via `chatSessions` -> `messages`)

### Other

<!-- - `consolidatedAiLogSuggestions` (Client uses `aiLogSuggestions`) -->

- `publicUser`
<!-- - `users` (Client uses `me`) -->

## 2. Unused Mutations

### Deletion Operations

No explicit "delete" mutations were found in the client usage.

<!-- - `deleteArtifact`
- `deleteAssociation`
- `deleteCharacter`
- `deleteGameLog`
- `deleteItem`
- `deletePlace`
- `deleteRace` -->

### Specific "Release Lock" Mutations

The client appears to use the generic `unlock` mutation, making these specific variants redundant.

<!-- - `artifactReleaseLock`
- `associationReleaseLock`
- `characterReleaseLock`
- `gamelogReleaseLock`
- `itemReleaseLock`
- `placeReleaseLock`
- `raceReleaseLock` -->

### Specific "Lock" Mutations

The client uses `lock` (generic) and some specific locks (`associationLock`, `characterLock`, etc.), but these specific ones were **not** found in the usage brief:

<!-- - `artifactLock`
- `gamelogLock` -->
<!-- I removed them all — they are all using `lock` it looks like -->

### Specific "Add Image" Mutations

The client uses the generic `entityAddImage`, likely rendering these obsolete.

<!-- - `artifactAddImage`
- `associationAddImage`
- `characterAddImage`
- `itemAddImage`
- `placeAddImage`
- `raceAddImage` -->

### Content Processing / RAG Maintenance

These admin/maintenance tasks don't seem to be called by the client.

- `cleanupOrphanedChunks`
- `processAllContent`
- `processContent`

### Auth / User

- `revokeToken`
- `verifyToken`

## 3. Unused Types & Embeddables

### Types

These types are return types or inputs for the unused operations above.

- `ContentChunkType` & `ContentChunkTypeConnection`
- `ContentStatsType`
- `QueryCacheType` & `QueryCacheTypeConnection`
- `ProcessContentPayload`, `ProcessAllContentPayload`
- `*Filter` arguments or inputs related specifically to filtered queries.

### Entity Fields

These fields exists on `Entity` implementations (`Artifact`, `Place`, etc.) but are not listed in the usage report.

- **Common Fields:**
  - `slug` (Only `id` and `name` are typically used for identification)
  - `created`, `updated` (Mostly unused on entities, though `dateJoined` is used on User)
- **Item:**
  - `armor`, `weapon`, `equipment` (Note: `schema_brief` lists `ArmorTraits` etc, but check if the _wrapper_ field is what's used. The brief says "Specific Entity Fields... Item: armor, weapon, equipment". So these **ARE** used.)
- **Chat:**
  - `tokensUsed`, `similarityThreshold`, `contentTypesSearched` (Usage focuses on `message` and `response`)

## 4. Summary of Major Removal Candidates

1.  **Filtered Connection Queries**: Safe to remove if no "starts with" search exists in the UI.
2.  **Delete Mutations**: If the app doesn't support deleting entities, these are dead code.
3.  **Specific Lock/Unlock/AddImage**: Replaced by generic interfaces (`Lockable`, `Entity`).
4.  **RAG Internals**: The `ContentChunk`, `QueryCache`, and `Process` APIs appear to be backend-only or unused.
