import os
import uuid

import pytest
from playwright.sync_api import expect

if not os.environ.get("PYTEST_BASE_URL"):
    collect_ignore_glob = ["test_*.py"]


@pytest.fixture
def prefix(page):
    """A unique label for this test's tasks; anything using it is cleaned up.

    The tests run against a shared environment, so every task they create
    carries this prefix and is deleted through the UI afterwards, even if
    the test failed part-way through.
    """
    label = f"e2e-{uuid.uuid4().hex[:8]}"
    yield label

    page.goto("/")
    items = page.locator("li.task", has_text=label)
    for _ in range(10):
        remaining = items.count()
        if remaining == 0:
            break
        items.first.get_by_role("button", name="Delete").click()
        page.locator("#delete-dialog").get_by_role("button", name="Delete").click()
        try:
            expect(items).to_have_count(remaining - 1)
        except AssertionError:
            break  