from typing import Any

import requests


API_SERVER = "https://clinicaltrials.gov/api/v2"
REQUEST_TIMEOUT_SECONDS = 15


class StudyFetchError(RuntimeError):
    """Raised when a study JSON cannot be retrieved or parsed."""


def fetch_study_json(nct_id: str) -> dict[str, Any]:
    """Fetch a ClinicalTrials.gov study JSON document for a single NCT ID."""
    normalized_id = nct_id.strip().upper()
    if not normalized_id:
        raise StudyFetchError("NCT ID is empty.")

    url = f"{API_SERVER}/studies/{normalized_id}"

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "unknown"
        raise StudyFetchError(f"HTTP {status_code} while fetching {normalized_id}.") from exc
    except requests.exceptions.Timeout as exc:
        raise StudyFetchError(f"Request timed out while fetching {normalized_id}.") from exc
    except requests.exceptions.RequestException as exc:
        raise StudyFetchError(f"Request failed while fetching {normalized_id}: {exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise StudyFetchError(f"Invalid JSON returned for {normalized_id}.") from exc

    if not isinstance(data, dict):
        raise StudyFetchError(f"Unexpected JSON payload for {normalized_id}.")

    return data
