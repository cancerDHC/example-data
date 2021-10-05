import sys
import os
import json
import pytest
import logging
import rdflib
import requests
import yaml

from linkml_runtime.loaders.yaml_loader import YAMLLoader
from linkml.generators.jsonldcontextgen import ContextGenerator
from linkml_runtime.dumpers import json_dumper

import crdch_model
import jsonschema

# Demonstrators
def test_demonstrators():
    # JSON Schema URL
    json_schema_url = 'https://raw.githubusercontent.com/cancerDHC/ccdhmodel/main/crdch_model/json_schema/crdch_model.schema.json'
    req = requests.get(json_schema_url)
    ccdh_json_schema = req.json()

    # We need a RefResolver for the entire schema.
    ref_resolver = jsonschema.RefResolver.from_schema(ccdh_json_schema)

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
            logging.info(f'Validating {input_path}')
            examples = yaml.load_all(f, Loader=yaml.FullLoader)

            for entry in examples:
                first_key = list(entry)[0]
                example = entry[first_key]['Example']
                if first_key.endswith('_specimen'):
                    specimen = YAMLLoader().load(example, crdch_model.Specimen)
                    validator = jsonschema.Draft7Validator(ccdh_json_schema['$defs']['Specimen'], ref_resolver)
                    errors = validator.iter_errors(example)
                    for error in errors:
                        logging.error(f"Validation error in {input_path} at {error.path}: {error.message}")
                    validator.validate(example)
                elif first_key.endswith('_subject'):
                    subject = YAMLLoader().load(example, crdch_model.Subject)
                    validator = jsonschema.Draft7Validator(ccdh_json_schema['$defs']['Subject'], ref_resolver)
                    errors = validator.iter_errors(example)
                    for error in errors:
                        logging.error(f"Validation error in {input_path} at {error.path}: {error.message}")
                    validator.validate(example)
                elif first_key.endswith('_research_project'):
                    research_project = YAMLLoader().load(example, crdch_model.ResearchProject)
                    validator = jsonschema.Draft7Validator(ccdh_json_schema['$defs']['ResearchProject'], ref_resolver)
                    errors = validator.iter_errors(example)
                    for error in errors:
                        logging.error(f"Validation error in {input_path} at {error.path}: {error.message}")
                    validator.validate(example)
                elif first_key.endswith('_research_subject'):
                    research_subject = YAMLLoader().load(example, crdch_model.ResearchSubject)
                    validator = jsonschema.Draft7Validator(ccdh_json_schema['$defs']['ResearchSubject'], ref_resolver)
                    errors = validator.iter_errors(example)
                    for error in errors:
                        logging.error(f"Validation error in {input_path} at {error.path}: {error.message}")
                    validator.validate(example)
                elif first_key.endswith('_diagnosis'):
                    diagnosis = YAMLLoader().load(example, crdch_model.Diagnosis)
                    validator = jsonschema.Draft7Validator(ccdh_json_schema['$defs']['Diagnosis'], ref_resolver)
                    errors = validator.iter_errors(example)
                    for error in errors:
                        logging.error(f"Validation error in {input_path} at {error.path}: {error.message}")
                    validator.validate(example)
                else:
                    raise RuntimeError(f'Could not load entry: {entry}')
