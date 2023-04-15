from django.db import connection
from django.urls import reverse
from django.http import HttpRequest
from ahj_app.models import AHJ, Polygon, Address, User, Edit, Comment, APIToken, StatePolygon
from ahj_app.models_field_enums import AHJLevelCode, AHJ_LEVEL_CODE_CHOICES, BuildingCode, BUILDING_CODE_CHOICES, \
    ElectricCode, ELECTRIC_CODE_CHOICES
from django.utils import timezone

from fixtures import *
from constants import *
from ahj_app.utils import *
from ahj_app import views_ahjsearch, views_ahjsearch_api
from ahj_app.serializers import AHJSerializer
import pytest
import datetime
import requests

@pytest.fixture
def valid_address():
    return {
        'AddrLine1': '4040 Moorpark Ave #110',
        'City': '', 
        'StateProvince': 'California',
        'ZipPostalCode': '95117'
    }

@pytest.fixture
def valid_address_ob():
    return {
        'AddrLine1': {'Value': '4040 Moorpark Ave #110'},
        'City': {'Value': ''}, 
        'StateProvince': {'Value': 'California'},
        'ZipPostalCode': {'Value': '95117'}
    }

@pytest.fixture
def valid_location():
    return { 'Latitude': '25' , 'Longitude': '25' }


@pytest.fixture
def valid_location_ob():
    return { 
        'Latitude': { 
            'Value': '25' 
        }, 
        'Longitude': { 
            'Value': '25' 
        }
    }

def ahj_filter_create_ahj(ahjpk, ahjid, polygonTuple, ahjLevel, AHJCode, AHJName, StateProvince, BuildingCode=None, ElectricCode=None):
    p1 = geosPolygon(polygonTuple)
    mp = MultiPolygon(p1)
    polygon = Polygon.objects.create(Polygon=mp, LandArea=1, WaterArea=1, InternalPLatitude=1, InternalPLongitude=1)
    address = Address.objects.create(StateProvince=StateProvince)
    ahj = AHJ.objects.create(AHJPK=ahjpk, AHJID= ahjid, AHJCode=AHJCode, PolygonID=polygon, AddressID=address, AHJLevelCode=ahjLevel, BuildingCode=BuildingCode, ElectricCode=ElectricCode, AHJName=AHJName)
    StatePolygon.objects.create(PolygonID=polygon)
    return ahj

@pytest.fixture
def list_of_ahjs():
    ahjLevel1 = AHJLevelCode.objects.create(AHJLevelCodeID=1, Value=AHJ_LEVEL_CODE_CHOICES[0][0])
    ahjLevel2 = AHJLevelCode.objects.create(AHJLevelCodeID=2, Value=AHJ_LEVEL_CODE_CHOICES[1][0])
    ahjLevel3 = AHJLevelCode.objects.create(AHJLevelCodeID=3, Value=AHJ_LEVEL_CODE_CHOICES[2][0])
    buildingCode = BuildingCode.objects.create(BuildingCodeID=1, Value=BUILDING_CODE_CHOICES[0][0])
    buildingCode2 = BuildingCode.objects.create(BuildingCodeID=2, Value=BUILDING_CODE_CHOICES[1][0])
    electricCode = ElectricCode.objects.create(ElectricCodeID=1, Value=ELECTRIC_CODE_CHOICES[0][0])

    ahj1 = ahj_filter_create_ahj(1, '27389324-3y4u-2348-2344-324324678281', ((0, 0), (0, 10), (10, 10), (10, 0), (0,0)), ahjLevel1, 'AK-32789121', 'Sweetwater City', 'Arkansas') # AHJs 1 and 2 are in the same polygon as ahj_filter_polygon
    ahj2 = ahj_filter_create_ahj(2, 'f97ea81a-f9c4-4195-889e-ad414b736ce5', ((0, 3), (0, 13), (10, 13), (10, 3), (0, 3)), ahjLevel2, 'CA-0686300', 'Orange County', 'California')
    ahj3 = ahj_filter_create_ahj(3, '78d2735b-b581-45ba-8cb6-2dea58596e97', ((20, 20), (20, 30), (30, 30), (30, 20), (20,20)), ahjLevel3, 'UT-0681820', 'Orange City', 'Utah') # AHJ 3's polygon is over ahj_filter_location

    ahj4 = ahj_filter_create_ahj(4, 'cc3e36e2-340c-4301-a8f1-da3025eac647', ((-120, 30), (-130, 30), (-130, 40), (-120, 40), (-120, 30)), ahjLevel1, 'CA-0692300', 'Clemens County', 'California', buildingCode, electricCode) # AHJ 4 and 5 are found through the request 
    ahj5 = ahj_filter_create_ahj(5, '34329324-3y4u-2348-2344-324324678282', ((100, 100), (100, 110), (110, 110), (110, 100), (100, 100)), ahjLevel1, 'AL-3752395', 'Smith City', 'Alabama', buildingCode, electricCode)
    return ahj1, ahj2, ahj3, ahj4, ahj5

def get_ahjs_from_response(response, url_name):
    if url_name == 'ahj-public':
        return response.data['AuthorityHavingJurisdictions']
    else:
        return response.data['results']['ahjlist']

"""
    Public and Private AHJ Search Tests
"""

@pytest.mark.parametrize(
   'url_name', [
       ('ahj-private'),
       ('ahj-public')
   ])
@pytest.mark.django_db
def test_webpage_ahj_list__no_search_parameters(url_name, client_with_credentials, list_of_ahjs):
    url = reverse(url_name)
    response = client_with_credentials.post(url)
    assert response.data['count'] == 5 # returns all 5 AHJs due to no filtering

@pytest.mark.parametrize(
   'url_name, payload', [
       ('ahj-private', {'AHJName': 'Orange County'}),
       ('ahj-public', {'AHJName': { 'Value': 'Orange County'}})
   ])
@pytest.mark.django_db
def test_ahj_list__AHJName_search(url_name, payload, list_of_ahjs, client_with_credentials):
    ahj1, ahj2, ahj3, ahj4, ahj5 = list_of_ahjs
    url = reverse(url_name)
    response = client_with_credentials.post(url, payload, format='json')
    ahjs = get_ahjs_from_response(response, url_name)
    assert response.data['count'] == 1 
    assert ahjs[0]['AHJCode']['Value'] == ahj2.AHJCode # verify only the ahj2 was returned

@pytest.mark.parametrize(
   'url_name, payload', [
       ('ahj-private', {'AHJName': 'Orange'}),
       ('ahj-public', {'AHJName': { 'Value': 'Orange'}})
   ])
@pytest.mark.django_db
def test_ahj_list__AHJName_search_multiple_matches(url_name, payload, list_of_ahjs, client_with_credentials):
    ahj1, ahj2, ahj3, ahj4, ahj5 = list_of_ahjs
    url = reverse(url_name)
    response = client_with_credentials.post(url, payload, format='json')
    ahjs = get_ahjs_from_response(response, url_name)
    assert response.data['count'] == 2
    assert ahjs[0]['AHJCode']['Value'] == ahj2.AHJCode and ahjs[1]['AHJCode']['Value'] == ahj3.AHJCode
    

@pytest.mark.parametrize(
   'url_name, payload', [
       ('ahj-private', {'AHJID': 'f97ea81a-f9c4-4195-889e-ad414b736ce5'}),
       ('ahj-public', {'AHJID': {'Value': 'f97ea81a-f9c4-4195-889e-ad414b736ce5'}})
   ])
@pytest.mark.django_db
def test_ahj_list__AHJID_search(url_name, payload, list_of_ahjs, client_with_credentials):
    ahj1, ahj2, ahj3, ahj4, ahj5 = list_of_ahjs
    url = reverse(url_name)
    response = client_with_credentials.post(url, payload, format='json')
    ahjs = get_ahjs_from_response(response, url_name)
    assert response.data['count'] == 1 
    assert ahjs[0]['AHJCode']['Value'] == ahj2.AHJCode

@pytest.mark.parametrize(
   'url_name, payload', [
       ('ahj-private', {'AHJCode': 'CA-0686300'}),
       ('ahj-public', {'AHJCode': {'Value': 'CA-0686300'}})
   ])
@pytest.mark.django_db
def test_ahj_list__AHJCode_search(url_name, payload, list_of_ahjs, client_with_credentials):
    ahj1, ahj2, ahj3, ahj4, ahj5 = list_of_ahjs
    url = reverse(url_name)
    response = client_with_credentials.post(url, payload, format='json')
    ahjs = get_ahjs_from_response(response, url_name)
    assert response.data['count'] == 1 
    assert ahjs[0]['AHJCode']['Value'] == ahj2.AHJCode

@pytest.mark.parametrize(
   'url_name, payload', [
       ('ahj-private', {'AHJLevelCode': '040'}),
       ('ahj-public', {'AHJLevelCode': {'Value': '040'}})
   ])
@pytest.mark.django_db
def test_ahj_list__AHJLevelCode_search(url_name, payload, list_of_ahjs, client_with_credentials):
    ahj1, ahj2, ahj3, ahj4, ahj5 = list_of_ahjs
    url = reverse(url_name)
    response = client_with_credentials.post(url, payload, format='json')
    ahjs = get_ahjs_from_response(response, url_name)
    assert response.data['count'] == 3
    assert ahjs[0]['AHJCode']['Value'] == ahj1.AHJCode and ahjs[1]['AHJCode']['Value'] == ahj4.AHJCode and ahjs[2]['AHJCode']['Value'] == ahj5.AHJCode 

@pytest.mark.parametrize(
   'url_name, payload', [
       ('ahj-private', { "BuildingCode": [ "2021IBC" ],  "ElectricCode": [  "2020NEC"  ]}),
       ('ahj-public', { 'BuildingCodes': [ { 'Value': '2021IBC'} ],  'ElectricCodes': [  { 'Value':'2020NEC'}  ]})
   ])
@pytest.mark.django_db
def test_ahj_list__BuildingCode_search(url_name, payload, list_of_ahjs, client_with_credentials):
    ahj1, ahj2, ahj3, ahj4, ahj5 = list_of_ahjs
    url = reverse(url_name)
    response = client_with_credentials.post(url, payload, format='json')
    ahjs = get_ahjs_from_response(response, url_name)
    assert response.data['count'] == 2 
    assert ahjs[0]['AHJCode']['Value'] == ahj4.AHJCode and ahjs[1]['AHJCode']['Value'] == ahj5.AHJCode 

@pytest.mark.parametrize(
   'url_name, payload', [
       ('ahj-private', {'StateProvince': 'California'}),
       ('ahj-public', {'StateProvince': {'Value': 'California'}})
   ])
@pytest.mark.django_db
def test_ahj_list__StateProvince_search(url_name, payload, list_of_ahjs, client_with_credentials):
    ahj1, ahj2, ahj3, ahj4, ahj5 = list_of_ahjs
    url = reverse(url_name)
    response = client_with_credentials.post(url, payload, format='json')
    ahjs = get_ahjs_from_response(response, url_name)
    assert response.data['count'] == 2
    assert ahjs[0]['AHJCode']['Value'] == ahj2.AHJCode and ahjs[1]['AHJCode']['Value'] == ahj4.AHJCode 

@pytest.mark.parametrize(
   'url_name', [
       ('ahj-private'),
       ('ahj-public')
   ])
@pytest.mark.django_db
def test_ahj_list__Address_search(url_name, list_of_ahjs, client_with_credentials, valid_address, valid_address_ob):
    ahj1, ahj2, ahj3, ahj4, ahj5 = list_of_ahjs
    url = reverse(url_name)
    if url_name == 'ahj-public': response = client_with_credentials.post(url, {'Address': valid_address_ob}, format='json')
    else: response = client_with_credentials.post(url, {'Address': valid_address}, format='json')
    ahjs = get_ahjs_from_response(response, url_name)
    assert response.data['count'] == 1
    assert ahjs[0]['AHJCode']['Value'] == ahj4.AHJCode

@pytest.mark.parametrize(
   'url_name', [
       ('ahj-private'),
       ('ahj-public')
   ])
@pytest.mark.django_db
def test_ahj_list__Location_search(url_name, list_of_ahjs, client_with_credentials, valid_location, valid_location_ob):
    ahj1, ahj2, ahj3, ahj4, ahj5 = list_of_ahjs
    url = reverse(url_name)
    if url_name == 'ahj-public': 
        response = client_with_credentials.post(url, {'Location': valid_location_ob}, format='json')
    else: 
        response = client_with_credentials.post(url, {'Address': '25 25'}, format='json') # Address is the name of object sent to our ahj-private endpoint.
    
    ahjs = get_ahjs_from_response(response, url_name)
    assert response.data['count'] == 1
    assert ahjs[0]['AHJCode']['Value'] == ahj3.AHJCode

@pytest.mark.parametrize(
   'url_name, payload', [
       ('ahj-private', {'Address': '9, 9'}),
       ('ahj-public', {'Location': { 'Longitude': { 'Value': '9' }, 'Latitude': { 'Value': '9' }}})
   ])
@pytest.mark.django_db
def test_ahj_list__overlapping_polygons(url_name, payload, list_of_ahjs, client_with_credentials):
    ahj1, ahj2, ahj3, ahj4, ahj5 = list_of_ahjs
    url = reverse(url_name)
    response = client_with_credentials.post(url, payload, format='json')
    ahjs = get_ahjs_from_response(response, url_name)
    assert response.data['count'] == 2
    assert ahjs[0]['AHJCode']['Value'] == ahj2.AHJCode and ahjs[1]['AHJCode']['Value'] == ahj1.AHJCode 
    

@pytest.mark.parametrize(
   'url_name', [
       ('ahj-private'),
       ('ahj-public')
   ])
@pytest.mark.django_db
def test_ahj_list__multiple_search_params_two_ahjs(url_name, list_of_ahjs, client_with_credentials):
    ahj1, ahj2, ahj3, ahj4, ahj5 = list_of_ahjs
    url = reverse(url_name)
    if url_name == 'ahj-public': 
        response = client_with_credentials.post(url,{
                                                        'AHJLevelCode': [{'Value' : ahj4.AHJLevelCode.Value}],
                                                        'BuildingCodes': [{ 'Value' : '2021IBC' }, { 'Value' : '2018IBC'}],
                                                        'ElectricCodes': [{ 'Value' : '2020NEC' }, { 'Value' : '2017NEC'}],
                                                    }, format='json')
    else: 
        response = client_with_credentials.post(url, {
                                                        'AHJLevelCode': ahj4.AHJLevelCode.Value, 
                                                        'BuildingCode': [ '2021IBC', '2018IBC'], 
                                                        'ElectricCode': [ '2020NEC', '2017NEC']
                                                    }, format='json')
    ahjs = get_ahjs_from_response(response, url_name)
    assert response.data['count'] == 2
    assert ahjs[0]['AHJCode']['Value'] == ahj4.AHJCode and ahjs[1]['AHJCode']['Value'] == ahj5.AHJCode

@pytest.mark.parametrize(
   'url_name', [
       ('ahj-private'),
       ('ahj-public')
   ])
@pytest.mark.django_db
def test_ahj_list__multiple_search_params_one_ahj(url_name, list_of_ahjs, client_with_credentials):
    ahj1, ahj2, ahj3, ahj4, ahj5 = list_of_ahjs
    url = reverse(url_name)
    if url_name == 'ahj-public': 
        response = client_with_credentials.post(url,{
                                                        'Location': { 'Longitude': { 'Value': '-122' }, 'Latitude': { 'Value': '37' }},
                                                        'AHJLevelCode': [{'Value' : ahj4.AHJLevelCode.Value}],
                                                        'BuildingCodes': [{ 'Value' : '2021IBC' }, { 'Value' : '2018IBC'}],
                                                        'ElectricCodes': [{ 'Value' : '2020NEC' }, { 'Value' : '2017NEC'}],
                                                    }, format='json')
    else: 
        response = client_with_credentials.post(url, {
                                                        'Address': '37, -122', 
                                                        'AHJLevelCode': ahj4.AHJLevelCode.Value, 
                                                        'BuildingCode': [ '2021IBC', '2018IBC'], 
                                                        'ElectricCode': [ '2020NEC', '2017NEC']
                                                    }, format='json')
    ahjs = get_ahjs_from_response(response, url_name)
    assert response.data['count'] == 1
    assert ahjs[0]['AHJCode']['Value'] == ahj4.AHJCode

"""
    Only Private AHJ Search Tests
"""
# get_single_ahj Tests
@pytest.mark.django_db
def test_get_single_ahj__valid_ahj(ahj_obj, client_with_credentials):
    url = reverse('single_ahj')
    response = client_with_credentials.get(url, {'AHJPK': ahj_obj.AHJPK})
    assert response.data['AHJPK']['Value'] == ahj_obj.AHJPK

@pytest.mark.django_db
@pytest.mark.parametrize(
   'param', [
       ({}),
       ({'AHJPK': 2}),
   ]
)
def test_get_single_ahj__incorrect_param(param, ahj_obj, client_with_credentials):
    url_name = reverse('single_ahj')
    response = client_with_credentials.get(url_name, param)
    assert response.status_code == 400

@pytest.mark.parametrize(
    'view, expected_result', [
        ('latest', 'DateRequested'),
        ('latest-approved', 'DateEffective')
    ]
)
def test_get_edit_view_date_column(view, expected_result):
    assert views_ahjsearch.get_edit_view_date_column(view) == expected_result


@pytest.mark.parametrize(
    'source_table, value, approve_edit', [
        ('AHJInspection', [{}], True),
        ('Contact', [{'Address': {'Location': {}}}], True),
        ('DocumentSubmissionMethod', [{'Value': 'Email'}], True),
        ('EngineeringReviewRequirement', [{}], True),
        ('FeeStructure', [{}], True),
        ('PermitIssueMethod', [{'Value': 'Email'}], True),
        ('AHJInspection', [{}], False),
        ('Contact', [{'Address': {'Location': {}}}], False),
        ('DocumentSubmissionMethod', [{'Value': 'Email'}], False),
        ('EngineeringReviewRequirement', [{}], False),
        ('FeeStructure', [{}], False),
        ('PermitIssueMethod', [{'Value': 'Email'}], False)
    ]
)
@pytest.mark.django_db
def test_is_unapproved_edit_addition(source_table, value, approve_edit, generate_client_with_webpage_credentials, ahj_obj, add_enum_value_rows):
    """
    This is a helper method for running apply_edits_to_ob_dict with view='latest-approved'.
    See the doc-string for is_unapproved_edit_addition for an explanation what this is for.
    """
    url = reverse('edit-addition')
    client = generate_client_with_webpage_credentials()
    client.post(url, {'SourceTable': source_table,
                      'AHJPK': ahj_obj.AHJPK,
                      'ParentID': ahj_obj.AHJPK,
                      'ParentTable': 'AHJ',
                      'Value': value}, format='json')
    creating_edit = Edit.objects.first()
    if approve_edit:
        set_obj_field(creating_edit, 'ReviewStatus', 'A')
        all_approved_edits_for_row = Edit.objects.filter(SourceTable=creating_edit.SourceTable, SourceRow=creating_edit.SourceRow,
                                                         SourceColumn=creating_edit.SourceColumn, ReviewStatus='A')
    else:
        all_approved_edits_for_row = Edit.objects.none()
    if source_table in {'DocumentSubmissionMethod', 'PermitIssueMethod'}:
        model_name = f'AHJ{source_table}Use'
    else:
        model_name = source_table
    assert views_ahjsearch.is_unapproved_edit_addition(model_name, creating_edit.SourceRow, all_approved_edits_for_row) != approve_edit


@pytest.mark.django_db
def test_apply_edits_ob_dict_should_remove__is_deleted(generate_client_with_webpage_credentials, ahj_obj, create_minimal_obj):
    """
    Just testing the deletion case because the other cases are handled by is_unapproved_edit_addition.
    """
    contact = create_minimal_obj('Contact')
    set_obj_field(contact, 'ParentTable', 'AHJ')
    set_obj_field(contact, 'ParentID', ahj_obj.AHJPK)
    url = reverse('edit-deletion')
    client = generate_client_with_webpage_credentials()
    client.post(url, {'SourceTable': 'Contact',
                      'AHJPK': ahj_obj.AHJPK,
                      'Value': [contact.ContactID]}, format='json')
    deleting_edit = Edit.objects.first()
    assert views_ahjsearch.apply_edits_ob_dict_should_remove('Contact', contact.ContactID, [deleting_edit])


def create_edits_for_fields(edit_dict, fields):
    edit_accumulator = []
    for field in fields:
        edit_dict['SourceColumn'] = field
        edit_accumulator.append(Edit.objects.create(**edit_dict))
    edit_dict['SourceColumn'] = fields[0]
    return edit_accumulator


@pytest.mark.parametrize(
    'view', [
        'latest',
        'latest-approved'
    ]
)
@pytest.mark.django_db
def test_get_edit_values_for_row_fields(view, create_user, ahj_obj):
    user = create_user()
    fields_to_edit = ['AHJName', 'Description']
    edit_dict = {'ChangedBy': user, 'ApprovedBy': None,
                 'SourceTable': 'AHJ', 'SourceRow': ahj_obj.pk, 'SourceColumn': 'AHJName',
                 'OldValue': 'oldname', 'NewValue': 'newname',
                 'DateRequested': timezone.now(), 'DateEffective': None,
                 'ReviewStatus': 'P', 'EditType': 'U', 'AHJPK': ahj_obj}
    first_unapproved_edits = create_edits_for_fields(edit_dict, fields_to_edit)
    edit_dict['DateRequested'] += datetime.timedelta(days=1)
    second_unapproved_edits = create_edits_for_fields(edit_dict, fields_to_edit)
    edit_dict['DateRequested'] -= datetime.timedelta(days=1)
    edit_dict['DateEffective'] = timezone.now()
    first_approved_edits = create_edits_for_fields(edit_dict, fields_to_edit)
    edit_dict['DateEffective'] += datetime.timedelta(days=1)
    second_approved_edits = create_edits_for_fields(edit_dict, fields_to_edit)
    result_edits = views_ahjsearch.get_edit_values_for_row_fields('AHJ', ahj_obj.AHJPK, view=view)
    if view == 'latest':
        assert all(e in result_edits for e in second_unapproved_edits)
    elif view == 'latest-approved':
        assert all(e in result_edits for e in second_approved_edits)


@pytest.mark.parametrize(
    'model_name, fields_to_edit', [
        ('AHJ', ['AHJName', 'AHJLevelCode', 'Description']),
        ('Address', ['AddrLine1', 'AddressType']),
        ('Location', ['Elevation', 'LocationDeterminationMethod']),
        ('FeeStructure', ['FeeStructureID']),
        ('Contact', ['ContactStatus']),
        ('EngineeringReviewRequirement', ['RequirementLevel']),
        ('AHJInspection', ['Description', 'InspectionStatus'])
    ]
)
@pytest.mark.django_db
def test_get_edit_values_for_row_fields(model_name, fields_to_edit, create_user, ahj_obj, create_minimal_obj):
    user = create_user()
    row = create_minimal_obj(model_name)
    edit_dict = {'ChangedBy': user, 'ApprovedBy': None,
                 'SourceTable': model_name, 'SourceRow': row.pk, 'SourceColumn': '',
                 'OldValue': '', 'NewValue': '',
                 'DateRequested': timezone.now(), 'DateEffective': None,
                 'ReviewStatus': 'P', 'EditType': 'U', 'AHJPK': ahj_obj}
    first_unapproved_edits = create_edits_for_fields(edit_dict, fields_to_edit)
    edit_dict['DateRequested'] += datetime.timedelta(days=1)
    second_unapproved_edits = create_edits_for_fields(edit_dict, fields_to_edit)
    edit_dict['DateRequested'] -= datetime.timedelta(days=1)
    edit_dict['DateEffective'] = timezone.now()
    first_approved_edits = create_edits_for_fields(edit_dict, fields_to_edit)
    edit_dict['DateEffective'] += datetime.timedelta(days=1)
    second_approved_edits = create_edits_for_fields(edit_dict, fields_to_edit)
    result_edits = views_ahjsearch.get_edit_values_for_row_fields(model_name, row.pk, view='latest')
    assert all(e in result_edits for e in second_unapproved_edits)
    result_edits = views_ahjsearch.get_edit_values_for_row_fields(model_name, row.pk, view='latest-approved')
    assert all(e in result_edits for e in second_approved_edits)


@pytest.mark.parametrize(
    'view, is_approved', [
        ('latest', False),
        ('latest', True),
        ('latest-approved', False),
        ('latest-approved', True)
    ]
)
@pytest.mark.django_db
def test_apply_edits_to_ob_dict__edit_addition(view, is_approved, ahj_obj, generate_client_with_webpage_credentials):
    url = reverse('edit-addition')
    client = generate_client_with_webpage_credentials()
    client.post(url, {'SourceTable': 'FeeStructure',
                      'AHJPK': ahj_obj.AHJPK,
                      'ParentID': ahj_obj.AHJPK,
                      'ParentTable': 'AHJ',
                      'Value': [{}]}, format='json')
    creating_edit = Edit.objects.first()
    if is_approved:
        set_obj_field(creating_edit, 'DateEffective', timezone.now() + datetime.timedelta(days=1))
    data = AHJSerializer(ahj_obj, context={'annotations': True}).data
    views_ahjsearch.apply_edits_to_ob_dict(data, view=view)
    expect_added = not (view == 'latest-approved' and is_approved is False)
    assert any(creating_edit.SourceRow == f['FeeStructurePK']['Value'] for f in data['FeeStructures']) == expect_added


@pytest.mark.parametrize(
    'view, is_approved', [
        ('latest', False),
        ('latest', True),
        ('latest-approved', False),
        ('latest-approved', True)
    ]
)
@pytest.mark.django_db
def test_apply_edits_to_ob_dict__edit_update(view, is_approved, ahj_obj, generate_client_with_webpage_credentials):
    set_obj_field(ahj_obj, 'AHJName', 'oldname')
    url = reverse('edit-update')
    client = generate_client_with_webpage_credentials()
    client.post(url, [{'SourceTable': 'AHJ',
                      'SourceRow': ahj_obj.AHJPK,
                      'SourceColumn': 'AHJName',
                      'AHJPK': ahj_obj.AHJPK,
                      'NewValue': 'newname'}], format='json')
    creating_edit = Edit.objects.first()
    if is_approved:
        set_obj_field(creating_edit, 'DateEffective', timezone.now() + datetime.timedelta(days=1))
    data = AHJSerializer(ahj_obj, context={'annotations': True}).data
    views_ahjsearch.apply_edits_to_ob_dict(data, view=view)
    expect_updated = not (view == 'latest-approved' and is_approved is False)
    is_updated = 'newname' == data['AHJName']['Value']
    assert is_updated == expect_updated


@pytest.mark.parametrize(
    'view, is_approved', [
        ('latest', False),
        ('latest', True),
        ('latest-approved', False),
        ('latest-approved', True)
    ]
)
@pytest.mark.django_db
def test_apply_edits_to_ob_dict__edit_deletion(view, is_approved, ahj_obj, create_minimal_obj, generate_client_with_webpage_credentials):
    contact = create_minimal_obj('Contact')
    set_obj_field(contact, 'ParentTable', 'AHJ')
    set_obj_field(contact, 'ParentID', ahj_obj.AHJPK)
    url = reverse('edit-deletion')
    client = generate_client_with_webpage_credentials()
    client.post(url, {'SourceTable': 'Contact',
                      'AHJPK': ahj_obj.AHJPK,
                      'Value': [contact.ContactID]}, format='json')
    deleting_edit = Edit.objects.first()
    if is_approved:
        set_obj_field(deleting_edit, 'DateEffective', timezone.now() + datetime.timedelta(days=1))
    data = AHJSerializer(ahj_obj, context={'annotations': True}).data
    views_ahjsearch.apply_edits_to_ob_dict(data, view=view)
    expect_deleted = not (view == 'latest-approved' and is_approved is False)
    assert all(contact.ContactID != c['ContactID']['Value'] for c in data['Contacts']) == expect_deleted

"""
    Only Public AHJ Search Tests
"""
# ahj_geo_address Tests
@pytest.mark.django_db
def test_ahj_geo_address__missing_address(client_with_credentials):
    url = reverse('ahj-geo-address')
    response = client_with_credentials.post(url)
    assert response.status_code == 400

@pytest.mark.django_db
def test_ahj_geo_address__invalid_address_ob(client_with_credentials):
    url = reverse('ahj-geo-address')
    response = client_with_credentials.post(url, {'Address': {'AddrLine1': {'Value': '112 Baker St'}, 'AddrLine3': {''}}}, format='json')
    assert response.status_code == 400

@pytest.mark.django_db
def test_ahj_geo_address__valid_address_ob_format(client_with_credentials):
    url = reverse('ahj-geo-address')
    response = client_with_credentials.post(url, {'AddrLine1': {'Value': '112 Baker St'}, 'City': {'Value': 'Salt Lake City'}}, format='json')
    assert response.status_code == 200
    response = client_with_credentials.post(url, {'Address': {'AddrLine1': {'Value': '112 Baker St'}, 'City': {'Value': 'Salt Lake City'}}}, format='json')
    assert response.status_code == 200

@pytest.mark.django_db
def test_ahj_geo_address__both_params_with_outdated_address_format(client_with_credentials):
    url = reverse('ahj-geo-address')
    response = client_with_credentials.post(url, {'ahjs_to_search': ['ID1', 'ID2'], 'AddrLine1': {'Value': '112 Baker St'}, 'City': {'Value': 'Salt Lake City'}}, format='json')
    assert response.status_code == 200

@pytest.mark.django_db
def test_ahj_geo_address__both_params(client_with_credentials):
    url = reverse('ahj-geo-address')
    response = client_with_credentials.post(url, {'ahjs_to_search': ['ID1', 'ID2'], 'Address': {'AddrLine1': {'Value': '112 Baker St'}}}, format='json')
    assert response.status_code == 200

@pytest.mark.django_db
def test_ahj_geo_address__address_does_not_match_ahj(list_of_ahjs, client_with_credentials):
    url = reverse('ahj-geo-address')
    response = client_with_credentials.post(url, {'Address': {'AddrLine1': {'Value': '112 Baker St'}, 'City': {'Value': 'Salt Lake City'}}}, format='json')
    assert len(response.data) == 0
    assert response.status_code == 200

@pytest.mark.django_db
def test_ahj_geo_address__address_matches_ahj(list_of_ahjs, client_with_credentials, valid_address_ob):
    url = reverse('ahj-geo-address')
    response = client_with_credentials.post(url, {'Address': valid_address_ob}, format='json')
    assert len(response.data) == 1
    assert response.data[0]['AHJID']['Value'] == 'cc3e36e2-340c-4301-a8f1-da3025eac647'
    assert response.status_code == 200

@pytest.mark.django_db
def test_ahj_geo_address__search_array_does_not_have_ahj(list_of_ahjs, client_with_credentials, valid_address_ob):
    url = reverse('ahj-geo-address')
    response = client_with_credentials.post(url, { 'Address': valid_address_ob, 'ahjs_to_search': ['8ac31936-ebfc-4713-8ca6-1646ae38353c']}, format='json')
    assert len(response.data) == 0
    assert response.status_code == 200

@pytest.mark.django_db
def test_ahj_geo_address__search_array_has_ahj(list_of_ahjs, client_with_credentials, valid_address_ob):
    url = reverse('ahj-geo-address')
    response = client_with_credentials.post(url, {'Address': valid_address_ob, 'ahjs_to_search': ['cc3e36e2-340c-4301-a8f1-da3025eac647', '8ac31936-ebfc-4713-8ca6-1646ae38353c']}, format='json')
    assert len(response.data) == 1
    assert response.data[0]['AHJID']['Value'] == 'cc3e36e2-340c-4301-a8f1-da3025eac647'
    assert response.status_code == 200

# ahj_geo_location Tests

@pytest.mark.django_db
def test_ahj_geo_location__valid_location_ob_format(client_with_credentials, valid_location_ob):
    url = reverse('ahj-geo-location')
    response = client_with_credentials.post(url, { 'Latitude': { 'Value': '25' }, 'Longitude': { 'Value': '25' }}, format='json')
    assert response.status_code == 200
    response = client_with_credentials.post(url, {'Location': valid_location_ob}, format='json')
    assert response.status_code == 200

@pytest.mark.django_db
def test_ahj_geo_location__valid_location_format(client_with_credentials):
    url = reverse('ahj-geo-location')
    response = client_with_credentials.post(url, { 'Latitude': { 'Value': '25' }, 'Longitude': { 'Value': '25' }}, format='json')
    assert response.status_code == 200
    response = client_with_credentials.post(url, {'Location': { 'Latitude': { 'Value': '25' }, 'Longitude': { 'Value': '25' }}}, format='json')
    assert response.status_code == 200

@pytest.mark.django_db
def test_ahj_geo_location__empty_lat_lon(client_with_credentials):
    url = reverse('ahj-geo-location')
    response = client_with_credentials.post(url, {'Location': { 'Latitude': { 'Value': '' }, 'Longitude': { 'Value': '' }}}, format='json')
    assert response.status_code == 400

@pytest.mark.django_db
def test_ahj_geo_location__invalid_values_lat_lon(client_with_credentials):
    url = reverse('ahj-geo-location')
    response = client_with_credentials.post(url, {'Location': { 'Latitude': { 'Value': 'a' }, 'Longitude': { 'Value': 'a' }}}, format='json')
    assert response.status_code == 400

@pytest.mark.django_db
def test_ahj_geo_location__missing_lat_or_lon(client_with_credentials):
    url = reverse('ahj-geo-location')
    response = client_with_credentials.post(url, {'Location': { 'Latitude': { 'Value': '25' }}}, format='json')
    assert response.status_code == 400
    response = client_with_credentials.post(url, {'Location': {'Longitude': { 'Value': '25' }}}, format='json')
    assert response.status_code == 400

@pytest.mark.django_db
def test_ahj_geo_location__missing_location(client_with_credentials):
    url = reverse('ahj-geo-location')
    response = client_with_credentials.post(url)
    assert response.status_code == 400

@pytest.mark.django_db
def test_ahj_geo_location__invalid_location_ob_format(client_with_credentials):
    url = reverse('ahj-geo-location')
    response = client_with_credentials.post(url, {'Location': {'Latitude': '25', 'Longitude': '25'}}, format='json')
    assert response.status_code == 400

@pytest.mark.django_db
def test_ahj_geo_location__location_matches_ahj(list_of_ahjs, client_with_credentials, valid_location_ob):
    url = reverse('ahj-geo-location')
    response = client_with_credentials.post(url, {'Location': valid_location_ob}, format='json')
    assert len(response.data) == 1
    assert response.data[0]['AHJCode']['Value'] == 'UT-0681820'
    assert response.status_code == 200

@pytest.mark.django_db
def test_ahj_geo_location__location_does_not_match_ahj(list_of_ahjs, client_with_credentials):
    url = reverse('ahj-geo-location')
    response = client_with_credentials.post(url, {'Location': { 'Latitude': { 'Value': '90' }, 'Longitude': { 'Value': '90' }}}, format='json')
    assert len(response.data) == 0
    assert response.status_code == 200

@pytest.mark.django_db
def test_ahj_geo_location__search_array_does_not_have_ahj(list_of_ahjs, client_with_credentials, valid_location_ob):
    url = reverse('ahj-geo-location')
    response = client_with_credentials.post(url, { 'ahjs_to_search': ['8ac31936-ebfc-4713-8ca6-1646ae38353c'], 'Location': valid_location_ob}, format='json')
    assert len(response.data) == 0
    assert response.status_code == 200

@pytest.mark.django_db
def test_ahj_geo_location__search_array_has_ahj(list_of_ahjs, client_with_credentials, valid_location_ob):
    url = reverse('ahj-geo-location')
    response = client_with_credentials.post(url, { 'ahjs_to_search': ['78d2735b-b581-45ba-8cb6-2dea58596e97', '8ac31936-ebfc-4713-8ca6-1646ae38353c'], 'Location': valid_location_ob}, format='json')
    assert len(response.data) == 1
    assert response.status_code == 200

@pytest.mark.parametrize(
   'urlName, args', [
       ('ahj-public', { 'Location': {'Longitude': { 'Value': 'hello' }, 'Latitude': { 'Value': 'hello' }}}), # pass invalid args to each so early exit
       ('ahj-geo-address', {}),
       ('ahj-geo-location', { 'Latitude': { 'V': '25' }}),
   ]
)
@pytest.mark.django_db
def test_user_num_api_calls_updates(urlName, args, list_of_ahjs, generate_client_with_api_credentials, valid_location_ob):
    client = generate_client_with_api_credentials(Email='a@a.a')
    url = reverse(urlName)
    # call fails early, so it's expected that api call num is incremented at the start
    response = client.post(url, args, format='json')
    user = User.objects.get(Email='a@a.a')
    assert user.NumAPICalls == 1

@pytest.mark.django_db
def test_deactivate_expired_api_tokens(create_user_with_active_api_token):
    user = create_user_with_active_api_token()
    user.api_token.expires = timezone.now() - datetime.timedelta(days=1)
    user.api_token.save()
    views_ahjsearch_api.deactivate_expired_api_tokens()
    assert APIToken.objects.get(user=user).is_active is False
