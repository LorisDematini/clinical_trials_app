import requests


NEJM_BASE_URL = "https://www.nejm.org/doi/suppl"


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": (
        "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7"
    ),
}


def get_supplementary_urls(
    code_doi: str,
    code_nejm: str,
):

    code_lower = code_nejm.lower()

    base_url = (
        f"{NEJM_BASE_URL}/{code_doi}/{code_nejm}/suppl_file/"
    )

    return {
        "Protocol": (
            f"{base_url}"
            f"{code_lower}_protocol.pdf"
        ),
        "Appendix": (
            f"{base_url}"
            f"{code_lower}_appendix.pdf"
        ),
    }


def download_file(url: str):

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    return response.content