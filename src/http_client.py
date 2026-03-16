"""
Resilient HTTP client with retry logic, rotating user-agents,
and adaptive rate-limiting to respect the target site.
"""

import time
import random
import logging

import requests
from fake_useragent import UserAgent

from src.config import (
    DEFAULT_HEADERS,
    MAX_RETRIES,
    REQUEST_DELAY_RANGE,
    REQUEST_TIMEOUT,
    RETRY_BACKOFF,
)

logger = logging.getLogger(__name__)

_ua = UserAgent(fallback="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")


class ResilientClient:
    """HTTP client that handles retries, back-off, and header rotation."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self._last_request_ts = 0.0

    def _rotate_ua(self):
        self.session.headers["User-Agent"] = _ua.random

    def _polite_wait(self):
        """Enforce a randomised delay between consecutive requests."""
        elapsed = time.time() - self._last_request_ts
        delay = random.uniform(*REQUEST_DELAY_RANGE)
        if elapsed < delay:
            time.sleep(delay - elapsed)

    def get(self, url: str) -> requests.Response | None:
        """
        GET with exponential back-off on transient errors.
        Returns None when all retries are exhausted.
        """
        self._rotate_ua()

        for attempt in range(1, MAX_RETRIES + 1):
            self._polite_wait()
            try:
                resp = self.session.get(url, timeout=REQUEST_TIMEOUT)
                self._last_request_ts = time.time()

                if resp.status_code == 200:
                    return resp

                if resp.status_code == 429:
                    wait = RETRY_BACKOFF * (2 ** attempt) + random.uniform(0, 2)
                    logger.warning("Rate-limited (429). Sleeping %.1fs …", wait)
                    time.sleep(wait)
                    continue

                if resp.status_code >= 500:
                    logger.warning("Server error %d on attempt %d", resp.status_code, attempt)
                    time.sleep(RETRY_BACKOFF * attempt)
                    continue

                logger.error("Unexpected status %d for %s", resp.status_code, url)
                return None

            except requests.RequestException as exc:
                logger.warning("Request failed (attempt %d/%d): %s", attempt, MAX_RETRIES, exc)
                time.sleep(RETRY_BACKOFF * attempt)

        logger.error("All %d retries exhausted for %s", MAX_RETRIES, url)
        return None

    def close(self):
        self.session.close()
