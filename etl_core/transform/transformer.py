import logging
import pandas as pd

logger = logging.getLogger('pipeline')


class DataTransformer:
    """Apply transformation logic to raw DataFrames."""

    def run(self, df: pd.DataFrame, source_type: str) -> pd.DataFrame:
        logger.info(f"Transforming {len(df)} rows from source '{source_type}'")
        df = self._drop_duplicates(df)
        df = self._normalize_columns(df)
        df = self._cast_types(df)
        df = self._drop_nulls(df)
        logger.info(f"Transformation complete: {len(df)} rows remaining")
        return df

    def _drop_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        before = len(df)
        df = df.drop_duplicates()
        logger.debug(f"Dropped {before - len(df)} duplicate rows")
        return df

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
        return df

    def _cast_types(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in df.select_dtypes(include='object').columns:
            try:
                df[col] = pd.to_datetime(df[col], infer_datetime_format=True)
            except (ValueError, TypeError):
                pass
        return df

    def _drop_nulls(self, df: pd.DataFrame) -> pd.DataFrame:
        before = len(df)
        df = df.dropna(how='all')
        logger.debug(f"Dropped {before - len(df)} fully-null rows")
        return df
