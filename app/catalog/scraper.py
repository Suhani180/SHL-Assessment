# app/catalog/scraper.py

"""
Production-grade SHL catalog scraper.

Features:
- Pagination support
- Better selectors
- Proper metadata extraction
- SHL-only filtering
- Duplicate removal
- Semantic-friendly descriptions
- Improved skill extraction
- Improved test type extraction
"""

import json
import logging
import re
import time
from typing import Dict, List, Optional, Set

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

BASE_URL = "https://www.shl.com"

CATALOG_URL = (
    "https://www.shl.com/solutions/products/"
    "product-catalog/"
)

OUTPUT_FILE = "app/catalog/catalog.json"

REQUEST_TIMEOUT = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

# ---------------------------------------------------------
# LOGGING
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# SESSION
# ---------------------------------------------------------


def create_session() -> requests.Session:

    session = requests.Session()

    retries = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[
            429,
            500,
            502,
            503,
            504
        ]
    )

    adapter = HTTPAdapter(
        max_retries=retries
    )

    session.mount("https://", adapter)
    session.mount("http://", adapter)

    session.headers.update(HEADERS)

    return session


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------


def clean_text(text: Optional[str]) -> str:

    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def absolute_url(url: str) -> str:

    if url.startswith("http"):
        return url

    return BASE_URL + url


# ---------------------------------------------------------
# FETCH PAGE
# ---------------------------------------------------------


def fetch_page(
    session: requests.Session,
    url: str
) -> Optional[BeautifulSoup]:

    try:

        logger.info(f"Fetching: {url}")

        response = session.get(
            url,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        return BeautifulSoup(
            response.text,
            "html.parser"
        )

    except Exception as e:

        logger.error(
            f"Failed fetching {url}: {e}"
        )

        return None


# ---------------------------------------------------------
# EXTRACT PRODUCT LINKS
# ---------------------------------------------------------


def extract_product_links(
    soup: BeautifulSoup
) -> Set[str]:

    links = set()

    for a in soup.find_all("a", href=True):

        href = a["href"]

        if (
            "/products/product-catalog/view/"
            in href
        ):

            full_url = absolute_url(href)

            # Exclude job solutions
            if "job-solutions" not in full_url:

                links.add(full_url)

    return links


# ---------------------------------------------------------
# PAGINATION
# ---------------------------------------------------------


def collect_all_product_links(
    session: requests.Session
) -> List[str]:

    all_links = set()

    for page in range(0, 25):

        page_url = (
            f"{CATALOG_URL}?start={page * 12}"
        )

        soup = fetch_page(
            session,
            page_url
        )

        if not soup:
            continue

        page_links = extract_product_links(
            soup
        )

        logger.info(
            f"Page {page + 1}: "
            f"{len(page_links)} links found"
        )

        if not page_links:
            break

        all_links.update(page_links)

        time.sleep(1)

    logger.info(
        f"Total unique links: "
        f"{len(all_links)}"
    )

    return list(all_links)


# ---------------------------------------------------------
# EXTRACT PRODUCT DETAILS
# ---------------------------------------------------------


def extract_product_details(
    session: requests.Session,
    url: str
) -> Optional[Dict]:

    soup = fetch_page(session, url)

    if not soup:
        return None

    try:

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        title = ""

        title_candidates = soup.find_all(
            ["h1", "h2"]
        )

        for candidate in title_candidates:

            text = clean_text(
                candidate.get_text()
            )

            if len(text) > 3:

                title = text
                break

        # -------------------------------------------------
        # DESCRIPTION
        # -------------------------------------------------

        description = ""

        paragraphs = soup.find_all("p")

        candidate_paragraphs = []

        for p in paragraphs:

            text = clean_text(
                p.get_text()
            )

            # meaningful text only
            if len(text) > 80:

                candidate_paragraphs.append(
                    text
                )

        if candidate_paragraphs:

            description = (
                candidate_paragraphs[0]
            )

        # -------------------------------------------------
        # COMBINED TEXT
        # -------------------------------------------------

        combined_text = (
            f"{title} {description}"
        ).lower()

        # -------------------------------------------------
        # TEST TYPE
        # -------------------------------------------------

        test_type = "Unknown"

        test_type_patterns = {

            "personality": "P",

            "behavior": "P",

            "competency": "C",

            "ability": "A",

            "cognitive": "A",

            "knowledge": "K",

            "technical": "K",

            "simulation": "S"
        }

        for keyword, value in (
            test_type_patterns.items()
        ):

            if keyword in combined_text:

                test_type = value
                break

        # -------------------------------------------------
        # DURATION
        # -------------------------------------------------

        duration = ""

        duration_match = re.search(
            r"(\d+)\s*(minutes|min)",
            combined_text,
            re.IGNORECASE
        )

        if duration_match:

            duration = (
                duration_match.group(0)
            )

        # -------------------------------------------------
        # SKILLS
        # -------------------------------------------------

        skills = []

        skill_keywords = [

            "java",
            "python",
            "sql",
            "javascript",
            "cloud",
            "aws",
            "azure",
            "react",
            "node",
            "cybersecurity",
            "data analysis",
            "machine learning",
            "leadership",
            "communication",
            "problem solving",
            "analytical",
            "numerical",
            "cognitive",
            "sales",
            "customer service",
            "software development",
            "backend",
            "frontend",
            "accounting",
            "finance",
            "management",
            "personality"
        ]

        for keyword in skill_keywords:

            if keyword in combined_text:

                skills.append(
                    keyword.title()
                )

        skills = sorted(
            list(set(skills))
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not title:

            return None

        return {

            "name": title,

            "description": description,

            "url": url,

            "test_type": test_type,

            "duration": duration,

            "skills": skills
        }

    except Exception as e:

        logger.error(
            f"Error parsing {url}: {e}"
        )

        return None


# ---------------------------------------------------------
# REMOVE DUPLICATES
# ---------------------------------------------------------


def remove_duplicates(
    items: List[Dict]
) -> List[Dict]:

    unique = []

    seen = set()

    for item in items:

        key = item["url"]

        if key not in seen:

            seen.add(key)

            unique.append(item)

    return unique


# ---------------------------------------------------------
# SAVE JSON
# ---------------------------------------------------------


def save_catalog(
    data: List[Dict]
):

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )

    logger.info(
        f"Saved {len(data)} assessments."
    )


# ---------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------


def scrape_shl_catalog():

    session = create_session()

    logger.info(
        "Collecting SHL assessment links..."
    )

    product_links = collect_all_product_links(
        session
    )

    assessments = []

    for idx, url in enumerate(product_links):

        logger.info(
            f"[{idx + 1}/"
            f"{len(product_links)}] "
            f"Scraping: {url}"
        )

        assessment = extract_product_details(
            session,
            url
        )

        if assessment:

            assessments.append(
                assessment
            )

        # polite delay
        time.sleep(1)

    assessments = remove_duplicates(
        assessments
    )

    save_catalog(assessments)

    logger.info(
        "SHL catalog scraping completed."
    )


# ---------------------------------------------------------
# ENTRYPOINT
# ---------------------------------------------------------

if __name__ == "__main__":

    scrape_shl_catalog()