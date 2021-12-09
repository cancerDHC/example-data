import crdch_model as cm
from linkml_runtime.dumpers import yaml_dumper


def test_dumps_vcc():
    vcc_obs = cm.Observation(observation_type=cm.CodeableConcept(),
                             value_codeable_concept=cm.CodeableConcept(
                                 coding=cm.Coding(code="3.1415", system="math professor")))
    vcc_dump = yaml_dumper.dumps(vcc_obs)
    # print statements ignored by default in passing pytests?
    # https://stackoverflow.com/questions/24617397/how-to-print-to-console-in-pytest
    # https://intellij-support.jetbrains.com/hc/en-us/community/posts/360007644040-Show-logging-output-when-using-pytest
    # added `-p no:logging -s` to "Additional Arguments" in Run Configuration
    # also try (global?) Run Configuration Template for pytest
    print(vcc_dump)
    assert len(vcc_dump) > 0


def test_dumps_decimal():
    decimal_obs = cm.Observation(observation_type=cm.CodeableConcept(), value_decimal="1.23")
    vd_dump = ""
    try:
        vd_dump = yaml_dumper.dumps(decimal_obs)
    except Exception as e:
        # PEP 8: E722 do not use bare 'except'
        print(f"{e}\nCouldn't dump CRDC-H decimal value to YAML string")
    assert len(vd_dump) > 0
