from crdch_model import Diagnosis, CancerStageObservationSet, CodeableConcept
from linkml_runtime.loaders import yaml_loader

full_fname = "Diagnosis_id.yaml"

d = yaml_loader.load(full_fname, Diagnosis)

print(d)
