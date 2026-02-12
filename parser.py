import pandas as pd
from db import get_template_columns, get_numeric_columns


def read_file(filepath):
    try:
        if filepath.endswith(".csv"):
            df = pd.read_csv(filepath)
        elif filepath.endswith((".xls", ".xlsx")):
            df = pd.read_excel(filepath)
        else:
            return None, "Unsupported file format. Allowed: .csv, .xls, .xlsx"
    except Exception as e:
        return None, f"Failed to read file: {e}"

    df.columns = [c.strip().lower() for c in df.columns]
    return df, None


def validate_and_map(df):
    file_columns = set(df.columns)
    template_columns = set(get_template_columns())

    missing = template_columns - file_columns
    extra = file_columns - template_columns

    if missing:
        msg_parts = [
            "File does not match the template.",
            f"Missing required columns: {', '.join(sorted(missing))}",
        ]
        if extra:
            msg_parts.append(f"Extra columns in file: {', '.join(sorted(extra))}")
        msg_parts.append(f"Expected columns: {', '.join(sorted(template_columns))}")
        return None, "\n".join(msg_parts)

    template_cols_ordered = get_template_columns()
    df = df[template_cols_ordered].copy()

    numeric_cols = get_numeric_columns()
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if len(df) == 0:
        return None, "File contains no data rows."

    return df, None


def parse_file(filepath):
    # full pipeline
    df, error = read_file(filepath)
    if error:
        return None, error

    return validate_and_map(df)
