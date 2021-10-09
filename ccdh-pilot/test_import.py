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

# Some general constants
GDC_URL = 'http://crdc.nci.nih.gov/gdc'
ICD10_URL = 'http://hl7.org/fhir/ValueSet/icd-10'


# Helper method to create a codeable concept.
def codeable_concept(system, code, label=None, text=None, tags=[]):
    coding = crdch_model.Coding(system=system, code=code)
    if label is not None:
        coding.label = label
    if len(tags) > 0:
        coding.tag = tags
    cc = crdch_model.CodeableConcept(coding)
    if text is not None:
        cc.text = text
    return cc


# Some codeable concepts we use repeatedly.
DAY = codeable_concept('http://ncithesaurus.nci.nih.gov', 'C25301', 'Day')


# Demonstrators
def test_import_gdc_head_and_mouth():
    with open('head-and-mouth/gdc-head-and-mouth.json') as file:
        gdc_head_and_mouth = json.load(file)

    # Each entry is a GDC case. To transform this into CRDC-H instance data, we need to
    # transform it as a series of diagnoses.
    diagnoses = []
    for (index, gdc_case) in enumerate(gdc_head_and_mouth):
        for (diag_index, gdc_diagnosis) in enumerate(gdc_case['diagnoses']):
            diagnosis = crdch_model.Diagnosis(
                id=f'gdc_head_and_mouth_example:{index}_diagnosis_{diag_index}',

                # -- TODO: these fields do not currently validate.
                #identifier=[
                #    crdch_model.Identifier(value=f"gdc:{gdc_diagnosis['diagnosis_id']}")
                #],

                # -- TODO: I'm not sure how to model these fields
                # subject=crdch_model.Subject()
            )

            if gdc_diagnosis.get('age_at_diagnosis'):
                # TODO: this is caused by a weird LinkML bug that means that setting properties directly does NOT
                # convert it into the correct base type. We should, uh, iron these out at some point.
                diagnosis.age_at_diagnosis = crdch_model.Quantity(unit=DAY)
                diagnosis.age_at_diagnosis.value_decimal = gdc_diagnosis['age_at_diagnosis']

            condition_codings = []
            if gdc_diagnosis.get('primary_diagnosis'):
                condition_codings.append(crdch_model.Coding(
                    system=GDC_URL,
                    code=gdc_diagnosis.get('primary_diagnosis'),
                    tag=['original']
                ))

            # TODO: double-check with DMH if this makes sense
            if gdc_diagnosis.get('icd_10_code'):
                condition_codings.append(crdch_model.Coding(
                    system=ICD10_URL,
                    code=gdc_diagnosis.get('icd_10_code'),
                    tag=['original']
                ))

            diagnosis.condition = crdch_model.CodeableConcept(coding=condition_codings)

            #if gdc_diagnosis.get('tissue_or_organ_of_origin'):
            #    diagnosis.primary_site = crdch_model.BodySite(
            #        site=codeable_concept(GDC_URL, gdc_diagnosis.get('tissue_or_organ_of_origin'), tags=['original'])
            #    )

            if gdc_diagnosis.get('ajcc_staging_system_edition'):
                observations = []

                def add_observation(type_code, type_label, stage_code):
                    if stage_code:
                        observations.append(crdch_model.CancerStageObservation(
                            observation_type=codeable_concept(GDC_URL, type_code, type_label, tags=['harmonized']),
                            value_codeable_concept=codeable_concept(GDC_URL, stage_code, stage_code, tags=['original'])
                        ))

                # TODO: I couldn't find AJCC v7 in NCIt, so these codes reference the 8th edition. Need to be fixed.
                # TODO: This is the first piece we should uncomment, because it triggers exactly the same error as when
                # we try loading these observations from YAML.
                # add_observation('C177555', 'AJCC v8 Clinical Stage', gdc_diagnosis.get('ajcc_clinical_stage'))
                # add_observation('C177606', 'AJCC v8 Clinical M Category', gdc_diagnosis.get('ajcc_clinical_m'))
                # add_observation('C177611', 'AJCC v8 Clinical N Category', gdc_diagnosis.get('ajcc_clinical_n'))
                # add_observation('C177635', 'AJCC v8 Clinical T Category', gdc_diagnosis.get('ajcc_clinical_t'))
                # add_observation('C177556', 'AJCC v8 Pathologic Stage', gdc_diagnosis.get('ajcc_pathologic_stage'))
                # add_observation('C177607', 'AJCC v8 Pathologic M Category', gdc_diagnosis.get('ajcc_pathologic_m'))
                # add_observation('C177612', 'AJCC v8 Pathologic N Category', gdc_diagnosis.get('ajcc_pathologic_n'))
                # add_observation('C177636', 'AJCC v8 Pathologic T Category', gdc_diagnosis.get('ajcc_pathologic_t'))

                diagnosis.stage = [crdch_model.CancerStageObservationSet(
                    method_type=codeable_concept(GDC_URL, gdc_diagnosis.get('ajcc_staging_system_edition'), tags=['original']),
                    observations=observations
                )]

            # elif gdc_diagnosis.get('figo_stage'):

            diagnoses.append({
                f'gdc_head_and_mouth_example_{index}_diagnosis_{diag_index}_diagnosis': {
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
        linkml_runtime.utils.formatutils.remove_empty_items

    #yaml.dump(linkml_runtime.utils.formatutils.remove_empty_items(element, hide_protected_keys=True),
    #          Dumper=yaml.SafeDumper, sort_keys=False,
