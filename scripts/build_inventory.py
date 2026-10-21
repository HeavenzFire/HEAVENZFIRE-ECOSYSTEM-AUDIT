#!/usr/bin/env python3
"""Build a public-only GitHub repository inventory using the REST API.

Uses only the Python standard library. Set GITHUB_TOKEN or GH_TOKEN to
increase rate limits. Private repository metadata is always excluded.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


API_ROOT = "https://api.github.com"
USER_RE = re.compile(r"^[A-Za-z0-9-]{1,39}$")


def fetch_page(username: str, page: int, per_page: int, token: str | None) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode({
        "type": "owner",
        "sort": "updated",
        "direction": "desc",
        "per_page": per_page,
        "page": page,
    })
    request = urllib.request.Request(
        f"{API_ROOT}/users/{urllib.parse.quote(username, safe='')}/repos?{query}",
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "HeavenzFire-Ecosystem-Audit/1.0",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # Do not include request headers or tokens in diagnostics.
        raise RuntimeError(f"GitHub API returned HTTP {exc.code} on page {page}") from None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"GitHub API request failed on page {page}: {type(exc).__name__}") from None
    if not isinstance(payload, list):
        raise RuntimeError(f"Unexpected GitHub API response type on page {page}")
    return payload


def build_inventory(
    username: str,
    per_page: int = 100,
    token: str | None = None,
    page_fetcher: Callable[[str, int, int, str | None], list[dict[str, Any]]] = fetch_page,
    generated_at: str | None = None,
    max_pages: int = 100,
) -> dict[str, Any]:
    if not USER_RE.fullmatch(username):
        raise ValueError("username must be a valid GitHub account name")
    if not 1 <= per_page <= 100:
        raise ValueError("per_page must be between 1 and 100")
    if max_pages < 1:
        raise ValueError("max_pages must be positive")

    rows: list[dict[str, Any]] = []
    pages_read = 0
    for page in range(1, max_pages + 1):
        batch = page_fetcher(username, page, per_page, token)
        pages_read += 1
        rows.extend(batch)
        if len(batch) < per_page:
            break
    else:
        raise RuntimeError(
            f"Pagination reached max_pages={max_pages}; inventory is incomplete and was not written"
        )

    public: dict[str, dict[str, Any]] = {}
    private_excluded = 0
    missing_identity = 0
    for repo in rows:
        if repo.get("private") is True or repo.get("visibility") == "private":
            private_excluded += 1
            continue
        full_name = repo.get("full_name")
        repo_id = repo.get("id")
        if not full_name or repo_id is None:
            missing_identity += 1
            continue
        public[str(full_name)] = {
            "id": str(repo_id),
            "name": repo.get("name", ""),
            "full_name": str(full_name),
            "html_url": repo.get("html_url", ""),
            "default_branch": repo.get("default_branch"),
            "visibility": "public",
            "archived": bool(repo.get("archived", False)),
            "size_kb": repo.get("size") if isinstance(repo.get("size"), int) else None,
            "updated_at": repo.get("updated_at"),
        }

    repositories = sorted(public.values(), key=lambda item: item["full_name"].casefold())
    timestamp = generated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "schema_version": 1,
        "generated_at_utc": timestamp,
        "source": {
            "integration": "GitHub REST API",
            "endpoint": f"{API_ROOT}/users/{username}/repos",
            "query": {"type": "owner", "sort": "updated", "direction": "desc"},
            "pages_read": pages_read,
            "page_size": per_page,
            "raw_rows_returned": len(rows),
            "private_rows_excluded": private_excluded,
            "rows_missing_identity": missing_identity,
            "unique_public_repositories": len(repositories),
            "completeness": "Complete only for the API response and permissions available to this run; private repositories are intentionally excluded. API errors or pagination caps fail the run rather than writing a partial snapshot.",
        },
        "counts": {
            "public": len(repositories),
            "archived": sum(1 for repo in repositories if repo["archived"]),
        },
        "repositories": repositories,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", default="HeavenzFire", help="GitHub account login")
    parser.add_argument("--output", default="inventory/repositories.json", help="Output JSON path")
    parser.add_argument("--per-page", type=int, default=100)
    parser.add_argument("--max-pages", type=int, default=100)
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    try:
        inventory = build_inventory(args.user, args.per_page, token, max_pages=args.max_pages)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"inventory failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps({
        "output": str(output),
        "generated_at_utc": inventory["generated_at_utc"],
        "pages_read": inventory["source"]["pages_read"],
        "raw_rows_returned": inventory["source"]["raw_rows_returned"],
        "private_rows_excluded": inventory["source"]["private_rows_excluded"],
        "public_repositories": inventory["counts"]["public"],
        "archived_public_repositories": inventory["counts"]["archived"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
