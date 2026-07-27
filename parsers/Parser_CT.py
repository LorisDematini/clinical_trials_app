def extract_fields(study):

    protocol = study.get("protocolSection", {})

    eligibility = protocol.get(
        "eligibilityModule",
        {}
    )

    outcomes = (
        protocol
        .get("outcomesModule", {})
        .get("primaryOutcomes", [])
    )

    return {

        "nctId":
            protocol.get(
                "identificationModule",
                {}
            ).get("nctId"),

        "studyFirstSubmitDate":
            protocol.get(
                "statusModule",
                {}
            ).get("studyFirstSubmitDate"),

        "studyType":
            protocol.get(
                "designModule",
                {}
            ).get("studyType"),

        "primaryOutcomes":

            " || ".join(

                f"Measure: {o.get('measure','')}\n"
                f"TimeFrame: {o.get('timeFrame','')}\n"
                f"Description: {o.get('description','')}"

                for o in outcomes
            ),

        "eligibilityCriteria":
            eligibility.get(
                "eligibilityCriteria"
            ),

        "stdAges":
            " | ".join(
                eligibility.get(
                    "stdAges",
                    []
                )
            )
    }