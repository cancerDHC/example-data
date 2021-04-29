# Example data for the CCDH project

This repository is intended to act as a store of example data files from across
the [NCI Cancer Research Data Commons](https://datascience.cancer.gov/data-commons)
nodes in a number of formats. Each directory represents a single dataset downloaded
from a node, and contains a [Jupyter Notebook](https://jupyter.org/) documenting how
they were downloaded. [CCDH](https://datacommons.cancer.gov/center-cancer-data-harmonization)
will use this example data to build and test the CRDC-H data model.

## Using Jupyter Notebooks

Many of the processes in this repository are documented in
[Jupyter Notebook format](https://nbformat.readthedocs.io/) files,
which have an `.ipynb` extension. These files can be viewed directly in
GitHub (see
*[CDA example for subject 09CO022](./cptac2-subject-09CO022/CDA%20example%20for%20subject%2009CO022.ipynb)*
as an example). You can also run it in the [Jupyter Notebook viewer](https://nbviewer.jupyter.org/) (see
*[CDA example for subject 09CO022](https://nbviewer.jupyter.org/github/cancerDHC/example-data/blob/0a983991cbc274a7fbf3121aa8ae10047549fa1a/cptac2-subject-09CO022/CDA%20example%20for%20subject%2009CO022.ipynb)*
as an example).

If you would like to execute this file, you will need to
[install Jupyter Notebook](https://jupyter.org/install.html). You can then download
the `.ipynb` file and open it in Jupyter Notebook on your computer by running:

```bash
$ jupyter notebook cptac2-subject-09CO022/CDA\ example\ for\ subject\ 09CO022.ipynb
```
