ER Diagrams
===========

Authority Having Jurisdiction
-----------------------------

.. substitution-graph:: OrangeButtonAHJ

    layout=neato
    node [shape=box]
        AHJ; Address; Location; Contact; AHJInspection; FeeStructure; EngineeringReviewRequirement;
        DocumentSubmissionMethod; PermitIssueMethod;
    node [shape=diamond,style=filled,color=orange]
        {node [label="Is At"] };
        {node [label="Has"] AHJAddress; AHJContact; AHJAHJInspection; AHJFeeStructure; AHJEngineeringReviewRequirement;
                            AHJDocumentSubmissionMethod; AHJPermitIssueMethod; AHJInspectionContact;
                            ContactAddress; AddressLocation;};

    |#| AHJ table relations.

    AHJ -- AHJAddress [|one|, len=1.2, |edgerequired|];
    AHJAddress -- Address [|one|, len=1.2];

    AHJ -- AHJContact [|one|, len=1.2];
    AHJContact -- Contact [|many|];

    AHJ -- AHJAHJInspection [|one|, len=1.2];
    AHJAHJInspection -- AHJInspection [|many|];

    AHJ -- AHJFeeStructure [|one|, len=1.2];
    AHJFeeStructure -- FeeStructure [|many|, len=1.2];

    AHJ -- AHJEngineeringReviewRequirement [|one|, len=1.0];
    AHJEngineeringReviewRequirement -- EngineeringReviewRequirement [|many|];

    AHJ -- AHJDocumentSubmissionMethod [|many|, len=1.2];
    AHJDocumentSubmissionMethod -- DocumentSubmissionMethod [|many|, len=2.0];

    AHJ -- AHJPermitIssueMethod [|many|, len=0.9];
    AHJPermitIssueMethod -- PermitIssueMethod [|many|, len=1.0];

    |#| AHJInspection table relations.

    AHJInspection -- AHJInspectionContact [|one|, len=1.5];
    AHJInspectionContact -- Contact [|many|];

    |#| Contact table relations.

    Contact -- ContactAddress [|one|, |edgerequired|];
    ContactAddress -- Address [|one|];

    |#| Address table relations.

    Address -- AddressLocation [|one|, |edgerequired|];
    AddressLocation -- Location [|one|, len=1.2];

    label = "\n\nAuthority Having Jurisdiction Overview\n(Excluding Polygons)";
    fontsize=20;

Polygons and AHJs
-----------------

.. substitution-graph:: Polygon

    node [shape=box]
        AHJ [pos="0,3.5!"]; Polygon; StatePolygon; CountyPolygon; CountySubdivisionPolygon; CityPolygon;
    node [shape=triangle]
        {node [label="Is A",style=filled,color=lightblue] IsA;};
    node [shape=diamond,style=filled,color=orange]
        {node [label="Has"] AHJPolygon;};

    |#| AHJ table relations.

    AHJ -- AHJPolygon [|one|];
    AHJPolygon -- Polygon [|one|];

    |#| Polygon table relations.

    Polygon -- IsA;
    IsA -- {StatePolygon, CountyPolygon, CountySubdivisionPolygon, CityPolygon};

    label="\n\nPolygons and AHJs";
    fontsize=20;

Users and AHJs
--------------

.. substitution-graph:: User

    node [shape=box]
        AHJ; User; SunSpecAllianceMember; SunSpecAllianceMemberDomain; AHJOfficeDomain; Contact;
    node [shape=diamond,style=filled,color=orange]
        {node [label="Has"] AHJAHJOfficeDomain; AHJUser; SunSpecAllianceMemberSunSpecAllianceMemberDomain;
                            UserSunSpecAllianceMember; UserContact};

    |#| User table relations.

    User -- AHJUser [|many|];
    AHJUser -- AHJ [|many|];

    User -- UserContact [|one|, |edgerequired|];
    UserContact -- Contact [|one|];

    User -- UserSunSpecAllianceMember [|one|];
    UserSunSpecAllianceMember -- SunSpecAllianceMember [|one|];

    |#| AHJ table relations.

    AHJ -- AHJAHJOfficeDomain [|one|];
    AHJAHJOfficeDomain -- AHJOfficeDomain [|one|, |edgerequired|];

    |#| SunSpecAllianceMember table relations.

    SunSpecAllianceMember -- SunSpecAllianceMemberSunSpecAllianceMemberDomain [|one|];
    SunSpecAllianceMemberSunSpecAllianceMemberDomain -- SunSpecAllianceMemberDomain [|one|, |edgerequired|];

    label="\n\nUsers and AHJs";
    fontsize=20;


Models Orange with an Enumerated Value Field
--------------------------------------------

Multiple models have Orange Button definitions with enumerated value fields.
Each enumerated value field is separated into its own models where each row is an enumerated value of the field.
Other models then have a foreign key reference to these enumerated value field models.
For example, the model ``AHJ`` has a field ``BuildingCode`` which references the ``BuildingCode`` model.

.. substitution-graph:: Enums

    node [shape=box] Model, Enum;
    node [shape=diamond,style=filled,color=orange]
        {node [label="Has"] ModelEnum;};

    {rank=same Model, ModelEnum, Enum}

    Model -- ModelEnum [|many|];
    ModelEnum -- Enum [|one|];

    label="\n\nModels and Their Enumerated Value Fields"
    fontsize=20;
