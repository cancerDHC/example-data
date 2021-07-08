import json
import pytest

import ccdhmodel as ccdh

def create_body_site(site_name):
    """ Create a CCDH BodySite based on the name of a site in the human body."""

    # Accept 'None'.
    if site_name is None:
        return None

    # Some body sites are not currently included in the CCDH model. We will need to translate these sites
    # into values that *are* included in the CCDH model.
    site_mappings = {
        'Larynx, NOS': ccdh.EnumCCDHBodySiteSite.Larynx
    }

    # Map values if needed. Otherwise, pass them through unmapped.
    if site_name in site_mappings:
        return ccdh.BodySite(site=(site_mappings[site_name]))

    return ccdh.BodySite(site=site_name)


def test_create_body_site():
    with pytest.raises(ValueError):
        create_body_site('Laryn')

    body_site_larynx = create_body_site('Larynx')
    body_site_larynx_nos = create_body_site('Larynx, NOS')

    print(body_site_larynx)

    assert type(body_site_larynx) is ccdh.BodySite
    assert body_site_larynx.site.code.text == ccdh.EnumCCDHBodySiteSite.Larynx.text

    assert type(body_site_larynx_nos) is ccdh.BodySite
    assert body_site_larynx_nos.site.code.text == ccdh.EnumCCDHBodySiteSite.Larynx.text


def test_transform_gdc_data():
    """
    Transform the GDC JSON data into JSON-LD.
    """
    with open('head-and-mouth/gdc-head-and-mouth.json') as file:
        gdc_head_and_mouth = json.load(file)

    assert len(gdc_head_and_mouth) > 0, "At least one GDC Head and Mouth case loaded."

