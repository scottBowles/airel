"""
Generate the retrieval eval's fixtures from the three example logs.

Run it by hand, with a real OpenAI key, and commit what it writes:

    cd api
    .venv/bin/python -m rag_chat.eval.generate_fixtures

It needs OPENAI_API_KEY and OPENAI_EMBEDDINGS_MODEL (text-embedding-3-small) in
the environment or api/.env, as the app does. It does not read or write the
database, and it costs a few cents: one embedding call per chunk and per case.

What it does:

1. Reads the logs in .ideas/example_logs/ and builds an unsaved GameLog for
   each, with the fixed ids in LOGS that cases.yaml refers to.
2. Chunks each log with the app's own GameLogProcessor.process_content.
3. Embeds every chunk and every query in cases.yaml with get_embedding.
4. Writes fixtures/source_objects.json and fixtures/chunks.json, and replaces
   each case's ``query_embedding`` line in cases.yaml (the rest of the file,
   comments included, is left as it is).

Re-run it whenever chunking or embedding changes (a new chunk size, a new
processor, compiled-artifact chunks, another embedding model), so the eval
measures the pipeline as it is. To add a case, add it to cases.yaml with
``query_embedding: null`` and re-run. ``--dry-run`` shows the chunks it would
embed without calling OpenAI or writing anything.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
API_DIR = EVAL_DIR.parents[1]
EXAMPLE_LOGS_DIR = API_DIR.parent / ".ideas" / "example_logs"

# (id, file in .ideas/example_logs/, session_number). cases.yaml refers to these ids.
LOGS = [
    (1, "2019-04-04.txt", 1),
    (2, "2022-12-19.txt", 2),
    (3, "2023-06-05.txt", 3),
]

_EMBEDDING_LINE = re.compile(r"^(\s*)query_embedding:.*$")
_ID_LINE = re.compile(r"^\s*-\s*id:\s*(\S+)\s*$")


def build_logs():
    from nucleus.models import GameLog
    from place.models import Place

    logs = []
    for pk, filename, session_number in LOGS:
        date = filename.removesuffix(".txt")
        log = GameLog(
            pk=pk,
            title=f"Example log {date}",
            url=f"https://example.invalid/eval/{date}",
            google_id=f"eval-{date}",
            game_date=datetime.fromisoformat(date).replace(tzinfo=timezone.utc),
            session_number=session_number,
            full_text=(EXAMPLE_LOGS_DIR / filename).read_text(),
        )
        # No places: keeps build_metadata from querying the local database.
        log._prefetched_objects_cache = {"places_set_in": Place.objects.none()}
        logs.append(log)
    return logs


def source_object_record(log) -> dict:
    return {
        "model": "nucleus.gamelog",
        "pk": log.pk,
        "fields": {
            "title": log.title,
            "url": log.url,
            "google_id": log.google_id,
            "game_date": log.game_date.isoformat(),
            "session_number": log.session_number,
            "full_text": log.full_text,
        },
    }


def fill_query_embeddings(cases_text: str, embeddings: dict[str, list[float]]) -> str:
    """Replace each case's query_embedding line, keeping the rest of the file."""
    lines = cases_text.splitlines()
    current_id = None
    replaced = set()
    for i, line in enumerate(lines):
        if match := _ID_LINE.match(line):
            current_id = match.group(1).strip("\"'")
        elif (match := _EMBEDDING_LINE.match(line)) and current_id in embeddings:
            lines[i] = (
                f"{match.group(1)}query_embedding: {json.dumps(embeddings[current_id])}"
            )
            replaced.add(current_id)
    if replaced != set(embeddings):
        raise SystemExit(
            f"could not place query_embedding for {sorted(set(embeddings) - replaced)}; "
            "each case needs a `- id:` line and a `query_embedding:` line"
        )
    return "\n".join(lines) + "\n"


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="chunk the logs and list what would be embedded; no OpenAI calls, no writes",
    )
    args = parser.parse_args(argv)

    sys.path.insert(0, str(API_DIR))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")
    import django

    django.setup()

    from rag_chat.content_processors import GameLogProcessor
    from rag_chat.embeddings import get_embedding
    from rag_chat.eval.loaders import EMBEDDING_DIMENSIONS, GENERATED

    cases = GENERATED.load_cases()
    log_ids = {pk for pk, _, _ in LOGS}
    for case in cases:
        if case.expected_source_content_type != "gamelog":
            raise SystemExit(f"{case.id}: the generated fixtures only hold gamelogs")
        if unknown := set(case.expected_source_ids) - log_ids:
            raise SystemExit(f"{case.id}: no example log has id {sorted(unknown)}")

    logs = build_logs()
    processor = GameLogProcessor()
    chunked = [(log, processor.process_content(log)) for log in logs]

    total = sum(len(chunks) for _, chunks in chunked)
    for log, chunks in chunked:
        words = [len(text.split()) for text, _ in chunks]
        print(
            f"log {log.pk} ({log.title}): {len(chunks)} chunks, words per chunk {words}"
        )
    print(f"{total} chunks and {len(cases)} queries to embed")
    if args.dry_run:
        return

    def embed(text: str) -> list[float]:
        vector = get_embedding(text)
        if len(vector) != EMBEDDING_DIMENSIONS:
            raise SystemExit(
                f"the embeddings model returned {len(vector)} dimensions, "
                f"ContentChunk.embedding holds {EMBEDDING_DIMENSIONS}"
            )
        return vector

    chunk_records = []
    for log, chunks in chunked:
        for chunk_index, (chunk_text, metadata) in enumerate(chunks):
            chunk_records.append(
                {
                    "content_type": "nucleus.gamelog",
                    "object_id": log.pk,
                    "chunk_index": chunk_index,
                    "chunk_text": chunk_text,
                    "metadata": metadata,
                    "embedding": embed(chunk_text),
                }
            )
    query_embeddings = {case.id: embed(case.query) for case in cases}

    fixtures_dir = GENERATED.chunks_path.parent
    fixtures_dir.mkdir(exist_ok=True)
    GENERATED.source_objects_path.write_text(
        json.dumps(
            [source_object_record(log) for log in logs], indent=2, ensure_ascii=False
        )
        + "\n"
    )
    # One chunk per line keeps diffs readable when the fixtures are regenerated.
    GENERATED.chunks_path.write_text(
        "[\n"
        + ",\n".join(json.dumps(record, ensure_ascii=False) for record in chunk_records)
        + "\n]\n"
    )
    GENERATED.cases_path.write_text(
        fill_query_embeddings(GENERATED.cases_path.read_text(), query_embeddings)
    )
    print(f"wrote {GENERATED.source_objects_path.relative_to(API_DIR)}")
    print(f"wrote {GENERATED.chunks_path.relative_to(API_DIR)}")
    print(f"updated {GENERATED.cases_path.relative_to(API_DIR)}")


if __name__ == "__main__":
    main()
