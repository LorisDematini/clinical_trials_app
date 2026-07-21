import json, re
from io import BytesIO
from collections.abc import Iterable

import pandas as pd
import streamlit as st

from API.api_call_CT import StudyFetchError, fetch_study_json


NCT_ID_PATTERN = re.compile(r"^NCT\d{8}$")


def read_uploaded_ids(file):
    df = pd.read_csv(file, header=None, dtype=str) if file.name.endswith(".csv") else pd.read_excel(file, header=None, dtype=str)
    return df.iloc[:, 0].dropna().astype(str).tolist() if not df.empty else []


def normalize_nct_ids(ids: Iterable[str]):
    valid, invalid, dup, seen = [], [], [], set()

    for x in ids:
        nct = x.strip().upper()
        if not NCT_ID_PATTERN.fullmatch(nct):
            invalid.append(nct)
        elif nct in seen:
            dup.append(nct)
        else:
            seen.add(nct)
            valid.append(nct)

    return valid, invalid, dup


def extract_fields(study):
    p = study.get("protocolSection", {})
    e = p.get("eligibilityModule", {})

    outcomes = p.get("outcomesModule", {}).get("primaryOutcomes", [])

    return {
        "nctId": p.get("identificationModule", {}).get("nctId"),

        "studyFirstSubmitDate": p.get("statusModule", {}).get("studyFirstSubmitDate"),

        "studyType": p.get("designModule", {}).get("studyType"),

        "primaryOutcomes": " || ".join(
            f"Measure: {o.get('measure','')} \n "
            f"TimeFrame: {o.get('timeFrame','')}  \n "
            f"Description: {o.get('description','')}"
            for o in outcomes
        ),

        "eligibilityCriteria": e.get("eligibilityCriteria"),

        "stdAges": " | ".join(e.get("stdAges", []))
    }

st.title("ClinicalTrials Exporter")

file = st.file_uploader(
    "NCT ID file",
    type=["csv", "xlsx", "xls"]
)


if file:

    try:
        raw = read_uploaded_ids(file)
        valid, invalid, dup = normalize_nct_ids(raw)
    except Exception as e:
        st.error(e)
        st.stop()


    c = st.columns(4)
    c[0].metric("Rows", len(raw))
    c[1].metric("Valid", len(valid))
    c[2].metric("Invalid", len(invalid))
    c[3].metric("Duplicates", len(dup))


    if invalid:
        with st.expander("Invalid IDs"):
            st.write(invalid)

    if dup:
        with st.expander("Duplicate IDs"):
            st.write(dup)


    if st.button("Fetch studies", type="primary"):

        studies, rows, errors = {}, [], []
        bar = st.progress(0)

        for i, nct in enumerate(valid, 1):

            try:
                study = fetch_study_json(nct)
                studies[nct] = study
                rows.append(extract_fields(study))

            except StudyFetchError as e:
                errors.append({"nct_id": nct, "error": str(e)})

            bar.progress(i / len(valid))


        st.success(f"{len(studies)} studies retrieved")


        if errors:
            st.dataframe(pd.DataFrame(errors))


        col1, col2 = st.columns(2)

        col1.download_button(
            "Download JSON",
            BytesIO(json.dumps(studies, indent=2, ensure_ascii=False).encode()),
            "clinical_trials.json",
            "application/json"
        )

        col2.download_button(
            "Download CSV",
            BytesIO(pd.DataFrame(rows).to_csv(index=False).encode()),
            "clinical_trials.csv",
            "text/csv"
        )