from collections import OrderedDict

from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList

from .models import AHJ, Edit
from .serializers import AHJSerializer
from .utils import get_multipolygon, get_multipolygon_wkt, get_str_location, filter_ahjs, \
    order_ahj_list_AHJLevelCode_PolygonLandArea, get_location_gecode_address_str, remove_entries_dict, coerce_value


def get_edit_view_date_column(view):
    """
    Returns what Edit column should be considered for a given edit view.
    """
    view_modes = {'latest': 'DateRequested', 'latest-approved': 'DateEffective'}
    return view_modes[view]


def get_edit_values_for_row_fields(table, row, view='latest'):
    """
    Depending on **view**, returns a queryset of the most recently submitted or recently approved
    edits for a table and row. It returns at most one edit per column of the table.
    """
    view_column = get_edit_view_date_column(view)  # Validates view to ensure view_column is not an injection.
    return Edit.objects.raw('SELECT * FROM Edit outerloop '
                            f'WHERE {view_column}='
                            f'(SELECT MAX({view_column}) FROM Edit innerloop '
                            'WHERE outerloop.SourceColumn=innerloop.SourceColumn '
                            'AND outerloop.SourceRow=innerloop.SourceRow '
                            'AND outerloop.SourceTable=innerloop.SourceTable) '
                            'AND outerloop.SourceTable=%(table)s AND outerloop.SourceRow=%(row)s;',
                            params={'table': table, 'row': row})


def is_unapproved_edit_addition(model_name, row_id, edits):
    """
    Helper for ``apply_edits_to_dict`` when it is passed ``view='latest-approved'``.
    Determines whether a dict is an edit addition, and if so, if it has been approved.
    This helps distinguish dicts of rows that were added directly versus those added by an edit.
    """
    if not any(e.EditType == 'A' for e in edits):
        if Edit.objects.filter(SourceTable=model_name, SourceRow=row_id, EditType='A').exists():
            return True
    return False


def apply_edits_ob_dict_should_remove(model_name, row_id, edits, view='latest'):
    """
    Helper for ``apply_edits_to_ob_dict`` to tell when a dict should be removed from the result.
    For example, with ``view='latest-approved'``, any unapproved additions are removed.
    """
    has_edit_deletion = any(e.EditType == 'D' for e in edits)
    return has_edit_deletion or view == 'latest-approved' and is_unapproved_edit_addition(model_name, row_id, edits)


def apply_edits_to_ob_dict(obj, key_skip=lambda k: False, view='latest', primitive_name='Value'):
    """
    Applies edits to an Orange Button serialized dict (possibly nested) that has the extra entries:
        - _model_name
        - _id

    If the object is nested, each nested dict or dicts in a list must also have these entries
    if the caller wants edits applied to them.

    .. note::

        This method mutates the given dict.

    :param obj: the dict to apply edits to
    :param key_skip: function to indicate when not to update or examine a dict entry based on its key
    :param view: either 'latest' (most recently submitted edits) or 'latest-approved' (most recently approved edits) are applied
    :param primitive_name: under what the applied edit's NewValue should be applied
    :return: None
    """
    annotations = {'_model_name', '_id'}
    list_types = {list, ReturnList}
    dict_types = {dict, OrderedDict, ReturnDict}
    if len(annotations.intersection(obj.keys())) == 0:
        return obj
    model_name, row_id = obj['_model_name'], obj['_id']
    edits_to_apply = get_edit_values_for_row_fields(model_name, row_id, view=view)
    columns_to_edits = {e.SourceColumn: e for e in edits_to_apply}
    if apply_edits_ob_dict_should_remove(model_name, row_id, edits_to_apply, view=view):
        return None
    for k, v in obj.items():
        if k in annotations or key_skip(k):
            continue
        if type(v) in list_types:
            obj[k] = [r for r in  # Filter out any dicts removed by apply_edits_ob_dict_should_remove
                      [apply_edits_to_ob_dict(o, key_skip=key_skip, view=view, primitive_name=primitive_name) for o in v]
                      if r is not None]
        elif type(v) in dict_types and 'Value' not in v.keys():
            obj[k] = apply_edits_to_ob_dict(v, key_skip=key_skip, view=view, primitive_name=primitive_name)
        else:
            if k in columns_to_edits.keys():
                obj[k][primitive_name] = coerce_value(columns_to_edits[k].NewValue)
    return obj


@api_view(['POST'])
@throttle_classes([AnonRateThrottle])
def webpage_ahj_list(request):
    """
    Endpoint for the client app's AHJ Search.

    It is similar to to the public API endpoint documented in the API Documentation with these differences in filtering:
        - BuildingCode instead of BuildingCodes
        - ElectricCode instead of ElectricCodes
        - FireCode instead of FireCodes
        - ResidentialCode instead of ResidentialCodes
        - WindCode instead of WindCodes
        - Allows filtering with GeoJSON through the ``FeatureCollection`` parameter.

    See the AHJSearchPageFilter.vue and store.js for more information about how this endpoint is used.
    """
    json_location = get_location_gecode_address_str(request.data.get('Address', None))

    polygon = get_multipolygon(request=request, location=json_location)
    polygon_wkt = None
    if polygon is not None:
        polygon_wkt = get_multipolygon_wkt(multipolygon=polygon)
    str_location = get_str_location(location=json_location)
    ahjs = filter_ahjs(
        AHJName=request.data.get('AHJName', None),
        AHJID=request.data.get('AHJID', None),
        AHJPK=request.data.get('AHJPK', None),
        AHJCode=request.data.get('AHJCode', None),
        AHJLevelCode=request.data.get('AHJLevelCode', None),
        BuildingCode=request.data.get('BuildingCode', []),
        ElectricCode=request.data.get('ElectricCode', []),
        FireCode=request.data.get('FireCode', []),
        ResidentialCode=request.data.get('ResidentialCode', []),
        WindCode=request.data.get('WindCode', []),
        StateProvince=request.data.get('StateProvince', None),
        location=str_location, polygon=polygon_wkt)

    if polygon is not None and str_location is None:
        """
        If a polygon was searched, and a location was not,
        set the Location object returned to represent the center of the polygon.
        """
        polygon_center = polygon.centroid
        json_location = {'Latitude': {'Value': polygon_center[1]}, 'Longitude': {'Value': polygon_center[0]}}

    serializer = AHJSerializer
    paginator = LimitOffsetPagination()
    context = {'is_public_view': request.data.get('use_public_view', False)}
    page = paginator.paginate_queryset(ahjs, request)

    if str_location is not None or polygon is not None:
        """
        Sort the AHJs returned if a location or polygon was searched
        """
        page = order_ahj_list_AHJLevelCode_PolygonLandArea(page)

    payload = serializer(page, many=True, context=context).data

    return paginator.get_paginated_response({
        'Location': json_location,
        'ahjlist': payload
    })


@api_view(['GET'])
def get_single_ahj(request):
    """
    Endpoint to get a single AHJ given an ``AHJPK`` query parameter.
    """
    AHJPK = request.GET.get('AHJPK')
    try:
        ahj = AHJ.objects.get(AHJPK=AHJPK)
    except AHJ.DoesNotExist as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
    edit_view_mode = request.query_params.get('edit_view', '')
    if edit_view_mode in {'latest', 'latest-approved'}:
        serialized_ahj = AHJSerializer(ahj, context={'annotations': True}).data
        apply_edits_to_ob_dict(serialized_ahj, view=edit_view_mode)
        remove_entries_dict(serialized_ahj, {'_model_name', '_id'}, dict_check=lambda x: 'Value' not in x.keys())
    else:
        serialized_ahj = AHJSerializer(ahj).data
    serialized_ahj['LastEditTime'] = Edit.objects.filter(AHJPK=AHJPK).order_by('-DateRequested').values_list('DateRequested', flat=True).first()
    return Response(serialized_ahj, status=status.HTTP_200_OK)
