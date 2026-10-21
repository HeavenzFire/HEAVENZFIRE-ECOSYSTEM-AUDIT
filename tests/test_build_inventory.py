import unittest

from scripts.build_inventory import build_inventory


def repo(repo_id, name, *, private=False, archived=False):
    return {
        "id": repo_id,
        "name": name,
        "full_name": f"owner/{name}",
        "html_url": f"https://github.com/owner/{name}",
        "default_branch": "main",
        "private": private,
        "archived": archived,
        "size": 12,
        "updated_at": "2026-10-21T00:00:00Z",
    }


class BuildInventoryTests(unittest.TestCase):
    def test_paginates_and_excludes_private_repositories(self):
        pages = {
            1: [repo(1, "public-a"), repo(2, "private-b", private=True)],
            2: [repo(3, "public-c", archived=True)],
        }
        calls = []

        def fake_fetch(username, page, per_page, token):
            calls.append((username, page, per_page, token))
            return pages.get(page, [])

        result = build_inventory(
            "owner",
            per_page=2,
            token="not-a-real-token",
            page_fetcher=fake_fetch,
            generated_at="2026-10-21T00:00:00Z",
        )
        self.assertEqual([call[1] for call in calls], [1, 2])
        self.assertEqual(result["counts"], {"public": 2, "archived": 1})
        self.assertEqual(result["source"]["private_rows_excluded"], 1)
        self.assertEqual([r["full_name"] for r in result["repositories"]], ["owner/public-a", "owner/public-c"])
        self.assertTrue(all(r["visibility"] == "public" for r in result["repositories"]))

    def test_fails_instead_of_writing_incomplete_pagination(self):
        def full_page(username, page, per_page, token):
            return [repo(page * 10 + i, f"repo-{page}-{i}") for i in range(per_page)]

        with self.assertRaisesRegex(RuntimeError, "inventory is incomplete"):
            build_inventory("owner", per_page=2, page_fetcher=full_page, max_pages=2)

    def test_rejects_invalid_user(self):
        with self.assertRaises(ValueError):
            build_inventory("owner/path", page_fetcher=lambda *args: [])


if __name__ == "__main__":
    unittest.main()
