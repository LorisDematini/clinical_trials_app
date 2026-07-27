import json
from io import BytesIO

import pandas as pd
import streamlit as st

from API.api_call_CT import (
    StudyFetchError,
    fetch_study_json,
)

from parsers.Parser_CT import (
    extract_fields,
)

from utils.files import (
    read_uploaded_ids,
)

from utils.validation import (
    normalize_nct_ids,
)

st.title("ClinicalTrials Exporter")

file = st.file_uploader(
    "NCT ID file",
    type=["csv", "xlsx", "xls"],
)

if file:

    try:

        raw = read_uploaded_ids(file)

        valid, invalid, dup = (
            normalize_nct_ids(raw)
        )

    except Exception as e:

        st.error(e)
        st.stop()

    cols = st.columns(4)

    cols[0].metric("Rows", len(raw))
    cols[1].metric("Valid", len(valid))
    cols[2].metric("Invalid", len(invalid))
    cols[3].metric("Duplicates", len(dup))

    if invalid:
        with st.expander("Invalid IDs"):
            st.write(invalid)

    if dup:
        with st.expander("Duplicate IDs"):
            st.write(dup)

    if st.button(
        "Fetch studies",
        type="primary",
    ):

        studies = {}

        rows = []

        errors = []

        progress = st.progress(0)

        for i, nct in enumerate(valid, 1):

            try:

                study = fetch_study_json(nct)

                studies[nct] = study

                rows.append(
                    extract_fields(study)
                )

            except StudyFetchError as e:

                errors.append(
                    {
                        "nct_id": nct,
                        "error": str(e),
                    }
                )

            progress.progress(
                i / len(valid)
            )

        st.success(
            f"{len(studies)} studies retrieved"
        )

        if errors:
            st.dataframe(
                pd.DataFrame(errors)
            )

        left, right = st.columns(2)

        left.download_button(
            "Download JSON",
            BytesIO(
                json.dumps(
                    studies,
                    indent=2,
                    ensure_ascii=False,
                ).encode()
            ),
            "clinical_trials.json",
            "application/json",
        )

        right.download_button(
            "Download CSV",
            BytesIO(
                pd.DataFrame(rows)
                .to_csv(index=False)
                .encode()
            ),
            "clinical_trials.csv",
            "text/csv",
        )