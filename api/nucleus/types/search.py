from typing import List, Optional

import strawberry
from strawberry import relay

from nucleus import search

EntityType = strawberry.enum(search.EntityType, name="EntityType")


@strawberry.type
class SearchHit:
    id: relay.GlobalID
    name: str
    type: EntityType
    description: Optional[str]
    thumbnail: Optional[str]


@strawberry.type
class SearchQuery:
    @strawberry.field(
        description=(
            "Entities whose name or an alias matches the query, best first: exact, "
            "then prefix, then substring, then trigram similarity (for typos)."
        )
    )
    def search(
        self,
        query: str,
        types: Optional[List[EntityType]] = None,
        limit: int = search.DEFAULT_LIMIT,
    ) -> List[SearchHit]:
        return [
            SearchHit(
                id=relay.GlobalID(hit.type.value, str(hit.pk)),
                name=hit.name,
                type=hit.type,
                description=hit.description,
                thumbnail=hit.thumbnail,
            )
            for hit in search.search_entities(query, types=types, limit=limit)
        ]
