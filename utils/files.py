import pandas as pd 

def read_uploaded_ids(file):

    df = (
        pd.read_csv(
            file,
            header=None,
            dtype=str,
            quotechar='"'
        )
        if file.name.endswith(".csv")
        else pd.read_excel(file, header=None, dtype=str)
    )

    if df.empty:
        return []

    return (
        df.iloc[:, 0]
        .dropna()
        .astype(str)
        .tolist()
    )