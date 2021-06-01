# GDC to CCDH Conversion

This notebook demonstrates one method for converting GDC data into CCDH (CRDC-H) instance data: by reading node data as JSON and writing it out in the LinkML model. The LinkML can be used to [generate](https://github.com/linkml/linkml#python-dataclasses) [Python Data Classes](https://docs.python.org/3/library/dataclasses.html), which can then be exported in JSON-LD, a JSON-based format used to represent RDF data.

## Why Python Data Classes?

Python Data Classes provide several useful features that we will demonstrate below:

1. **Python Data Classes are generated automatically.** Rather than requiring additional effort to maintain a Python library for accessing the CCDH model, the [LinkML toolset](https://linkml.github.io/) can generate the Python Data Classes directly from the CCDH model, ensuring that users can always access the most recent version of the CCDH model programmatically. This also allows us to maintain Python Data Classes for accessing previous versions of the CCDH model, which we plan to use to implement [data migration between CCDH model versions](https://cancerdhc.github.io/ccdhmodel/latest/data-migration/)
2. **Python Data Classes provide validation on creation.** As we will demonstrate below, creating a Python Data Class requires that all required attributes are filled in, and all fields are filled in the format or enumeration expected.
3. **Easy to use in Python IDEs.** Since the generated Python Data Classes includes model documentation in Python, users using Python IDEs can see available options and documentation while writing their code.

## Setup

We start by installing the [LinkML](https://pypi.org/project/linkml/) and [pandas](https://pypi.org/project/pandas/) packages. You only need to do this once.


```python
import sys

# Install LinkML.
# We use our own fork of LinkML, but all changes made to this repository will eventually be sent
# upstream to the main LinkML release.
#!{sys.executable} -m pip install git+https://github.com/cancerDHC/linkml.git@ccdh-dev#egg=linkml

# Install pandas.
#!{sys.executable} -m pip install pandas

# Install rdflib.
#!{sys.executable} -m pip install rdflib

# Install JSON Schema.
#!{sys.executable} -m pip install jsonschema
```

## Loading GDC data as an example

In this demonstration, we will use a dataset of 560 cases relating to head and neck cancers previously downloaded from the public GDC API as [documented elsewhere in this repository](https://github.com/cancerDHC/example-data/blob/main/head-and-mouth/Head%20and%20Mouth%20Cancer%20Datasets.ipynb).


```python
import json
import pandas

with open('head-and-mouth/gdc-head-and-mouth.json') as file:
    gdc_head_and_mouth = json.load(file)
    
pandas.DataFrame(gdc_head_and_mouth)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>aliquot_ids</th>
      <th>case_id</th>
      <th>created_datetime</th>
      <th>diagnoses</th>
      <th>diagnosis_ids</th>
      <th>disease_type</th>
      <th>id</th>
      <th>primary_site</th>
      <th>sample_ids</th>
      <th>samples</th>
      <th>...</th>
      <th>submitter_sample_ids</th>
      <th>submitter_slide_ids</th>
      <th>updated_datetime</th>
      <th>analyte_ids</th>
      <th>portion_ids</th>
      <th>submitter_analyte_ids</th>
      <th>submitter_portion_ids</th>
      <th>days_to_lost_to_followup</th>
      <th>index_date</th>
      <th>lost_to_followup</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[cfcde639-3045-4f66-84a6-ec74b090a5b6]</td>
      <td>cd7e514f-71ba-4cc1-b74a-a22c6248169c</td>
      <td>2017-06-01T08:57:57.249456-05:00</td>
      <td>[{'age_at_diagnosis': 19592, 'classification_o...</td>
      <td>[5d2d67d1-4611-4a18-9a66-89823aaa8e3c]</td>
      <td>Adenomas and Adenocarcinomas</td>
      <td>cd7e514f-71ba-4cc1-b74a-a22c6248169c</td>
      <td>Nasopharynx</td>
      <td>[bdc73f48-dc0b-487d-abbe-e3a977b6830a]</td>
      <td>[{'created_datetime': '2017-06-01T10:44:57.790...</td>
      <td>...</td>
      <td>[AD6426_sample]</td>
      <td>[AD6426_slide]</td>
      <td>2018-10-25T11:34:27.425461-05:00</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>[9069bdd7-e16a-462c-881c-581c8aab6910, a74915f...</td>
      <td>9023c9bf-02a0-4396-8161-304089957b62</td>
      <td>None</td>
      <td>[{'age_at_diagnosis': 24286, 'ajcc_clinical_m'...</td>
      <td>[706b1290-3a85-54ea-a123-e8bd14b085bc]</td>
      <td>Squamous Cell Neoplasms</td>
      <td>9023c9bf-02a0-4396-8161-304089957b62</td>
      <td>Larynx</td>
      <td>[8b2588c8-4261-492b-b173-2490a5de668f, badeaed...</td>
      <td>[{'created_datetime': '2018-05-17T12:19:46.292...</td>
      <td>...</td>
      <td>[TCGA-CN-6012-10A, TCGA-CN-6012-01A, TCGA-CN-6...</td>
      <td>[TCGA-CN-6012-01Z-00-DX1, TCGA-CN-6012-01A-01-...</td>
      <td>2019-08-06T14:25:25.511101-05:00</td>
      <td>[80c6fde2-b6bb-4f40-908a-f116c466d296, 6f77017...</td>
      <td>[bada788e-5112-4d21-a079-72729bd0cc83, fe24eea...</td>
      <td>[TCGA-CN-6012-01A-11D, TCGA-CN-6012-10A-01W, T...</td>
      <td>[TCGA-CN-6012-01A-13-2072-20, TCGA-CN-6012-10A...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>[8f695cd3-01dd-4601-8b17-37cf40514422, f0e325f...</td>
      <td>55f96a9c-e2c8-4243-8a7e-94bc6fab73a6</td>
      <td>None</td>
      <td>[{'age_at_diagnosis': 20992, 'ajcc_clinical_m'...</td>
      <td>[40954a8e-e4c2-5604-937b-0a79ac7489d2]</td>
      <td>Squamous Cell Neoplasms</td>
      <td>55f96a9c-e2c8-4243-8a7e-94bc6fab73a6</td>
      <td>Larynx</td>
      <td>[a7692585-a129-4671-bfe5-98342a326776, b069c55...</td>
      <td>[{'composition': None, 'created_datetime': Non...</td>
      <td>...</td>
      <td>[TCGA-CV-7261-01Z, TCGA-CV-7261-11A, TCGA-CV-7...</td>
      <td>[TCGA-CV-7261-01A-01-TS1, TCGA-CV-7261-01Z-00-...</td>
      <td>2019-08-06T14:26:28.608672-05:00</td>
      <td>[a72f2de7-eb40-4818-a104-edb508d5517b, e8120e5...</td>
      <td>[177fa10b-0135-468d-b5a3-6f30cc3cd390, f51d76a...</td>
      <td>[TCGA-CV-7261-10A-01D, TCGA-CV-7261-01A-11R, T...</td>
      <td>[TCGA-CV-7261-10A-01, TCGA-CV-7261-01A-13-2074...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>3</th>
      <td>[1265fd12-4706-43b0-84f3-d16d46f20963, 3443e1b...</td>
      <td>c9a36eb5-ac3e-424e-bc2e-303de7105957</td>
      <td>None</td>
      <td>[{'age_at_diagnosis': 21886, 'ajcc_clinical_m'...</td>
      <td>[48e8dd81-ed4d-5c54-af66-84e86477d5c8]</td>
      <td>Squamous Cell Neoplasms</td>
      <td>c9a36eb5-ac3e-424e-bc2e-303de7105957</td>
      <td>Oropharynx</td>
      <td>[256469d0-5f36-4966-bf4f-3b4297e55f43, bd90f96...</td>
      <td>[{'composition': None, 'created_datetime': Non...</td>
      <td>...</td>
      <td>[TCGA-BA-A6DL-10A, TCGA-BA-A6DL-01Z, TCGA-BA-A...</td>
      <td>[TCGA-BA-A6DL-01Z-00-DX1, TCGA-BA-A6DL-01A-02-...</td>
      <td>2019-08-06T14:25:14.243346-05:00</td>
      <td>[ec4487c1-6976-4161-9236-5e6810ed31b7, ffd1e03...</td>
      <td>[7f327ef6-4fe6-40c8-aac7-731e051177bb, 2a4b0be...</td>
      <td>[TCGA-BA-A6DL-01A-21D, TCGA-BA-A6DL-01A-21R, T...</td>
      <td>[TCGA-BA-A6DL-10A-01, TCGA-BA-A6DL-01A-11-A45L...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4</th>
      <td>[59b70846-64f0-489e-8ea5-84a347aedeb8, c8e46ce...</td>
      <td>4cffea0b-90a7-4c86-a73f-bb8feca3ada7</td>
      <td>None</td>
      <td>[{'age_at_diagnosis': 14190, 'ajcc_clinical_m'...</td>
      <td>[1da5c51a-ee25-51a6-a4c2-27d8fdcbe24e]</td>
      <td>Squamous Cell Neoplasms</td>
      <td>4cffea0b-90a7-4c86-a73f-bb8feca3ada7</td>
      <td>Tonsil</td>
      <td>[1ed245de-fea4-42c9-9197-773bcd12d2a8, 665d4bf...</td>
      <td>[{'created_datetime': '2018-05-17T12:19:46.292...</td>
      <td>...</td>
      <td>[TCGA-CN-5365-01Z, TCGA-CN-5365-10A, TCGA-CN-5...</td>
      <td>[TCGA-CN-5365-01Z-00-DX1, TCGA-CN-5365-01A-01-...</td>
      <td>2019-08-06T14:25:25.511101-05:00</td>
      <td>[d46b5e9b-3652-45a1-a91d-46277aea3916, 35122dd...</td>
      <td>[38c5a4c1-6d01-4885-ba35-0032e6b835b0, 516f802...</td>
      <td>[TCGA-CN-5365-01A-01D, TCGA-CN-5365-01A-01W, T...</td>
      <td>[TCGA-CN-5365-10A-01, TCGA-CN-5365-01A-21-2072...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>555</th>
      <td>[1d3b16fd-f98b-45ef-a423-861975f098b6, 0eabe3e...</td>
      <td>97640ef0-0259-4244-95ba-48d28c60b372</td>
      <td>None</td>
      <td>[{'age_at_diagnosis': 19621, 'ajcc_clinical_m'...</td>
      <td>[b725e6d2-92c0-5585-9de7-14bb623b472e]</td>
      <td>Squamous Cell Neoplasms</td>
      <td>97640ef0-0259-4244-95ba-48d28c60b372</td>
      <td>Larynx</td>
      <td>[fb06ae75-8516-4cdc-ba9e-093444907fc7, 5162217...</td>
      <td>[{'composition': None, 'created_datetime': Non...</td>
      <td>...</td>
      <td>[TCGA-CN-4738-01A, TCGA-CN-4738-01Z, TCGA-CN-4...</td>
      <td>[TCGA-CN-4738-01Z-00-DX1, TCGA-CN-4738-01A-01-...</td>
      <td>2019-08-06T14:25:25.511101-05:00</td>
      <td>[4dc95dbe-b10f-4d6e-9413-ae47a0a49865, e637c1c...</td>
      <td>[56c7d4e4-5703-4686-98b1-0c3125e5913e, 60d72bd...</td>
      <td>[TCGA-CN-4738-01A-02D, TCGA-CN-4738-10A-01W, T...</td>
      <td>[TCGA-CN-4738-01A-31-2072-20, TCGA-CN-4738-01A...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>556</th>
      <td>[96f09bc8-a194-482c-bd17-baf28739e4f8]</td>
      <td>422a72e7-fe76-411d-b59e-1f0f0812c3cf</td>
      <td>2018-09-13T13:42:10.444091-05:00</td>
      <td>[{'age_at_diagnosis': None, 'ajcc_clinical_m':...</td>
      <td>[842d6984-7c03-4ab6-95db-42fa2ea699db]</td>
      <td>Squamous Cell Neoplasms</td>
      <td>422a72e7-fe76-411d-b59e-1f0f0812c3cf</td>
      <td>Larynx</td>
      <td>[6f9eeaa3-8bd1-479c-a0fc-98317eb458dc]</td>
      <td>[{'biospecimen_anatomic_site': None, 'biospeci...</td>
      <td>...</td>
      <td>[GENIE-DFCI-010671-11105]</td>
      <td>NaN</td>
      <td>2019-11-18T13:54:59.294543-06:00</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>Initial Genomic Sequencing</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>557</th>
      <td>[cd211e89-63f7-44f0-8a76-51703ae45112, 866292c...</td>
      <td>4b50aea4-4ad1-4bf6-9cf1-984c28a99c84</td>
      <td>None</td>
      <td>[{'age_at_diagnosis': 21731, 'ajcc_clinical_m'...</td>
      <td>[95d85e5a-b82c-59f8-b7ad-710e019cdebc]</td>
      <td>Squamous Cell Neoplasms</td>
      <td>4b50aea4-4ad1-4bf6-9cf1-984c28a99c84</td>
      <td>Hypopharynx</td>
      <td>[1077bf93-cf23-41db-925c-c633921894cc, 4a0d79f...</td>
      <td>[{'created_datetime': '2018-05-17T12:19:46.292...</td>
      <td>...</td>
      <td>[TCGA-TN-A7HL-01A, TCGA-TN-A7HL-01Z, TCGA-TN-A...</td>
      <td>[TCGA-TN-A7HL-01Z-00-DX1, TCGA-TN-A7HL-01A-01-...</td>
      <td>2019-08-06T14:27:14.277986-05:00</td>
      <td>[6ffc3548-d593-47ab-adf8-6d73075b5fa0, 9426e53...</td>
      <td>[cd5864c8-b4e0-4405-b7df-1e0a51865670, f9ef56b...</td>
      <td>[TCGA-TN-A7HL-01A-11R, TCGA-TN-A7HL-01A-11D, T...</td>
      <td>[TCGA-TN-A7HL-01A-21-A45L-20, TCGA-TN-A7HL-10A...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>558</th>
      <td>[0c2f310b-fa59-4f6f-894a-dad920214004, 6ddd527...</td>
      <td>0394060d-010e-405f-983d-db525f01f2c3</td>
      <td>None</td>
      <td>[{'age_at_diagnosis': 23640, 'ajcc_clinical_m'...</td>
      <td>[7a67eecc-6f46-5181-8b64-c022d0fd0060]</td>
      <td>Squamous Cell Neoplasms</td>
      <td>0394060d-010e-405f-983d-db525f01f2c3</td>
      <td>Hypopharynx</td>
      <td>[5c2b4403-cdd4-4550-ba01-d8ebad9fcbc8, 4467ee1...</td>
      <td>[{'created_datetime': '2018-05-17T12:19:46.292...</td>
      <td>...</td>
      <td>[TCGA-BB-A5HY-10A, TCGA-BB-A5HY-01A, TCGA-BB-A...</td>
      <td>[TCGA-BB-A5HY-01Z-00-DX1, TCGA-BB-A5HY-01A-01-...</td>
      <td>2019-08-06T14:25:25.511101-05:00</td>
      <td>[ee7f98c5-9c78-4bbe-b44a-a9e357a18058, 2d82983...</td>
      <td>[9576f242-6874-4df9-8744-e0755d565358, 8842cbd...</td>
      <td>[TCGA-BB-A5HY-01A-11W, TCGA-BB-A5HY-01A-11D, T...</td>
      <td>[TCGA-BB-A5HY-01A-11, TCGA-BB-A5HY-10A-01]</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>559</th>
      <td>[53800455-66fa-4193-9308-390fd663a40c, 9c20138...</td>
      <td>df132eb8-174b-4427-a16b-953e0f28bf2f</td>
      <td>None</td>
      <td>[{'age_at_diagnosis': 20763, 'ajcc_clinical_m'...</td>
      <td>[d20b4711-8757-5d39-a8cc-b8ece86592cd]</td>
      <td>Squamous Cell Neoplasms</td>
      <td>df132eb8-174b-4427-a16b-953e0f28bf2f</td>
      <td>Larynx</td>
      <td>[c22e9fe0-a052-4c6f-9fb2-e58289277e2a, 6bd5367...</td>
      <td>[{'composition': None, 'created_datetime': Non...</td>
      <td>...</td>
      <td>[TCGA-CV-7430-11A, TCGA-CV-7430-01A, TCGA-CV-7...</td>
      <td>[TCGA-CV-7430-01A-01-BS1, TCGA-CV-7430-01Z-00-...</td>
      <td>2019-08-06T14:26:28.608672-05:00</td>
      <td>[9645e3d2-e245-4d0b-a4f3-a14ec7508b28, a5a93bc...</td>
      <td>[71900a0b-da4a-444c-bfd5-4ba5e530761f, 06546fd...</td>
      <td>[TCGA-CV-7430-01A-11D, TCGA-CV-7430-10A-01D, T...</td>
      <td>[TCGA-CV-7430-01A-13-2074-20, TCGA-CV-7430-11A...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>560 rows × 25 columns</p>
</div>



## Loading the Python classes for the CCDH model

The Python DataClasses for the CCDH model as available at https://github.com/cancerDHC/ccdhmodel/. The Python DataClasses cannot be directly loaded from this GitHub repository yet, but we [plan to implement this functionality soon](https://github.com/cancerDHC/ccdhmodel/issues/40). For now, we have copied the file into this repository so we can import them here.

Note that the Python Data Classes includes documentation on entities and enumerations.


```python
from ccdh import ccdhmodel as ccdh

# Documentation for an entity.
print(f"Documentation for Specimen: {ccdh.Specimen.__doc__}")

# Documentation for an enumeration.
print(f"Documentation for Specimen.specimen_type: {ccdh.EnumCCDHSpecimenSpecimenType.__doc__}")

# List of permissible values for Specimen.specimen_type
print("Permissible values in enumeration Specimen.specimen_type:")
pvalues = [pv for key, pv in ccdh.EnumCCDHSpecimenSpecimenType.__dict__.items() if isinstance(pv, ccdh.PermissibleValue)]
for pv in pvalues:
    print(f' - Value "{pv.text}": {pv.description}')
```

    Documentation for Specimen: 
        Any material taken as a sample from a biological entity (living or dead), or from a physical object or the
        environment. Specimens are usually collected as an example of their kind, often for use in some investigation.
        
    Documentation for Specimen.specimen_type: 
        A high-level type of specimen, based on its derivation provenance (i.e. how far removed it is from the original
        sample extracted from a source).
        
    Permissible values in enumeration Specimen.specimen_type:
     - Value "portion": A physical sub-part taken from an existing specimen.
     - Value "aliquot": A specimen that results from the division of some parent specimen into equal amounts for downstream analysis.
     - Value "analyte": A specimen generated through the extraction of a specified class of substance/chemical (e.g. DNA, RNA, protein) from a parent specimen, which is stored in solution as an analyte.
     - Value "slide": A specimen that is mounted on a slide or coverslip for microscopic analysis.
     - Value "initial sample": A specimen representing the material that was directly collected from a subject (i.e. not generated through portioning, aliquoting, or analyte extraction from an existing specimen).


## Transforming GDC cases into CCDH Research Subject

The primary transformation we will demonstrate here is transforming a [GDC case](https://docs.gdc.cancer.gov/Data_Dictionary/viewer/#?view=table-definition-view&id=case) into a [CCDH Research Subject](https://cancerdhc.github.io/ccdhmodel/latest/ResearchSubject/). To do this, we need to translate three additional components as well:
* Each GDC case includes a diagnosis, which we need to transform into a [CCDH Diagnosis](https://cancerdhc.github.io/ccdhmodel/latest/Diagnosis/).
* Each GDC diagnosis includes a description of the cancer stage (see properties named `ajcc_*` in [the GDC documentation](https://docs.gdc.cancer.gov/Data_Dictionary/viewer/#?view=table-definition-view&id=diagnosis)). We will translate this into a [CCDH Cancer Stage Observation Set](https://cancerdhc.github.io/ccdhmodel/latest/CancerStageObservationSet/).
* Each GDC case contains a hierarchy of samples, portions, analytes, aliquots and slides. For the purposes of this demonstration, we will focus on transforming only the top-level specimens into [CCDH Specimens](https://cancerdhc.github.io/ccdhmodel/latest/Specimen/), but the same method can be used to transform other parts of the hierarchy. We plan to [include that transformation](https://github.com/cancerDHC/example-data/issues/6) in this tutorial eventually. Note that in our model, specimens are associated with diagnoses rather than directly with Research Subjects.

The CCDH Python Data Classes help in writing these transformation methods by applying validation on the data and ensuring that constraints (such as the required fields) are met. We begin by defining a transformation for creating a [CCDH BodySite](https://cancerdhc.github.io/ccdhmodel/latest/BodySite/), which we also use to demonstrate the validation features available on CCDH Python Data Classes.


```python
def create_body_site(site_name):
    """ Create a CCDH BodySite based on the name of a site in the human body."""
    
    # Accept 'None'.
    if site_name is None:
        return None
    
    # Some body sites are not currently included in the CCDH model. We will need to translate these sites
    # into values that *are* included in the CCDH model.
    site_mappings = {
        'Larynx, NOS': ccdh.EnumCCDHBodySiteSite.Larynx
    }
    
    # Map values if needed. Otherwise, pass them through unmapped.
    if site_name in site_mappings:
        return ccdh.BodySite(site=(site_mappings[site_name]))
    
    return ccdh.BodySite(site=site_name)

# Try to create a body site for a site name not currently included in the CCDH model.
try:
    create_body_site('Laryn') # Note misspelling.
except ValueError as v:
    print(f'Could not create BodySite: {v}')

# Using a valid name generates no errors.
create_body_site('Larynx')    

# Using a mapped name generates no errors, as it is mapped to a valid name.
create_body_site('Larynx, NOS')
```

    Could not create BodySite: Unknown EnumCCDHBodySiteSite enumeration code: Laryn





    BodySite(site=(text='Larynx', description='Larynx'), qualifier=[])



We need a more sophisticated transformation method for transforming the GDC cancer stage information into [CCDH Cancer Stage Observation Set](https://cancerdhc.github.io/ccdhmodel/latest/CancerStageObservationSet/). Each observation set is made up of a number of [CCDH Cancer Stage Observations](https://cancerdhc.github.io/ccdhmodel/latest/CancerStageObservation/), each of which represents a different type of observation.


```python
def create_stage_observation(type, value):
    """ Create a CCDHCancerStageObservation from a type of observation and a codeable concept."""
    # As with the body site example above, we need to map GDC values into the values
    # allowed under the CCDH model.
    stage_mappings = {
        'not reported': 'Not Reported',
        'unknown': 'Unknown',
        'stage i': 'Stage I',
        'stage ii': 'Stage II',
        'stage iii': 'Stage III',
        'stage iva': 'Stage IVA',
        'stage ivb': 'Stage IVB',
        'stage ivc': 'Stage IVC',
    }
    
    if value in stage_mappings:
        return ccdh.CancerStageObservation(
            observation_type=type,
            valueCodeableConcept=stage_mappings[value]
        )
    
    return ccdh.CancerStageObservation(
        observation_type=type,
        valueCodeableConcept=value
    )

def create_stage_from_gdc(diagnosis):
    cancer_stage_method_type = None
    if diagnosis.get('ajcc_staging_system_edition') == '7th':
        cancer_stage_method_type = 'AJCC staging system 7th edition'

    # Create an observation set 
    obs = ccdh.CancerStageObservationSet(
        method_type=cancer_stage_method_type
    )
    
    # Add observations for every type of observation in the GDC diagnosis.
    if diagnosis.get('tumor_stage') is not None:
        obs.observations.append(create_stage_observation('Overall', diagnosis.get('tumor_stage')))
        
    if diagnosis.get('ajcc_clinical_stage') is not None:
        obs.observations.append(create_stage_observation('Clinical Overall', diagnosis.get('ajcc_clinical_stage')))
        
    if diagnosis.get('ajcc_clinical_t') is not None:
        obs.observations.append(create_stage_observation('Clinical Tumor (T)', diagnosis.get('ajcc_clinical_t')))
        
    if diagnosis.get('ajcc_clinical_n') is not None:
        obs.observations.append(create_stage_observation('Clinical Node (N)', diagnosis.get('ajcc_clinical_n')))
        
    if diagnosis.get('ajcc_clinical_m') is not None:
        obs.observations.append(create_stage_observation('Clinical Metastasis (M)', diagnosis.get('ajcc_clinical_m')))
    
    if diagnosis.get('ajcc_pathologic_stage') is not None:
        obs.observations.append(create_stage_observation('Pathological Overall', diagnosis.get('ajcc_pathologic_stage')))
        
    if diagnosis.get('ajcc_pathologic_t') is not None:
        obs.observations.append(create_stage_observation('Pathological Tumor (T)', diagnosis.get('ajcc_pathologic_t')))
        
    if diagnosis.get('ajcc_pathologic_n') is not None:
        obs.observations.append(create_stage_observation('Pathological Node (N)', diagnosis.get('ajcc_pathologic_n')))
        
    if diagnosis.get('ajcc_pathologic_m') is not None:
        obs.observations.append(create_stage_observation('Pathological Metastasis (M)', diagnosis.get('ajcc_pathologic_m')))
    
    return obs

# Test transform with the diagnosis from the first loaded case.
# Note that the resulting CancerStageObservationSet contains descriptions for the concepts included in it.
# example_observation_set = create_stage_from_gdc(gdc_head_and_mouth[131]['diagnoses'][0], ccdh.Subject(id='1234'))
example_observation_set = create_stage_from_gdc(gdc_head_and_mouth[131]['diagnoses'][0])
example_observation_set
```




    CancerStageObservationSet(id=None, category=None, focus=[], subject=None, method_type=[(text='AJCC staging system 7th edition', description='The 7th edition of the criteria developed by the American Joint Committee on Cancer (AJCC) in 2010, used for the classification and staging of neoplastic diseases.')], performed_by=None, observations=[CancerStageObservation(observation_type=(text='Overall', description='The overall stage of the disease'), valueCodeableConcept=(text='Stage IVC', description='Stage IVC'), id=None, category=None, method_type=None, focus=None, subject=None, performed_by=None, valueEntity=None), CancerStageObservation(observation_type=(text='Clinical Overall', description='The overall stage of the disease; clinical stage is determined from evidence acquired before treatment (including clinical examination, imaging, endoscopy, biopsy, surgical exploration)'), valueCodeableConcept=(text='Stage IVC', description='Stage IVC'), id=None, category=None, method_type=None, focus=None, subject=None, performed_by=None, valueEntity=None), CancerStageObservation(observation_type=(text='Clinical Tumor (T)', description='T classifies the size or direct extent of the primary tumor; clinical stage is determined from evidence acquired before treatment (including clinical examination, imaging, endoscopy, biopsy, surgical exploration)'), valueCodeableConcept=(text='T3', description='T3 Stage Finding'), id=None, category=None, method_type=None, focus=None, subject=None, performed_by=None, valueEntity=None), CancerStageObservation(observation_type=(text='Clinical Node (N)', description='N classifies the degree of spread to regional lymph nodes; clinical stage is determined from evidence acquired before treatment (including clinical examination, imaging, endoscopy, biopsy, surgical exploration)'), valueCodeableConcept=(text='N1', description='N1 Stage Finding'), id=None, category=None, method_type=None, focus=None, subject=None, performed_by=None, valueEntity=None), CancerStageObservation(observation_type=(text='Clinical Metastasis (M)', description='M classifies the presence of distant metastasis; clinical stage is determined from evidence acquired before treatment (including clinical examination, imaging, endoscopy, biopsy, surgical exploration)'), valueCodeableConcept=(text='M1', description='M1 Stage Finding'), id=None, category=None, method_type=None, focus=None, subject=None, performed_by=None, valueEntity=None), CancerStageObservation(observation_type=(text='Pathological Overall', description='The overall stage of the disease; stage given by histopathologic examination of a surgical specimen'), valueCodeableConcept=(text='Stage IVC', description='Stage IVC'), id=None, category=None, method_type=None, focus=None, subject=None, performed_by=None, valueEntity=None), CancerStageObservation(observation_type=(text='Pathological Tumor (T)', description='T classifies the size or direct extent of the primary tumor; stage given by histopathologic examination of a surgical specimen'), valueCodeableConcept=(text='T3', description='T3 Stage Finding'), id=None, category=None, method_type=None, focus=None, subject=None, performed_by=None, valueEntity=None), CancerStageObservation(observation_type=(text='Pathological Node (N)', description='N classifies the degree of spread to regional lymph nodes; stage given by histopathologic examination of a surgical specimen'), valueCodeableConcept=(text='N1', description='N1 Stage Finding'), id=None, category=None, method_type=None, focus=None, subject=None, performed_by=None, valueEntity=None), CancerStageObservation(observation_type=(text='Pathological Metastasis (M)', description='M classifies the presence of distant metastasis; stage given by histopathologic examination of a surgical specimen'), valueCodeableConcept=(text='M1', description='M1 Stage Finding'), id=None, category=None, method_type=None, focus=None, subject=None, performed_by=None, valueEntity=None)])



Reading Python Data Classes in its default text output can be difficult! However, we can use LinkML's [YAML](https://en.wikipedia.org/wiki/YAML) dumper to display this Cancer Stage Observation Set as a YAML string. YAML objects are a good way to export LinkML data, and include detailed descriptions of all the enumerations referenced from this object. We currently include basic descriptions for the permissible values (see e.g. "N1 Stage Finding" below), but we will include more detailed descriptions in the future.


```python
from linkml.dumpers.yaml_dumper import dumps as yaml_dumps

print(yaml_dumps(example_observation_set))
```

    method_type:
    - text: AJCC staging system 7th edition
      description: The 7th edition of the criteria developed by the American Joint Committee
        on Cancer (AJCC) in 2010, used for the classification and staging of neoplastic
        diseases.
    observations:
    - observation_type:
        text: Overall
        description: The overall stage of the disease
      valueCodeableConcept:
        text: Stage IVC
        description: Stage IVC
    - observation_type:
        text: Clinical Overall
        description: The overall stage of the disease; clinical stage is determined from
          evidence acquired before treatment (including clinical examination, imaging,
          endoscopy, biopsy, surgical exploration)
      valueCodeableConcept:
        text: Stage IVC
        description: Stage IVC
    - observation_type:
        text: Clinical Tumor (T)
        description: T classifies the size or direct extent of the primary tumor; clinical
          stage is determined from evidence acquired before treatment (including clinical
          examination, imaging, endoscopy, biopsy, surgical exploration)
      valueCodeableConcept:
        text: T3
        description: T3 Stage Finding
    - observation_type:
        text: Clinical Node (N)
        description: N classifies the degree of spread to regional lymph nodes; clinical
          stage is determined from evidence acquired before treatment (including clinical
          examination, imaging, endoscopy, biopsy, surgical exploration)
      valueCodeableConcept:
        text: N1
        description: N1 Stage Finding
    - observation_type:
        text: Clinical Metastasis (M)
        description: M classifies the presence of distant metastasis; clinical stage is
          determined from evidence acquired before treatment (including clinical examination,
          imaging, endoscopy, biopsy, surgical exploration)
      valueCodeableConcept:
        text: M1
        description: M1 Stage Finding
    - observation_type:
        text: Pathological Overall
        description: The overall stage of the disease; stage given by histopathologic
          examination of a surgical specimen
      valueCodeableConcept:
        text: Stage IVC
        description: Stage IVC
    - observation_type:
        text: Pathological Tumor (T)
        description: T classifies the size or direct extent of the primary tumor; stage
          given by histopathologic examination of a surgical specimen
      valueCodeableConcept:
        text: T3
        description: T3 Stage Finding
    - observation_type:
        text: Pathological Node (N)
        description: N classifies the degree of spread to regional lymph nodes; stage
          given by histopathologic examination of a surgical specimen
      valueCodeableConcept:
        text: N1
        description: N1 Stage Finding
    - observation_type:
        text: Pathological Metastasis (M)
        description: M classifies the presence of distant metastasis; stage given by histopathologic
          examination of a surgical specimen
      valueCodeableConcept:
        text: M1
        description: M1 Stage Finding
    


Diagnoses can contain samples, which we transform into [CCDH Samples](https://cancerdhc.github.io/ccdhmodel/latest/Specimen/).


```python
def transform_sample_to_specimen(sample):
    """
    A method for transforming a GDC Sample into CCDH Specimen.
    """
    specimen = ccdh.Specimen(id = sample.get('sample_id'))
    specimen.source_material_type = sample.get('sample_type')
    specimen.general_tissue_morphology = sample.get('tissue_type')
    specimen.specific_tissue_morphology = sample.get('tumor_code')
    specimen.tumor_status_at_collection = sample.get('tumor_descriptor')
    specimen.creation_activity = ccdh.SpecimenCreationActivity(
        date_ended=ccdh.TimePoint(
            dateTime=sample.get('created_datetime')
        )
    )
    return specimen

# Let's try creating a test specimen.
test_specimen = transform_sample_to_specimen(gdc_head_and_mouth[2]['samples'][0])
test_specimen
```




    Specimen(id='69a89590-eb61-41d5-b33e-e7bc5adb92bf', identifier=[], description=None, specimen_type=None, analyte_type=None, associated_project=None, data_provider=None, source_material_type='Solid Tissue Normal', parent_specimen=[], source_subject=None, source_model_system=None, tumor_status_at_collection=None, creation_activity=SpecimenCreationActivity(activity_type=None, date_started=None, date_ended=TimePoint(id=None, dateTime=None, indexTimePoint=None, offsetFromIndex=None, eventType=[]), performed_by=None, collection_method_type=None, derivation_method_type=None, additive=[], collection_site=None, quantity_collected=None, execution_time_observation=[], execution_condition_observation=[], specimen_order=None), processing_activity=[], storage_activity=[], transport_activity=[], contained_in=None, dimensional_measure=None, quantity_measure=[], quality_measure=[], cellular_composition_type=None, histological_composition_measure=[], general_tissue_morphology='Not Reported', specific_tissue_morphology=None, preinvasive_tissue_morphology=None, morphology_pathologically_confirmed=None, morphology_assessor_role=None, morphlogy_assessment_method=None, degree_of_dysplasia=None, dysplasia_fraction=None, related_document=[], section_location=None, derived_product=[], distance_from_paired_specimen=None)



We can now transform an entire diagnosis into a [CCDH Diagnosis](https://cancerdhc.github.io/ccdhmodel/latest/Diagnosis/).


```python
def transform_diagnosis(diagnosis, case):
    ccdh_diagnosis = ccdh.Diagnosis(
        id=diagnosis.get('diagnosis_id'),
        condition=diagnosis.get('primary_diagnosis'),
        morphology=diagnosis.get('morphology'),
        metastatic_site=create_body_site(diagnosis.get('primary_site')),
        grade=diagnosis.get('grade'),
        stage=create_stage_from_gdc(diagnosis),
        year_at_diagnosis=diagnosis.get('year_of_diagnosis'),
        related_specimen=[
            transform_sample_to_specimen(
                sample
            ) for sample in case.get('samples')
        ]
    )
    ccdh_diagnosis.identifier = [
        ccdh.Identifier(
            system='GDC-submitter-id',
            value=diagnosis.get('submitter_id')
        )
    ]

    return ccdh_diagnosis

example_diagnosis = transform_diagnosis(gdc_head_and_mouth[131]['diagnoses'][0], gdc_head_and_mouth[131])
print(yaml_dumps(example_diagnosis))
```

    id: 9e30aa6c-91e6-5dd3-9512-75c162a89913
    identifier:
    - value: TCGA-QK-A8Z8_diagnosis
      system: GDC-submitter-id
    year_at_diagnosis: 2013
    condition:
      text: Squamous cell carcinoma, NOS
    stage:
    - method_type:
      - text: AJCC staging system 7th edition
        description: The 7th edition of the criteria developed by the American Joint Committee
          on Cancer (AJCC) in 2010, used for the classification and staging of neoplastic
          diseases.
      observations:
      - observation_type:
          text: Overall
          description: The overall stage of the disease
        valueCodeableConcept:
          text: Stage IVC
          description: Stage IVC
      - observation_type:
          text: Clinical Overall
          description: The overall stage of the disease; clinical stage is determined
            from evidence acquired before treatment (including clinical examination, imaging,
            endoscopy, biopsy, surgical exploration)
        valueCodeableConcept:
          text: Stage IVC
          description: Stage IVC
      - observation_type:
          text: Clinical Tumor (T)
          description: T classifies the size or direct extent of the primary tumor; clinical
            stage is determined from evidence acquired before treatment (including clinical
            examination, imaging, endoscopy, biopsy, surgical exploration)
        valueCodeableConcept:
          text: T3
          description: T3 Stage Finding
      - observation_type:
          text: Clinical Node (N)
          description: N classifies the degree of spread to regional lymph nodes; clinical
            stage is determined from evidence acquired before treatment (including clinical
            examination, imaging, endoscopy, biopsy, surgical exploration)
        valueCodeableConcept:
          text: N1
          description: N1 Stage Finding
      - observation_type:
          text: Clinical Metastasis (M)
          description: M classifies the presence of distant metastasis; clinical stage
            is determined from evidence acquired before treatment (including clinical
            examination, imaging, endoscopy, biopsy, surgical exploration)
        valueCodeableConcept:
          text: M1
          description: M1 Stage Finding
      - observation_type:
          text: Pathological Overall
          description: The overall stage of the disease; stage given by histopathologic
            examination of a surgical specimen
        valueCodeableConcept:
          text: Stage IVC
          description: Stage IVC
      - observation_type:
          text: Pathological Tumor (T)
          description: T classifies the size or direct extent of the primary tumor; stage
            given by histopathologic examination of a surgical specimen
        valueCodeableConcept:
          text: T3
          description: T3 Stage Finding
      - observation_type:
          text: Pathological Node (N)
          description: N classifies the degree of spread to regional lymph nodes; stage
            given by histopathologic examination of a surgical specimen
        valueCodeableConcept:
          text: N1
          description: N1 Stage Finding
      - observation_type:
          text: Pathological Metastasis (M)
          description: M classifies the presence of distant metastasis; stage given by
            histopathologic examination of a surgical specimen
        valueCodeableConcept:
          text: M1
          description: M1 Stage Finding
    morphology:
      text: 8070/3
    related_specimen:
    - id: a118da56-784d-4b67-aade-d9a7a8b49f18
      source_material_type: Primary Tumor
      creation_activity:
        date_ended: {}
      general_tissue_morphology: Not Reported
    - id: cff6967e-e8f7-4a25-aa31-9328e4b42816
      source_material_type: Primary Tumor
      creation_activity:
        date_ended:
          dateTime: '2018-05-17T12:19:46.292188-05:00'
      general_tissue_morphology: Not Reported
    - id: 1efb2d28-ac51-4d70-a24d-667a2b53467a
      source_material_type: Blood Derived Normal
      creation_activity:
        date_ended: {}
      general_tissue_morphology: Not Reported
    


## Exporting Python Data Classes as JSON-LD

Python Data Classes can be exported as [JSON-LD](https://en.wikipedia.org/wiki/JSON-LD), allowing CCDH instance data to be shared in a [JSON](https://en.wikipedia.org/wiki/JSON)-based [RDF](https://en.wikipedia.org/wiki/Resource_Description_Framework) format. RDF formats are particularly useful in sharing data, since they allow us to share [Linked Data](https://en.wikipedia.org/wiki/Linked_data) that can be understood by other consumers.


```python
from linkml.generators.jsonldcontextgen import ContextGenerator
from linkml.dumpers.json_dumper import dumps as jsonld_dumps

jsonldContext = ContextGenerator('ccdh/ccdhmodel.yaml').serialize()

# Display the example diagnosis we constructed in a previous step.
print(jsonld_dumps(example_diagnosis, jsonldContext))
```

    {
      "id": "9e30aa6c-91e6-5dd3-9512-75c162a89913",
      "identifier": [
        {
          "value": "TCGA-QK-A8Z8_diagnosis",
          "system": "GDC-submitter-id"
        }
      ],
      "year_at_diagnosis": 2013,
      "condition": {
        "text": "Squamous cell carcinoma, NOS"
      },
      "stage": [
        {
          "method_type": [
            {}
          ],
          "observations": [
            {
              "observation_type": {
                "text": "Overall",
                "description": "The overall stage of the disease"
              },
              "valueCodeableConcept": {
                "text": "Stage IVC",
                "description": "Stage IVC"
              }
            },
            {
              "observation_type": {
                "text": "Clinical Overall",
                "description": "The overall stage of the disease; clinical stage is determined from evidence acquired before treatment (including clinical examination, imaging, endoscopy, biopsy, surgical exploration)"
              },
              "valueCodeableConcept": {
                "text": "Stage IVC",
                "description": "Stage IVC"
              }
            },
            {
              "observation_type": {
                "text": "Clinical Tumor (T)",
                "description": "T classifies the size or direct extent of the primary tumor; clinical stage is determined from evidence acquired before treatment (including clinical examination, imaging, endoscopy, biopsy, surgical exploration)"
              },
              "valueCodeableConcept": {
                "text": "T3",
                "description": "T3 Stage Finding"
              }
            },
            {
              "observation_type": {
                "text": "Clinical Node (N)",
                "description": "N classifies the degree of spread to regional lymph nodes; clinical stage is determined from evidence acquired before treatment (including clinical examination, imaging, endoscopy, biopsy, surgical exploration)"
              },
              "valueCodeableConcept": {
                "text": "N1",
                "description": "N1 Stage Finding"
              }
            },
            {
              "observation_type": {
                "text": "Clinical Metastasis (M)",
                "description": "M classifies the presence of distant metastasis; clinical stage is determined from evidence acquired before treatment (including clinical examination, imaging, endoscopy, biopsy, surgical exploration)"
              },
              "valueCodeableConcept": {
                "text": "M1",
                "description": "M1 Stage Finding"
              }
            },
            {
              "observation_type": {
                "text": "Pathological Overall",
                "description": "The overall stage of the disease; stage given by histopathologic examination of a surgical specimen"
              },
              "valueCodeableConcept": {
                "text": "Stage IVC",
                "description": "Stage IVC"
              }
            },
            {
              "observation_type": {
                "text": "Pathological Tumor (T)",
                "description": "T classifies the size or direct extent of the primary tumor; stage given by histopathologic examination of a surgical specimen"
              },
              "valueCodeableConcept": {
                "text": "T3",
                "description": "T3 Stage Finding"
              }
            },
            {
              "observation_type": {
                "text": "Pathological Node (N)",
                "description": "N classifies the degree of spread to regional lymph nodes; stage given by histopathologic examination of a surgical specimen"
              },
              "valueCodeableConcept": {
                "text": "N1",
                "description": "N1 Stage Finding"
              }
            },
            {
              "observation_type": {
                "text": "Pathological Metastasis (M)",
                "description": "M classifies the presence of distant metastasis; stage given by histopathologic examination of a surgical specimen"
              },
              "valueCodeableConcept": {
                "text": "M1",
                "description": "M1 Stage Finding"
              }
            }
          ]
        }
      ],
      "morphology": {
        "text": "8070/3"
      },
      "related_specimen": [
        {
          "id": "a118da56-784d-4b67-aade-d9a7a8b49f18",
          "source_material_type": "Primary Tumor",
          "creation_activity": {
            "date_ended": {}
          },
          "general_tissue_morphology": "Not Reported"
        },
        {
          "id": "cff6967e-e8f7-4a25-aa31-9328e4b42816",
          "source_material_type": "Primary Tumor",
          "creation_activity": {
            "date_ended": {
              "dateTime": "2018-05-17T12:19:46.292188-05:00"
            }
          },
          "general_tissue_morphology": "Not Reported"
        },
        {
          "id": "1efb2d28-ac51-4d70-a24d-667a2b53467a",
          "source_material_type": "Blood Derived Normal",
          "creation_activity": {
            "date_ended": {}
          },
          "general_tissue_morphology": "Not Reported"
        }
      ],
      "@type": "Diagnosis",
      "@context": {
        "GDC": "http://example.org/gdc/",
        "HTAN": "http://example.org/htan/",
        "ICDC": "http://example.org/icdc/",
        "NCIT": {
          "@id": "http://purl.obolibrary.org/obo/NCIT_",
          "@prefix": true
        },
        "PDC": "http://example.org/pdc/",
        "ccdh": "https://example.org/ccdh/",
        "linkml": "https://w3id.org/linkml/",
        "skos": "http://www.w3.org/2004/02/skos/core#",
        "@vocab": "https://example.org/ccdh/",
        "category": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "focus": {
          "@type": "@id"
        },
        "method_type": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "observation_type": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "performed_by": {
          "@type": "@id"
        },
        "subject": {
          "@type": "@id"
        },
        "valueCodeableConcept": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "valueInteger": {
          "@type": "xsd:integer"
        },
        "identifier": {
          "@type": "@id"
        },
        "passage_number": {
          "@type": "xsd:integer"
        },
        "product_type": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "qualifier": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "site": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "observations": {
          "@type": "@id"
        },
        "valueEntity": {
          "@type": "@id"
        },
        "coding": {
          "@type": "@id"
        },
        "age_at_diagnosis": {
          "@type": "@id"
        },
        "condition": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "dimensional_measure": {
          "@type": "@id"
        },
        "disease_status": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "grade": {
          "@type": "@id"
        },
        "metastatic_site": {
          "@type": "@id"
        },
        "method_of_diagnosis": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "morphology": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "primary_site": {
          "@type": "@id"
        },
        "prior_diagnosis": {
          "@type": "@id"
        },
        "related_specimen": {
          "@type": "@id"
        },
        "stage": {
          "@type": "@id"
        },
        "supporting_observation": {
          "@type": "@id"
        },
        "year_at_diagnosis": {
          "@type": "xsd:integer"
        },
        "valueQuantity": {
          "@type": "@id"
        },
        "document_type": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "alcohol_exposure": {
          "@type": "@id"
        },
        "environmental_exposure": {
          "@type": "@id"
        },
        "tobacco_exposure": {
          "@type": "@id"
        },
        "type": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "valueBoolean": {
          "@type": "xsd:boolean"
        },
        "valueDateTime": {
          "@type": "xsd:dateTime"
        },
        "valueDecimal": {
          "@type": "xsd:decimal"
        },
        "unit": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "associated_timepoint": {
          "@type": "@id"
        },
        "date_ended": {
          "@type": "@id"
        },
        "date_started": {
          "@type": "@id"
        },
        "part_of": {
          "@type": "@id"
        },
        "primary_anatomic_site": {
          "@type": "@id"
        },
        "research_project_type": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "age_at_enrollment": {
          "@type": "@id"
        },
        "associated_subject": {
          "@type": "@id"
        },
        "comorbid_diagnosis": {
          "@type": "@id"
        },
        "index_timepoint": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "member_of_research_project": {
          "@type": "@id"
        },
        "originating_site": {
          "@type": "@id"
        },
        "primary_diagnosis": {
          "@type": "@id"
        },
        "primary_diagnosis_condition": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "primary_diagnosis_site": {
          "@type": "@id"
        },
        "analyte_type": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "associated_project": {
          "@type": "@id"
        },
        "cellular_composition_type": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "contained_in": {
          "@type": "@id"
        },
        "creation_activity": {
          "@type": "@id"
        },
        "data_provider": {
          "@type": "@id"
        },
        "degree_of_dysplasia": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "derived_product": {
          "@type": "@id"
        },
        "distance_from_paired_specimen": {
          "@type": "@id"
        },
        "general_tissue_morphology": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "histological_composition_measure": {
          "@type": "@id"
        },
        "morphlogy_assessment_method": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "morphology_assessor_role": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "morphology_pathologically_confirmed": {
          "@type": "xsd:boolean"
        },
        "parent_specimen": {
          "@type": "@id"
        },
        "preinvasive_tissue_morphology": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "processing_activity": {
          "@type": "@id"
        },
        "quality_measure": {
          "@type": "@id"
        },
        "quantity_measure": {
          "@type": "@id"
        },
        "related_document": {
          "@type": "@id"
        },
        "section_location": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "source_material_type": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "source_model_system": {
          "@type": "@id"
        },
        "source_subject": {
          "@type": "@id"
        },
        "specific_tissue_morphology": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "specimen_type": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "storage_activity": {
          "@type": "@id"
        },
        "transport_activity": {
          "@type": "@id"
        },
        "tumor_status_at_collection": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "additive": {
          "@type": "@id"
        },
        "container_type": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "parent_container": {
          "@type": "@id"
        },
        "activity_type": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "collection_method_type": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "collection_site": {
          "@type": "@id"
        },
        "derivation_method_type": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "execution_condition_observation": {
          "@type": "@id"
        },
        "execution_time_observation": {
          "@type": "@id"
        },
        "quantity_collected": {
          "@type": "@id"
        },
        "specimen_order": {
          "@type": "xsd:integer"
        },
        "duration": {
          "@type": "@id"
        },
        "container": {
          "@type": "@id"
        },
        "transport_destination": {
          "@type": "@id"
        },
        "transport_origin": {
          "@type": "@id"
        },
        "age_at_death": {
          "@type": "@id"
        },
        "breed": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "cause_of_death": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "ethnicity": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "race": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "sex": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "species": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "vital_status": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "year_of_birth": {
          "@type": "xsd:integer"
        },
        "year_of_death": {
          "@type": "xsd:integer"
        },
        "role": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "substance_quantity": {
          "@type": "@id"
        },
        "substance_type": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "periodEnd_end": {
          "@type": "@id"
        },
        "periodStart_start": {
          "@type": "@id"
        },
        "dateTime": {
          "@type": "xsd:dateTime"
        },
        "eventType": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "indexTimePoint": {
          "@type": "@id"
        },
        "offsetFromIndex": {
          "@type": "@id"
        },
        "concurrent_treatment": {
          "@type": "@id"
        },
        "number_of_cycles": {
          "@type": "xsd:integer"
        },
        "regimen": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "therapeutic_agent": {
          "@type": "@id"
        },
        "treatment_anatomic_site": {
          "@type": "@id"
        },
        "treatment_effect": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "treatment_end_reason": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "treatment_for_diagnosis": {
          "@type": "@id"
        },
        "treatment_frequency": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "treatment_intent": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "treatment_outcome": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        },
        "treatment_type": {
          "@context": {
            "@vocab": "@null",
            "text": "skos:notation",
            "description": "skos:prefLabel",
            "meaning": "@id"
          }
        }
      }
    }


We can also transform all the diagnoses in this file and store them in a file as JSON-LD.


```python
diagnoses = []
for case in gdc_head_and_mouth:
    for diagnosis in case['diagnoses']:
        diagnoses.append(transform_diagnosis(diagnosis, case))

jsonld = ''.join(jsonld_dumps(diagnoses, jsonldContext))
with open('head-and-mouth/diagnoses.jsonld', 'w') as file:
    file.write(jsonld)
```

## Converting JSON-LD to Turtle

While JSON-LD is a full dialect of RDF, people are more familiar looking at RDF in a format like [Turtle](https://en.wikipedia.org/wiki/Turtle_(syntax)). We can convert the generated JSON-LD output into Turtle by using the [rdflib](https://rdflib.readthedocs.io/en/stable/) package.

Note that this section is intended to be illustrative -- these are *not* finalized IRIs for properties and entities. We will choose IRIs and develop a canonical RDF representation in future phases of development.


```python
# We can read this JSON-LD in Turtle.
from rdflib import Graph

g = Graph()
g.parse(data=jsonld, format="json-ld")
rdfAsTurtle = g.serialize(format="turtle").decode()
print(''.join(rdfAsTurtle[0:1000]))
with open('head-and-mouth/diagnoses.ttl', 'w') as file:
    file.write(rdfAsTurtle)
```

    @prefix : <https://example.org/ccdh/> .
    @prefix ccdh: <https://example.org/ccdh/> .
    
    [] ccdh:condition [ ccdh:_code [ ccdh:text "Squamous cell carcinoma, NOS" ] ] ;
        ccdh:id "eb8958ba-0798-5ab3-b4f4-258d441d7e03" ;
        ccdh:identifier [ ccdh:system "GDC-submitter-id" ;
                ccdh:value "TCGA-P3-A6T5_diagnosis" ] ;
        ccdh:morphology [ ccdh:_code [ ccdh:text "8070/3" ] ] ;
        ccdh:related_specimen [ ccdh:creation_activity [ ccdh:date_ended [ ] ] ;
                ccdh:general_tissue_morphology "Not Reported" ;
                ccdh:id "e45c81dc-4143-4e97-8212-85032c760221" ;
                ccdh:source_material_type "Primary Tumor" ],
            [ ccdh:creation_activity [ ccdh:date_ended [ ccdh:dateTime "2018-05-17T12:19:46.292188-05:00"^^<xsd:dateTime> ] ] ;
                ccdh:general_tissue_morphology "Not Reported" ;
                ccdh:id "7fddfc05-49ef-4ebc-8572-05059a5fc363" ;
                ccdh:source_material_type "Primary Tumor" ],
            [ ccdh:creation_activity [ ccdh:date_ended [ ] ] ;

