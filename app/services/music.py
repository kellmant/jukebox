import hashlib
import json
import logging
import os
import re
import tempfile
import time
from dataclasses import asdict, dataclass

import yt_dlp

logger = logging.getLogger(__name__)

MAX_QUERY_LENGTH = 200
CACHE_TTL_SECONDS = 300  # 5 minutes
CACHE_DIR = os.path.join(tempfile.gettempdir(), "jukebox_cache")


@dataclass
class SearchResult:
    id: str
    title: str
    artist: str
    thumbnail: str | None
    duration: int | None
    stream_url: str
    expires_at: float


# File-based cache so all gunicorn workers can share results
os.makedirs(CACHE_DIR, exist_ok=True)


def _cache_put(search_id: str, result: SearchResult) -> None:
    path = os.path.join(CACHE_DIR, f"{search_id}.json")
    with open(path, "w") as f:
        json.dump(asdict(result), f)


def _cache_get(search_id: str) -> SearchResult | None:
    path = os.path.join(CACHE_DIR, f"{search_id}.json")
    try:
        with open(path) as f:
            data = json.load(f)
        result = SearchResult(**data)
        if result.expires_at > time.time():
            return result
        os.unlink(path)
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        pass
    return None


def _sanitize_query(query: str) -> str:
    """Strip dangerous characters, limit length."""
    query = query.strip()[:MAX_QUERY_LENGTH]
    # Remove shell metacharacters but keep musical characters like & and '
    query = re.sub(r'[;`$|><\\{}]', '', query)
    return query


def _make_id(query: str) -> str:
    return hashlib.sha256(query.lower().encode()).hexdigest()[:12]


def search(query: str) -> SearchResult:
    """Search for a track and extract its audio stream URL."""
    query = _sanitize_query(query)
    if not query:
        raise ValueError("Empty search query")

    search_id = _make_id(query)

    # Return cached result if still valid
    cached = _cache_get(search_id)
    if cached:
        logger.info("Cache hit for query: %s", query)
        return cached

    # Determine search term
    if "youtube.com" in query or "youtu.be" in query:
        search_term = query
    else:
        search_term = f"ytsearch:{query} audio"

    opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'noplaylist': True,
    }

    logger.info("Searching for: %s", query)

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(search_term, download=False)

    # ytsearch returns entries list, direct URLs return the info directly
    if 'entries' in info:
        entries = list(info['entries'])
        if not entries:
            raise ValueError(f"No results found for: {query}")
        entry = entries[0]
    else:
        entry = info

    result = SearchResult(
        id=search_id,
        title=entry.get('title', query),
        artist=entry.get('artist') or entry.get('uploader') or 'Unknown',
        thumbnail=entry.get('thumbnail'),
        duration=entry.get('duration'),
        stream_url=entry.get('url', ''),
        expires_at=time.time() + CACHE_TTL_SECONDS,
    )

    _cache_put(search_id, result)
    logger.info("Found: %s by %s", result.title, result.artist)
    return result


def get_result(search_id: str) -> SearchResult | None:
    """Retrieve a cached search result by ID."""
    return _cache_get(search_id)


def refresh_stream_url(search_id: str) -> SearchResult | None:
    """Re-extract stream URL for an expired result."""
    cached = _cache_get(search_id)
    if not cached:
        return None
    # Re-search using the original title
    return search(cached.title)
