# 3-Site-Scraper-Demo
[DEMO] De-identified code sample from a client test of Bot Protection on three parallel websites.

Client requested test of Bot Protection capabilities. Test was configured with three parallel servers.
Victory condition was to scrape 20,000 pages in less than a minute without triggering an auto-ban from their Bot Protection.
Earliest versions completed the scrape in as little at 13 seconds, but triggered Bot Protection bans.
To throw off Bot Protection, this version includes failsified HTTP request headers, a cycling list of User-Agent Headers, and a random delay before and after each request.
Final product was able to complete the scan in 52-58 seconds without triggering Bot Protection.
