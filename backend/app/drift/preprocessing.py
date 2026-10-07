import numpy as np
import pandas as pd


def clean_weather_frame(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    for column in cleaned.columns:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
    cleaned = cleaned.dropna(subset=["observation_date"]).sort_values("observation_date")
    cleaned = cleaned.reset_index(drop=True)
    return cleaned


def prepare_variable_series(df: pd.DataFrame, variable: str) -> pd.Series:
    values = pd.to_numeric(df[variable], errors="coerce").dropna()
    return values.astype(float)
