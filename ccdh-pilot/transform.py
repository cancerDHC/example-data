# Shared code for transforming data into the CRDC-H instance format.
# The goal is to eventually build a library that we can move into the ccdhmodel repo
# as a part of the crdch_model repository, implementing what is effectively a
# domain-specific language for doing transforms into the CRDC-H instance format.

import crdch_model


def codeable_concept(system, code, label=None, text=None, tags=[]):
    """Create a crdch_model.CodeableConcept for a given [single] system and code."""
    coding = crdch_model.Coding(system=system, code=code)
    if label is not None:
        coding.label = label
    if len(tags) > 0:
        coding.tag = tags
    cc = crdch_model.CodeableConcept(coding)
    if text is not None:
        cc.text = text
    return cc


def quantity_decimal(value_decimal, unit):
    """Create a crdch_model.Quantity for a given decimal value and a unit (expressed as a CodeableConcept)."""
    q = crdch_model.Quantity(unit=unit)
    # TODO: this should be converted to a Decimal, but that doesn't work/pass validation
    # So instead we truncate it to an integer for now.
    # Filed as issue https://github.com/cancerDHC/ccdhmodel/issues/131
    q.value_decimal = int(value_decimal)
    return q
