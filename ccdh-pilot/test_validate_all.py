import glob
import logging
import os

import crdch_model
import jsonschema
import requests
import yaml
from linkml_runtime.loaders.yaml_loader import YAMLLoader


# Generate tests for each file to validate.
def pytest_generate_tests(metafunc):
    # Identify all the files that need to be validated.
    # These are all the YAML files in this directory or any subdirectories.
    path_to_script = os.path.dirname(os.path.abspath(__file__))
    query = os.path.join(path_to_script, '**', '*.yaml')
    files_to_validate = glob.glob(query, recursive=True)

    metafunc.parametrize("input_file", files_to_validate)


# Test each input file.
def test_files(input_file):
    # JSON Schema URL
    json_schema_url = 'https://raw.githubusercontent.com/cancerDHC/ccdhmodel/main/crdch_model/json_schema/crdch_model.schema.json'
    req = requests.get(json_schema_url)
    ccdh_json_schema = req.json()

    # We need a RefResolver for the entire schema.
    ref_resolver = jsonschema.RefResolver.from_schema(ccdh_json_schema)

    # TODO: change this to relative paths
    with open(input_file) as f:
        logging.info(f'Validating {input_file}')
        examples = yaml.load_all(f, Loader=yaml.FullLoader)

        for entry in examples:
            first_key = list(entry)[0]
            example = entry[first_key]['Example']
            if first_key.endswith('_specimen'):
                specimen = YAMLLoader().load(example, crdch_model.Specimen)
                validator = jsonschema.Draft7Validator(ccdh_json_schema['$defs']['Specimen'], ref_resolver)
                errors = validator.iter_errors(example)
                for error in errors:
                    logging.error(f"Validation error in {input_file} at {error.path}: {error.message}")
                validator.validate(example)
            elif first_key.endswith('_subject'):
                subject = YAMLLoader().load(example, crdch_model.Subject)
                validator = jsonschema.Draft7Validator(ccdh_json_schema['$defs']['Subject'], ref_resolver)
                errors = validator.iter_errors(example)
                for error in errors:
                    logging.error(f"Validation error in {input_file} at {error.path}: {error.message}")
                validator.validate(example)
            elif first_key.endswith('_research_project'):
                research_project = YAMLLoader().load(example, crdch_model.ResearchProject)
                validator = jsonschema.Draft7Validator(ccdh_json_schema['$defs']['ResearchProject'], ref_resolver)
                errors = validator.iter_errors(example)
                for error in errors:
                    logging.error(f"Validation error in {input_file} at {error.path}: {error.message}")
                validator.validate(example)
            elif first_key.endswith('_research_subject'):
                research_subject = YAMLLoader().load(example, crdch_model.ResearchSubject)
                validator = jsonschema.Draft7Validator(ccdh_json_schema['$defs']['ResearchSubject'], ref_resolver)
                errors = validator.iter_errors(example)
                for error in errors:
                    logging.error(f"Validation error in {input_file} at {error.path}: {error.message}")
                validator.validate(example)
            elif first_key.endswith('_diagnosis'):
                diagnosis = YAMLLoader().load(example, crdch_model.Diagnosis)
                validator = jsonschema.Draft7Validator(ccdh_json_schema['$defs']['Diagnosis'], ref_resolver)
                errors = validator.iter_errors(example)
                for error in errors:
                    logging.error(f"Validation error in {input_file} at {error.path}: {error.message}")
                validator.validate(example)
            else:
                raise RuntimeError(f'Could not load entry: {entry}')
