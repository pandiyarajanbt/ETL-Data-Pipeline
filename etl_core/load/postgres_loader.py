import logging
import pandas as pd
from django.db import connection

logger = logging.getLogger('pipeline')


class PostgresLoader:
    """Load transformed DataFrames into PostgreSQL."""

    def load(self, df: pd.DataFrame, table: str, if_exists: str = 'append') -> int:
        if df.empty:
            logger.warning(f"Empty DataFrame — skipping load to {table}")
            return 0

        from sqlalchemy import create_engine
        from django.conf import settings

        db = settings.DATABASES['default']
        engine = create_engine(
            f"postgresql+psycopg2://{db['USER']}:{db['PASSWORD']}@{db['HOST']}:{db['PORT']}/{db['NAME']}"
        )
        df.to_sql(table, engine, if_exists=if_exists, index=False, method='multi', chunksize=1000)
        logger.info(f"Loaded {len(df)} rows into table '{table}'")
        return len(df)

    def execute_raw(self, sql: str, params=None) -> None:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
