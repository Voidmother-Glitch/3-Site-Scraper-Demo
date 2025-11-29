#Made by Voidmother-Glitch
#Website scraper made for client test. Scrapes MD5 hashes off of 3 websites. Used in research testing for a Bot Protection Service.
#All Client-Identifiable data has been removed and replaced with placeholders.
#ONLY USE ON SITES/SYSTEMS FOR WHICH YOU HAVE AUTHORIZATION
#On servers with JavaScript validation, this will result in a 403, but was still able to pull the MD5s hashes out of the pages under Bot Protection
#Includes random delays before and after loading a page to prevent uniform site interactions.
#Running the code as-is allows for 20,000 pages to be scraped in 52-58 seconds.
#Output to file, including URL, MD5 hash, and HTTP request status code.

import subprocess
import sys
import time
import random
import re
from itertools import cycle
import asyncio

# === PRE-FLIGHT PACKAGE CHECK ===
try:
    import aiohttp
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print("WARNING: Required packages not found!")
    print("Missing at least one of the following: 'aiohttp', 'requests', and 'beautifulsoup4'.")
    print("Gimme. >:(")
    print()

    choice = input("Install missing packages? (y/n): ").strip().lower()
    if choice not in ['y', 'yes']:
        print("\nINSTALLATION CANCELLED. EXTREMELY RUDE. Install manually:")
        print("    pip install aiohttp requests beautifulsoup4")
        print("Or use: python -m pip install aiohttp requests beautifulsoup4")
        exit(1)

    print("\nINSTALLING PACKAGES... please wait.")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp", "requests", "beautifulsoup4"])
        print("PACKAGES INSTALLED SUCCESSFULLY!")
        print("Restarting script...")
        print("-" * 50)
        import aiohttp
        import requests
        from bs4 import BeautifulSoup
    except Exception as install_error:
        print(f"\nINSTALLATION FAILED: {install_error}")
        print("Please install manually with the following command:")
        print("    pip install aiohttp requests beautifulsoup4")
        exit(1)

# === BOT PROTECTION EVASION ===

# List of realistic User-Agent strings
#USER_AGENTS = [
#    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.1958",
#    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Trailer/93.3.8652.5",
#    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_3_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/134.0.6998.99 Mobile/15E148 Safari/604",
#    "Mozilla/5.0 (Android 14; Mobile; rv:136.0) Gecko/136.0 Firefox/136",
#    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
#    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
#    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15",
#]
#On viewing the above agent strings, client JavaScript Validation attempted to run and loaded an alternate page saying, "Please enable JS and disable any adblockers."


#List of realistic, 'dumb' User-Agent strings
USER_AGENTS = [
    "curl/7.64.1",  # curl - no JS
    "wget/1.20.3",  # wget - no JS
    "Python-urllib/3.12",  # Python's default - no JS
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",  # Old IE - JS may be disabled
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",  # Real browser - keep for comparison
]
#This list did not fail to the JavaScript validation, likely due to appearing to be User-Agents that are incompatible with JavaScript.

# Cycle through User-Agents
user_agent_cycle = cycle(USER_AGENTS)

# DELAY CONTROL: Simulate manual interaction
USE_DELAY = True
MIN_DELAY = 0.01   # 10ms
MAX_DELAY = 0.35    # 350ms (simulate "thinking time")

# Concurrency limit - NOTE: Do not flood client server. Hard limit at 100 concurrent threads for this test.
MAX_CONCURRENT = 100  # Adjust based on server tolerance

# === ASYNC SCRAPING FUNCTION ===
async def scrape_url_async(session, url, page_count, semaphore):
    async with semaphore:  # Limit concurrent requests
        # Get next User-Agent
        headers = { 
            "User-Agent": next(user_agent_cycle),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
            "Referer": "https://example.com/", # Client URL redacted with placeholder
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "DNT": "1",  # Do Not Track
            "Upgrade-Insecure-Requests": "1",  # A real browser might set this header, worth a shot
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            #  "X-Requested-With": "XMLHttpRequest",  in case of AJAX request
            "Origin": "https://example.com/",       # in case of CORS request, Client URL redacted with placeholder
            "X-JavaScript-Enabled": "false",        # Pretend to deny JS execution

}
        #Using these headers created "close enough" HTTP requests


        # Add random delay between requests
        if USE_DELAY:
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            await asyncio.sleep(delay)

        try:
            async with session.get(url, headers=headers, timeout=10) as response:
                status_code = response.status
                html = await response.text()

                # Parse w/ BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')

                # Isolate MD5 hash (32-character hex string)
                md5_match = re.search(r'[a-fA-F0-9]{32}', html)
                md5_hash = md5_match.group(0) if md5_match else "NOT_FOUND"

                # Simulate actually looking at the page (wait a bit after scraping)
                if USE_DELAY:
                    post_delay = random.uniform(0.01, 0.05)  # 10–50ms after page load
                    await asyncio.sleep(post_delay)

                return {
                    'url': url,
                    'status_code': status_code,
                    'md5_hash': md5_hash,
                }

        except Exception as e:
            return {
                'url': url,
                'status_code': 'ERROR',
                'md5_hash': 'ERROR',
                'error': str(e)
            }

# === MAIN ASYNC FUNCTION ===
async def main():
    print("Provide 3 targets:")
    sites = []
    for i in range(3):
        url = input(f"Site {i+1}: ").strip()
        sites.append(url)

    # Define range to scrape
    start_num = 0
    # Adjust as needed
    total_pages = 20000  

    # Randomize page order
    page_numbers = list(range(total_pages))
    random.shuffle(page_numbers)

# Create aiohttp session with cookie jar
    cookie_jar = aiohttp.CookieJar()
    async with aiohttp.ClientSession(cookie_jar=cookie_jar) as session:
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)  # Limit concurrent requests
        tasks = []
        page_count = 0

        # Generate URLs in random order
        # Random order URLs helped to avoid bot protection by not creating a predictable or sequential pattern.
        for i in page_numbers:
            site_index = i % 3
            number = start_num + i
            url = f"{sites[site_index]}scraping/{number}"
            page_count += 1
            tasks.append(scrape_url_async(session, url, page_count, semaphore))

        print(f"STARTING ASYNC SCRAPE OF {total_pages} BUT WE SNEAKY...")
        start_time = time.time()

        # Run all tasks concurrently
        results = await asyncio.gather(*tasks)

        end_time = time.time()
        elapsed = end_time - start_time

        print(f"SCRAPED {len(results)} PAGES IN {elapsed:.2f} SECONDS ({len(results)/elapsed:.0f} PAGES/SEC)")

        # === OUTPUT TO FILE ===
        output_file = "scrape_results.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("=== COLLECTED DATA ===\n")
            for item in results:
                f.write(f"URL: {item['url']}\n")
                f.write(f"Status: {item['status_code']}\n")
                f.write(f"MD5: {item['md5_hash']}\n")
                f.write("-" * 50 + "\n")

        print(f"\nALL DATA SAVED TO: {output_file}")

        # Optional: Print first 10 results to console
        print("\n=== FIRST 10 RESULTS ===")
        for item in results[:10]:
            print(f"URL: {item['url']}")
            print(f"Status: {item['status_code']}")
            print(f"MD5: {item['md5_hash']}")
            print("-" * 50)

# === RUN SCRIPT ===
if __name__ == "__main__":
    asyncio.run(main())