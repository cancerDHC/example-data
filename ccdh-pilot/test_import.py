#!/usr/bin/env python

#
# test_import.py - Import GDC and PDC data via public APIs and transform them into CRDC-H Instance data.
#

import json
import yaml

import linkml_runtime
from linkml_runtime.loaders.yaml_loader import YAMLLoader
from linkml_runtime.dumpers.yaml_dumper import YAMLDumper

import crdch_model
import jsonschema

# Demonstrators
def test_import_gdc_head_and_mouth():
    with open('head-and-mouth/gdc-head-and-mouth.json') as file:
        gdc_head_and_mouth = json.load(file)

    # Each entry is a GDC case. To transform this into CRDC-H instance data, we need to
    # transform it as a series of diagnoses.
    diagnoses = []
    for (index, gdc_case) in enumerate(gdc_head_and_mouth):
        diagnosis = crdch_model.Diagnosis(
            id=f'gdc_head_and_mouth_example:{index}',
            #identifier=[
            #    crdch_model.Identifier(value=f"gdc:{gdc_case['id']}")
            #]
        )

        diagnoses.append({
            f'gdc_head_and_mouth_example_{index}_diagnosis': {
                'Provenance':
                    'Downloaded from the GDC Public API (see ' +
                    'https://github.com/cancerDHC/example-data/blob/main/head-and-mouth/Head%20and%20Mouth%20Cancer%20Datasets.ipynb ' +
                    'for instructions)."',
                'Type': 'Diagnosis',
                'Documentation': 'https://cancerdhc.github.io/ccdhmodel/v1.1/Diagnosis/',
                'Example': diagnosis
            }
        })

    # Write out all diagnoses into a single YAML file in the imported-node-data directory.
    with open('ccdh-pilot/imported-node-data/gdc-head-and-mouth.yaml', 'w') as f:
        yaml.dump_all(diagnoses,
                      f, Dumper=yaml.SafeDumper,
                      sort_keys=False)
    #yaml.dump(linkml_runtime.utils.formatutils.remove_empty_items(element, hide_protected_keys=True),
    #          Dumper=yaml.SafeDumper, sort_keys=False,
