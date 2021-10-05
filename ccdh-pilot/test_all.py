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

# Demonstrator 1
# TODO: change this to relative paths
d1_gdc_path = 'ccdh-pilot/demonstrator-1/d1_harmonized_gdc_specimen_cc.yaml'
with open(d1_gdc_path) as f:
    d1_gdc = yaml.load_all(f, Loader=yaml.FullLoader)

    for entry in d1_gdc:
        first_key = list(entry)[0]
        if first_key.endswith('_specimen'):
            specimen1 = YAMLLoader().load(entry[first_key]['Example'], crdch_model.Specimen)
            assert specimen1 is crdch_model.Specimen
            assert str(specimen1) == ''
        else:
            raise RuntimeError(f'Could not load entry: {entry}')
