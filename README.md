# Electronics

This repository accompanies the article *"Automatic Metadata Extraction Leveraging Large Language Models in Digital Humanities"*, from *Electronics* journal. It contains the code and experiment setup used to evaluate automatic metadata extraction using large language models in Digital Humanities contexts. <br> ⚠️ Warning: In this work, the Geonames API has been used to obtain the URIs of the locations, as far as possible. This API can be used free of charge, but it allows 1,000 requests per hour per user, so it is likely that the same user will not be able to generate the metadata for both datasets in one hour. 

---

## Repository Structure

```
├── code/           # Source code and experiment scripts
├── data/           # Datasets and generated metadata
├── evaluation/     # Manual evaluation results
└── README.md       # This document
```

---

## Requirements

Before running the experiment, make sure the following are installed:

- Python 3.9 or higher  
- Dependencies listed in `requirements.txt`

Install dependencies with:

```pip install -r requirements.txt```

---

## Running the Experiment

To launch the experiment, navigate to the `code` directory:

```cd code```

### Spanish Dataset

```python main.py -l spa```

### English Dataset

```python main.py -l eng```

---

## Contact

For questions or collaborations, please contact the corresponding author at:  
**[adriana.morejon@ua.es]**
