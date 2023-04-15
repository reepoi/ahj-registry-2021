Admin Actions
=============

As mentioned in **Dashboard Layout and Organization**, the entries on the **Change List** can be selected to run an admin action on them.
Here will list each admin action available on the **Change List**.
Some admin actions are available on every change list while others are specific to certain models' change lists.
Some admin actions have intermediate forms with these buttons: ``Confirm``, to apply the changes presented by the action, and ``Cancel``, to return to the **Change List** without taking any action.

For Every Model Change List
---------------------------

Delete Selected
^^^^^^^^^^^^^^^

This will delete the selected entries from the database.
There is an intermediate page to confirm their deletion.

Export CSV
^^^^^^^^^^

This will export the selected entries as a CSV file.

AHJ Change List
---------------

Query AHJ Official Users
^^^^^^^^^^^^^^^^^^^^^^^^

This will retrieve the users that are AHJ officials of the selected AHJs and display them in the User **Change List**.

Comment Change List
-------------------

Query Submitting Users
^^^^^^^^^^^^^^^^^^^^^^

This will retrieve the users that submitted the selected comments and display them in the User **Change List**.

Edit Change List
----------------

Approve Edits
^^^^^^^^^^^^^

This loads an intermediate form listing the selected edits in the following format:

    .. code-block:: xml

        Edit(<EditID>): <SourceTable>(<SourceRow>).<SourceColumn> from '<OldValue>' to '<NewValue>'

For example,

    .. code-block:: python

        Edit(123): AHJ(123).AHJName from 'Old Name' to 'New Name'

For each edit, choose a date effective.
This will set when the to-be-approved edit's changes will be applied.
If ``---`` is selected in any of the dropdown selects for choosing the date effective, no date effective will be set and the edit will **not** be approved.
The dropdown selects at the top of the page will set the date effective for all of the edits.

.. note::

    The Django server runs on **UTC 0:00** time.
    In addition, the server checks for edits that need their changes applied at **3 am UTC 0:00**.
    To illustrate, when attempting to have an edit applied on **03/15/2022 PST**, it will be applied at **7:00pm 03/14/2022 PST**.

If ``Today`` is chosen for a day effective, the edit will be approved and its changes will applied applied immediately after clicking ``Confirm``.

.. note::

    The admin who runs this admin action will be named as the user who approved the selected edits (setting the edits' ``ApprovedBy`` field).

Roll Back Edits
^^^^^^^^^^^^^^^

This loads an intermediate form listing the selected edits in the following format:

    .. code-block:: xml

        Edit(<EditID>): Revert <SourceTable>(<SourceRow>).<SourceColumn> from '<OldValue>' to '<NewValue>'

For example,

    .. code-block:: python

        Edit(123): Revert AHJ(123).AHJName from 'Old Name' to 'New Name'

The listed edits are split into three lists specifying how the edits' changes will be rolled back:
    - **Edits that will be set pending and whose changes will be undone, if any changes were made:**
        - Edits are rolled back in this way if they meet any of the following criteria:
            #. The edit is **rejected** (i.e. not approved and its change is not applied).
            #. The edit is **approved** but its change is **not applied** (i.e. its date effective has not passed yet).
            #. The edit is **approved** and its change **is applied**, but **no other edits** have been applied after it to the **same** source table, source row, and source column.
    - **Edits for which new edits will be created to reverse the edit's changes:** These edits do not meet any of the criteria to be in the first list.

        .. note::

            The admin who runs this admin action will be named as the user who submitted and approved these newly created edits (setting the edits' ``ChangedBy`` and ``ApprovedBy`` fields).

    - **Pending edits for which no action will be taken:** Since pending edits' changes are not applied, their changes do not need to be rolled back.

Query Submitting Users
^^^^^^^^^^^^^^^^^^^^^^

This will retrieve the users that submitted the selected edits and display them in the User **Change List**.

Query Approving User
^^^^^^^^^^^^^^^^^^^^

This will retrieve the users that submitted the selected edits that were approved by an AHJ official and display them in the User **Change List**.

User Change List
----------------

Reset Password
^^^^^^^^^^^^^^

Enter the new password for the selected user in plain text into the intermediate form.
After clicking ``Confirm``, the password will be hashed and saved as the new password for the selected User entry.

Generate API Token
^^^^^^^^^^^^^^^^^^

This loads an intermediate form with two lists:
    #. The selected users without an API token. This admin action will create new API tokens for these users.
    #. The selected users already with an API token. This admin action will have no effect for these users.

.. note::

    The new API tokens are deactivated when they are created.
    See the **Delete/Toggle API Token** admin action to see how to activate them.

For each user without an API token, choose an expiration date for each user's new API token.
This is the date when the user's token will be deactivated.
In addition, no expiration date will be set if ``---`` is selected in any of the dropdown selects for the expiration date.
The dropdown selects at the top of the page will set the expiration date for all the new API tokens.

.. note::

    The Django server runs on **UTC 0:00** time.
    In addition, the server checks for expired API tokens at **3 am UTC 0:00**.
    To illustrate, when attempting to set a token to expire on **03/15/2022 PST**, it will be deactivated at **7:00pm 03/14/2022 PST**.

Delete/Toggle API Token
^^^^^^^^^^^^^^^^^^^^^^^

This loads an intermediate form with two lists:
    #. The selected users with an API token. This admin action will toggle or delete these users' API tokens.
    #. The selected users without an API token. This admin action will have no effect for these users.

For each user with an API token, choose whether to toggle their API token ``On`` or ``Off``, or delete their API token.
Toggling a user's API token ``On`` will activate it, and toggling it ``Off`` will deactivate it.
Choosing the toggle option ``Do Nothing`` will not change the activation state of the API token.
Use the dropdown select and checkbox at the top of the page to set the toggle or delete all the API tokens of the selected users.

Query API Tokens
^^^^^^^^^^^^^^^^

This will retrieve the API tokens of the selected users and display them in the API token **Change List**.

Query Is AHJ Official Of
^^^^^^^^^^^^^^^^^^^^^^^^

This will retrieve the AHJs that the selected users are AHJ officials of and display them in the AHJ **Change List**.

Query Submitted Edits
^^^^^^^^^^^^^^^^^^^^^

This will retrieve the edits submitted by the selected users and display them in the Edit **Change List**.

Query Approved Edits
^^^^^^^^^^^^^^^^^^^^

This will retrieve the edits submitted by the selected users that were approved by an AHJ official and display them in the Edit **Change List**.

Query Submitted Comments
^^^^^^^^^^^^^^^^^^^^^^^^

This will retrieve the comments submitted by the selected users and display them in the Comment **Change List**.
