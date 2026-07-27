import time
import xml.etree.ElementTree as ET
from io import BytesIO

import pandas as pd
import streamlit as st

from API.api_call_PM import (
    ArticleFetchError,
    fetch_article_xml,
)

from parsers.Parser_PM import (
    extract_fields,
)

from utils.files import (
    read_uploaded_ids,
)

from utils.validation import (
    normalize_pm_ids,
)

st.title("PubMed Exporter")

file = st.file_uploader(
    "Reference file",
    type=["csv", "xlsx", "xls"],
)

if file:

    raw = read_uploaded_ids(file)

    valid, invalid, dup = normalize_pm_ids(raw)

    cols = st.columns(4)

    cols[0].metric("Rows", len(raw))
    cols[1].metric("Valid DOI", len(valid))
    cols[2].metric("Invalid", len(invalid))
    cols[3].metric("Duplicates", len(dup))

    if st.button(
        "Fetch articles",
        type="primary",
    ):

        articles = {}
        rows = []
        errors = []

        progress = st.progress(0)

        for i, doi in enumerate(valid, 1):

            try:

                xml = fetch_article_xml(doi)

                articles[doi] = xml

                rows.append(
                    extract_fields(xml)
                )

            except ArticleFetchError as e:

                errors.append(
                    {
                        "doi": doi,
                        "error": str(e),
                    }
                )

            time.sleep(0.2)

            progress.progress(
                i / len(valid)
            )

        st.success(
            f"{len(articles)} articles retrieved"
        )

        if errors:
            st.dataframe(
                pd.DataFrame(errors)
            )

        root = ET.Element(
            "PubmedArticleSet"
        )

        for xml in articles.values():

            article_root = ET.fromstring(xml)

            for article in article_root.findall(
                "PubmedArticle"
            ):
                root.append(article)

        xml_content = ET.tostring(
            root,
            encoding="utf-8",
            xml_declaration=True,
        )

        left, right = st.columns(2)

        left.download_button(
            "Download XML",
            BytesIO(xml_content),
            "pubmed_articles.xml",
            "application/xml",
        )

        right.download_button(
            "Download CSV",
            BytesIO(
                pd.DataFrame(rows)
                .to_csv(index=False)
                .encode("utf-8")
            ),
            "pubmed_articles.csv",
            "text/csv",
        )