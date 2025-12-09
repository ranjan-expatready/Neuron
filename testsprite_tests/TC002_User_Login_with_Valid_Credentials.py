import asyncio

from config import TEST_USER_EMAIL, TEST_USER_PASSWORD, UI_BASE_URL
from playwright import async_api
from playwright.async_api import expect


async def run_test():
    pw = None
    browser = None
    context = None

    try:
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
        context.set_default_timeout(10000)
        page = await context.new_page()

        await page.goto(f"{UI_BASE_URL}/auth/login", wait_until="networkidle", timeout=15000)

        await page.get_by_test_id("login-email").fill(TEST_USER_EMAIL)
        await page.get_by_test_id("login-password").fill(TEST_USER_PASSWORD)
        await page.get_by_test_id("login-submit").click()

        await page.wait_for_url(f"{UI_BASE_URL}/dashboard", timeout=20000)
        await expect(page.get_by_role("heading", name="Canada Immigration OS")).to_be_visible()
        await expect(page.locator("text=Welcome, TestSprite Automation")).to_be_visible()
    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()


asyncio.run(run_test())
