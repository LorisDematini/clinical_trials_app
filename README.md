# ClinicalTrials & PubMed Exporter

This Streamlit application was developed to automate the retrieval of information from **ClinicalTrials.gov** and **PubMed**, based on the needs of the [SBIM](https://www.sbim-stlouis.org/).

The application provides two independent modules:

* **ClinicalTrials Exporter**: retrieves complete study records from ClinicalTrials.gov using NCT identifiers.
* **PubMed Exporter**: retrieves complete PubMed XML records from bibliography references containing DOI identifiers.

## ClinicalTrials Exporter

**Input**

* `.csv`, `.xlsx` or `.xls`
* One **NCT ID** per row in the first column.

The application:

* validates NCT IDs
* removes duplicates
* reports invalid IDs
* downloads the complete study JSON
* generates a summary CSV containing:

  * NCT ID
  * Study first submission date
  * Study type
  * Primary outcomes
  * Eligibility criteria
  * Standard ages

Outputs:

* `clinical_trials.json`
* `clinical_trials.csv`

---

## PubMed Exporter

**Input**

* `.csv`, `.xlsx` or `.xls`
* One bibliography reference per row containing a DOI.

The application:

* extracts DOI identifiers
* validates references
* removes duplicates
* retrieves the corresponding PubMed record
* downloads the complete PubMed XML

Output:

* `pubmed_articles.xml`

---

## Run locally

```bash
uv sync
uv run streamlit run app.py
```

The application is usually available at `http://localhost:8501`.

---

## Run with Docker

```bash
docker build -t clinical-trials-app .
docker run --rm -p 8501:8501 clinical-trials-app
```

---

## Technologies

* Python
* Streamlit
* Pandas
* Requests
* ClinicalTrials.gov API v2
* NCBI Entrez E-utilities
* Docker
* uv
