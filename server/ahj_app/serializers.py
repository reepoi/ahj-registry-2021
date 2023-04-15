from collections import OrderedDict

from djoser.compat import get_user_email, get_user_email_field_name
from django.conf import settings
from django.db import connection
from rest_framework import serializers
from rest_framework_gis import serializers as geo_serializers
from djoser.serializers import UserCreateSerializer
from .models import *
from .utils import get_enum_value_row_else_null


def filter_related(is_public_view, model, filters):
    """
    Returns a queryset of a model with RELATION_STATUS_FIELD defined and considering
    is_public_view to include those with RELATION_STATUS_FIELD != True or not.
    For example, filtering Contacts for when is_public_view=True will only include
    Contacts whose ContactStatus=True; otherwise, it includes ContactStatus!=False.
    """
    queryset = model.objects.filter(**filters)
    status_field = model.RELATION_STATUS_FIELD
    if is_public_view:
        return queryset.filter(**{status_field: True})
    return queryset.exclude(**{status_field: False})


def filter_excluded_fields(serializer_instance, serializer_model):
    """
    Removes fields to be serialized by a serializer instance
    that are in the serializer's model's SERIALIZER_EXCLUDED_FIELDS.
    """
    for field in serializer_model.SERIALIZER_EXCLUDED_FIELDS:
        if field in serializer_instance.fields:
            serializer_instance.fields.pop(field)


def add_instance_annotations(serializer_instance, serializer_model):
    model_name = serializers.CharField(source='__class__.__name__')
    model_id = serializers.IntegerField(source=serializer_model._meta.pk.name)
    serializer_instance.fields['_model_name'] = model_name
    serializer_instance.fields['_id'] = model_id


class PolygonSerializer(geo_serializers.GeoFeatureModelSerializer):
    """
    Class to serialize Polygon objects into GeoJSON format
    plus extra properties in the properties section of
    the GeoJSON
    """
    AHJID = serializers.SerializerMethodField()

    class Meta:
        model = Polygon
        geo_field = 'Polygon'
        id_field = False
        fields = ['AHJID', 'LandArea', 'GEOID', 'InternalPLatitude', 'InternalPLongitude']

    def get_AHJID(self, instance):
        return self.context.get('AHJID', '')


class OrangeButtonSerializer(serializers.Field):
    """
    Custom serializer to add the Orange Button primitives to each field.
    Below is example JSON:
    
    .. code-block:: json

        {
            "<field_name>": {
                "Value": "<value>"
            }
        }

    Currently, only Orange Button's **Value** primitive is added.
    """
    def get_attribute(self, instance):
        """
        Overridden method for correctly adding
        Orange Button primitives even when the
        field's value is null.
        Otherwise, this class' to_representation
        will not be called by the calling serializer.
        """
        attribute = super().get_attribute(instance)
        if attribute is None:
            return {'Value': None}
        else:
            return attribute

    def to_representation(self, value):
        if type(value) is dict and 'Value' in value and value['Value'] is None:
            return value
        ob_obj = {'Value': value}
        return ob_obj

class EnumModelSerializer(serializers.Serializer):
    Value = serializers.CharField()

    def get_attribute(self, instance):
        attribute = super().get_attribute(instance)
        if attribute is None:
            return {'Value': ''}
        else:
            return attribute

    def to_representation(self, value):
        if type(value) is dict and 'Value' in value and value['Value'] == '':
            return value
        return super().to_representation(value)


class FeeStructureSerializer(serializers.Serializer):
    """
    Serializes Orange Button FeeStructure object to OrderedDict
    """
    FeeStructurePK = OrangeButtonSerializer()
    FeeStructureID = OrangeButtonSerializer()
    FeeStructureName = OrangeButtonSerializer()
    FeeStructureType = EnumModelSerializer()
    Description = OrangeButtonSerializer()
    FeeStructureStatus = OrangeButtonSerializer()

    def to_representation(self, feestructure):
        """
        Returns an OrderedDict representing an FeeStructure object
        Note not every AHJ has every child object.
        If 'is_public_view' is True, will not serialize fields
        that are not meant for public api users.
        """
        if self.context.get('is_public_view', False):
            filter_excluded_fields(self, FeeStructure)
        if self.context.get('annotations', False):
            add_instance_annotations(self, FeeStructure)
        return super().to_representation(feestructure)


class LocationSerializer(serializers.Serializer):
    """
    Serializes Orange Button Location object to OrderedDict
    """
    LocationID = OrangeButtonSerializer()
    Altitude = OrangeButtonSerializer()
    Elevation = OrangeButtonSerializer()
    Latitude = OrangeButtonSerializer()
    Longitude = OrangeButtonSerializer()
    Description = OrangeButtonSerializer()
    LocationDeterminationMethod = EnumModelSerializer()
    LocationType = EnumModelSerializer()

    def to_representation(self, location):
        """
        Returns an OrderedDict representing an Location object
        Note not every AHJ has every child object.
        If 'is_public_view' is True, will not serialize fields
        that are not meant for public api users.
        """
        if self.context.get('is_public_view', False):
            filter_excluded_fields(self, Location)
        if self.context.get('annotations', False):
            add_instance_annotations(self, Location)
        return super().to_representation(location)


class AddressSerializer(serializers.Serializer):
    """
    Serializes Orange Button Address object to OrderedDict
    """
    AddressID = OrangeButtonSerializer()
    AddrLine1 = OrangeButtonSerializer()
    AddrLine2 = OrangeButtonSerializer()
    AddrLine3 = OrangeButtonSerializer()
    City = OrangeButtonSerializer()
    Country = OrangeButtonSerializer()
    County = OrangeButtonSerializer()
    StateProvince = OrangeButtonSerializer()
    ZipPostalCode = OrangeButtonSerializer()
    Description = OrangeButtonSerializer()
    AddressType = EnumModelSerializer()
    Location = LocationSerializer(source='LocationID')

    def to_representation(self, address):
        """
        Returns an OrderedDict representing an Address object
        Note not every AHJ has every child object.
        If 'is_public_view' is True, will not serialize fields
        that are not meant for public api users.
        """
        if self.context.get('is_public_view', False):
            filter_excluded_fields(self, Address)
        if self.context.get('annotations', False):
            add_instance_annotations(self, Address)
        return super().to_representation(address)


class ContactSerializer(serializers.Serializer):
    """
    Serializes Orange Button Contact object to OrderedDict
    """
    ContactID = OrangeButtonSerializer()
    FirstName = OrangeButtonSerializer()
    MiddleName = OrangeButtonSerializer()
    LastName = OrangeButtonSerializer()
    HomePhone = OrangeButtonSerializer()
    MobilePhone = OrangeButtonSerializer()
    WorkPhone = OrangeButtonSerializer()
    ContactType = EnumModelSerializer()
    ContactTimezone = OrangeButtonSerializer()
    Description = OrangeButtonSerializer()
    Email = OrangeButtonSerializer()
    Title = OrangeButtonSerializer()
    URL = OrangeButtonSerializer()
    PreferredContactMethod = EnumModelSerializer()
    Address = AddressSerializer(source='AddressID')
    ContactStatus = OrangeButtonSerializer()

    def to_representation(self, contact):
        """
        Returns an OrderedDict representing an Contact object
        Note not every AHJ has every child object.
        If 'is_public_view' is True, will not serialize fields
        that are not meant for public api users.
        """
        if self.context.get('is_public_view', False):
            filter_excluded_fields(self, Contact)
        if self.context.get('annotations', False):
            add_instance_annotations(self, Contact)
        return super().to_representation(contact)


class RecursiveField(serializers.Serializer):
    """
    Serializer that calls the caller serializer on the value
    of the field that was passed to it.
    Used for serializing Comments
    """
    def to_representation(self, value):
        """
        Calls the caller serializer that called this serializer
        """
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class APITokenSerializer(serializers.Serializer):
    """
    Serializes APIToken to OrderedDict
    """
    auth_token = serializers.CharField(source='key')
    is_active = serializers.BooleanField()
    expires = serializers.DateTimeField()


class UserSerializer(serializers.Serializer):
    """
    Serializes User to OrderedDict
    """
    UserID = serializers.IntegerField(read_only=True)
    ContactID = ContactSerializer()
    Username = serializers.CharField()
    Email = serializers.CharField()
    PersonalBio = serializers.CharField()
    CompanyAffiliation = serializers.CharField()
    Photo = serializers.CharField()
    NumAPICalls = serializers.IntegerField()
    SignUpDate = serializers.DateField()
    AcceptedEdits = serializers.IntegerField(source='get_num_accepted_edits')
    SubmittedEdits = serializers.IntegerField(source='get_num_submitted_edits')
    MaintainedAHJs = serializers.ListField(source='get_maintained_ahjs')
    APIToken = APITokenSerializer(source='get_API_token')
    is_superuser = serializers.BooleanField()

    def to_representation(self, user):
        """
        Returns an OrderedDict representing an User object
        Note not every AHJ has every child object.
        If 'is_public_view' is True, will not serialize fields
        that are not meant for public api users. Unlike other
        serializers, the default is True to passively prevent
        sensitive data being serialized when it's not needed.
        """
        if self.context.get('is_public_view', True):
            filter_excluded_fields(self, User)
        return super().to_representation(user)


class UserCreateSerializer(UserCreateSerializer):
    """
    Serializes User to Ordered Dict.
    Used when a new user is created.
    """
    FirstName = serializers.CharField()
    MiddleName = serializers.CharField(allow_blank=True)
    LastName = serializers.CharField()
    Title = serializers.CharField(allow_blank=True)
    WorkPhone = serializers.CharField(allow_blank=True)
    PreferredContactMethod = serializers.CharField(allow_blank=True)
    ContactTimezone = serializers.CharField(allow_blank=True)

    def validate(self, attrs):
        contact_fields = {field.name for field in Contact._meta.get_fields()}
        pcm = get_enum_value_row_else_null('PreferredContactMethod', attrs['PreferredContactMethod'])
        if pcm is None:
            attrs.pop('PreferredContactMethod')
        else:
            attrs['PreferredContactMethod'] = pcm
        user_dict = OrderedDict({k: v for k, v in attrs.items() if k not in contact_fields})
        super().validate(user_dict)
        return attrs

    def to_representation(self, user):
        return UserSerializer(user).data

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('UserID',
                  'ContactID',
                  'Username',
                  'password',
                  'Email',
                  'is_staff',
                  'is_active',
                  'SignUpDate',
                  'PersonalBio',
                  'URL',
                  'CompanyAffiliation',
                  'Photo',
                  'SecurityLevel',
                  'NumAPICalls',
                  'FirstName',
                  'MiddleName',
                  'LastName',
                  'Title',
                  'WorkPhone',
                  'PreferredContactMethod',
                  'ContactTimezone')


class CommentSerializer(serializers.Serializer):
    """
    Serializes Comment to OrderedDict.
    """
    CommentID = OrangeButtonSerializer()
    User = UserSerializer(source='UserID')
    CommentText = OrangeButtonSerializer()
    Date = OrangeButtonSerializer()
    Replies = RecursiveField(source='get_replies', many=True)


class DocumentSubmissionMethodUseSerializer(serializers.Serializer):
    """
    Serializes Orange Button DocumentSubmissionMethod object value to OrderedDict
    """
    UseID = serializers.IntegerField()
    Value = serializers.CharField(source='get_value')
    MethodStatus = serializers.BooleanField()

    def to_representation(self, dsmu):
        """
        Returns an OrderedDict representing an DocumentSubmissionMethod object
        Note not every AHJ has every child object.
        If 'is_public_view' is True, will not serialize fields
        that are not meant for public api users.
        """
        if self.context.get('is_public_view', False):
            filter_excluded_fields(self, AHJDocumentSubmissionMethodUse)
        return super().to_representation(dsmu)

class PermitIssueMethodUseSerializer(serializers.Serializer):
    """
    Serializes Orange Button PermitIssueMethod object value to OrderedDict
    """
    UseID = serializers.IntegerField()
    Value = serializers.CharField(source='get_value')
    MethodStatus = serializers.BooleanField()

    def to_representation(self, pimu):
        """
        Returns an OrderedDict representing an PermitIssueMethod object
        Note not every AHJ has every child object.
        If 'is_public_view' is True, will not serialize fields
        that are not meant for public api users.
        """
        if self.context.get('is_public_view', False):
            filter_excluded_fields(self, AHJPermitIssueMethodUse)
        return super().to_representation(pimu)

class AHJInspectionSerializer(serializers.Serializer):
    """
    Serializes Orange Button AHJInspection object
    """
    InspectionID = OrangeButtonSerializer()
    InspectionType = EnumModelSerializer()
    AHJInspectionName = OrangeButtonSerializer()
    AHJInspectionNotes = OrangeButtonSerializer()
    Description = OrangeButtonSerializer()
    FileFolderURL = OrangeButtonSerializer()
    TechnicianRequired = OrangeButtonSerializer()
    InspectionStatus = OrangeButtonSerializer()
    Contacts = serializers.SerializerMethodField()

    def to_representation(self, inspection):
        """
        Returns an OrderedDict representing an AHJInspection object
        Note not every AHJ has every child object.
        If 'is_public_view' is True, will not serialize fields
        that are not meant for public api users.
        """
        if self.context.get('is_public_view', False):
            filter_excluded_fields(self, AHJInspection)
        if self.context.get('annotations', False):
            add_instance_annotations(self, AHJInspection)
        return super().to_representation(inspection)

    def get_Contacts(self, instance):
        queryset = filter_related(self.context.get('is_public_view', False), Contact, {'ParentTable': 'AHJInspection', 'ParentID': instance.InspectionID})
        return ContactSerializer(queryset, many=True, context=self.context).data


class EngineeringReviewRequirementSerializer(serializers.Serializer):
    """
    Serializes Orange Button EngineeringReviewRequirement object to OrderedDict
    """
    EngineeringReviewRequirementID = OrangeButtonSerializer()
    Description = OrangeButtonSerializer()
    EngineeringReviewType = EnumModelSerializer()
    RequirementLevel = EnumModelSerializer()
    RequirementNotes = OrangeButtonSerializer()
    StampType = EnumModelSerializer()
    EngineeringReviewRequirementStatus = OrangeButtonSerializer()

    def to_representation(self, err):
        """
        Returns an OrderedDict representing an EngineeringReviewRequirement object to OrderedDict
        Note not every AHJ has every child object.
        If 'is_public_view' is True, will not serialize fields
        that are not meant for public api users.
        """
        if self.context.get('is_public_view', False):
            filter_excluded_fields(self, EngineeringReviewRequirement)
        if self.context.get('annotations', False):
            add_instance_annotations(self, EngineeringReviewRequirement)
        return super().to_representation(err)


class AHJSerializer(serializers.Serializer):
    """
    Serializes Orange Button AHJ object
    """
    AHJPK = OrangeButtonSerializer()
    AHJID = OrangeButtonSerializer()
    AHJCode = OrangeButtonSerializer()
    AHJLevelCode = EnumModelSerializer()
    AHJName = OrangeButtonSerializer()
    Description = OrangeButtonSerializer()
    DocumentSubmissionMethodNotes = OrangeButtonSerializer()
    PermitIssueMethodNotes = OrangeButtonSerializer()
    EstimatedTurnaroundDays = OrangeButtonSerializer()
    FileFolderURL = OrangeButtonSerializer()
    URL = OrangeButtonSerializer()
    BuildingCode = EnumModelSerializer()
    BuildingCodeNotes = OrangeButtonSerializer()
    ElectricCode = EnumModelSerializer()
    ElectricCodeNotes = OrangeButtonSerializer()
    FireCode = EnumModelSerializer()
    FireCodeNotes = OrangeButtonSerializer()
    ResidentialCode = EnumModelSerializer()
    ResidentialCodeNotes = OrangeButtonSerializer()
    WindCode = EnumModelSerializer()
    WindCodeNotes = OrangeButtonSerializer()
    Address = AddressSerializer(source='AddressID')
    Contacts = serializers.SerializerMethodField()
    Polygon = serializers.SerializerMethodField()
    Comments = serializers.SerializerMethodField()
    AHJInspections = serializers.SerializerMethodField()
    DocumentSubmissionMethods = serializers.SerializerMethodField()
    PermitIssueMethods = serializers.SerializerMethodField()
    EngineeringReviewRequirements = serializers.SerializerMethodField()
    FeeStructures = serializers.SerializerMethodField()

    def to_representation(self, ahj):
        """
        Returns an OrderedDict representing an AHJ object
        Note not every AHJ has every child object.
        If 'is_public_view' is True, will not serialize fields
        that are not meant for public api users.
        """
        if self.context.get('is_public_view', False):
            filter_excluded_fields(self, AHJ)
        if self.context.get('annotations', False):
            add_instance_annotations(self, AHJ)
        return super().to_representation(ahj)

    def get_Polygon(self, instance):
        """
        Helper method to serialize the polygon associated with an AHJ
        """
        if instance.PolygonID is None:
            return None
        return PolygonSerializer(instance.PolygonID, context={'AHJID': instance.AHJID}).data

    def get_AHJInspections(self, instance):
        queryset = filter_related(self.context.get('is_public_view', False), AHJInspection, {'AHJPK': instance.AHJPK})
        return AHJInspectionSerializer(queryset, many=True, context=self.context).data

    def get_Contacts(self, instance):
        queryset = filter_related(self.context.get('is_public_view', False), Contact, {'ParentTable': 'AHJ', 'ParentID': instance.AHJPK})
        return ContactSerializer(queryset, many=True, context=self.context).data

    def get_Comments(self, instance):
        queryset = Comment.objects.filter(AHJPK=instance.AHJPK).order_by('-Date')
        return CommentSerializer(queryset, many=True).data

    def get_DocumentSubmissionMethods(self, instance):
        queryset = filter_related(self.context.get('is_public_view', False), AHJDocumentSubmissionMethodUse, {'AHJPK': instance.AHJPK})
        return DocumentSubmissionMethodUseSerializer(queryset, many=True, context=self.context).data

    def get_EngineeringReviewRequirements(self, instance):
        queryset = filter_related(self.context.get('is_public_view', False), EngineeringReviewRequirement, {'AHJPK': instance.AHJPK})
        return EngineeringReviewRequirementSerializer(queryset, many=True, context=self.context).data

    def get_FeeStructures(self, instance):
        queryset = filter_related(self.context.get('is_public_view', False), FeeStructure, {'AHJPK': instance.AHJPK})
        return FeeStructureSerializer(queryset, many=True, context=self.context).data

    def get_PermitIssueMethods(self, instance):
        queryset = filter_related(self.context.get('is_public_view', False), AHJPermitIssueMethodUse, {'AHJPK': instance.AHJPK})
        return PermitIssueMethodUseSerializer(queryset, many=True, context=self.context).data


class EditSerializer(serializers.Serializer):
    """
    Serializes edits for the webpage AHJPage.
    """
    EditID = serializers.IntegerField(read_only=True)
    ChangedBy = UserSerializer()
    ApprovedBy = UserSerializer()
    AHJPK = serializers.IntegerField(source='AHJPK.AHJPK')
    SourceTable = serializers.CharField()
    SourceColumn = serializers.CharField()
    SourceRow = serializers.IntegerField()
    ReviewStatus = serializers.CharField()
    OldValue = serializers.CharField(read_only=True)
    NewValue = serializers.CharField()
    DateRequested = serializers.DateTimeField(read_only=True)
    DateEffective = serializers.DateTimeField(read_only=True)
    EditType = serializers.CharField()
    DataSourceComment = serializers.CharField()

    def to_representation(self, edit):
        if self.context.get('drop_users', False):
            """
            This gives the option for callers of the serializer to only serialize the username of the user.
            """
            self.fields['ChangedBy'] = serializers.CharField(source='ChangedBy.Username')
            if edit.ApprovedBy is None:
                self.fields['ApprovedBy'] = UserSerializer()
            else:
                self.fields['ApprovedBy'] = serializers.CharField(source='ApprovedBy.Username')
        return super().to_representation(edit)


class WebpageTokenSerializer(serializers.Serializer):
    """
    Serializes webpage token and user info when a user logs
    into the webpage.
    """
    auth_token = serializers.CharField(source='key')
    User = UserSerializer(source='get_user')


# Serializer used in Djoser's password reset endpoint. 
class UserFunctionsMixin:
    def get_user(self):
        try:
            user = User._default_manager.get(
                **{self.email_field: self.data.get(self.email_field, "")},
            )
            if user.has_usable_password():
                return user
        except User.DoesNotExist:
            pass
        if (
            settings.PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND
            or settings.USERNAME_RESET_SHOW_EMAIL_NOT_FOUND
        ):
            self.fail("email_not_found")

# Serializer used in Djoser's password reset endpoint
class SendEmailResetSerializer(serializers.Serializer, UserFunctionsMixin):
    default_error_messages = {
        "email_not_found": "User with given email does not exist."
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.email_field = get_user_email_field_name(User)
        self.fields[self.email_field] = serializers.EmailField()
