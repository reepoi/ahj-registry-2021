"""
This contains models for the Orange Button Authority Having Jurisdiction object definition.
In addition, there are models that support user account information, crowd-source editing,
and the Address/Location-to-AHJ search.
"""
import datetime

from django.apps import apps
from django.conf import settings
from .models_field_enums import *
from django.contrib.gis.db import models
from django.utils.timezone import now
import rest_framework.authtoken.models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from simple_history.models import HistoricalRecords

class AHJ(models.Model):
    AHJPK = models.AutoField(db_column='AHJPK', primary_key=True)
    AHJID = models.CharField(db_column='AHJID', unique=True, max_length=36)
    AHJCode = models.CharField(db_column='AHJCode', max_length=20, blank=True)
    AHJLevelCode = models.ForeignKey('AHJLevelCode', on_delete=models.DO_NOTHING, db_column='AHJLevelCode', null=True, blank=True)
    PolygonID = models.ForeignKey('Polygon', on_delete=models.DO_NOTHING, db_column='PolygonID', null=True, blank=True)
    AddressID = models.ForeignKey('Address', on_delete=models.DO_NOTHING, db_column='AddressID', null=True, blank=True)
    AHJName = models.CharField(db_column='AHJName', max_length=100)
    Description = models.CharField(db_column='Description', max_length=255, blank=True)
    DocumentSubmissionMethodNotes = models.CharField(db_column='DocumentSubmissionMethodNotes', max_length=255, blank=True)
    PermitIssueMethodNotes = models.CharField(db_column='PermitIssueMethodNotes', max_length=255, blank=True)
    EstimatedTurnaroundDays = models.IntegerField(db_column='EstimatedTurnaroundDays', null=True, blank=True)
    FileFolderURL = models.CharField(db_column='FileFolderURL', max_length=255, blank=True)
    URL = models.CharField(db_column='URL', max_length=2048, blank=True)
    BuildingCode = models.ForeignKey('BuildingCode', on_delete=models.DO_NOTHING, db_column='BuildingCode', null=True, blank=True)
    BuildingCodeNotes = models.CharField(db_column='BuildingCodeNotes', max_length=255, blank=True)
    ElectricCode = models.ForeignKey('ElectricCode', on_delete=models.DO_NOTHING, db_column='ElectricCode', null=True, blank=True)
    ElectricCodeNotes = models.CharField(db_column='ElectricCodeNotes', max_length=255, blank=True)
    FireCode = models.ForeignKey('FireCode', on_delete=models.DO_NOTHING, db_column='FireCode', null=True, blank=True)
    FireCodeNotes = models.CharField(db_column='FireCodeNotes', max_length=255, blank=True)
    ResidentialCode = models.ForeignKey('ResidentialCode', on_delete=models.DO_NOTHING, db_column='ResidentialCode', null=True, blank=True)
    ResidentialCodeNotes = models.CharField(db_column='ResidentialCodeNotes', max_length=255, blank=True)
    WindCode = models.ForeignKey('WindCode', on_delete=models.DO_NOTHING, db_column='WindCode', null=True, blank=True)
    WindCodeNotes = models.CharField(db_column='WindCodeNotes', max_length=255, blank=True)
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'AHJ'
        verbose_name = 'AHJ'
        verbose_name_plural = 'AHJs'

    SERIALIZER_EXCLUDED_FIELDS = ['Polygon', 'AHJPK', 'Comments']

class Comment(models.Model):
    """
    Stores comments made by users on the AHJPage.
    """
    CommentID = models.AutoField(db_column='CommentID', primary_key=True)
    UserID = models.ForeignKey('User', on_delete=models.DO_NOTHING, db_column='UserID')
    CommentText = models.TextField(db_column='CommentText', null=True, blank=True)
    AHJPK = models.IntegerField(db_column='AHJPK', null=True)
    Date = models.DateTimeField(db_column='Date', default=now)
    ReplyingTo = models.IntegerField(db_column='ReplyingTo', null=True)
    history = HistoricalRecords()

    def get_replies(self):
        return Comment.objects.filter(ReplyingTo=self.CommentID).order_by('-Date')

    class Meta:
        managed = True
        db_table = 'Comment'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

class Address(models.Model):
    AddressID = models.AutoField(db_column='AddressID', primary_key=True)
    LocationID = models.ForeignKey('Location', models.DO_NOTHING, db_column='LocationID', null=True)
    AddrLine1 = models.CharField(db_column='AddrLine1', max_length=100, blank=True)
    AddrLine2 = models.CharField(db_column='AddrLine2', max_length=100, blank=True)
    AddrLine3 = models.CharField(db_column='AddrLine3', max_length=100, blank=True)
    City = models.CharField(db_column='City', max_length=100, blank=True)
    Country = models.CharField(db_column='Country', max_length=100, blank=True)
    County = models.CharField(db_column='County', max_length=100, blank=True)
    StateProvince = models.CharField(db_column='StateProvince', max_length=100, blank=True)
    ZipPostalCode = models.CharField(db_column='ZipPostalCode', max_length=100, blank=True)
    Description = models.CharField(db_column='Description', max_length=255, blank=True)
    AddressType = models.ForeignKey('AddressType', on_delete=models.DO_NOTHING, db_column='AddressType', null=True)
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'Address'
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

    SERIALIZER_EXCLUDED_FIELDS = ['AddressID']

class Contact(models.Model):
    ParentTable = models.CharField(db_column='ParentTable', max_length=255, blank=True)
    ParentID = models.IntegerField(db_column='ParentID', null=True)
    ContactID = models.AutoField(db_column='ContactID', primary_key=True)
    AddressID = models.ForeignKey(Address, models.DO_NOTHING, db_column='AddressID', null=True)
    FirstName = models.CharField(db_column='FirstName', max_length=255, blank=True)
    MiddleName = models.CharField(db_column='MiddleName', max_length=255, blank=True)
    LastName = models.CharField(db_column='LastName', max_length=255, blank=True)
    HomePhone = models.CharField(db_column='HomePhone', max_length=31, blank=True)
    MobilePhone = models.CharField(db_column='MobilePhone', max_length=31, blank=True)
    WorkPhone = models.CharField(db_column='WorkPhone', max_length=31, blank=True)
    ContactType = models.ForeignKey('ContactType', on_delete=models.DO_NOTHING, db_column='ContactType', null=True)
    ContactTimezone = models.CharField(db_column='ContactTimezone', max_length=255, blank=True)
    Description = models.CharField(db_column='Description', max_length=255, blank=True)
    Email = models.CharField(db_column='Email', max_length=50, blank=True)
    Title = models.CharField(db_column='Title', max_length=255, blank=True)
    URL = models.CharField(db_column='URL', max_length=255, blank=True)
    PreferredContactMethod = models.ForeignKey('PreferredContactMethod', on_delete=models.DO_NOTHING, db_column='PreferredContactMethod', null=True)
    ContactStatus = models.BooleanField(db_column='ContactStatus', null=True)
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'Contact'
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        index_together = (('ParentTable', 'ParentID'),)

    SERIALIZER_EXCLUDED_FIELDS = ['ContactID', 'ContactStatus']

    def create_relation_to(self, to):
        if to.__class__.__name__ != 'AHJ' and to.__class__.__name__ != 'AHJInspection':
            raise ValueError('\'Contact\' cannot be related to \'{to_model}\''.format(to_model=to.__class__.__name__))
        self.ParentTable = to.__class__.__name__
        self.ParentID = to.pk
        self.ContactStatus = None
        self.save()
        return self

    RELATION_STATUS_FIELD = 'ContactStatus'


class AHJInspection(models.Model):
    InspectionID = models.AutoField(db_column='InspectionID', primary_key=True)
    AHJPK = models.ForeignKey(AHJ, models.DO_NOTHING, db_column='AHJPK')
    InspectionType = models.ForeignKey('InspectionType', on_delete=models.DO_NOTHING, db_column='InspectionType', null=True)
    AHJInspectionName = models.CharField(db_column='AHJInspectionName', max_length=255)
    AHJInspectionNotes = models.CharField(db_column='AHJInspectionNotes', max_length=255, blank=True)
    Description = models.CharField(db_column='Description', max_length=255, blank=True)
    FileFolderURL = models.CharField(db_column='FileFolderURL', max_length=255, blank=True)
    TechnicianRequired = models.BooleanField(db_column='TechnicianRequired', null=True)
    InspectionStatus = models.BooleanField(db_column='InspectionStatus', null=True)
    history = HistoricalRecords()

    def create_relation_to(self, to):
        if to.__class__.__name__ == 'AHJ':
            self.InspectionStatus = None
            return self
        else:
            raise ValueError('\'AHJInspection\' cannot be related to \'{to_model}\''.format(to_model=to.__class__.__name__))

    RELATION_STATUS_FIELD = 'InspectionStatus'

    class Meta:
        managed = True
        db_table = 'AHJInspection'
        verbose_name = 'AHJ Inspection'
        verbose_name_plural = 'AHJ Inspections'
        unique_together = (('AHJPK', 'AHJInspectionName'),)

    SERIALIZER_EXCLUDED_FIELDS = ['InspectionID', 'InspectionStatus']

class FeeStructure(models.Model):
    FeeStructurePK = models.AutoField(db_column='FeeStructurePK', primary_key=True)
    AHJPK = models.ForeignKey(AHJ, models.DO_NOTHING, db_column='AHJPK')
    FeeStructureID = models.CharField(db_column='FeeStructureID', max_length=36) # UUIDField
    FeeStructureName = models.CharField(db_column='FeeStructureName', unique=True, max_length=255)
    FeeStructureType = models.ForeignKey('FeeStructureType', on_delete=models.DO_NOTHING, db_column='FeeStructureType', null=True)
    Description = models.CharField(db_column='Description', max_length=255, blank=True)
    FeeStructureStatus = models.BooleanField(db_column='FeeStructureStatus', null=True)
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'FeeStructure'
        verbose_name = 'Fee Structure'
        verbose_name_plural = 'Fee Structures'
        unique_together = (('FeeStructureID', 'AHJPK'),)

    SERIALIZER_EXCLUDED_FIELDS = ['FeeStructurePK', 'FeeStructureStatus']

    def create_relation_to(self, to):
        if to.__class__.__name__ == 'AHJ':
            self.FeeStructureStatus = None
            return self
        else:
            raise ValueError('\'FeeStructure\' cannot be related to \'{to_model}\''.format(to_model=to.__class__.__name__))

    RELATION_STATUS_FIELD = 'FeeStructureStatus'

class Edit(models.Model):
    EditID = models.AutoField(db_column='EditID', primary_key=True)
    ChangedBy = models.ForeignKey('User', models.DO_NOTHING, db_column='ChangedBy', related_name='related_primary_edit')
    ApprovedBy = models.ForeignKey('User', models.DO_NOTHING, db_column='ApprovedBy', null=True, related_name='related_secondary_edit', blank=True,
                                   help_text="""Tracks whether a user under a SunSpec Alliance Membership. """
                                             """Note ``blank=True`` in addition to ``null=True`` is necessary to """
                                             """make it **not** required in the Django Admin User Change Form.""")
    AHJPK = models.ForeignKey('AHJ', models.DO_NOTHING, db_column='AHJPK', null=True)
    SourceTable = models.CharField(db_column='SourceTable', max_length=255)
    SourceColumn = models.CharField(db_column='SourceColumn', max_length=255)
    SourceRow = models.IntegerField(db_column='SourceRow')
    # status is P = pending, R = rejected, A = approved
    ReviewStatus = models.CharField(db_column='ReviewStatus', max_length=1, default='P')
    OldValue = models.CharField(db_column='OldValue', max_length=255, blank=True, null=True)
    NewValue = models.CharField(db_column='NewValue', max_length=255, blank=True, null=True)
    DateRequested = models.DateTimeField(db_column='DateRequested', db_index=True)
    DateEffective = models.DateTimeField(db_column='DateEffective', blank=True, null=True, db_index=True)
    IsApplied = models.BooleanField(db_column='IsApplied', default=False)
    # Edit type: A = addition, D = deletion, U = update
    EditType = models.CharField(db_column='EditType', max_length=1, default='U')
    DataSourceComment = models.CharField(db_column='DataSourceComment', max_length=255, blank=True)
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'Edit'
        verbose_name = 'Edit'
        verbose_name_plural = 'Edits'

    def get_edited_row(self):
        model = apps.get_model('ahj_app', self.SourceTable)
        row = model.objects.get(**{model._meta.pk.name: self.SourceRow})
        return row


class Location(models.Model):
    LocationID = models.AutoField(db_column='LocationID', primary_key=True)
    Altitude = models.DecimalField(db_column='Altitude', max_digits=15, decimal_places=6, null=True)
    Elevation = models.DecimalField(db_column='Elevation', max_digits=17, decimal_places=8, null=True)
    Latitude = models.DecimalField(db_column='Latitude', max_digits=10, decimal_places=8, null=True)
    Longitude = models.DecimalField(db_column='Longitude', max_digits=11, decimal_places=8, null=True)
    Description = models.CharField(db_column='Description', max_length=255, blank=True)
    LocationDeterminationMethod = models.ForeignKey('LocationDeterminationMethod', on_delete=models.DO_NOTHING, db_column='LocationDeterminationMethod', null=True)
    LocationType = models.ForeignKey('LocationType', on_delete=models.DO_NOTHING, db_column='LocationType', null=True)
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'Location'
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'

    SERIALIZER_EXCLUDED_FIELDS = ['LocationID']

class EngineeringReviewRequirement(models.Model):
    EngineeringReviewRequirementID = models.AutoField(db_column='EngineeringReviewRequirementID', primary_key=True)
    AHJPK = models.ForeignKey(AHJ, models.DO_NOTHING, db_column='AHJPK')
    Description = models.CharField(db_column='Description', max_length=255, blank=True)
    EngineeringReviewType = models.ForeignKey('EngineeringReviewType', on_delete=models.DO_NOTHING, db_column='EngineeringReviewType', null=True)
    RequirementLevel = models.ForeignKey('RequirementLevel', on_delete=models.DO_NOTHING, db_column='RequirementLevel', null=True)
    RequirementNotes = models.CharField(db_column='RequirementNotes', max_length=255, blank=True)
    StampType = models.ForeignKey('StampType', on_delete=models.DO_NOTHING, db_column='StampType', null=True)
    EngineeringReviewRequirementStatus = models.BooleanField(db_column='EngineeringReviewRequirementStatus', null=True)
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'EngineeringReviewRequirement'
        verbose_name = 'Engineering Review Requirement'
        verbose_name_plural = 'Engineering Review Requirements'

    SERIALIZER_EXCLUDED_FIELDS = ['EngineeringReviewRequirementID', 'EngineeringReviewRequirementStatus']

    def create_relation_to(self, to):
        if to.__class__.__name__ == 'AHJ':
            self.EngineeringReviewRequirementStatus = None
            return self
        else:
            raise ValueError('\'EngineeringReviewRequirement\' cannot be related to \'{to_model}\''.format(to_model=to.__class__.__name__))

    RELATION_STATUS_FIELD = 'EngineeringReviewRequirementStatus'

class DocumentSubmissionMethod(models.Model):
    DocumentSubmissionMethodID = models.AutoField(db_column='DocumentSubmissionMethodID', primary_key=True)
    Value = models.CharField(db_column='Value', choices=DOCUMENT_SUBMISSION_METHOD_CHOICES, unique=True, max_length=11)
    history = HistoricalRecords()

    def create_relation_to(self, to):
        status_fields = {
            'DocumentSubmissionMethodID': self,
            'MethodStatus': None
        }
        if to.__class__.__name__ == 'AHJ':
            status_fields['AHJPK'] = to
            return AHJDocumentSubmissionMethodUse.objects.create(**status_fields)
        else:
            raise ValueError('\'DocumentSubmissionMethod\' cannot be related to \'{to_model}\''.format(to_model=to.__class__.__name__))

    RELATION_STATUS_FIELD = 'MethodStatus'

    class Meta:
        verbose_name = 'Document Submission Method'
        verbose_name_plural = 'Document Submission Methods'

class AHJDocumentSubmissionMethodUse(models.Model):
    """
    Stores what DocumentSubmissionMethods an AHJ uses.
    """
    UseID = models.AutoField(db_column='UseID', primary_key=True)
    AHJPK = models.ForeignKey(AHJ, models.DO_NOTHING, db_column='AHJPK')
    DocumentSubmissionMethodID = models.ForeignKey('DocumentSubmissionMethod', models.DO_NOTHING, db_column='DocumentSubmissionMethodID')
    MethodStatus = models.BooleanField(db_column='MethodStatus', null=True)
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'AHJDocumentSubmissionMethodUse'
        verbose_name = 'AHJ Document Submission Method Use'
        verbose_name_plural = 'AHJ Document Submission Method Uses'
        unique_together = (('AHJPK', 'DocumentSubmissionMethodID'),)

    SERIALIZER_EXCLUDED_FIELDS = ['UseID', 'MethodStatus']

    def get_value(self):
        return self.DocumentSubmissionMethodID.Value

    RELATION_STATUS_FIELD = 'MethodStatus'

class PermitIssueMethod(models.Model):
    PermitIssueMethodID = models.AutoField(db_column='PermitIssueMethodID', primary_key=True)
    Value = models.CharField(db_column='Value', choices=PERMIT_ISSUE_METHOD_CHOICES, unique=True, max_length=11)
    history = HistoricalRecords()

    def create_relation_to(self, to):
        status_fields = {
            'PermitIssueMethodID': self,
            'MethodStatus': None
        }
        if to.__class__.__name__ == 'AHJ':
            status_fields['AHJPK'] = to
            return AHJPermitIssueMethodUse.objects.create(**status_fields)
        else:
            raise ValueError('\'PermitIssueMethod\' cannot be related to \'{to_model}\''.format(to_model=to.__class__.__name__))

    RELATION_STATUS_FIELD = 'MethodStatus'

    class Meta:
        verbose_name = 'Permit Issue Method'
        verbose_name_plural = 'Permit Issue Methods'

class AHJPermitIssueMethodUse(models.Model):
    """
    Stores what PermitIssueMethods an AHJ uses.
    """
    UseID = models.AutoField(db_column='UseID', primary_key=True)
    AHJPK = models.ForeignKey(AHJ, models.DO_NOTHING, db_column='AHJPK')
    PermitIssueMethodID = models.ForeignKey('PermitIssueMethod', models.DO_NOTHING, db_column='PermitIssueMethodID')
    MethodStatus = models.BooleanField(db_column='MethodStatus', null=True)
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'AHJPermitIssueMethodUse'
        verbose_name = 'AHJ Permit Issue Method Use'
        verbose_name_plural = 'AHJ Permit Issue Method Uses'
        unique_together = (('AHJPK', 'PermitIssueMethodID'),)

    SERIALIZER_EXCLUDED_FIELDS = ['UseID', 'MethodStatus']

    def get_value(self):
        return self.PermitIssueMethodID.Value

    RELATION_STATUS_FIELD = 'MethodStatus'

class Polygon(models.Model):
    PolygonID = models.AutoField(db_column='PolygonID', primary_key=True)
    Name = models.CharField(db_column='Name', max_length=100,
                            help_text="""Name of the jurisdiction the polygon represents. Census name: NAME.""")
    GEOID = models.CharField(db_column='GEOID', max_length=10,
                             help_text="""Geographic identifier for County, City, CountySubdivision, and State. """
                                       """``max_length=10`` to accommodate all different lengths of GEOID. Census name: GEOID.""")
    Polygon = models.MultiPolygonField(db_column='Polygon', help_text="""MySQL MultiPolygon of the jurisdiction. Census name: MULTIPOLYGON.""")
    LandArea = models.BigIntegerField(db_column='LandArea', help_text="""Land area of the jurisdiction. Census name: ALAND.""")
    WaterArea = models.BigIntegerField(db_column='WaterArea', help_text="""Water area of the jurisdiction. Census name: AWATER.""")
    InternalPLatitude = models.DecimalField(db_column='InternalPLatitude', max_digits=10, decimal_places=8,
                                            help_text="""Latitude of a coordinate within the area of the Polygon. Census name: INTPLAT.""")
    InternalPLongitude = models.DecimalField(db_column='InternalPLongitude', max_digits=11, decimal_places=8,
                                             help_text="""Longitude of a coordinate within the area of the Polygon. Census name: INTPLON.""")
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'Polygon'
        verbose_name = 'Polygon'
        verbose_name_plural = 'Polygons'

class StatePolygon(models.Model):
    PolygonID = models.OneToOneField(Polygon, models.DO_NOTHING, db_column='PolygonID', primary_key=True)
    FIPSCode = models.CharField(db_column='FIPSCode', max_length=2, help_text="""State FIPS code. Census name: STATEFP.""")
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'StatePolygon'
        verbose_name = 'State Polygon'
        verbose_name_plural = 'State Polygons'

class CountyPolygon(models.Model):
    PolygonID = models.OneToOneField('Polygon', models.DO_NOTHING, db_column='PolygonID', primary_key=True)
    StatePolygonID = models.ForeignKey('StatePolygon', models.DO_NOTHING, db_column='StatePolygonID')
    LSAreaCodeName = models.CharField(db_column='LSAreaCodeName', max_length=100,
                                      help_text="""NAMELSAD: Name concatenated with the Legal/Statistical Area Description (LSAD) Description. """
                                                """This field is matched to the original AHJNames from NREL to pair CityPolygons to their AHJs.""")
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'CountyPolygon'
        verbose_name = 'County Polygon'
        verbose_name_plural = 'County Polygons'

class CityPolygon(models.Model):
    PolygonID = models.OneToOneField('Polygon', models.DO_NOTHING, db_column='PolygonID', primary_key=True)
    StatePolygonID = models.ForeignKey('StatePolygon', models.DO_NOTHING, db_column='StatePolygonID')
    LSAreaCodeName = models.CharField(db_column='LSAreaCodeName', max_length=100,
                                      help_text="""Name concatenated with the Legal/Statistical Area Description (LSAD) Description. Census name: NAMELSAD. """
                                                """This field is matched to the original AHJNames from NREL to pair CityPolygons to their AHJs.""")
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'CityPolygon'
        verbose_name = 'City Polygon'
        verbose_name_plural = 'City Polygons'

class CountySubdivisionPolygon(models.Model):
    PolygonID = models.OneToOneField('Polygon', models.DO_NOTHING, db_column='PolygonID', primary_key=True)
    StatePolygonID = models.ForeignKey('StatePolygon', models.DO_NOTHING, db_column='StatePolygonID')
    LSAreaCodeName = models.CharField(db_column='LSAreaCodeName', max_length=100,
                                      help_text="""Name concatenated with the Legal/Statistical Area Description (LSAD) Description. Census name: NAMELSAD. """
                                                """This field is matched to the original AHJNames from NREL to pair CityPolygons to their AHJs.""")
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'CountySubdivisionPolygon'
        verbose_name = 'County Subdivision Polygon'
        verbose_name_plural = 'County Subdivision Polygons'

class SunSpecAllianceMember(models.Model):
    """
    Stores SunSpec Alliance member organizations and their names.
    """
    MemberID = models.AutoField(db_column='MemberID', primary_key=True)
    MemberName = models.CharField(db_column='MemberName', max_length=254, unique=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'SunSpec Alliance Member'
        verbose_name_plural = 'SunSpec Alliance Members'

class SunSpecAllianceMemberDomain(models.Model):
    """
    Stores the domain name of a SunSpec Alliance member.
    """
    DomainID = models.AutoField(db_column='DomainID', primary_key=True)
    MemberID = models.ForeignKey(SunSpecAllianceMember, models.DO_NOTHING, db_column='MemberID')
    Domain = models.CharField(max_length=254, db_column='Domain')
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'SunSpec Alliance Member Domain'
        verbose_name_plural = 'SunSpec Alliance Member Domains'

class AHJOfficeDomain(models.Model):
    """
    Stores the domain name of an AHJ office.
    """
    DomainID = models.AutoField(db_column='DomainID', primary_key=True)
    AHJID = models.ForeignKey(AHJ, models.DO_NOTHING, db_column='AHJID')
    Domain = models.CharField(max_length=254, db_column='Domain')
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'AHJ Office Domain'
        verbose_name_plural = 'AHJ Office Domains'

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, **extra_fields):
        extra_fields['Email'] = self.normalize_email(extra_fields['Email'])
        user_fields = {field.name for field in self.model._meta.get_fields()}
        user_dict = {k: v for k, v in extra_fields.items() if k in user_fields}
        contact_fields = {field.name for field in Contact._meta.get_fields()}
        contact_dict = {k: v for k, v in extra_fields.items() if k in contact_fields}
        contact_dict['AddressID'] = Address.objects.create(LocationID=Location.objects.create())
        user_dict['SignUpDate'] = datetime.date.today()
        user_dict['ContactID'] = Contact.objects.create(**contact_dict)
        password = user_dict.pop('password')
        user = self.model(**user_dict)
        user.set_password(password)
        user.save(using=self._db)
        APIToken.objects.create(user=user, is_active=False)
        return user

    def create_superuser(self, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(**extra_fields)


class User(AbstractBaseUser):
    UserID = models.AutoField(db_column='UserID', primary_key=True)
    ContactID = models.ForeignKey(Contact, models.DO_NOTHING, db_column='ContactID', null=True)
    Username = models.CharField(db_column='Username', unique=True, max_length=254)
    password = models.CharField(max_length=128)
    Email = models.CharField(db_column='Email', unique=True, max_length=254)
    MemberID = models.ForeignKey(SunSpecAllianceMember, models.DO_NOTHING, db_column='MemberID', null=True, blank=True,
                                 help_text="""Tracks whether a user under a SunSpec Alliance Membership. """
                                           """Note ``blank=True`` in addition to ``null=True`` is necessary to """
                                           """make it **not** required in the Django Admin User Change Form.""")
    is_staff = models.BooleanField(db_column='IsStaff', default=False)
    is_active = models.BooleanField(db_column='IsActive', default=False)
    is_superuser = models.BooleanField(db_column='IsSuperuser', default=False)
    SignUpDate = models.DateField(db_column='SignUpDate', blank=True)
    PersonalBio = models.CharField(db_column='PersonalBio', max_length=255, blank=True)
    URL = models.CharField(db_column='URL', max_length=255, blank=True, null=True)
    CompanyAffiliation = models.CharField(db_column='CompanyAffiliation', max_length=255, blank=True)
    Photo = models.CharField(db_column='Photo', max_length=255, blank=True, null=True)
    NumAPICalls = models.IntegerField(db_column='NumAPICalls', default=0)
    SecurityLevel = models.IntegerField(db_column='SecurityLevel', default=3)
    history = HistoricalRecords()

    USERNAME_FIELD = 'Email'
    SERIALIZER_EXCLUDED_FIELDS = ['APIToken', 'is_superuser', 'MaintainedAHJs']
    objects = UserManager()

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, core):
        return self.is_superuser

    def get_email_field_name(self=None):
        return "Email"
    
    def get_num_submitted_edits(self):
        return Edit.objects.filter(ChangedBy=self).count()
    
    def get_num_accepted_edits(self):
        return Edit.objects.filter(ChangedBy=self).filter(ReviewStatus='A').count()

    def get_maintained_ahjs(self):
        return AHJUserMaintains.objects.filter(UserID=self, MaintainerStatus=True).values_list('AHJPK__AHJPK')

    def is_ahj_official(self):
        return self.get_maintained_ahjs().count() > 0

    def get_API_token(self):
        return APIToken.objects.filter(user=self).first()

    class Meta:
        db_table = 'User'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        managed = True

class AHJUserMaintains(models.Model):
    """
    Stores what AHJs a user is an AHJ official of.
    """
    MaintainerID = models.AutoField(db_column='MaintainerID', primary_key=True)
    AHJPK = models.ForeignKey(AHJ, models.DO_NOTHING, db_column='AHJPK')
    UserID = models.ForeignKey(User, models.DO_NOTHING, db_column='UserID')
    MaintainerStatus = models.BooleanField(db_column='MaintainerStatus')
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'AHJUserMaintains'
        verbose_name = 'AHJ User Maintains'
        verbose_name_plural = 'AHJ User Maintains'
        unique_together = (('AHJPK', 'UserID'),)

class WebpageToken(rest_framework.authtoken.models.Token):
    """
    A token controlled by the Django library `Djoser`_.
    This token is generated when a user logs into the AHJ Registry client app, and is deleted when they log out.

    .. _Djoser: https://djoser.readthedocs.io/en/latest/getting_started.html
    """
    key = models.CharField(max_length=40, primary_key=True, serialize=False, verbose_name='Key')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Created')
    user = models.OneToOneField(on_delete=models.CASCADE, related_name='webpage_token', to=settings.AUTH_USER_MODEL, verbose_name='User')
    history = HistoricalRecords()
    def get_user(self):
        return self.user

    class Meta:
        verbose_name = 'Webpage Token'
        verbose_name_plural = 'Webpage Tokens'

    def __str__(self):
        return f'WebpageToken({self.key})'

class APIToken(rest_framework.authtoken.models.Token):
    key = models.CharField(max_length=40, primary_key=True, serialize=False, verbose_name='Key')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Created')
    expires = models.DateTimeField(verbose_name='Expires', default=None, null=True)
    user = models.OneToOneField(on_delete=models.CASCADE, related_name='api_token', to=settings.AUTH_USER_MODEL, verbose_name='User')
    is_active = models.BooleanField(default=False)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'API Token'
        verbose_name_plural = 'API Tokens'

    def __str__(self):
        return f'APIToken({self.key})'

class StateTemp(models.Model):
    """
    Used by usf.py to help upload shapefiles into the database.
    This temporarily stores state shapefile data to next be copied into the Polygon and StatePolygon tables.
    """
    GEOID = models.CharField(max_length=2,
                             help_text="""Geographic identifier for County, City, CountySubdivision, and State.""")
    NAME = models.CharField(max_length=100,
                            help_text="""Name of the jurisdiction the polygon represents.""")
    ALAND = models.BigIntegerField(help_text="""Land area of the jurisdiction.""")
    AWATER = models.BigIntegerField(help_text="""Water area of the jurisdiction.""")
    INTPTLAT = models.CharField(max_length=11,
                                help_text="""Latitude of a coordinate within the area of the Polygon.""")
    INTPTLON = models.CharField(max_length=12,
                                help_text="""Longitude of a coordinate within the area of the Polygon.""")
    history = HistoricalRecords()

    mpoly = models.MultiPolygonField(help_text="""MySQL MultiPolygon of the jurisdiction.""")

    def __str__(self):
        return self.NAME

    class Meta:
        verbose_name = 'Temporary State Polygon'
        verbose_name_plural = 'Temporary State Polygons'

# Census county shapefile model
class CountyTemp(models.Model):
    """
    Used by usf.py to help upload shapefiles into the database.
    This temporarily stores county shapefile data to next be copied into the Polygon and CountyPolygon tables.
    """
    STATEFP = models.CharField(max_length=2, help_text="""State FIPS code.""")
    GEOID = models.CharField(max_length=5,
                             help_text="""Geographic identifier for County, City, CountySubdivision, and State.""")
    NAME = models.CharField(max_length=100,
                            help_text="""Name of the jurisdiction the polygon represents.""")
    NAMELSAD = models.CharField(max_length=100,
                                help_text="""Name concatenated with the Legal/Statistical Area Description (LSAD) Description.""")
    ALAND = models.BigIntegerField(help_text="""Land area of the jurisdiction.""")
    AWATER = models.BigIntegerField(help_text="""Water area of the jurisdiction.""")
    INTPTLAT = models.CharField(max_length=11,
                                help_text="""Latitude of a coordinate within the area of the Polygon.""")
    INTPTLON = models.CharField(max_length=12,
                                help_text="""Longitude of a coordinate within the area of the Polygon.""")
    history = HistoricalRecords()

    mpoly = models.MultiPolygonField(help_text="""MySQL MultiPolygon of the jurisdiction.""")

    def __str__(self):
        return self.NAMELSAD

    class Meta:
        verbose_name = 'Temporary County Polygon'
        verbose_name_plural = 'Temporary County Polygons'

# Census cousub shapefile model
class CousubTemp(models.Model):
    """
    Used by usf.py to help upload shapefiles into the database.
    This temporarily stores county subdivision shapefile data to next be copied into the Polygon and CountySubdivisionPolygon tables.
    """
    STATEFP = models.CharField(max_length=2, help_text="""State FIPS code.""")
    GEOID = models.CharField(max_length=10,
                             help_text="""Geographic identifier for County, City, CountySubdivision, and State.""")
    NAME = models.CharField(max_length=100,
                            help_text="""Name of the jurisdiction the polygon represents.""")
    NAMELSAD = models.CharField(max_length=100,
                                help_text="""Name concatenated with the Legal/Statistical Area Description (LSAD) Description.""")
    ALAND = models.BigIntegerField(help_text="""Land area of the jurisdiction.""")
    AWATER = models.BigIntegerField(help_text="""Water area of the jurisdiction.""")
    INTPTLAT = models.CharField(max_length=11,
                                help_text="""Latitude of a coordinate within the area of the Polygon.""")
    INTPTLON = models.CharField(max_length=12,
                                help_text="""Longitude of a coordinate within the area of the Polygon.""")
    history = HistoricalRecords()

    mpoly = models.MultiPolygonField(help_text="""MySQL MultiPolygon of the jurisdiction.""")

    def __str__(self):
        return self.NAMELSAD

    class Meta:
        verbose_name = 'Temporary Cousub Polygon'
        verbose_name_plural = 'Temporary Cousub Polygons'

# Census place shapefile model
class CityTemp(models.Model):
    """
    Used by usf.py to help upload shapefiles into the database.
    This temporarily stores city shapefile data to next be copied into the Polygon and CityPolygon tables.
    """
    STATEFP = models.CharField(max_length=2, help_text="""State FIPS code.""")
    GEOID = models.CharField(max_length=7,
                             help_text="""Geographic identifier for County, City, CountySubdivision, and State.""")
    NAME = models.CharField(max_length=100,
                            help_text="""Name of the jurisdiction the polygon represents.""")
    NAMELSAD = models.CharField(max_length=100,
                                help_text="""Name concatenated with the Legal/Statistical Area Description (LSAD) Description.""")
    ALAND = models.BigIntegerField(help_text="""Land area of the jurisdiction.""")
    AWATER = models.BigIntegerField(help_text="""Water area of the jurisdiction.""")
    INTPTLAT = models.CharField(max_length=11,
                                help_text="""Latitude of a coordinate within the area of the Polygon.""")
    INTPTLON = models.CharField(max_length=12,
                                help_text="""Longitude of a coordinate within the area of the Polygon.""")
    history = HistoricalRecords()

    mpoly = models.MultiPolygonField(help_text="""MySQL MultiPolygon of the jurisdiction.""")

    def __str__(self):
        return self.NAMELSAD

    class Meta:
        verbose_name = 'Temporary City Polygon'
        verbose_name_plural = 'Temporary City Polygons'

class AHJCensusName(models.Model):
    """
    Stores the names and states of AHJ jurisdictions provided by National Renewable Energy Laboratory (NREL).
    This list can be found on the `Orange Button Google Drive`_ in the AHJ Registry/AHJ Data Uploads/NREL directory.

    .. _Orange Button Google Drive: https://drive.google.com/drive/u/1/folders/12vSNzJmEnTzVMArF5ADVzmLX93SlkpFs
    """
    AHJPK = models.OneToOneField('AHJ', on_delete=models.DO_NOTHING, db_column='AHJPK', primary_key=True)
    AHJCensusName = models.CharField(db_column='AHJCensusName', max_length=100)
    StateProvince = models.CharField(db_column='StateProvince', max_length=2)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'AHJ Census Name'
        verbose_name_plural = 'AHJ Census Names'
