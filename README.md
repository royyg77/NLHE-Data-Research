# NLHE Data Research

A poker research tool for studying No-Limit Hold'em (NLHE) population tendencies from
hand-history data stored in a [PokerTracker 4](https://www.pokertracker.com/) (PT4)
PostgreSQL database.

It runs as a parameterized pipeline: pick a study and its parameters (stake, minimum
hands, and so on), and the tool extracts the relevant data from your PT4 database,
computes the statistics, and returns results from the command line. An interactive
Streamlit dashboard is in progress.

---

## Features

- **One shared core, multiple front-ends** — the same study logic powers the CLI today,
  and a Streamlit dashboard (in progress), so results stay consistent across them.
- **Parameterized runs** — pick a study, stake, and parameters at runtime instead of
  editing scripts.
- **Direct database access** — queries your PT4 PostgreSQL database directly; no manual
  export step.
- **Study-module architecture** — each research direction is a self-contained module.
  New studies are added as new folders, not piled into ever-growing files.
- **Organized and extensible** — studies declare a category and optional relationships,
  so they group cleanly in both front-ends as the catalog grows.
- **Notebooks preserved** — the exploratory notebooks still work and reuse the same core
  functions.

---

## Project Structure


```
NLHE-Data-Research/
├── config/settings.yaml                  # non-secret defaults (stakes, default min-hands, output dir)
├── pipeline/
│   ├── core/                             # the plumbing — written once, rarely touched
│   │   ├── db.py                         #   database connection (reads from .env)
│   │   ├── runner.py                     #   loads a SQL file, runs it parameterized → DataFrame
│   │   ├── io.py                         #   save / load results
│   │   └── base.py                       #   the Study contract (base class every study follows)
│   ├── registry.py                       # auto-discovers studies, groups by category → feeds front-ends
│   └── studies/                          # ONE folder per research direction
│       ├── example/            #   v1.0 study: flop c-bet by board texture
│       │   ├── example.py                  #declares name/category/params/outputs + run()
│       │   └── sql/
│       │       └── example.sql
│       └── .../
├── cli.py                                # command-line entry point (never changes as studies grow)
├── dashboard.py                          # Streamlit dashboard (in progress; never changes as studies grow)
├── notebooks/                            # exploratory notebooks (import from pipeline/)
├── results/                              # run outputs (git-ignored)
├── .env.example                          # template for database credentials (copy to .env)
└── requirements.txt
```

### How it fits together

The architecture has three layers, top to bottom:

1. **Front-ends** (`cli.py`, `dashboard.py`) — thin layers that ask the registry which
   studies exist and render them. They do not change when you add a study.
2. **Core** (`pipeline/core/`) — generic plumbing: connect to the database, run a
   parameterized query, save results, and define the contract every study follows. This
   does not grow as the catalog grows.
3. **Studies** (`pipeline/studies/`) — where the substance lives. Each study is a
   self-contained folder with its own logic and its own versioned SQL. Adding a study
   means adding a folder, never editing the front-ends.

The registry automatically discovers the studies and groups them by the `category` each
one declares, so the front-ends can present them as an organized list rather than a flat
dump.

---

## Getting Started

### Prerequisites

- A local **PokerTracker 4** PostgreSQL database with hand-history data
- **Python 3.10+**
- Database connection details (host, port, database name, username, password)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/royyg77/NLHE-Data-Research.git
   cd NLHE-Data-Research
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

The tool reads your database credentials from a `.env` file that you create locally.
It is **not** committed to git, so your credentials stay private.

1. **Copy the example file**

   ```bash
   cp .env.example .env
   ```

2. **Edit `.env`** with your PT4 PostgreSQL connection details:

   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=PT4_DB
   DB_USER=your_username
   DB_PASSWORD=your_password
   ```

3. *(Optional)* Adjust non-secret defaults — available stakes, default minimum hands,
   output directory — in `config/settings.yaml`.

---

## Usage

### Command line

Run a single study by passing its name and parameters:

```bash
python cli.py --study flop-cbet-texture --stake 0.5 --min-hands 10000
```

List the available studies (grouped by category) and stakes:

```bash
python cli.py --list
```

Results are saved to `results/<run>/` as CSV (and charts, where applicable).

| Flag          | Description                       | Example             |
| ------------- | --------------------------------- | ------------------- |
| `--study`     | Which study to run                | `flop-cbet-texture` |
| `--stake`     | Stake level to filter on          | 0.5 \[1.0] \[2.0]   |
| `--min-hands` | Minimum hands threshold           | `1000`              |
| `--list`      | Show available studies and stakes | —                   |

Note: available parameters depend on the study. Each study declares the parameters it
accepts, so `--list` is the source of truth for what a given study expects.

### Dashboard (in progress)

An interactive Streamlit dashboard is planned. Once available, it will let you select a
study (organized by category), set its parameters, run the pipeline, and view tables and
charts directly — no command line needed. The study plotting functions are already
Streamlit-compatible in preparation for this; `dashboard.py` itself is not yet
implemented.

### Notebooks

The notebooks in `notebooks/v1_0/` are kept for open-ended exploration. They import the
same functions from `pipeline/`, so any study available in the CLI or dashboard can be
called and extended interactively.

---

## Available Studies

| Study | Category | Description |
| --- | --- | --- |
| Flop c-bet by texture | Single-Raised Pots | Flop continuation-bet frequency and sizing broken down by board texture (the v1.0 study) |

The catalog will expand over time. Planned directions include 4-bet-pot analysis
(preflop ranges, board textures, reactions to facing a raise) and showdown range
visualization.

---

## Adding a New Study

Each study is a self-contained folder, so adding one does not touch the front-ends or
the core.

1. **Create the study folder** under `pipeline/studies/<study_name>/`.
2. **Add the SQL** to `pipeline/studies/<study_name>/sql/` (versioned, e.g. `v1_0.sql`).
3. **Write `study.py`** — implement the study against the contract in
   `pipeline/core/base.py`: declare its `name`, `category`, `description`, the `params`
   it accepts, and a `run` method that takes the queried data and returns a result
   (table and/or figure).

The registry discovers the new study automatically — there is no manual registration
step. It then becomes available in the CLI (`--study`) and, once the dashboard ships, the
dashboard too, grouped under the category it declares.

### Organizing related studies

Studies that belong to the same research direction can share a category and live under a
common parent folder (for example, several 4-bet-pot studies under `fourbet_pots/`).
A study may also list `related` studies, which the front-ends use to surface connections
between them. Grouping is opt-in per study — a standalone study simply declares its own
category and is listed on its own.

---

## Troubleshooting

- **Connection refused / authentication failed** — confirm the values in `.env` match
  your PostgreSQL setup and that the database is running.
- **Empty results** — your `--min-hands` threshold may be filtering everything out, or the
  selected stake has no hands in your database.
- **Schema errors** — PT4 schema and column names can vary by version; confirm they match
  the queries in the relevant study's `sql/` folder.

---

## Version History

- **v1.0**
  - Standalone flop c-bet strategy study: continuation-bet frequency and sizing by board
    texture, with supporting pool-overview and texture-frequency outputs
  - Parameterized pipeline with a CLI front-end (Streamlit dashboard in progress)
  - Study-module architecture: shared core plus self-contained study folders
  - Results export workflow and exploratory notebooks

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for
details.

---

## Contact

For questions about the project or collaboration opportunities, contact
[royguo77@gmail.com](mailto:royguo77@gmail.com).
