"""Provenance table"""

import os
import re
import pandas as pd
import panel as pn
from functools import lru_cache
from aiida.orm.querybuilder import QueryBuilder
from aiida.orm import Node, Group
from pipeline_pyrenemofs import TAG_KEY, GROUP_DIR, EXPLORE_URL, get_db_nodes_dict

from figure.config import load_profile
load_profile()

try:
    this_dir = os.path.dirname(os.path.abspath(__file__)) + '/'
except:
    this_dir = ''

AIIDA_LOGO_URL = "select_pyrenemofs/static/images/aiida-128.png"
DOI_LOGO_URL = 'select_pyrenemofs/static/images/paper-128.png'
MAT_LOGO_URL = 'select_pyrenemofs/static/images/mat-128.png'

def doi_link(mat_dict):
    """Return the DOI link of the article."""
    doi = mat_dict['orig_cif'].extras['doi_ref']
    return "<a href='https://doi.org/{}' target='_blank'><img class='provenance-logo' src='{}'></a>".format(
        doi, DOI_LOGO_URL)

def detail_link(mat_id):
    """Return representation of workflow link."""
    return "<a href='detail_pyrenemofs?mat_id={}' target='_blank'><img class='provenance-logo' src='{}'></a>".format(
        mat_id, MAT_LOGO_URL)

@lru_cache()
def get_elements_from_cifdata(cifdata):
    formula = cifdata.get_ase().get_chemical_formula()
    elements = [e for e in re.split(r'\d+', formula) if e]
    return ",".join(elements)


@lru_cache()
def get_table():
    """Get the entries for the right table of select-figure."""

    pd.set_option('max_colwidth', 10)

    df = pd.DataFrame(columns=[  # Set the order of the columns
        'Name', 'Article', 'Elements', 'Surface (m2/g)', 'Structure'
    ])

    db_nodes_dict = get_db_nodes_dict()

    for mat_id, mat_dict in db_nodes_dict.items():
        new_row = {
            'Name': mat_dict['orig_cif'].extras['name_conventional'],
            'Article': doi_link(mat_dict),
            'Elements': get_elements_from_cifdata(mat_dict['orig_cif']),
            'Structure': detail_link(mat_id)
        }

        if 'opt_zeopp' in mat_dict:
            new_row['Surface (m2/g)'] = int(mat_dict['opt_zeopp']['ASA_m^2/g'])
        else: 
            new_row['Surface (m2/g)'] = int(mat_dict['orig_zeopp']['ASA_m^2/g'])

        df = df.append(new_row, ignore_index=True)

    df = df.sort_values(by=['Name'])
    df = df.reset_index(drop=True)
    df.index += 1
    return df


def fake_button(link, label, button_type):
    return """<span><a href="{link}" target="_blank">
        <button class="bk bk-btn bk-btn-{bt}" type="button">{label}</button></a></span>""".format(link=link,
                                                                                                  label=label,
                                                                                                  bt=button_type)


buttons = pn.Row()
buttons.append(
    fake_button(link="pipeline_config/static/pyrene-mofs-info.csv", label="Info CSV", button_type="primary")) #audoderect to the GitHub file!
buttons.append(
    fake_button(link="https://archive.materialscloud.org/file/2019.0034/v2/cifs_cellopt_Dec19.zip", #make an archive
                label="CURATED CIFs",
                button_type="primary"))
buttons.append(
    fake_button(link="figure_pyrenemofs", #make an archive
                label="Interactive Plot",
                button_type="primary"))

pn.extension()

t = pn.Column()
t.append(buttons)
t.append(get_table().to_html(escape=False))
t.servable()
