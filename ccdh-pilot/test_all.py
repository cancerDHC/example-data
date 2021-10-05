import sys
import os
import json
import pytest
import logging
import rdflib
import yaml

from linkml_runtime.loaders.yaml_loader import YAMLLoader
from linkml.generators.jsonldcontextgen import ContextGenerator
from linkml_runtime.dumpers import json_dumper

import crdch_model

# Demonstrators
def test_demonstrators():
    # TODO: change this to relative paths
    input_paths = [
        # Demonstrator 1
        'ccdh-pilot/demonstrator-1/d1_harmonized_gdc_specimen_cc.yaml',
        'ccdh-pilot/demonstrator-1/d1_harmonized_pdc_specimen_cc.yaml',
        'ccdh-pilot/demonstrator-1/d1_harmonized_icdc_specimen_cc.yaml',

        # Demonstrator 2
        'ccdh-pilot/demonstrator-2/d2_gdc_TCGA-13-1409_cc.yaml',
        'ccdh-pilot/demonstrator-2/d2_harmonized_TCGA-13-1409_cc.yaml',
        'ccdh-pilot/demonstrator-2/d2_idc_TCGA-13-1409_cc.yaml',
        'ccdh-pilot/demonstrator-2/d2_pdc_TCGA-13-1409_cc.yaml'
    ]
    for input_path in input_paths:
        with open(input_path) as f:
            examples = yaml.load_all(f, Loader=yaml.FullLoader)

            for entry in examples:
                first_key = list(entry)[0]
                example = entry[first_key]['Example']
                if first_key.endswith('_specimen'):
                    specimen = YAMLLoader().load(example, crdch_model.Specimen)
                elif first_key.endswith('_subject'):
                    subject = YAMLLoader().load(example, crdch_model.Subject)
                elif first_key.endswith('_research_project'):
                    research_project = YAMLLoader().load(example, crdch_model.ResearchProject)
                elif first_key.endswith('_research_subject'):
                    research_subject = YAMLLoader().load(example, crdch_model.ResearchSubject)
                elif first_key.endswith('_diagnosis'):
                    diagnosis = YAMLLoader().load(example, crdch_model.Diagnosis)
                else:
                    raise RuntimeError(f'Could not load entry: {entry}')
