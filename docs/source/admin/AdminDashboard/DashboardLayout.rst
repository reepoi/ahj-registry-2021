Dashboard Layout and Organization
=================================

The admin dashboard has five main pages.

Home
----

The **Home** page is the landing page after logging in.
Here it lists all the Django models that are not purely controlled by Django.

The models are organized into three groups:
    - **User Data:** Those modified or used directly by user action.
        - ``AHJ Office Domains``, ``API Tokens``, ``Comments``, ``Edits``, ``SunSpec Alliance Member Domains``, ``SunSpec Alliance Members``, ``Users``
    - **AHJ Data:** Those that hold the main records of the Orange Button AuthorityHavingJurisdiction object data.
        - ``AHJ Census Names``, ``AHJ Document Submission Method Uses``, ``AHJ Inspections``, ``AHJ Level Codes``, ``AHJ Permit Issue Method Uses``, ``AHJ User Maintains``, ``AHJs``, ``Address Types``, ``Addresses``, ``Building Codes``, ``Contact Types``, ``Contacts``, ``Document Submission Methods``, ``Electric Codes``, ``Engineering Review Requirements``, ``Engineering Review Types``, ``Fee Structure Types``, ``Fee Structures``, ``Fire Codes``, ``Inspection Types``, ``Location Determination Methods``, ``Location Types``, ``Locations``, ``Permit Issue Methods``, ``Preferred Contact Methods``, ``Requirement Levels``, ``Residential Codes``, ``Stamp Types``, ``Wind Codes``
    - **Polygon Data:** Those that hold the Polygon data.
        - ``City Polygons``, ``Temporary City Polygons``, ``County Polygons``, ``County Subdivision Polygons``, ``Temporary County Polygons``, ``Temporary County Subdivision Polygons``, ``Polygon``, ``State Polygons``, ``Temporary State Polygons``

Aside from these, there are other Django models but these are hidden because they are only controlled by Django automatically.

Change Lists
------------

Clicking on any model on the **Home** will load the **Change List** page for that model.
It displays a paginated table of all the entries stored in the model's database table.
There is a search bar to filter the entries, and entries can be selected to run an **Admin Action** on them.
Some admin actions allow filtering entries on other models' change list pages using the current change list entries.
**Admin Actions** will be discussed more in its own section.

Change Form
------------

Clicking on an entry on the **Change List** of a model loads the **Change Form** page for that entry.
It presents a form representing the columns and data of the entry.
Data can be entered and changed in the form, and then saving the form will save the changes to the entry.
The fields named in **bold** are required before the form will save.

Entry History
-------------

In the top-right corner of the **Change Form** page is a button labeled ``History``.
Clicking it will load the **Entry History** page of the entry.
This displays logs of every time an entry's data was changed and saved, and each log saves a snapshot of the entry.
Clicking on a log will load a **Change Form** page with the data from the snapshot.
The entry can be reverted to the snapshot by clicking ``Revert`` at the bottom of the page.
