import logging

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.services import music

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)


class SearchResponse(BaseModel):
    id: str
    title: str
    artist: str
    thumbnail: str | None
    duration: int | None


@router.post("/search", response_model=SearchResponse)
async def search(req: SearchRequest):
    try:
        result = music.search(req.query)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Search failed for query: %s", req.query)
        raise HTTPException(
            status_code=500,
            detail="The jukebox jammed. Try again.",
        )

    return SearchResponse(
        id=result.id,
        title=result.title,
        artist=result.artist,
        thumbnail=result.thumbnail,
        duration=result.duration,
    )


@router.get("/stream/{search_id}")
async def stream(search_id: str, request: Request):
    result = music.get_result(search_id)
    if not result:
        raise HTTPException(status_code=404, detail="Track not found or expired. Search again.")

    if not result.stream_url:
        raise HTTPException(status_code=500, detail="No stream URL available.")

    # Forward range headers from browser to upstream
    upstream_headers = {}
    range_header = request.headers.get("range")
    if range_header:
        upstream_headers["Range"] = range_header

    # Make upstream request and forward response headers + status
    client = httpx.AsyncClient(follow_redirects=True, timeout=120.0)
    upstream = await client.send(
        client.build_request("GET", result.stream_url, headers=upstream_headers),
        stream=True,
    )

    # Pick headers to forward from YouTube's response
    forward_headers = {}
    for key in ("content-length", "content-range", "accept-ranges", "content-type"):
        if key in upstream.headers:
            forward_headers[key] = upstream.headers[key]
    forward_headers["cache-control"] = "no-cache"

    content_type = upstream.headers.get("content-type", "audio/webm")
    status_code = upstream.status_code  # 200 or 206 for range requests

    async def _proxy():
        try:
            async for chunk in upstream.aiter_bytes(chunk_size=65536):
                yield chunk
        finally:
            await upstream.aclose()
            await client.aclose()

    return StreamingResponse(
        _proxy(),
        status_code=status_code,
        media_type=content_type,
        headers=forward_headers,
    )
