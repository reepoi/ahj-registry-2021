Census Bureau Shapefiles (Polygons)
===================================

The Polygon models in **models.py** represent the :censusshapefiles:`Census Bureau TIGER/Line Shapefiles <>` which are used to determine what jurisdictions contain an :obeditorview:`Address` or :obeditorview:`Location`.
Documentation for these shapefiles can be found in the :censusshapefilesdoc2020:`TGRSHP2020_TechDoc.pdf`. Definitions and descriptions of the Polygon's fields can be found in the :censusshapefilesdoc2020:`TGRSHP2020_TechDoc_F-R.pdf`.
Information on each of the Polygon's fields is also in **models.py**.

This page will cover how to download the shapefiles (which from now on will be called polygons), and all the steps to upload them into a database using Django.
The file **usf.py** (usf standing for 'upload shapefiles') is a useful reference and provides multiple utility functions to speed up the tasks presented on this page.

Downloading the Polygons
------------------------

Visit :censusshapefiles:`Census Bureau TIGER/Line Shapefiles <>`, and click a year to choose what year polygons to donwload.

There are four types of polygons (what the Census Bureau calls a **layer type**) to download:
    #. State
    #. County
    #. County Subdivision
    #. City

The Census Bureau provides two interfaces for downloading the polygons: an **FTP Archive**, and a **Web Interface**.
The following will go through how to download each type using either of these interfaces.
Note that downloading the polygons through the FTP Archive is less tedious.
The links to access both are under **Download**.

Downloading with the FTP Archive
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The FTP Archive page shows a list of many file directories.

The directories of interest are:
    #. ``STATE/`` for downloading State polygons.
    #. ``COUNTY/`` for downloading County polygons.
    #. ``COUSUB/`` for downloading County Subdivision polygons.
    #. ``PLACE/`` for downloading City polygons.

Download all of the ``.zip`` files in these directories.

Downloading with the Web Interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Web Interface has a dropdown select for the year of polygons to download, and the layer type.
Make sure that the **Select year** dropdown has selected the correct year.

The layer types of interest are:
    #. ``States (and equivalent)`` for downloading State polygons.
    #. ``Counties (and equivalent)`` for downloading County polygons.
    #. ``County Subdivisions`` for downloading County Subdivision polygons.
    #. ``Places`` for downloading City polygons.

For each of these layer types, click **Submit**.
For ``States (and equivalent)`` and ``Counties (and equivalent)``, click **Download national file**.
For ``County Subdivisions`` and ``Places``, click **Download** for every selection in the **Select a State** dropdown select.

Uploading the Polygons with Django
----------------------------------

The next sections are based off Django's own documentation `here <https://docs.djangoproject.com/en/3.2/ref/contrib/gis/tutorial/#use-ogrinfo-to-examine-spatial-data>`_.
First, unzip all of the files downloaded from the Census.
To use the utility functions in **usf.py**, arrange them in the file structure laid out there.

The steps to uploading the polygons with Django are:
    #. Inspect a ``.shp`` file for each polygon type to see what data columns it has.
    #. Create a Django model for each polygon type with fields for the data columns of the polygons.
    #. Create a Python dict which defines a mapping from the polygon's data column names to the Django models.
    #. Run Django's ``LayerMapping`` function which uses the mapping dict to upload the polygon data into the table created by the Django model.

Inspecting a ``.shp`` File
^^^^^^^^^^^^^^^^^^^^^^^^^^

Inside any unzipped polygon file download from the Census is a ``.shp`` file.
To see what data columns it has, run this command:

.. code-block:: console

    $ ogrinfo -so <path/to/.shp/file> <.shp file name without the file extension>

    Example:
    $ ogrinfo -so tl_2020_us_state.shp tl_2020_us_state

This will print various meta data about the file, and then data column names along with their data types.
The important part to pay attention to are the data columns and data types.

Data column and data type format and example:
    .. code-block:: yaml

        <column_name>: <data type>

        Example:

        FIPS: String (2.0)
        ISO2: String (2.0)
        ISO3: String (3.0)
        UN: Integer (3.0)
        NAME: String (50.0)
        AREA: Integer (7.0)
        POP2005: Integer (10.0)
        REGION: Integer (3.0)
        SUBREGION: Integer (3.0)
        LON: Real (8.3)
        LAT: Real (7.3)

Modeling the Data with a Django Model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Knowing the data columns and their types, create a Django model with fields for the columns.
Note the Django models fields can be a subset of the data columns.
Remember to create a inspect each polygon type's ``.shp`` file and create a Django model for it (4 total).
After creating the models, create a Python dict for each polygon type.
The dicts' keys should be the Django field names, and the values should be the polygon data column names.

.. note::

    **models.py** already has these models, and **usf.py** has the Python dicts.

    **models.py** has:
        #. ``StateTemp`` for the State polygons.
        #. ``CountyTemp`` for the County polygons.
        #. ``CousubTemp`` for the County Subdivision polygons.
        #. ``CityTemp`` for the City polygons.

    **usf.py** has:
        #. ``state_mapping`` for mapping the State polygon data to ``StateTemp``.
        #. ``county_mapping`` for mapping the County polygon data to ``CountyTemp``.
        #. ``cousub_mapping`` for mapping the County Subdivision polygon data to ``CousubTemp``.
        #. ``city_mapping`` for mapping the State polygon data to ``CityTemp``.

    These are set up for the 2020 Census Polygons, so make sure they are updated if a different year was downloaded.

Uploading the Polygon Data
^^^^^^^^^^^^^^^^^^^^^^^^^^

With the Django models and mapping dicts set up, the next step is uploading the polygon data into the Django model's tables.
Django provides a function for doing this called ``LayerMapping``.
To use it, create a Python script with the Django models, ``LayerMapping`` and mapping dicts.
Below it a Python script that will upload the State polygons to the StateTemp Django model table.

Example Python script:
    .. code-block:: python

        from django.contrib.gis.utils import LayerMapping
        from .models import ahj_registry_django_polygon_model, StateTemp, CountyTemp, CountySubdivisionTemp, CityTemp, \
            state_mapping, county_mapping, cousub_mapping, city_mapping

        path_to_state_shp = '/path/to/shp/file.shp/'

        lm = LayerMapping(StateTemp, path_to_state_shp, state_mapping, transform=False)
        lm.save(strict=True, verbose=True)

Run ``LayerMapping`` the ``.shp`` file in every polygon data download.

.. note::

    **usf.py** has functions to upload all the ``.shp`` files at once.

Moving the Polygon Data into the Tables Used in the AHJ Registry
----------------------------------------------------------------

By now, the polygon data will be in the database, but they are not in the correct tables to be used by the AHJ Registry.
The AHJ Registry uses the ``Polygon``, ``StatePolygon``, ``CountyPolygon``, ``CountySubdivisionPolygon``, and ``CityPolygon`` tables.
The data needs to be copied, or translated into those tables.
Look at **usf.py** to see how this translation is done.
