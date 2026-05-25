"""
Survey De-identification Tool
==============================
Removes personally identifiable information (PII) from survey CSV exports,
assigns anonymous IDs, separates open-ended responses, and renames columns
to Q-numbers for safe sharing or analysis.

Usage
-----
    python deidentify.py                         # uses defaults in config section
    python deidentify.py --input my_survey.csv   # override input file
    python deidentify.py --help                  # show all options

Outputs (written to the same folder as the input file by default)
---------
    survey_anonymous.csv   – all rows, PII columns dropped, AnonymousID added
    survey_openended.csv   – AnonymousID + open-ended text answers only
    survey_clean.csv       – AnonymousID + closed questions renamed Q1, Q2 …
    column_mapping.csv     – maps every Qn label back to the original column name
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


# ─────────────────────────────────────────────────────────────────────────────
# DEFAULT CONFIGURATION  (edit these or override via command-line flags)
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_INPUT        = "new survey.csv"
DEFAULT_OUTPUT_DIR   = None          # None → same directory as the input file

PII_COLUMNS          = ["Timestamp", "Email Address"]   # columns to drop 
##replace with your own colum names

OPEN_ENDED_QUESTIONS = ["Q17", "Q64"]                   # after Q-renaming
##replace with your own colum names

ID_PREFIX            = "SID"
ID_START             = 1001 #change if you want
RANDOM_SEED          = 42
# ─────────────────────────────────────────────────────────────────────────────


def parse_args():
    p = argparse.ArgumentParser(
        description="De-identify a survey CSV and split open-ended responses."
    )
    p.add_argument("--input",    default=DEFAULT_INPUT,
                   help=f"Path to raw survey CSV (default: {DEFAULT_INPUT})")
    p.add_argument("--outdir",   default=DEFAULT_OUTPUT_DIR,
                   help="Directory for output files (default: same as input)")
    p.add_argument("--pii",      nargs="*", default=PII_COLUMNS,
                   help="Column names to treat as PII and drop "
                        f"(default: {PII_COLUMNS})")
    p.add_argument("--openended", nargs="*", default=OPEN_ENDED_QUESTIONS,
                   help="Q-numbers of open-ended questions after renaming "
                        f"(default: {OPEN_ENDED_QUESTIONS})")
    p.add_argument("--prefix",   default=ID_PREFIX,
                   help=f"Prefix for anonymous IDs (default: {ID_PREFIX})")
    p.add_argument("--start",    type=int, default=ID_START,
                   help=f"Starting number for anonymous IDs (default: {ID_START})")
    p.add_argument("--seed",     type=int, default=RANDOM_SEED,
                   help=f"Random seed for reproducibility (default: {RANDOM_SEED})")
    return p.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 – Drop PII columns and assign anonymous IDs
# ─────────────────────────────────────────────────────────────────────────────
def remove_pii(df: pd.DataFrame, pii_cols: list, prefix: str,
               start: int, seed: int) -> pd.DataFrame:
    found    = [c for c in pii_cols if c in df.columns]
    missing  = [c for c in pii_cols if c not in df.columns]

    if missing:
        print(f"  ⚠  Column(s) not found (skipped): {missing}")
    if found:
        df = df.drop(columns=found)
        print(f"  ✓  Dropped PII column(s): {found}")

    # Shuffle IDs so row order can't be reverse-engineered from the ID
    np.random.seed(seed)
    ids = np.arange(start, start + len(df))
    np.random.shuffle(ids)
    formatted = [f"{prefix}{i:04d}" for i in ids]

    df.insert(0, "AnonymousID", formatted)

    # Also shuffle row order
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    print(f"  ✓  Assigned {len(df)} anonymous IDs  ({prefix}{start:04d} … )")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 – Rename columns to Q-numbers and save mapping
# ─────────────────────────────────────────────────────────────────────────────
def rename_columns(df: pd.DataFrame, out_dir: Path):
    original_cols = df.columns.tolist()
    q_labels      = ["AnonymousID"] + [f"Q{i+1}" for i in range(len(original_cols) - 1)]

    mapping_df = pd.DataFrame({
        "Q_Number":        q_labels,
        "Original_Column": original_cols,
    })
    mapping_path = out_dir / "column_mapping.csv"
    mapping_df.to_csv(mapping_path, index=False)
    print(f"  ✓  Column mapping saved → {mapping_path}")

    return df.rename(columns=dict(zip(original_cols, q_labels))), mapping_df


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 – Split open-ended vs. closed questions
# ─────────────────────────────────────────────────────────────────────────────
def split_questions(df: pd.DataFrame, open_ended_qs: list, out_dir: Path):
    available = [q for q in open_ended_qs if q in df.columns]
    missing   = [q for q in open_ended_qs if q not in df.columns]
    if missing:
        print(f"  ⚠  Open-ended Q-number(s) not found (skipped): {missing}")

    # ── Open-ended file ──────────────────────────────────────────────────────
    oe_path = out_dir / "survey_openended.csv"
    df_oe   = df[["AnonymousID"] + available].copy()
    df_oe.to_csv(oe_path, index=False)
    print(f"  ✓  Open-ended responses  → {oe_path}  "
          f"({df_oe.shape[0]} rows × {df_oe.shape[1]} cols)")

    # ── Closed-questions file ────────────────────────────────────────────────
    closed_path = out_dir / "survey_clean.csv"
    df_closed   = df.drop(columns=available)

    # Re-number Q columns so they are consecutive after dropping open-ended
    closed_cols      = df_closed.columns.tolist()          # ['AnonymousID', ...]
    renumber         = {c: f"Q{i+1}" for i, c in enumerate(closed_cols[1:])}
    df_closed        = df_closed.rename(columns=renumber)
    df_closed.to_csv(closed_path, index=False)
    print(f"  ✓  Closed questions       → {closed_path}  "
          f"({df_closed.shape[0]} rows × {df_closed.shape[1]} cols)")

    return df_oe, df_closed


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    args     = parse_args()
    in_path  = Path(args.input)

    if not in_path.exists():
        sys.exit(f"❌  Input file not found: {in_path}")

    out_dir  = Path(args.outdir) if args.outdir else in_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'─'*55}")
    print(f"  Survey De-identification Tool")
    print(f"{'─'*55}")
    print(f"  Input  : {in_path}")
    print(f"  Output : {out_dir}")
    print(f"{'─'*55}\n")

    # Load
    df_raw = pd.read_csv(in_path)
    print(f"  Loaded {df_raw.shape[0]} rows × {df_raw.shape[1]} columns\n")

    # Step 1 – Remove PII
    print("[ Step 1 ]  Remove PII & assign anonymous IDs")
    df_anon = remove_pii(df_raw, args.pii, args.prefix, args.start, args.seed)
    anon_path = out_dir / "survey_anonymous.csv"
    df_anon.to_csv(anon_path, index=False)
    print(f"  ✓  Full anonymised file  → {anon_path}\n")

    # Step 2 – Rename columns
    print("[ Step 2 ]  Rename columns to Q-numbers")
    df_renamed, mapping = rename_columns(df_anon, out_dir)
    print()

    # Step 3 – Split open-ended vs closed
    print("[ Step 3 ]  Split open-ended and closed questions")
    split_questions(df_renamed, args.openended, out_dir)

    print(f"\n{'─'*55}")
    print("  ✅  Done!  Check the output folder for your files.")
    print(f"{'─'*55}\n")


if __name__ == "__main__":
    main()
