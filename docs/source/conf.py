# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import json
import os
import sys
import django
sys.path.insert(0, os.path.abspath('../../server'))
sys.path.insert(0, os.path.abspath('.'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'TheAHJRegistry.settings'
django.setup()


# -- Project information -----------------------------------------------------

project = 'AHJ Registry'
copyright = '2021, SunSpec Alliance'
author = 'SunSpec Alliance'

# The full version, including alpha/beta/rc tags
release = '2.1.1'


# -- General configuration ---------------------------------------------------

master_doc = 'index'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.extlinks',
    'sphinx.ext.autodoc',
    'sphinxcontrib_django',
    'sphinx.ext.graphviz',
    'ext_graph_substitution'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

html_context = {
    'display_github': True,
    'github_user': 'SunSpecOrangeButton',
    'github_repo': 'ahj-registry',
    'github_version': 'HEAD',
    'conf_py_path': '/docs/source/',
    'source_suffix': '.rst'
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_favicon = f'{html_static_path[0]}/favicon.ico'

# -- Options for code-block syntax highlighting ------------------------------

# Set to none to allow for plain text literal blocks with '::'
# For code syntax highlighting, use '.. code-block:: <language; (default is python)>'
highlight_language = 'none'

# -- External link aliases ---------------------------------------------------

# Note the key names must be all lowercase
extlinks = {'orangebuttonio': ('https://orangebutton.io/%s', None),
            'obeditor': ('https://obeditor.sunspec.org/%s', None),
            'obeditorview': ('https://obeditor.sunspec.org/#/?views=%s', '%s'),
            'ahjregistry': ('https://ahjregistry.sunspec.org/%s', None),
            'censusshapefiles': ('https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html%s', None),
            'censusshapefilesdoc2020': ('https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2020/%s', '%s')}

# -- Substitution definitions for graphs ---------------------

graphviz_output_format = 'svg'

graph_substitutions = [('|#|', ''),
                       ('|edgerequired|', 'color="black:white:black"'),
                       ('|one|', 'label="1"'),
                       ('|many|', 'label="M"')]


def json_for_label(obj, indent=4, justification='\l'):
    """
    Formats a dict to be substituted into a node label for Graphviz.
    justification can be either:
        - <backslash>l: Left-justified
        - <backslash>n: Center-justified
        - <backslash>r: Right-justified
    """
    return f'{json.dumps(json.dumps(obj, indent=indent))[1:-1]}\\n'.replace('\\n', justification)


example_address = json_for_label({'AddrLine1': {'Value': '4040 Moorpark Ave. Suite 110'},
                                  'City': {'Value': 'San Jose'},
                                  'StateProvince': {'Value': 'CA'},
                                  'ZipPostalCode': {'Value': '95117'}})

example_location = json_for_label({'Latitude': {'Value': 37.3155858},
                                   'Longitude': {'Value': -121.97358}})

example_result_polygons = '<Polygon: San Jose city>\l<Polygon: Santa Clara County>\l<Polygon: California state>\l'

example_result_ahjs = '<AHJ: San Jose city, AHJLevelCode: 162>\l<AHJ: Santa Clara County, AHJLevelCode: 050>\l<AHJ: California state, AHJLevelCode: 040>\l'

ahjlevelcode_link = 'https://www.census.gov/programs-surveys/popest/guidance-geographies/terms-and-definitions.html'

wiki_political_divisions_link = 'https://www.census.gov/programs-surveys/popest/guidance-geographies/terms-and-definitions.html'

digraph_substitutions = [('|#|', ''),
                         ('|exampleaddress|', example_address),
                         ('|examplelocation|', example_location),
                         ('|exampleresultpolygons|', example_result_polygons),
                         ('|exampleresultahjs|', example_result_ahjs),
                         ('|ahjlevelcodelink|', ahjlevelcode_link),
                         ('|wikipoliticaldivisions|', wiki_political_divisions_link)]
