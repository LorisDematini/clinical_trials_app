# ClinicalTrials JSON Exporter

Based on the [SBIM](https://www.sbim-stlouis.org/) need of automating the extraction of Clinical Trials items, the first step is to retrieve the data associated to each clinical trial. A unique NCT id is associated to each clinical trial.
We provide here a small dockerized Streamlit webapp built with Codex (GPT5.5 high reasonning). The user must upload a CSV or Excel file containing NCT IDs. The app fetches study JSON from ClinicalTrials.gov, and downloads the retrieved studies as one JSON object keyed by NCT ID.

## Input file

Use a `.csv`, `.xlsx`, or `.xls` file with one NCT ID per row in the first column.

## Run locally with uv

```bash
uv run streamlit run app.py
```

Open the URL Streamlit prints, usually `http://localhost:8501`.

## Run with Docker

```bash
docker build -t clinical-trials-app .
docker run --rm -p 8501:8501 clinical-trials-app
```

Then open `http://localhost:8501`.

## Output

The download is `clinical_trials_studies.json`, containing a JSON object of successfully retrieved study records. Each key is an NCT ID, and each value is the fetched study JSON. Invalid IDs, duplicate IDs, and failed API calls are shown in the app and excluded from the download.
