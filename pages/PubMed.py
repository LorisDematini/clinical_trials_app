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

import xml.etree.ElementTree as ET


def extract_fields(xml: str):

    root = ET.fromstring(xml)

    article = root.find(".//PubmedArticle")
    citation = article.find("MedlineCitation")
    article_data = citation.find("Article")


    # PMID
    pmid = citation.findtext("PMID")


    # DOI
    doi = next(
        (
            x.text
            for x in article.findall(".//ArticleId")
            if x.attrib.get("IdType") == "doi"
        ),
        None
    )


    # Publication date
    pubdate = article_data.find(".//JournalIssue/PubDate")

    date = "-".join(
        filter(
            None,
            [
                pubdate.findtext("Year"),
                pubdate.findtext("Month"),
                pubdate.findtext("Day"),
            ],
        )
    ) if pubdate is not None else None


    # Title
    title = "".join(article_data.find("ArticleTitle").itertext())


    # Abstract
    methods = []
    results = []

    for abstract in article.findall(".//AbstractText"):

        label = abstract.attrib.get("Label", "").upper()
        category = abstract.attrib.get("NlmCategory", "").upper()

        text = "".join(abstract.itertext()).strip()

        if "METHOD" in label or category == "METHODS":
            methods.append(text)

        elif "RESULT" in label or category == "RESULTS":
            results.append(text)

        elif "FINDINGS" in label or category == "FINDINGS":
            results.append(text)


    # Affiliations
    affiliations = " | ".join(
        a.text.strip()
        for a in article.findall(".//Affiliation")
        if a.text
    )


    # Sponsors (Grant + Funding section)

    grant_sponsors = [
        f"{g.findtext('Agency','')} ({g.findtext('GrantID','')})".strip()
        for g in article.findall(".//Grant")
    ]

    funding_sponsors = [
        "".join(a.itertext()).strip()
        for a in article.findall(".//AbstractText")
        if a.attrib.get("Label", "").upper() == "FUNDING"
        or a.attrib.get("NlmCategory", "").upper() == "FUNDING"
    ]

    sponsors = " | ".join(
        x for x in grant_sponsors + funding_sponsors if x
    )


    return {
        "pmid": pmid,
        "doi": doi,
        "date": date,
        "title": title,
        "methods": "\n".join(methods),
        "results": "\n".join(results),
        "affiliations": affiliations,
        "sponsors": sponsors,
    }




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
        articles, rows, errors = {}, [], []
        bar = st.progress(0)
        for i, doi in enumerate(valid, 1):
            try:
                xml = fetch_article_xml(doi)
                articles[doi] = xml
                rows.append(extract_fields(xml))
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

        st.download_button(
            "Download CSV",
            BytesIO(
                pd.DataFrame(rows).to_csv(index=False).encode("utf-8")
            ),
            "pubmed_articles.csv",
            "text/csv"
        )