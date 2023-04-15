Flow Diagrams
=============

Address-to-AHJ Search
---------------------

.. substitution-digraph:: AddressAHJSearch

    node [shape=box]
        Address [label="POST Address for Search\n|exampleaddress|"];
        Geocode [label="Google Maps Geocoding API returns (Longitude, Latitude) for Address\n|examplelocation|"];
        IntersectPolygons [label="Search the Polygon table's MULTIPOLYGON to find those that contain the (Lng, Lat)\n\nPolygons:\l|exampleresultpolygons|"];
        RetrieveAHJs [label="Retrieve AHJs that have a foreign key reference the Polygons found.\n"];
        SortAHJs [label="Sort AHJs by AHJLevelCode* (descending), then secondarily, by their Polygon's LandArea (descending).\lAHJLevelCodes:\l162 or 061: State-Incorporated place, county subdivisions including towns, townships, districts (Third level**)\l050: State-County (Second level**)\l040: State (First level**)\l"];
        SerializeResult [label="Serialize the AHJs\nAHJs:\l|exampleresultahjs|"];
        AHJLevelCodesFootnote [label="*: \"How are geographic summary levels used?\"", href="|ahjlevelcodelink|", target="_blank", color=invis];
        PoliticalDivisionsFootnote [label="**: \"Political divisions of the United States\"", href="|wikipoliticaldivisions|", target="_blank", color=invis];

    Address -> Geocode;
    Geocode -> IntersectPolygons;
    IntersectPolygons -> RetrieveAHJs;
    RetrieveAHJs -> SortAHJs;
    SortAHJs -> SerializeResult;

    |#| Arrange footnotes.

    SerializeResult -> {AHJLevelCodesFootnote, PoliticalDivisionsFootnote} [style=invis];

    label = "Address-to-AHJ Search Flow"
    fontsize=20;
