import re
import xml.etree.ElementTree as ET

from utils.regex import (
    PHASE_PATTERN,
    TOTAL_PATTERN,
    DATE_PATTERN,
    DESIGN_PATTERNS,
)

ROMAN = {
    "I": 1,
    "II": 2,
    "III": 3
}

def extract_dates(text):

    match = DATE_PATTERN.search(text)

    if not match:
        return None, None

    return (
        match.group(1),
        match.group(2)
    )

def convert_phase(value):
    value = value.upper()

    if value.isdigit():
        return str(int(value))

    return str(ROMAN[value])

def extract_trial_features(methods, results):

    text = methods + "\n" + results
    lower = text.lower()

    phase = None

    match = PHASE_PATTERN.search(text)

    if match:
        values = re.split(r"\s*[,/]\s*", match.group(1))
        phase = " | ".join(convert_phase(v) for v in values)

    design = " | ".join(
        x
        for x in DESIGN_PATTERNS
        if x in lower
    )

    inclusion_start, inclusion_end = extract_dates(results)

    total_patients = None

    match = TOTAL_PATTERN.search(results)
    if not match:
        match = TOTAL_PATTERN.search(methods)

    if match:
        number = match.group(1).replace(",", "").strip()

        if number.isdigit():
            total_patients = int(number)

    return {
        "phase": phase,
        "study_design": design,
        "inclusion_start": inclusion_start,
        "inclusion_end": inclusion_end,
        "total_patients": total_patients,
    }


def extract_fields(xml):

    root = ET.fromstring(xml)

    article = root.find(".//PubmedArticle")

    if article is None:
        return {}


    citation = article.find("MedlineCitation")
    article_data = citation.find("Article")


    pmid = citation.findtext("PMID")


    doi = next(
        (
            x.text
            for x in article.findall(".//ArticleId")
            if x.attrib.get("IdType") == "doi"
        ),
        None
    )


    pubdate = article_data.find(
        ".//JournalIssue/PubDate"
    )

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



    title_node = article_data.find(
        "ArticleTitle"
    )

    title = (
        "".join(title_node.itertext())
        if title_node is not None
        else None
    )


    methods = []
    results = []


    for abstract in article.findall(
        ".//AbstractText"
    ):

        label = abstract.attrib.get(
            "Label",
            ""
        ).upper()

        category = abstract.attrib.get(
            "NlmCategory",
            ""
        ).upper()

        text = "".join(
            abstract.itertext()
        ).strip()


        if (
            "METHOD" in label
            and "CLASSIFICATION" not in label
        ):
            methods.append(text)


        elif (
            "RESULT" in label
            or category == "RESULTS"
            or "FINDINGS" in label
        ):
            results.append(text)



    methods = "\n".join(methods)
    results = "\n".join(results)

    sponsors = []


    for grant in article.findall(".//Grant"):

        agency = grant.findtext(
            "Agency",
            ""
        )

        grant_id = grant.findtext(
            "GrantID",
            ""
        )

        sponsors.append(
            f"{agency} ({grant_id})"
        )


    for abstract in article.findall(
        ".//AbstractText"
    ):

        if abstract.attrib.get(
            "Label",
            ""
        ).upper() == "FUNDING":

            sponsors.append(
                "".join(
                    abstract.itertext()
                )
            )



    return {
        "pmid": pmid,
        "doi": doi,
        "date": date,
        "title": title,

        **extract_trial_features(
            methods,
            results
        ),

        "methods": methods,
        "results": results,
        "sponsors": " | ".join(sponsors),
    }
