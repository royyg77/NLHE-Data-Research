# from db import get_connection

# conn = get_connection()
# cur = conn.cursor()
# cur.execute("SELECT 1;")
# print("Result:", cur.fetchone())
# print("Connection works!")
# cur.close()
# conn.close()


from runner import run_sql_file, resolve_stakes

# params = resolve_stakes(["0.02", "0.05"])   # or resolve_stakes("all")
params = resolve_stakes(["all"])  
params["min_hands"] = 30000
df = run_sql_file("sql/v1_0/01_pool_overview.sql", params)
# df = run_sql_file("sql/v1_0/02_flop_cbet_strategy_by_texture.sql", params)
# df = run_sql_file("sql/v1_0/03_texture_frequency.sql", params)
print(df.head())
print(df.tail())
