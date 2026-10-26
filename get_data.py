"""Download the Survey of Consumer Finances summary extracts (1989-2025) and
tabulate family net worth by the education of the family's reference person.

Source: Federal Reserve Board, SCF Summary Extract Public Data
https://www.federalreserve.gov/econres/scfindex.htm

All extracts are distributed with dollar values already adjusted to 2025
dollars, so no inflation adjustment is done here.

Output: data/scf_networth_by_education.csv (one row per survey year x group)
"""

import io
import time
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

YEARS = list(range(1989, 2026, 3))  # 1989, 1992, ..., 2022, 2025
URL = "https://www.federalreserve.gov/econres/files/scfp{year}excel.zip"

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "raw"
OUT_FILE = ROOT / "data" / "scf_networth_by_education.csv"

# EDCL (education of reference person), as defined in the Fed's bulletin.macro.txt:
#   1 = no high school diploma, 2 = high school diploma or GED,
#   3 = some college or associate degree, 4 = bachelor's degree or higher
GROUPS = {
    "High school or less": [1, 2],
    "Some college": [3],
    "College degree": [4],
}


def download(year):
    """Fetch the CSV extract zip for one survey year, skipping it if already cached."""
    path = RAW_DIR / f"scfp{year}excel.zip"
    if path.exists():
        return path
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    url = URL.format(year=year)
    print(f"Downloading {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        path.write_bytes(resp.read())
    time.sleep(1)  # be polite to the Fed's server
    return path


def read_extract(path):
    """Read the columns we need from the CSV inside the zip."""
    with zipfile.ZipFile(path) as zf:
        member = next(n for n in zf.namelist() if n.lower().endswith(".csv"))
        with zf.open(member) as f:
            df = pd.read_csv(
                io.BytesIO(f.read()),
                usecols=lambda c: c.upper() in {
                    "YY1", "Y1", "XX1", "X1", "WGT", "EDCL", "NETWORTH"},
            )
    # Older extracts (e.g. 1989) name the family/record IDs XX1/X1 instead of YY1/Y1.
    df.columns = df.columns.str.upper()
    df = df.rename(columns={"XX1": "YY1", "X1": "Y1"})
    # Each family appears five times, once per multiple-imputation implicate.
    df = df.sort_values(["YY1", "Y1"])
    df["IMPLICATE"] = df.groupby("YY1").cumcount() + 1
    return df


def weighted_median(values, weights):
    order = np.argsort(values)
    v, w = values[order], weights[order]
    cum = np.cumsum(w)
    return v[np.searchsorted(cum, cum[-1] / 2)]


def summarize(df, year):
    """Compute weighted statistics on all five implicates pooled together, as the
    Fed does for its published tables (WGT is already divided by 5 for this)."""
    total_wgt = df["WGT"].sum()
    rows = []
    for group, codes in GROUPS.items():
        g = df[df["EDCL"].isin(codes)]
        nw, w = g["NETWORTH"].to_numpy(float), g["WGT"].to_numpy(float)
        rows.append({
            "year": year,
            "group": group,
            "median_networth": weighted_median(nw, w),
            "mean_networth": np.average(nw, weights=w),
            "share_of_families": w.sum() / total_wgt,
            "n_families": g["YY1"].nunique(),
        })
    return pd.DataFrame(rows)


def main():
    results = []
    for year in YEARS:
        df = read_extract(download(year))
        assert df["IMPLICATE"].max() == 5, f"{year}: expected 5 implicates"
        results.append(summarize(df, year))
        print(f"{year}: {df['YY1'].nunique():,} families")

    out = pd.concat(results, ignore_index=True)
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_FILE, index=False, float_format="%.4f")
    print(f"\nWrote {OUT_FILE}")
    print(out.pivot(index="year", columns="group", values="median_networth").round(-2))


if __name__ == "__main__":
    main()
