"""
Downloads PUBLIC solution notes (mark schemes) for Part IB courses, into
data/papers/<course>/<year>/pPqQ-solution.pdf — matching the question layout.

Uses each link's own href directly (no URL reconstruction) and validates that
the response is a real PDF, so 404 pages / restricted notes are skipped, not saved.
Public notes only: 2025/2026 are Raven-locked and excluded by the year filter.
"""
import re
import time
from pathlib import Path
import httpx
from bs4 import BeautifulSoup

BASE_SITE = "https://www.cl.cam.ac.uk"
TOPIC_BASE = f"{BASE_SITE}/teaching/exams/pastpapers"
OUT = Path("data/papers")
YEAR_MIN, YEAR_MAX = 2015, 2024      # public notes only — stop at 2024
DELAY = 0.5

COURSES = {
    "Concurrent-and-Distributed-Systems": "ConcurrentandDistributedSystems",
    "Data-Science":                        "DataScience",
    "Economics-Law-and-Ethics":            "EconomicsLawandEthics",
    "Further-Graphics":                    "FurtherGraphics",
    "Introduction-to-Computer-Architecture": "IntroductiontoComputerArchitecture",
    "Programming-in-C-and-C++":            "ProgramminginCandC++",
    "Compiler-Construction":               "CompilerConstruction",
    "Computation-Theory":                  "ComputationTheory",
    "Computer-Networking":                 "ComputerNetworking",
    "Further-HCI":                         "FurtherHuman-ComputerInteraction",
    "Logic-and-Proof":                     "LogicandProof",
    "Prolog":                              "Prolog",
    "Semantics-of-Programming-Languages":  "SemanticsofProgrammingLanguages",
    "Artificial-Intelligence":             "ArtificialIntelligence",
    "Complexity-Theory":                   "ComplexityTheory",
    "Cybersecurity":                       "Cybersecurity",
    "Formal-Models-of-Language":           "FormalModelsofLanguage",
}

# Captures (year, paper, question) from a solution href, for naming the saved file.
# Matches e.g. .../solutions/2024/2024-p05-q04-solutions.pdf
SOLUTION_RE = re.compile(r"/solutions/\d{4}/(\d{4})-p(\d+)-q(\d+)-solutions\.pdf", re.I)


def process_course(client: httpx.Client, folder: str, slug: str) -> tuple[int, int]:
    page_url = f"{TOPIC_BASE}/t-{slug}.html"
    resp = client.get(page_url)
    if resp.status_code != 200:
        print(f"  !! could not fetch topic page for {folder} ({resp.status_code})")
        return (0, 0)

    soup = BeautifulSoup(resp.text, "html.parser")
    got = skipped = 0

    for link in soup.find_all("a", href=True):
        href = link["href"]
        m = SOLUTION_RE.search(href)
        if not m:
            continue                          # not a solution link
        year, paper, q = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if not (YEAR_MIN <= year <= YEAR_MAX):
            continue                          # skips 2025/2026 locked years automatically

        # Use the page's OWN href directly — never reconstruct the URL.
        sol_url = href if href.startswith("http") else f"{BASE_SITE}{href}"

        dest = OUT / folder / str(year) / f"p{paper}q{q}-solution.pdf"
        if dest.exists():
            skipped += 1
            continue

        r = client.get(sol_url)
        if r.status_code != 200:
            print(f"    skip {sol_url} ({r.status_code})")
            continue

        # Validate it's a real PDF, not an HTML 404/restricted page served at 200.
        if not r.content.startswith(b"%PDF"):
            print(f"    not a PDF, skipping {sol_url}")
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(r.content)
        got += 1
        print(f"    got {folder}/{year}/p{paper}q{q}-solution.pdf")
        time.sleep(DELAY)

    return (got, skipped)


def main():
    total_got = total_skipped = 0
    with httpx.Client(timeout=30, follow_redirects=True) as client:
        for folder, slug in COURSES.items():
            print(f"\n== {folder} ==")
            got, skipped = process_course(client, folder, slug)
            total_got += got
            total_skipped += skipped
            time.sleep(DELAY)
    print(f"\nDone. solutions downloaded={total_got}  skipped(existing)={total_skipped}")


if __name__ == "__main__":
    main()