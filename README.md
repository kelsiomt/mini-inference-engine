# Mini Inference Engine

Lightweight logical inference engine focused exclusively on sentences using the verb “to be”, supported by minimal spaCy text preprocessing.

---

## Key Features

- Text Preprocessing (spaCy) Uses the pt_core_news_sm model only for cleaning, tokenization and normalization.
- Simplified Logical Inference Supports forward chaining based solely on statements like:
  - “A is B”,
  - “B is C”, enabling inference such as “A is C”.
- Knowledge Queries Ability to query stored and inferred relations.
- Minimal Web Interface Simple UI for inserting facts and viewing inferred knowledge.
- Local JSON Persistence Knowledge base stored in a JSON file for transparency and easy versioning.
- Docker or Local Execution Ready for development environments and rapid deployment scenarios.

---

## Installation & Execution

### Run Locally

Requirements:

- Python 3.11+
- Updated pip
- spaCy + Portuguese model
- .venv config

Activate venv

```bash
python -m venv .venv

# for Windows
.\.venv\Scripts\activate

# for UNIX
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
python -m spacy download pt_core_news_sm
```

Start the server:

```bash
python app.py
```

---

Run with Docker (Recommended)

Build the image:

```sh
docker build -t inference-engine .
```

Run the container:

```sh
docker run -p 8080:8080 inference-engine
```

Open in browser: [http://localhost:8080](http://localhost:8080)
