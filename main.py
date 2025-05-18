import asyncio
from pyppeteer import launch
import os
import random
import json

# Load config
with open("config.json", "r", encoding="utf-8") as cfg:
    config = json.load(cfg)

CHROMIUM_PATH = config.get("CHROMIUM_PATH")
MAX_PROFILE_ID = config.get("MAX_PROFILE_ID")
OUTPUT_FILE = "users.txt"

async def scrape_roblox_profiles_puppeteer(attempts: int):
    if not os.path.exists(CHROMIUM_PATH):
        print(f"Chromium-based browser not found at: {CHROMIUM_PATH}")
        return

    browser = await launch(
        headless=True,
        executablePath=CHROMIUM_PATH,
        args=["--no-sandbox"]
    )
    page = await browser.newPage()

    successful_scrapes = 0
    tried_ids = set()

    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        while successful_scrapes < attempts:
            current_id = random.randint(1, MAX_PROFILE_ID)

            if current_id in tried_ids:
                continue
            tried_ids.add(current_id)

            url = f"https://www.roblox.com/users/{current_id}"
            try:
                await page.goto(url, {'waitUntil': 'domcontentloaded'})
                await asyncio.sleep(1)

                error_element = await page.querySelector("div.message-container")
                if error_element:
                    continue

                username_elem = await page.querySelector("span.profile-header-username")
                nickname_elem = await page.querySelector(
                    "span.web-blox-css-tss-1sr4lqx-Typography-h1-Typography-root"
                )

                if username_elem:
                    username = await page.evaluate('(el) => el.textContent', username_elem)
                    username = username.strip().lstrip("@")

                    if nickname_elem:
                        nickname = await page.evaluate('(el) => el.textContent', nickname_elem)
                        nickname = nickname.strip()
                    else:
                        nickname = username

                    line = f"{nickname} ({username}) | {url}"
                    print(f"[{successful_scrapes + 1}/{attempts}] {line}")
                    f.write(line + "\n")
                    f.flush()

                    successful_scrapes += 1

                await asyncio.sleep(1)
            except Exception as e:
                print(f"Error on ID {current_id}: {e}")

    await browser.close()
    print(f"Done. {successful_scrapes} profiles written to {OUTPUT_FILE}")

if __name__ == "__main__":
    try:
        raw_input = input("How many profiles to attempt? (default 500): ").strip()
        attempts = int(raw_input) if raw_input else 500
        asyncio.get_event_loop().run_until_complete(
            scrape_roblox_profiles_puppeteer(attempts)
        )
    except KeyboardInterrupt:
        print("\nScript interrupted by user.")
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write("\n")
            f.flush()
