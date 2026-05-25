# 🔒 Survey De-identification Tool

A lightweight Python script that removes personally identifiable information (PII) from survey CSV exports, assigns randomised anonymous IDs, and produces clean files ready for safe sharing or quantitative analysis.

---

## ✨ What it does

| Step | Action | Output file |
|------|--------|-------------|
| 1 | Drops PII columns (e.g. *Timestamp*, *Email Address*) | `survey_anonymous.csv` |
| 2 | Renames all columns to `Q1, Q2, …` and saves a lookup table | `column_mapping.csv` |
| 3 | Separates open-ended text answers from closed questions | `survey_openended.csv` |
| 3 | Saves closed questions only with consecutive Q-numbers | `survey_clean.csv` |

Row order is shuffled and IDs are randomly assigned so the original submission sequence cannot be inferred.

---

## 📁 Project structure

```
survey-deidentifier/
├── deidentify.py          # Main script – all logic lives here
├── generate_sample.py     # Creates a sample CSV to try the tool
├── requirements.txt
├── example/
│   └── sample_survey.csv  # 10-row demo dataset (auto-generated)
└── README.md
```

---

## 🚀 Quick start

### 1. Clone & install dependencies

```bash
git clone https://github.com/YOUR_USERNAME/survey-deidentifier.git
cd survey-deidentifier
pip install -r requirements.txt
```

### 2. Try it on the sample data

```bash
# Generate the sample CSV first
python generate_sample.py

# Run de-identification on the sample
python deidentify.py \
  --input example/sample_survey.csv \
  --pii "Timestamp" "Email Address" \
  --openended Q14
```

### 3. Run on your own survey

```bash
python deidentify.py --input "my_survey.csv"
```

All output files are written to the same folder as the input by default.

---

## ⚙️ Configuration

You can configure the tool in two ways:

### A) Edit the defaults at the top of `deidentify.py`

```python
DEFAULT_INPUT        = "new survey.csv"
PII_COLUMNS          = ["Timestamp", "Email Address"]
OPEN_ENDED_QUESTIONS = ["Q14", "Q60"]   # Q-numbers after renaming
ID_PREFIX            = "SID"
ID_START             = 1001
RANDOM_SEED          = 42
```

### B) Use command-line flags (override defaults at runtime)

| Flag | Description | Default |
|------|-------------|---------|
| `--input` | Path to raw survey CSV | `new survey.csv` |
| `--outdir` | Output directory | Same as input file |
| `--pii` | PII column names to drop | `Timestamp` `Email Address` |
| `--openended` | Q-numbers of open-ended questions | `Q14` `Q60` |
| `--prefix` | Anonymous ID prefix | `SID` |
| `--start` | Starting number for IDs | `1001` |
| `--seed` | Random seed (for reproducibility) | `42` |

```bash
python deidentify.py --help   # show all options
```

---

## 📋 How to find your open-ended question numbers

After running the script once, open `column_mapping.csv` — it maps every `Qn` label back to the original column name. Find the rows for your open-ended questions, note their `Q_Number` values, then rerun with `--openended Q14 Q60` (or set `OPEN_ENDED_QUESTIONS` in the script).

---

## 🔍 Example output

**`column_mapping.csv`**
```
Q_Number, Original_Column
AnonymousID, AnonymousID
Q1,  What is your age group?
Q2,  What is your gender?
...
Q14, Please share any additional comments:
```

**`survey_clean.csv`** (first 3 rows)
```
AnonymousID, Q1,    Q2,    Q3, ...
SID1007,     25-34, Female, 4, ...
SID1003,     18-24, Male,   5, ...
```

---

## 🛡️ Privacy notes

- The original file is **never modified**.
- Row order is shuffled so submission sequence cannot be inferred from position.
- Anonymous IDs are randomly assigned (not sequential from the original order).
- The same `--seed` value always produces the same IDs, making results reproducible.
- Open-ended text is kept in a **separate file** so it can be handled with extra care (e.g. manual review before sharing).

---

## 📄 License

MIT — free to use, modify, and share.
