from decimal import Decimal

from ahj_app.models import Polygon, AHJLevelCode, User, Edit
from django.utils import timezone
from rest_framework import serializers

from fixtures import *
import pytest
import datetime

from ahj_app.serializers import OrangeButtonSerializer, EnumModelSerializer, PolygonSerializer, AHJSerializer, \
    LocationSerializer, AddressSerializer, AHJInspectionSerializer, ContactSerializer, \
    DocumentSubmissionMethodUseSerializer, EngineeringReviewRequirementSerializer, FeeStructureSerializer, \
    PermitIssueMethodUseSerializer, UserSerializer, EditSerializer, filter_related


@pytest.mark.django_db
def test_polygon_serializer(ahj_obj, mpoly_obj):
    polygon = Polygon.objects.create(Polygon=mpoly_obj, LandArea=1, WaterArea=1, InternalPLatitude=1, InternalPLongitude=1)
    ahj_obj.PolygonID = polygon
    ahj_obj.save()
    polygon_dict = PolygonSerializer(polygon).data
    properties = ['AHJID', 'LandArea', 'GEOID', 'InternalPLatitude', 'InternalPLongitude']
    assert all(prop in polygon_dict['properties'] for prop in properties)
    ahj_dict = AHJSerializer(ahj_obj).data
    polygon_dict = ahj_dict['Polygon']
    assert all(prop in polygon_dict['properties'] for prop in properties)
    assert polygon_dict['properties']['AHJID'] == ahj_dict['AHJID']['Value']


@pytest.mark.parametrize(
    'field_value', [
        None,
        'string',
        Decimal('1.00000000')
    ]
)
def test_orange_button_serializer(field_value):
    class Instance:
        field = field_value

    class Serializer(serializers.Serializer):
        field = OrangeButtonSerializer()

    result = Serializer(Instance()).data
    assert result == {'field': {'Value': field_value}}


@pytest.mark.django_db
def test_enum_model_serializer():
    class Instance:
        field = None

    instance = Instance()

    class Serializer(serializers.Serializer):
        field = EnumModelSerializer()

    instance.field = None
    result = Serializer(instance).data
    assert result == {'field': {'Value': ''}}
    instance.field = AHJLevelCode.objects.create(Value='040')
    result = Serializer(instance).data
    assert result == {'field': {'Value': '040'}}


@pytest.mark.parametrize(
    'serializer, model_name', [
        (AddressSerializer, 'Address'),
        (AHJSerializer, 'AHJ'),
        (AHJInspectionSerializer, 'AHJInspection'),
        (ContactSerializer, 'Contact'),
        (DocumentSubmissionMethodUseSerializer, 'DocumentSubmissionMethod'),
        (EngineeringReviewRequirementSerializer, 'EngineeringReviewRequirement'),
        (FeeStructureSerializer, 'FeeStructure'),
        (LocationSerializer, 'Location'),
        (PermitIssueMethodUseSerializer, 'PermitIssueMethod'),
        (UserSerializer, 'User')
    ]
)
@pytest.mark.django_db
def test_serializers__is_public_view(serializer, model_name, create_minimal_obj, create_user):
    if model_name == 'User':
        obj = create_user()
    else:
        obj = create_minimal_obj(model_name)
    if model_name in ['DocumentSubmissionMethod', 'PermitIssueMethod']:
        obj = create_obj_from_dict(f'AHJ{model_name}Use', {'AHJPK': create_minimal_obj('AHJ'), f'{model_name}ID': obj})
    result = serializer(obj, context={'is_public_view': True}).data
    assert all(field not in result for field in obj.__class__.SERIALIZER_EXCLUDED_FIELDS)


def test_user_serializer__is_public_view_defaults_to_true(create_user):
    user_dict = UserSerializer(create_user()).data
    assert all(field not in user_dict for field in User.SERIALIZER_EXCLUDED_FIELDS)


def test_ahj_serializer__get_polygon(create_minimal_obj, mpoly_obj):
    ahj = create_minimal_obj('AHJ')
    assert AHJSerializer(ahj).data['Polygon'] is None
    polygon = Polygon.objects.create(Polygon=mpoly_obj, LandArea=1, WaterArea=1, InternalPLatitude=1, InternalPLongitude=1)
    ahj.PolygonID = polygon
    ahj.save()
    assert AHJSerializer(ahj).data['Polygon'] is not None


def test_edit_serializer__drop_users(create_user, ahj_obj):
    user = create_user()
    edit_dict = {'ChangedBy': user, 'ApprovedBy': user,
                 'SourceTable': 'AHJ', 'SourceRow': ahj_obj.pk, 'SourceColumn': 'AHJName',
                 'OldValue': 'oldname', 'NewValue': 'newname',
                 'DateRequested': timezone.now(), 'DateEffective': timezone.now(),
                 'ReviewStatus': 'A', 'EditType': 'U', 'AHJPK': ahj_obj}
    edit = Edit.objects.create(**edit_dict)
    result = EditSerializer(edit, context={'drop_users': True}).data
    assert result['ChangedBy'] == user.Username
    assert result['ApprovedBy'] == user.Username


@pytest.mark.parametrize(
    'serializer, model_name', [
        (AddressSerializer, 'Address'),
        (AHJSerializer, 'AHJ'),
        (AHJInspectionSerializer, 'AHJInspection'),
        (ContactSerializer, 'Contact'),
        (EngineeringReviewRequirementSerializer, 'EngineeringReviewRequirement'),
        (FeeStructureSerializer, 'FeeStructure'),
        (LocationSerializer, 'Location')
    ]
)
def test_serializer_context__annotations(serializer, model_name, create_minimal_obj):
    obj = create_minimal_obj(model_name)
    data = serializer(obj, context={'annotations': True}).data
    assert len({'_model_name', '_id'}.intersection(data.keys())) == 2


@pytest.mark.django_db
def test_filter_related(ahj_obj, create_minimal_obj):
    num = 8  # multiple of 4
    for x in range(num):
        contact = create_minimal_obj('Contact')
        set_obj_field(contact, 'ParentTable', 'AHJ')
        set_obj_field(contact, 'ParentID', ahj_obj.AHJPK)
        if x < num / 4:
            set_obj_field(contact, Contact.RELATION_STATUS_FIELD, True)
        elif x >= num * 3 / 4:
            set_obj_field(contact, Contact.RELATION_STATUS_FIELD, False)
    filters = {'ParentTable': 'AHJ', 'ParentID': ahj_obj.AHJPK}
    result = filter_related(False, Contact, filters)
    assert result.count() == num * 3 / 4
    assert False not in result.values_list(Contact.RELATION_STATUS_FIELD, flat=True)
    result = filter_related(True, Contact, filters)
    assert result.count() == num / 4
    assert None not in result.values_list(Contact.RELATION_STATUS_FIELD, flat=True)
    assert False not in result.values_list(Contact.RELATION_STATUS_FIELD, flat=True)
