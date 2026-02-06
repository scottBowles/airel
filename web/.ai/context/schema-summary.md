# Schema Summary (D&D / Spacer Campaign)

## Core Domain: "The Chronicle"
- **GameLog**: The central temporal unit. Represents a session.
    - Fields: `title`, `brief` (short), `synopsis` (med), `fullText` (long), `richText` (Markdown).
    - Links: `characters`, `places`, `items` (entities present in this log).
    - AI: `aiSummary`, `suggestions`.

## Core Domain: "The Database" (Entities)
All implement interface `Entity` & `Lockable`.
- **Common Fields**: `id`, `name`, `description`, `imageIds`, `markdownNotes`, `logs` (history).
- **Types**:
    - **Character**: Has `race`, `relatedPlaces`, `relatedItems`.
    - **Place**: Has `parentPlace`, `childPlaces`.
    - **Item**: General items.
    - **Artifact**: Special items.
    - **Association`: Organizations or groups.
    - **Race**: Species/Lineage.

## Core Domain: "Comms" (Processors)
- **ChatSessionType**: A conversation with the AI.
- **ChatMessageType**: Individual messages.
    - Role: `user` | `assistant`.
    - RAG: Linked `contextChunks`.
- **ContentChunkType**: Vector embeddings references used for RAG.

## System
- **User**: Authentication & "Locking" (Edit collision prevention).
- **Lockable**: Mechanism to prevent concurrent edits (`lockUser`, `lockTime`).
