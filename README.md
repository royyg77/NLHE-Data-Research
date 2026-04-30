# NLHE Data Research

A modular research framework for studying No-Limit Hold’em population tendencies using hand-history data from a PokerTracker 4 PostgreSQL database.


## Overview

This project is designed as a reusable research workflow. SQL scripts extract and structure analysis-ready datasets from the PT4 schema, while Python notebooks handle statistical analysis, visualization, and reporting.

The framework is built to grow over time. Each study targets a specific part of the game tree — such as a street, decision node, or board-texture class — and follows a consistent pipeline: SQL extraction → CSV export → notebook analysis. New studies can be added as the project expands into additional situations, deeper street-level breakdowns, and more granular texture classifications.


---

## Studies

| Version | Focus | Status |
|---------|-------|--------|
| [v1.0](docs/v1_0/analysis.md) | Flop continuation-bet strategy and board texture frequency | Complete |

---

## Project Structure

```
NLHE-Data-Research/
├── sql/              # SQL extraction scripts, organized by version
│   └── v1_0/
├── notebooks/        # Jupyter notebooks for analysis and reporting
│   └── v1_0/
├── results/          # Exported CSVs and outputs
│   └── v1_0/
├── docs/             # Writeup
│   └── v1_0/
└── README.md
```

Each study version follows the same layout: SQL scripts in `sql/`, notebooks in `notebooks/`, and exported data in `results/`.

---

## Getting Started

### Dependencies

This project assumes access to a local PokerTracker 4 PostgreSQL database and a working Python environment.

Required tools:
- PostgreSQL / PokerTracker 4 database access
- DBeaver (recommended) or another SQL client
- Python 3
- Jupyter Notebook or VS Code notebook support

Python libraries used in the analysis stage:
- pandas
- numpy
- matplotlib
- seaborn

### Installation

1. Clone the repository

```
git clone https://github.com/royyg77/NLHE-Data-Research.git
cd NLHE-Data-Research
```

2. Configure database access

Open your SQL client and connect to the PostgreSQL instance that contains your PokerTracker 4 database.

3. Prepare a Python environment

```
python -m venv .venv
source .venv/bin/activate
pip install pandas numpy matplotlib seaborn jupyter
```

### Running a Study

Each study follows the same workflow. Using v1.0 as an example:

**Step 1:** Run the SQL scripts in `sql/v1_0/` against your PT4 database.

**Step 2:** Export each result set to CSV and save into `results/v1_0/`.

**Step 3:** Open the notebook in `notebooks/v1_0/` and load the exported CSVs for analysis.

---

## Help

Common issues:
- If SQL queries fail unexpectedly in DBeaver, ensure blank lines are not being treated as statement delimiters.
- Confirm exported CSV files include column headers.
- Ensure PT4 schema names and column names match the local database version being queried.

---

## Authors

For questions about the project or collaboration opportunities, contact royguo77@gmail.com

---

## License

License information to be added.