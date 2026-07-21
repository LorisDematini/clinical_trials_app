import re
from io import BytesIO
from collections.abc import Iterable
import time
import xml.etree.ElementTree as ET

import pandas as pd
import streamlit as st

from API.api_call_PM import ArticleFetchError, fetch_article_xml


DOI_PATTERN = re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+")

def read_refs(file):
    df = pd.read_csv(file, header=None, dtype=str) if file.name.endswith(".csv") else pd.read_excel(file, header=None, dtype=str)
    return df.iloc[:,0].dropna().astype(str).tolist() if not df.empty else []

def normalize_refs(refs: Iterable[str]):
    valid, invalid, dup, seen = [], [], [], set()

    for ref in refs:
        m = DOI_PATTERN.search(ref)
        if not m:
            invalid.append(ref)
            continue
        doi = m.group()

        if doi in seen:
            dup.append(doi)
        else:
            seen.add(doi)
            valid.append(doi)

    return valid, invalid, dup

st.title("PubMed Exporter")

file = st.file_uploader(
    "Reference file",
    type=["csv","xlsx","xls"]
)


if file:
    try:
        raw = read_refs(file)
        valid, invalid, dup = normalize_refs(raw)
    except Exception as e:
        st.error(e)
        st.stop()

    c = st.columns(4)
    c[0].metric("Rows", len(raw))
    c[1].metric("Valid DOI", len(valid))
    c[2].metric("Invalid", len(invalid))
    c[3].metric("Duplicates", len(dup))

    if invalid:
        with st.expander("Invalid references"):
            st.write(invalid)

    if dup:
        with st.expander("Duplicate DOI"):
            st.write(dup)

    if st.button("Fetch articles", type="primary"):
        articles, errors = {}, []
        bar = st.progress(0)
        for i, doi in enumerate(valid, 1):
            try:
                xml = fetch_article_xml(doi)
                articles[doi] = xml
            except ArticleFetchError as e:
                errors.append({
                    "doi": doi,
                    "error": str(e)
                })
            time.sleep(0.2)
            bar.progress(i / len(valid))

        st.success(f"{len(articles)} articles retrieved")

        if errors:
            st.dataframe(pd.DataFrame(errors))
        root = ET.Element("PubmedArticleSet")

        for xml in articles.values():
            article_root = ET.fromstring(xml)
            for article in article_root.findall("PubmedArticle"):
                root.append(article)
                xml_content = ET.tostring(
                    root,
                    encoding="utf-8",
                    xml_declaration=True
                )

        st.download_button(
            "Download XML",
            BytesIO(xml_content),
            "pubmed_articles.xml",
            "application/xml"
        )