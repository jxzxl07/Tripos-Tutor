"""
For each course, fetches its 'questions sorted by topic' page, extracts the
public question PDF links, and saves them to data/papers/<course>/<year>/.
"""
import re
import time
from pathlib import Path
import httpx
from bs4 import BeautifulSoup

BASE = "https://www.cl.cam.ac.uk/teaching/exams/pastpapers"
OUT = Path("data/papers")
YEAR_MIN, YEAR_MAX = 2015, 2026
DELAY = 0.5

# Map a clean folder name -> the topic-page slug used in t-<slug>.html
# (slug = course name with spaces removed, punctuation stripped)
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

# Matches a public question PDF and captures (year, paper, question)
QUESTION_RE = re.compile(r"y(\d{4})p(\d+)q(\d+)\.pdf$")

def process_course(client: httpx.Client, folder: str, slug: str) -> tuple[int, int]:
    """Fetch one course's topic page, download its in-range question PDFs."""
    page_url = f"{BASE}/t-{slug}.html"
    resp = client.get(page_url)
    if resp.status_code != 200:
        print(f"  !! could not fetch topic page for {folder} ({resp.status_code})")
        return (0, 0)

    soup = BeautifulSoup(resp.text, "html.parser")
    got = skipped = 0

    for link in soup.find_all("a", href=True):
        m = QUESTION_RE.search(link["href"])
        if not m:
            continue                       # not a question PDF (nav link, solution, etc.)
        year, paper, q = int(m.group(1)), m.group(2), m.group(3)
        if not (YEAR_MIN <= year <= YEAR_MAX):
            continue                       # outside our window

        url = f"{BASE}/y{year}p{paper}q{q}.pdf"   # rebuild absolute URL from parts
        dest = OUT / folder / str(year) / f"p{paper}q{q}.pdf"

        if dest.exists():
            skipped += 1
            continue

        pdf = client.get(url)
        if pdf.status_code != 200:
            print(f"    skip {url} ({pdf.status_code})")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(pdf.content)
        got += 1
        print(f"    got {folder}/{year}/p{paper}q{q}.pdf")
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
    print(f"\nDone. downloaded={total_got}  skipped(existing)={total_skipped}")

if __name__ == "__main__":
    main()