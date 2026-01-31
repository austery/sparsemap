from playwright.sync_api import sync_playwright, expect


def verify_frontend_fix():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Navigate to the app
            page.goto("http://localhost:8003")

            # Check if title is correct
            expect(page).to_have_title("SparseMap - 高信号知识图谱")

            # Check for input screen visibility
            expect(page.locator("#input-screen")).to_be_visible()

            # Interact with tabs
            page.click("button[data-tab='text']")
            expect(page.locator("#text-input-group")).to_be_visible()
            expect(page.locator("#url-input-group")).not_to_be_visible()

            page.click("button[data-tab='url']")
            expect(page.locator("#url-input-group")).to_be_visible()
            expect(page.locator("#text-input-group")).not_to_be_visible()

            # Take a screenshot
            page.screenshot(path="verification/frontend_fix.png")
            print("Screenshot saved to verification/frontend_fix.png")

        except Exception as e:
            print(f"Verification failed: {e}")
        finally:
            browser.close()


if __name__ == "__main__":
    verify_frontend_fix()
