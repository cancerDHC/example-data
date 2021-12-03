from crdch_model import Coding, CodeableConcept, CancerStageObservation, CancerStageObservationSet
from linkml_runtime.loaders import yaml_loader

Coding_fn = "linkml_linkml_issue_463_test_data/Coding.yaml"
CodeableConcept_fn = "linkml_linkml_issue_463_test_data/CodeableConcept.yaml"
CancerStageObservation_fn = "linkml_linkml_issue_463_test_data/CancerStageObservation.yaml"
CancerStageObservationSet_fn = "linkml_linkml_issue_463_test_data/CancerStageObservationSet.yaml"


def load_and_type(fn, expected_type):
    obj = None
    try:
        obj = yaml_loader.load(fn, expected_type)
    except Exception:
        print(f"Exception on loading {fn} vs crdch_model")
    assert isinstance(obj, expected_type)


def test_Coding():
    load_and_type(Coding_fn, Coding)


def test_CodeableConcept():
    load_and_type(CodeableConcept_fn, CodeableConcept)


def test_CancerStageObservation():
    load_and_type(CancerStageObservation_fn, CancerStageObservation)


def test_CancerStageObservationSet():
    load_and_type(CancerStageObservationSet_fn, CancerStageObservationSet)
