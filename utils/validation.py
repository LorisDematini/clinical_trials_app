from collections.abc import Iterable
from utils.regex import NCT_ID_PATTERN, DOI_PATTERN

def normalize_nct_ids(ids: Iterable[str]):

    valid = []
    invalid = []
    duplicates = []

    seen = set()

    for value in ids:

        nct = value.strip().upper()

        if not NCT_ID_PATTERN.fullmatch(nct):
            invalid.append(nct)

        elif nct in seen:
            duplicates.append(nct)

        else:
            seen.add(nct)
            valid.append(nct)

    return valid, invalid, duplicates

def normalize_pm_ids(refs: Iterable[str]):

    valid = []
    invalid = []
    duplicates = []

    seen = set()

    for ref in refs:

        match = DOI_PATTERN.search(ref)

        if not match:
            invalid.append(ref)
            continue

        doi = match.group()

        if doi in seen:
            duplicates.append(doi)

        else:
            seen.add(doi)
            valid.append(doi)

    return valid, invalid, duplicates