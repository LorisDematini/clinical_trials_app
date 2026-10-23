LANCET_BASE_URL = (
    "https://www.thelancet.com/journals/lancet/article/"
)


def get_lancet_article_url(code_lancet: str):

    return (
        f"{LANCET_BASE_URL}"
        f"PII{code_lancet}"
    )