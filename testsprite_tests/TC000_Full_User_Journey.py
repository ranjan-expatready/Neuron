import asyncio
import uuid
from pathlib import Path

from config import TEST_USER_EMAIL, TEST_USER_PASSWORD, UI_BASE_URL
from playwright import async_api
from playwright.async_api import expect

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
DOCUMENT_PATH = ASSETS_DIR / "sample-document.txt"


async def run_test():
    pw = await async_api.async_playwright().start()
    browser = await pw.chromium.launch(
        headless=True,
        args=[
            "--window-size=1280,720",
            "--disable-dev-shm-usage",
            "--ipc=host",
            "--single-process",
        ],
    )
    context = await browser.new_context()
    context.set_default_timeout(15000)
    page = await context.new_page()

    try:
        await page.goto(f"{UI_BASE_URL}/auth/login", wait_until="networkidle", timeout=20000)

        await page.get_by_test_id("login-email").fill(TEST_USER_EMAIL)
        await page.get_by_test_id("login-password").fill(TEST_USER_PASSWORD)
        await page.get_by_test_id("login-submit").click()

        await page.wait_for_url(f"{UI_BASE_URL}/dashboard", timeout=20000)
        await expect(page.get_by_test_id("dashboard-title")).to_be_visible()
        await expect(page.locator("text=Welcome,")).to_contain_text("Welcome")

        await page.get_by_test_id("dashboard-new-case").click()
        await page.wait_for_url(f"{UI_BASE_URL}/cases/new", timeout=15000)

        suffix = uuid.uuid4().hex[:8]
        case_title = f"Automation Case {suffix}"
        person_first = f"Test{suffix}"
        person_last = f"Client{suffix}"
        document_title = f"Test Document {suffix}"

        await page.get_by_test_id("new-case-person-first-name").fill(person_first)
        await page.get_by_test_id("new-case-person-last-name").fill(person_last)
        await page.get_by_test_id("new-case-person-email").fill(f"{suffix}@example.com")
        await page.get_by_test_id("new-case-title").fill(case_title)
        await page.get_by_test_id("new-case-type").fill("EXPRESS_ENTRY_FSW")
        await page.get_by_test_id("new-case-description").fill("Canonical E2E journey case")
        await page.get_by_test_id("new-case-submit").click()

        await expect(page.get_by_test_id("case-detail-title")).to_have_text(
            case_title, timeout=20000
        )

        await page.get_by_test_id("case-detail-tab-documents").click()
        await page.get_by_test_id("case-detail-upload-link").click()
        await page.wait_for_url("**/upload", timeout=15000)

        await page.get_by_test_id("upload-document-type").select_option("passport")
        await page.get_by_test_id("upload-title").fill(document_title)
        await page.get_by_test_id("upload-description").fill(
            "Test document uploaded via Playwright"
        )
        await page.get_by_test_id("upload-file-input").set_input_files(str(DOCUMENT_PATH))
        await page.get_by_test_id("upload-submit").click()

        await page.wait_for_url("**/cases/*", timeout=20000)
        await expect(page.get_by_test_id("case-detail-title")).to_have_text(
            case_title, timeout=20000
        )

        await page.get_by_test_id("case-detail-tab-documents").click()
        await expect(page.locator("[data-testid='case-documents-table']")).to_contain_text(
            document_title, timeout=20000
        )
    finally:
        await context.close()
        await browser.close()
        await pw.stop()


asyncio.run(run_test())
