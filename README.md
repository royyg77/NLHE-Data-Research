# NLHE Data Research

---

## Description

NLHE Data Research is an ongoing poker research project for studying No-Limit Hold'em (NLHE) population tendencies using hand-history data stored in a PokerTracker 4 (PT4) PostgreSQL database.

The repository is designed as a reusable research workflow rather than a one-off analysis. SQL scripts are used to extract and structure analysis-ready datasets from the PT4 schema, while Python notebooks are used for statistical analysis, visualization, and longer-form reporting. As more hands are collected over time, the project can be extended with new studies, refined board-texture definitions, additional street-level analysis, and broader population research questions.

## Getting Started

### Dependencies

This project assumes access to a local PokerTracker 4 PostgreSQL relational database and a working Python environment. 

Required tools: 
- PostgreSQL / PokerTracker 4 database access
- DBeaver (recommended) or another SQL client 
- Python 3
- Jupyter Notebook or VS Code notebook support 

Typical Python libraries used in the analysis stage: 
- pandas
- numpy
- matplotlib
- seaborn 
- scipy

### Installing 

1. Clone the repository

```
git clone <your-repo-url>
cd NLHE-Data-Research
```

2. Configure database access

Open your SQL client and connect to the PostgreSQL instance that contains your PokerTracker 4 database.

3. Prepare a Python environment 

```
python -m venv .venv
source .venv/bin/activate
pip install pandas numpy matplotlib seaborn scipy jupyter
```

### Executing the Project

Execute the SQL files in sql/v1_0/ against your PT4 database.

Step 1: Run SQL scripts

```
01_pool_overview.sql
02_flop_cbet_strategy_by_texture.sql
03_flop_cbet_size_by_stake.sql
04_texture_frequency.sql
```

Step 2: Export outputs

Export each result set to CSV and save into:

`results/v1_0/`

Open the notebook in:

`notebook/v1_0/`

Load the exported CSV files for statistical analysis, visualization, and report generation.

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

## Version History 

- v1.0
    - Initial SQL layer for pool overview, flop c-bet strategy by texture, c-bet sizing extract, and texture frequency outputs
    - Initial results export workflow
    - Python analysis and report layer 

---

## License 

License information to be added. 




