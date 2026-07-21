from typing import Any
import time
import requests


API_SERVER = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
REQUEST_TIMEOUT_SECONDS = 15
API_KEY = "07f68a6d208c1677d0019bf4108661d81908"

HEADERS = {
    "User-Agent": "PubMedExporter/1.0"
}

class ArticleFetchError(RuntimeError):
    """Raised when a PubMed article cannot be retrieved or parsed."""


def ncbi_request(endpoint, params):
    params["api_key"] = API_KEY
    params["tool"] = "PubMedExporter"

    for attempt in range(3):
        try:
            response = requests.get(
                f"{API_SERVER}/{endpoint}",
                params=params,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            if response.status_code == 429:
                time.sleep(2)
                continue
            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            if attempt == 2:
                raise e
            time.sleep(2)



def fetch_article_xml(doi: str) -> str:
    doi = doi.strip()
    if not doi:
        raise ArticleFetchError("DOI is empty.")
    
    try:
        response = ncbi_request(
            "esearch.fcgi",
            {
                "db": "pubmed",
                "term": f"{doi}[doi]",
                "retmode": "json",
            }
        )
        search = response.json()

    except Exception as e:
        raise ArticleFetchError(
            f"Search failed for {doi}: {e}"
        )

    pmids = (
        search
        .get("esearchresult", {})
        .get("idlist", [])
    )

    if not pmids:
        raise ArticleFetchError(
            f"No PMID found for {doi}"
        )
    pmid = pmids[0]

    try:
        response = ncbi_request(
            "efetch.fcgi",
            {
                "db": "pubmed",
                "id": pmid,
                "retmode": "xml",
            }
        )
        xml = response.text

    except Exception as e:
        raise ArticleFetchError(
            f"XML fetch failed for PMID {pmid}: {e}"
        )

    if not xml:
        raise ArticleFetchError(
            f"Empty XML returned for PMID {pmid}"
        )

    return xml