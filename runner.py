# import pandas as pd
# from db import get_connection

# def run_sql_file(path):
#     with open(path) as f:
#         query = f.read()
#     conn = get_connection()
#     df = pd.read_sql_query(query, conn)
#     conn.close()
#     return df

##### Using sqlalchemy instead of psycopg2 


# import pandas as pd
# from db import get_engine

# def run_sql_file(path, params=None):
#     with open(path) as f:
#         query = f.read()
#     engine = get_engine()
#     df = pd.read_sql_query(query, engine, params=params)
#     return df


"""
runner.py

Reads a .sql file and runs it (parameterized) against the SQLAlchemy engine
from db.py, returning a pandas DataFrame.

Two public helpers:
  - resolve_stakes(...)  : translate human --stake input into the query params
                           {"all_stakes": bool, "stake_list": [...]}
  - run_sql_file(...)    : load a .sql file, bind params, return a DataFrame
"""

from decimal import Decimal

import pandas as pd
from sqlalchemy import text, bindparam
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import Numeric

from db import get_engine  # adjust if your db.py exposes the engine differently


# ---------------------------------------------------------------------------
# Stake translation
# ---------------------------------------------------------------------------
def resolve_stakes(stake_input):
    """
    Translate human --stake input into the params the SQL expects.

    Accepts:
      - None                      -> default to "all"
      - "all" / "All" / "ALL"     -> all stakes (no filter)
      - a single value: "0.02"    -> that one stake
      - a list: ["0.02", "0.05"]  -> those stakes

    Returns a dict:
      {"all_stakes": bool, "stake_list": [Decimal, ...]}

    The SQL never sees the string "all"; it only sees the boolean flag and
    the (possibly empty) numeric list.
    """
    # Missing flag -> explicit "all" default (least-surprising).
    if stake_input is None:
        return {"all_stakes": True, "stake_list": []}

    # Normalize to a list so single value and list are handled the same way.
    if isinstance(stake_input, str):
        items = [stake_input]
    else:
        items = list(stake_input)

    # Case-insensitive "all" detection. If "all" appears anywhere, it wins.
    if any(str(s).strip().lower() == "all" for s in items):
        return {"all_stakes": True, "stake_list": []}

    # Otherwise these are specific stake values. Use Decimal so the values
    # match the ROUND(..., 2) numeric type on the SQL side exactly.
    stake_list = [Decimal(str(s).strip()) for s in items]
    return {"all_stakes": False, "stake_list": stake_list}


# ---------------------------------------------------------------------------
# Query execution
# ---------------------------------------------------------------------------
def run_sql_file(path, params=None):
    """
    Read a .sql file and run it parameterized, returning a DataFrame.

    `params` is a plain dict of name -> value, using SQLAlchemy :name style
    in the SQL. For the stake-filtered studies, pass the dict produced by
    resolve_stakes(...) (optionally merged with other params like min_hands).
    """
    params = params or {}

    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()

    stmt = text(sql)

    # If this query uses :stake_list, declare it as a Postgres numeric array
    # so `= ANY(:stake_list)` receives a real array rather than a scalar.
    # Declaring an expanding=False array bind is what makes ANY() work here.
    if ":stake_list" in sql or "stake_list" in params:
        stmt = stmt.bindparams(
            bindparam("stake_list", type_=ARRAY(Numeric))
        )

    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql_query(stmt, conn, params=params)

    return df