import json
import re
from collections.abc import Iterable
from io import BytesIO

import pandas as pd
import streamlit as st

from api_call import StudyFetchError, fetch_study_json


NCT_ID_PATTERN = re.compile(r"^NCT\d{8}$")


def read_uploaded_ids(uploaded_file) -> list[str]:
    """Read the first column from an uploaded CSV or Excel file."""
    filename = uploaded_file.name.lower()

    if filename.endswith(".csv"):
        dataframe = pd.read_csv(uploaded_file, header=None, dtype=str)
    elif filename.endswith((".xlsx", ".xls")):
        dataframe = pd.read_excel(uploaded_file, header=None, dtype=str)
    else:
        raise ValueError("Upload a CSV or Excel file.")

    if dataframe.empty or dataframe.shape[1] == 0:
        return []

    return dataframe.iloc[:, 0].dropna().astype(str).tolist()


def normalize_nct_ids(raw_ids: Iterable[str]) -> tuple[list[str], list[str], list[str]]:
    """Normalize, de-duplicate, and validate NCT IDs."""
    valid_ids: list[str] = []
    skipped_ids: list[str] = []
    duplicate_ids: list[str] = []
    seen: set[str] = set()

    for raw_id in raw_ids:
        nct_id = raw_id.strip().upper()
        if not nct_id:
            continue

        if not NCT_ID_PATTERN.fullmatch(nct_id):
            skipped_ids.append(nct_id)
            continue

        if nct_id in seen:
            duplicate_ids.append(nct_id)
            continue

        seen.add(nct_id)
        valid_ids.append(nct_id)

    return valid_ids, skipped_ids, duplicate_ids


def build_download_payload(studies: dict[str, dict]) -> bytes:
    return json.dumps(studies, indent=2, ensure_ascii=False).encode("utf-8")


st.set_page_config(page_title="ClinicalTrials JSON Exporter", page_icon=":material/download:", layout="wide")

st.title("ClinicalTrials JSON Exporter")
st.caption("Upload NCT IDs, fetch study records, and download one JSON object keyed by NCT ID.")

uploaded_file = st.file_uploader("NCT ID file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    try:
        raw_ids = read_uploaded_ids(uploaded_file)
        valid_ids, skipped_ids, duplicate_ids = normalize_nct_ids(raw_ids)
    except Exception as exc:
        st.error(f"Could not read the uploaded file: {exc}")
        st.stop()

    summary_columns = st.columns(4)
    summary_columns[0].metric("Rows found", len(raw_ids))
    summary_columns[1].metric("Valid unique IDs", len(valid_ids))
    summary_columns[2].metric("Invalid skipped", len(skipped_ids))
    summary_columns[3].metric("Duplicates skipped", len(duplicate_ids))

    if skipped_ids:
        with st.expander("Invalid IDs skipped"):
            st.write(skipped_ids)

    if duplicate_ids:
        with st.expander("Duplicate IDs skipped"):
            st.write(duplicate_ids)

    if not valid_ids:
        st.error("No valid NCT IDs were found in the first column.")
        st.stop()

    if st.button("Fetch study JSON", type="primary"):
        studies: dict[str, dict] = {}
        failures: list[dict[str, str]] = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        for index, nct_id in enumerate(valid_ids, start=1):
            status_text.write(f"Fetching {nct_id} ({index}/{len(valid_ids)})")

            try:
                studies[nct_id] = fetch_study_json(nct_id)
            except StudyFetchError as exc:
                failures.append({"nct_id": nct_id, "error": str(exc)})

            progress_bar.progress(index / len(valid_ids))

        status_text.write("Fetch complete.")

        result_columns = st.columns(2)
        result_columns[0].metric("Studies retrieved", len(studies))
        result_columns[1].metric("Fetch failures", len(failures))

        if failures:
            with st.expander("Fetch failures"):
                st.dataframe(pd.DataFrame(failures), hide_index=True, use_container_width=True)

        if not studies:
            st.error("No studies were retrieved, so there is no JSON file to download.")
            st.stop()

        download_payload = build_download_payload(studies)
        st.download_button(
            "Download JSON by NCT ID",
            data=BytesIO(download_payload),
            file_name="clinical_trials_studies.json",
            mime="application/json",
        )
