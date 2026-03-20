import psycopg2
import pandas as pd
from urllib.parse import urlparse, parse_qs


def run_query(query, neon_url: str, fetch=True):
    parsed = urlparse(neon_url)
    query_params = parse_qs(parsed.query)

    sslmode = query_params.get("sslmode", ["require"])[0]
    channel_binding = query_params.get("channel_binding", [None])[0]

    connect_kwargs = {
        "dbname": parsed.path.lstrip("/"),
        "user": parsed.username,
        "password": parsed.password,
        "host": parsed.hostname,
        "port": parsed.port or 5432,
        "sslmode": sslmode,
    }

    if channel_binding:
        connect_kwargs["channel_binding"] = channel_binding

    with psycopg2.connect(**connect_kwargs) as conn:
        with conn.cursor() as cur:
            cur.execute(query)

            if fetch:
                rows = cur.fetchall()
                colnames = [desc[0] for desc in cur.description]
                return pd.DataFrame(rows, columns=colnames)
            else:
                conn.commit()