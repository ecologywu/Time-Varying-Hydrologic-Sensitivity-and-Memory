"""Verify the revised manuscript: structure, citations, equations, tables, images."""
import os
import re
import docx

_BASE = r"C:\Users\dell\Documents\Trae-CN\temp_20261018_01"
_candidates = [os.path.join(_BASE, "WRR_manuscript.docx"),
               os.path.join(_BASE, "WRR_manuscript_updated.docx")]
DOCX_PATH = max([p for p in _candidates if os.path.exists(p)], key=os.path.getmtime)
print("Verifying:", os.path.basename(DOCX_PATH))
d = docx.Document(DOCX_PATH)
text = "\n".join(p.text for p in d.paragraphs)

imgs = 0
for shp in d.inline_shapes:
    imgs += 1

print("Paragraphs:", len(d.paragraphs))
print("Tables:", len(d.tables))
print("Inline images:", imgs)

# Main text only (everything before the References heading)
main_text = text.split("\nReferences\n")[0]

# Citation coverage checks
checks = {
    "Nemec & Schaake cited": "Němec and Schaake (1982)" in main_text,
    "Sankarasubramanian 2001": "Sankarasubramanian et al., 2001" in main_text,
    "Awasthi 2024": "Awasthi et al., 2024" in main_text,
    "Anderson 2025": "Anderson et al., 2025" in main_text,
    "Gnann 2025": "Gnann et al., 2025" in main_text,
    "Moges 2022": "Moges et al., 2022" in main_text,
    "Ji 2025": "Ji et al., 2025" in main_text,
    "Collins 2025": "Collins et al., 2025" in main_text,
    "Ponds 2025": "Ponds et al., 2025" in main_text,
    "Xu 2025 (corrected year)": "Xu et al. (2025)" in main_text,
    "No stale Xu 2020": "Xu et al., 2020" not in main_text and "Xu et al. (2020)" not in main_text,
    "Turner 2025": "Turner et al., 2025" in main_text,
    "Gasparrini 2010": "Gasparrini et al., 2010" in main_text,
    "Rushworth 2013": "Rushworth et al., 2013" in main_text,
    "de Lavenne 2022": "de Lavenne et al., 2022" in main_text,
    "Durbin & Koopman": "Durbin and Koopman, 2012" in main_text,
    "Nanditha 2025": "Nanditha et al., 2025" in main_text,
    "Yue 2026": "Yue et al., 2026" in main_text,
    "Data Availability": "Data Availability Statement" in text,
    "Key Points present": "Key Points:" in text,
    "Plain Language Summary present": "Plain Language Summary" in text,
    "Table 1 caption": "Table 1. Drift of response parameters" in text,
    "Fig3 base-map note": "major rivers and lakes are included" in text,
    # --- Round-3 expansion checks ---
    "Milly 2008": "Milly et al. (2008)" in main_text,
    "Merz 2011": "Merz et al., 2011" in main_text,
    "Westra 2014": "Westra et al., 2014" in main_text,
    "Gudmundsson 2021": "Gudmundsson et al., 2021" in main_text,
    "Munoz-Sabater 2021": "Muñoz-Sabater et al., 2021" in main_text,
    "Kirchner 2009": "Kirchner, 2009" in main_text or "Kirchner (2009)" in main_text,
    "Montanari & Koutsoyiannis 2014": "Montanari and Koutsoyiannis, 2014" in main_text,
    "Budyko 1974": "Budyko, 1974" in main_text,
    "Dooge 1986": "Dooge, 1986" in main_text,
    "Donohue 2007": "Donohue et al., 2007" in main_text,
    "Addor 2017": "Addor et al., 2017" in main_text,
    "Hamon 1961": "Hamon, 1961" in main_text,
    "Institute of Hydrology 1980": "Institute of Hydrology, 1980" in main_text,
    "Moran 1950": "Moran, 1950" in main_text,
    "Sen 1968": "Sen, 1968" in main_text,
    # --- Round-4: data sources & screening (2,172 stations) ---
    "Farber 2025 (GRDC-Caravan)": "Färber et al., 2025" in main_text,
    "USGS NWIS": "U.S. Geological Survey, 2025" in main_text,
    "HIDROWEB (ANA)": "Agência Nacional de Águas e Saneamento Básico, 2025" in main_text,
    "Datos de Caudales (CR2)": "Centro de Ciencia del Clima y la Resiliencia, 2025" in main_text,
    "GSIM Part 1 (Do 2018)": "Do et al., 2018" in main_text,
    "GSIM Part 2 (Gudmundsson 2018)": "Gudmundsson et al., 2018" in main_text,
    "Ministry of Water Resources": "Ministry of Water Resources, 2025" in main_text,
    "GRanD (Lehner 2011)": "Lehner et al., 2011" in main_text,
    "GlobCover (Bontemps 2011)": "Bontemps et al., 2011" in main_text,
    "Global Forest Change (Hansen 2013)": "Hansen et al., 2013" in main_text,
    "2172 compiled stations": "2,172 stations worldwide" in main_text,
    "2146 final sample": "2,146" in main_text,
    "Median record 38.0 / min 35.0": "38.0 years" in main_text and "35.0" in main_text,
    # --- Round-4: removed edge citations stay removed ---
    "No stale Sawicz": "Sawicz" not in main_text,
    "No stale Jakeman": "Jakeman" not in main_text,
    "No stale Gentine": "Gentine" not in main_text,
    "No stale Milly & Dunne 2016": "Milly and Dunne" not in main_text and "Milly & Dunne" not in main_text,
    "No stale Lehner 2019": "Lehner et al., 2019" not in main_text and "Lehner et al. (2019" not in main_text,
    "No stale Savenije": "Savenije" not in main_text,
    "No stale Otto": "Otto" not in main_text,
    "No stale Slater 2021": "Slater et al., 2021" not in main_text and "Slater et al. (2021" not in main_text,
    "No stale Hrachowitz 2013": "Hrachowitz et al., 2013" not in main_text and "Hrachowitz et al. (2013" not in main_text,
    # --- Round-4: panel labels & in-text panel references ---
    "Fig1 caption panel a": "(a) Coefficient of variation of precipitation sensitivity" in text,
    "Fig1 caption panel b": "(b) coefficient of variation of vapor-pressure" in text,
    "Fig1 caption panel c": "(c) standard deviation (days)" in text,
    "Fig2 caption panel a": "(a) Residual drift fraction against aridity index" in text,
    "Fig2 caption panel b": "(b) residual drift fraction against snow fraction" in text,
    "In-text Figure 1a": "(Figure 1a" in main_text,
    "In-text Figure 1b": "(Figure 1b" in main_text,
    "In-text Figure 1c": "(Figure 1c" in main_text,
    "In-text Figure 2a": "Figure 2a" in main_text,
    # --- Round-4: Open Research data URLs ---
    "Open Research heading": "Open Research" in text,
    "ROBIN Zenodo DOI": "https://doi.org/10.5281/zenodo.14801702" in text,
    "GRDC-Caravan Zenodo DOI": "https://doi.org/10.5281/zenodo.7540792" in text,
    "USGS NWIS URL": "https://waterdata.usgs.gov/nwis" in text,
    "HIDROWEB URL": "https://www.snirh.gov.br/hidroweb/apresentacao" in text,
    "CR2 URL": "https://www.cr2.cl/datos-de-caudales/" in text,
    "GSIM Pangaea DOI": "https://doi.pangaea.de/10.1594/PANGAEA.887470" in text,
    "GRanD URL": "https://sedac.ciesin.columbia.edu/data/set/grand-v1-dams-rev01" in text,
    "GlobCover URL": "http://due.esrin.esa.int/page_globcover.php" in text,
    "Global Forest Change URL": "http://earthenginepartners.appspot.com/science-2013-global-forest" in text,
    "ERA5-Land URL": "https://www.ecmwf.int/en/era5-land" in text,
}
n_pass = 0
for k, v in checks.items():
    print(("PASS " if v else "FAIL ") + k)
    n_pass += int(bool(v))
print("Checks: %d/%d PASS" % (n_pass, len(checks)))

# Plain Language Summary word count (AGU target ~150 words)
pls_match = re.search(r"Plain Language Summary\n(.*?)\n1\. Introduction", text, re.DOTALL)
if pls_match:
    print("PLS word count: %d" % len(pls_match.group(1).split()))
else:
    print("PLS word count: section not found")

# Count reference entries
refs_started = False
ref_entries = []
for p in d.paragraphs:
    if p.text.strip() == "References":
        refs_started = True
        continue
    if refs_started:
        if p.text.strip().startswith("Supporting Information"):
            break
        if p.text.strip():
            ref_entries.append(p.text.strip())
print("\nReference entries:", len(ref_entries))

# ---------- Bidirectional citation cross-check ----------
# Institutional entries need explicit citation strings (no extractable surname)
ENTRY_SPECIAL = [
    ("Institute of Hydrology", "Institute of Hydrology, 1980"),
    ("U.S. Geological Survey", "U.S. Geological Survey, 2025"),
    ("Agência Nacional de Águas e Saneamento Básico",
     "Agência Nacional de Águas e Saneamento Básico, 2025"),
    ("Centro de Ciencia del Clima y la Resiliencia",
     "Centro de Ciencia del Clima y la Resiliencia, 2025"),
    ("Ministry of Water Resources", "Ministry of Water Resources, 2025"),
]


def norm_surname(s):
    s = s.replace(" et al.", "").strip()
    s = re.split(r" (?:and|&) ", s)[0].strip()
    if s.lower().startswith("de "):
        s = s[3:]
    return s.lower()


entry_pairs = set()
uncited = []
for entry in ref_entries:
    special = None
    for prefix, cite in ENTRY_SPECIAL:
        if entry.startswith(prefix):
            special = cite
            break
    m = re.search(r"\((\d{4})\)", entry)
    if special:
        name, year = special.rsplit(", ", 1)
        cited = special in main_text
        entry_pairs.add((norm_surname(name), year))
    elif m:
        year = m.group(1)
        surname = entry.split(",")[0].strip()
        cited = re.search(re.escape(surname) + r".{0,160}?" + year, main_text, re.DOTALL) is not None
        entry_pairs.add((norm_surname(surname), year))
    else:
        cited = False
    if not cited:
        uncited.append(entry[:70])

print("\nCross-check: every reference cited in main text")
if uncited:
    for u in uncited:
        print("UNCITED? " + u)
else:
    print("PASS all %d references cited in main text" % len(ref_entries))

# In-text unique (surname, year) pairs (repeated citations count once)
pat_a = re.compile(r"([A-Z][\w'’\-À-ÿ]+(?: (?:and|&) [A-Z][\w'’\-À-ÿ]+)?(?: et al\.?)?), ((?:19|20)\d{2})")
pat_b = re.compile(r"([A-Z][\w'’\-À-ÿ]+(?: (?:and|&) [A-Z][\w'’\-À-ÿ]+)?(?: et al\.?)?) \(((?:19|20)\d{2})")
cited_pairs = set()
for pat in (pat_a, pat_b):
    for m in pat.finditer(main_text):
        cited_pairs.add((norm_surname(m.group(1)), m.group(2)))
for _, cite in ENTRY_SPECIAL:
    if cite in main_text:
        name, year = cite.rsplit(", ", 1)
        cited_pairs.add((norm_surname(name), year))
# Drop name fragments subsumed by longer institutional citations
# (e.g. 'Hydrology, 1980' inside 'Institute of Hydrology, 1980')
special_names = {norm_surname(c.rsplit(", ", 1)[0]): c.rsplit(", ", 1)[1] for _, c in ENTRY_SPECIAL}
for s, y in list(cited_pairs):
    for sname, syear in special_names.items():
        if y == syear and s != sname and sname.endswith(s):
            cited_pairs.discard((s, y))
            break

print("\nUnique in-text citations (repeats counted once):", len(cited_pairs))
print("Reference entries:", len(entry_pairs))
missing = entry_pairs - cited_pairs
extra = cited_pairs - entry_pairs
if missing:
    print("Entries never matched in text:")
    for s, y in sorted(missing):
        print("  IN-LIST-NOT-TEXT? %s %s" % (s, y))
if extra:
    print("In-text pairs with no entry:")
    for s, y in sorted(extra):
        print("  IN-TEXT-NOT-LIST? %s %s" % (s, y))
if not missing and not extra and len(entry_pairs) == len(cited_pairs):
    print("PASS citation count matches: %d in-text == %d entries" % (len(cited_pairs), len(entry_pairs)))
