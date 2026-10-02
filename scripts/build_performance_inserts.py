# VERSION 3 - substitutes + leading-zero date fix + progress output
# Builds INSERT statements for [Wsoc.Performance] from umterps.com box scores.
# Setup:  pip install requests beautifulsoup4
# Run:    python build_performance_inserts.py
# Output: performance_inserts.sql (plus a check report printed to the screen)

import re
import time
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}
SEASON_PAGES = {
    "2019": "https://umterps.com/sports/womens-soccer/stats/2019",
    "2020": "https://umterps.com/sports/womens-soccer/stats/2020",
    "2021": "https://umterps.com/sports/womens-soccer/stats/2021",
}

# Game date -> gameId (matches the Games insert)
GAME_IDS = {
    "8/22/2019": "01", "8/25/2019": "02", "8/30/2019": "03", "9/1/2019": "04",
    "9/5/2019": "05", "9/8/2019": "06", "9/12/2019": "07", "9/15/2019": "08",
    "9/20/2019": "09", "9/22/2019": "10", "9/28/2019": "11", "10/3/2019": "12",
    "10/6/2019": "13", "10/11/2019": "14", "10/13/2019": "15", "10/17/2019": "16",
    "10/20/2019": "17", "10/24/2019": "18", "10/27/2019": "19", "11/3/2019": "20",
    "2/20/2021": "21", "2/25/2021": "22", "2/28/2021": "23", "3/4/2021": "24",
    "3/7/2021": "25", "3/13/2021": "26", "3/18/2021": "27", "3/21/2021": "28",
    "3/25/2021": "29", "3/28/2021": "30", "4/3/2021": "31", "4/8/2021": "32",
    "8/19/2021": "33", "8/22/2021": "34", "8/26/2021": "35", "8/29/2021": "36",
    "9/2/2021": "37", "9/5/2021": "38", "9/9/2021": "39", "9/12/2021": "40",
    "9/19/2021": "41", "9/23/2021": "42", "9/26/2021": "43", "9/30/2021": "44",
    "10/3/2021": "45", "10/8/2021": "46", "10/14/2021": "47", "10/17/2021": "48",
    "10/21/2021": "49",
}

# "first last" (lowercase) -> playerId (matches the Player insert)
PLAYER_IDS = {
    "alyssa poarch": "01", "mikayla dayes": "02", "loren sefcik": "03",
    "jlon flippens": "04", "adalee broadbent": "05", "hope lewandoski": "06",
    "emily mcnesby": "07", "anissa mose": "08", "alexis hogarth": "09",
    "mia isaac": "10", "sydney staier": "11", "keyera wynn": "12",
    "malikae dayes": "13", "taylor whitmer": "14", "brynn drury": "15",
    "niven hegeman": "16", "olivia hicks": "17", "kaylee kozlowski": "18",
    "katie krotee": "19", "nicole kwoczka": "20", "darby moore": "21",
    "julia new": "22", "madison oracion": "23", "erin seppi": "24",
    "kate swetz": "25", "andi wenck": "26", "brooke weston": "27",
    "zora jackson": "28", "anna carazza": "29", "catherine derosa": "30",
    "tori paul": "31", "milan pierre-jerome": "32", "olivia reese": "33",
    "avery rice": "34", "kennedy tolson": "35", "kori locksley": "36",
    "mori sokoloff": "37", "toni domingos": "38", "liz brucia": "39",
    "madeline smith": "40", "krista varrichione": "41",
    # spelling variants seen in the stat sheets
    "niven hegemen": "16", "loren sefick": "03", "mikalya dayes": "02",
    "kayle krotee": "19",
}


def get_soup(url):
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    time.sleep(1)  # be polite to the server
    return BeautifulSoup(resp.text, "html.parser")


def normalize_name(raw):
    raw = " ".join(raw.split())
    if "," in raw:
        last, first = [p.strip() for p in raw.split(",", 1)]
        raw = f"{first} {last}"
    return raw.lower()


def to_int(text):
    text = text.strip()
    return int(text) if text.isdigit() else None


def boxscore_links(season_url, year):
    soup = get_soup(season_url)
    links = []
    pattern = re.compile(rf"/stats/{year}/[^/]+/boxscore/\d+")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if pattern.search(href):
            full = href if href.startswith("http") else "https://umterps.com" + href
            if full not in links:
                links.append(full)
    return links


def parse_boxscore(url):
    soup = get_soup(url)
    match = re.search(r"Date:\s*(\d{1,2})/(\d{1,2})/(\d{4})", soup.get_text(" "))
    if not match:
        return None, []
    # strip leading zeros so 02/20/2021 matches 2/20/2021
    m, d, y = (int(x) for x in match.groups())
    date = f"{m}/{d}/{y}"

    rows = {}
    idx = None
    for table in soup.find_all("table"):
        header_cells = [th.get_text(strip=True).lower() for th in table.find_all("th")]
        if {"sh", "g", "a", "min"}.issubset(header_cells):
            idx = {name: header_cells.index(name) for name in ("sh", "g", "a", "min")}
        if idx is None:
            continue
        # Substitutes tables have no stat headers, so they reuse the
        # starters' column positions. Goalkeeping rows are too short and get skipped.
        for tr in table.find_all("tr"):
            link = tr.find("a", href=re.compile(r"womens-soccer/roster/"))
            if not link:
                continue  # opponent players have no Maryland roster link
            cells = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
            if len(cells) <= max(idx.values()):
                continue
            name = normalize_name(link.get_text())
            stats = [to_int(cells[idx[k]]) for k in ("g", "a", "sh", "min")]
            if name in rows:  # same player listed twice: add the numbers together
                rows[name] = [
                    (x or 0) + (y or 0) if (x is not None or y is not None) else None
                    for x, y in zip(rows[name], stats)
                ]
            else:
                rows[name] = stats
    return date, list(rows.items())


def sql_value(v):
    return "NULL" if v is None else str(v)


def main():
    output = []
    unmatched = set()
    found_games = set()
    for year, url in SEASON_PAGES.items():
        season_rows = []
        goal_total = 0
        for link in boxscore_links(url, year):
            date, players = parse_boxscore(link)
            game_id = GAME_IDS.get(date)
            print(f"  {date} -> game {game_id} ({len(players)} players)  {link}")
            if game_id is None:
                continue  # games outside the project (e.g. after 10/21/2021)
            found_games.add(game_id)
            for name, (g, a, sh, mins) in players:
                player_id = PLAYER_IDS.get(name)
                if player_id is None:
                    unmatched.add(f"{name} ({date})")
                    continue
                goal_total += g or 0
                season_rows.append(
                    f"        ('{player_id}', '{game_id}', {sql_value(g)}, "
                    f"{sql_value(a)}, {sql_value(sh)}, {sql_value(mins)})"
                )
        if season_rows:
            output.append(f"-- {year} season")
            output.append("INSERT INTO [Wsoc.Performance] VALUES")
            output.append(",\n".join(season_rows))
            output.append("")
        print(f"{year}: {len(season_rows)} rows, {goal_total} player goals")

    with open("performance_inserts.sql", "w") as f:
        f.write("-- Insert into Performance table\n" + "\n".join(output))

    missing = sorted(set(GAME_IDS.values()) - found_games)
    print("\nMissing gameIds:", missing if missing else "none")
    print("Players not in the Player table:", sorted(unmatched) if unmatched else "none")
    print("\nWrote performance_inserts.sql")


if __name__ == "__main__":
    main()
