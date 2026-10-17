import os
import re

import pytest
from playwright.sync_api import Page, expect


def task_item(page: Page, text: str):
    return page.locator("li.task", has_text=text)


def create_task(page: Page, title: str, description: str = ""):
    page.goto("/")
    page.get_by_title("Add task").click()
    expect(page).to_have_url(re.compile(r"/tasks/new$"))
    page.locator('input[name="title"]').fill(title)
    page.locator('textarea[name="description"]').fill(description)
    page.get_by_role("button", name="Save task").click()
    expect(page).to_have_url(re.compile(r"/$"))


@pytest.fixture
def title(prefix):
    return f"{prefix} task"


# ---------- create ----------


def test_create_task_appears_in_the_list_as_pending(page, title):
    create_task(page, title, "created by the end-to-end test")

    item = task_item(page, title)
    expect(item).to_be_visible()
    expect(item).to_contain_text("created by the end-to-end test")
    expect(item.locator(".status")).to_have_text("Pending")


def test_task_cannot_be_saved_without_a_title(page):
    page.goto("/tasks/new")

    page.get_by_role("button", name="Save task").click()

    # the browser blocks the empty form, so we stay on the same page
    expect(page).to_have_url(re.compile(r"/tasks/new$"))


def test_cancel_on_the_new_task_page_returns_to_the_list(page):
    page.goto("/tasks/new")

    page.get_by_role("button", name="Cancel").click()

    expect(page).to_have_url(re.compile(r"/$"))
    expect(page.get_by_role("heading", name="Tasks")).to_be_visible()


# ---------- status ----------


def test_task_moves_through_its_statuses(page, title):
    create_task(page, title)
    item = task_item(page, title)
    status = item.locator(".status")

    item.get_by_role("button", name="Start").click()
    expect(status).to_have_text("In progress")

    item.get_by_role("button", name="Complete").click()
    expect(status).to_have_text("Complete")
    expect(item).to_have_class(re.compile(r"task-complete"))

    item.get_by_role("button", name="Undo").click()
    expect(status).to_have_text("Pending")
    expect(item).not_to_have_class(re.compile(r"task-complete"))


# ---------- edit ----------


def test_edit_task_changes_title_description_and_status(page, title):
    create_task(page, title, "before")
    new_title = f"{title} (edited)"

    task_item(page, title).get_by_role("link", name="Edit").click()
    expect(page).to_have_url(re.compile(r"/tasks/\d+/edit$"))
    page.locator("#title").fill(new_title)
    page.locator("#description").fill("after")
    page.locator("#status").select_option("in_progress")
    page.get_by_role("button", name="Save changes").click()

    expect(page).to_have_url(re.compile(r"/$"))
    item = task_item(page, new_title)
    expect(item).to_be_visible()
    expect(item).to_contain_text("after")
    expect(item.locator(".status")).to_have_text("In progress")


# ---------- delete ----------


def test_delete_task_removes_it_after_confirmation(page, title):
    create_task(page, title)
    item = task_item(page, title)

    item.get_by_role("button", name="Delete").click()
    dialog = page.locator("#delete-dialog")
    expect(dialog).to_be_visible()
    expect(page.locator("#delete-title")).to_have_text(title)
    dialog.get_by_role("button", name="Delete").click()

    expect(item).to_have_count(0)


def test_cancelling_the_delete_dialog_keeps_the_task(page, title):
    create_task(page, title)
    item = task_item(page, title)

    item.get_by_role("button", name="Delete").click()
    expect(page.locator("#delete-dialog")).to_be_visible()
    page.locator("#delete-cancel").click()

    expect(page.locator("#delete-dialog")).not_to_be_visible()
    expect(item).to_be_visible()


# ---------- version, environment and health ----------


def test_footer_shows_version_and_environment(page):
    page.goto("/")

    version = page.get_by_test_id("app-version")
    environment = page.locator("footer.site-footer code").nth(1)
    expect(version).to_have_text(re.compile(r".+"))
    expect(environment).to_have_text(re.compile(r".+"))

    # optional: the pipeline can state what it expects to be live
    expected_version = os.environ.get("E2E_EXPECTED_VERSION")
    if expected_version:
        expect(version).to_have_text(expected_version)
    expected_env = os.environ.get("E2E_EXPECTED_ENV")
    if expected_env:
        expect(environment).to_have_text(expected_env)


def test_health_endpoint_reports_a_healthy_app(page):
    response = page.goto("/health")

    assert response is not None
    assert response.status == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "connected"
    assert body["version"]
    assert body["environment"]