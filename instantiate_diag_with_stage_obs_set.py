from crdch_model import Diagnosis
from linkml_runtime.loaders import yaml_loader

diagnosis_fn = "gen_diag_with_stage_obs_set.yaml"

diag = yaml_loader.load(diagnosis_fn, Diagnosis)

print(diag)
