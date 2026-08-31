#A partir d'un code 10.1056/NEJMoa050522, le séparé en 10.1056 et NEJMoa050522 avec une fonction qui prend en entrée un code DOI et retourne le préfixe et le suffixe.

def clean_doi(doi: str):

    # Remove any leading/trailing whitespace
    doi = doi.strip()

    # Check if the DOI is valid
    if not doi.startswith("10."):
        raise ValueError("Invalid DOI format")

    # Split the DOI into prefix and suffix
    code_doi, code_nejm = doi.split("/", 1)

    return code_doi, code_nejm