import time
import xml.etree.ElementTree as ET
from io import BytesIO
import zipfile

import pandas as pd
import streamlit as st

from API.api_call_PM import (
    ArticleFetchError,
    fetch_article_xml,
)

from API.api_call_nejm import (
    get_supplementary_urls,
    download_file,
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

from utils.clean_ids import (
    clean_doi,
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
        nejm_files = {}

        progress = st.progress(0)

        for i, doi in enumerate(valid, 1):

            try:

                xml = fetch_article_xml(doi)

                articles[doi] = xml

                code_doi, code_nejm = clean_doi(doi)

                article_data = extract_fields(xml)

                article_data["doi_prefix"] = code_doi
                article_data["nejm_code"] = code_nejm

                rows.append(article_data)

                existing_files = get_supplementary_urls(
                    code_doi,
                    code_nejm,
                )
                
                if code_nejm.startswith("NEJM"):
                    nejm_files[doi] = {
                        "code": code_nejm,
                        "files": existing_files,
                    }

            except (ArticleFetchError, ValueError) as e:

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


        st.session_state["nejm_files"] = nejm_files


        st.success(
            f"{len(articles)} articles retrieved"
        )


        if nejm_files:

            number_of_files = sum(
                len(article["files"])
                for article in nejm_files.values()
            )

            st.info(
                f"{number_of_files} NEJM supplementary "
                f"files found for {len(nejm_files)} articles."
            )

        else:

            st.info(
                "No NEJM supplementary files found."
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

        left, middle = st.columns(2)


        left.download_button(
            "Download XML",
            BytesIO(xml_content),
            "pubmed_articles.xml",
            "application/xml",
        )


        middle.download_button(
            "Download CSV",
            BytesIO(
                pd.DataFrame(rows)
                .to_csv(index=False)
                .encode("utf-8")
            ),
            "pubmed_articles.csv",
            "text/csv",
        )


nejm_files = st.session_state.get(
    "nejm_files",
    {}
)


if nejm_files:

    st.subheader(
        "NEJM Supplementary Materials"
    )

    number_of_files = sum(
        len(article["files"])
        for article in nejm_files.values()
    )

    st.write(
        f"{number_of_files} files available "
        f"for {len(nejm_files)} articles."
    )

    if st.button(
        "Download All Files (ZIP)",
        type="primary",
    ):

        zip_buffer = BytesIO()

        downloaded_files = []
        failed_files = []

        total_files = number_of_files
        current_file = 0

        progress = st.progress(0)

        with zipfile.ZipFile(
            zip_buffer,
            "w",
            zipfile.ZIP_DEFLATED,
        ) as zip_file:

            for doi, article in nejm_files.items():

                code_nejm = article["code"]
                files = article["files"]

                for file_type, url in files.items():

                    try:

                        pdf_content = download_file(url)

                        filename = (
                            f"{code_nejm}_"
                            f"{file_type.lower()}.pdf"
                        )

                        zip_file.writestr(
                            filename,
                            pdf_content,
                        )

                        downloaded_files.append(
                            filename
                        )

                    except Exception as e:

                        failed_files.append(
                            {
                                "doi": doi,
                                "file": file_type,
                                "url": url,
                                "error": str(e),
                            }
                        )

                    current_file += 1

                    progress.progress(
                        current_file / total_files
                    )

        zip_buffer.seek(0)

        if downloaded_files:

            st.success(
                f"{len(downloaded_files)} files "
                f"successfully downloaded."
            )

            st.download_button(
                "Save ZIP",
                zip_buffer,
                "nejm_supplementary_files.zip",
                "application/zip",
            )

        else:

            st.error(
                "No NEJM files could be downloaded."
            )

        if failed_files:

            st.warning(
                f"{len(failed_files)} files "
                f"could not be downloaded."
            )

            with st.expander("Failed downloads"):

                st.dataframe(
                    pd.DataFrame(failed_files)
                )

    st.divider()

    st.subheader(
        "Download individually"
    )

    for doi, article in nejm_files.items():

        code_nejm = article["code"]

        st.markdown(
            f"### {code_nejm}"
        )

        for file_type, url in article["files"].items():

            st.link_button(
                f"Download {file_type}",
                url,
            )