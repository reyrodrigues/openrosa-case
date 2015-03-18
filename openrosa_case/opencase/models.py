from uuid import uuid4
import datetime
import base64
import os
from django.db import models

CASE_FORMAT = (
    ('plain', 'Plain'),
    ('date', 'Date'),
    ('time-ago', 'Time Since or Until Date'),
    ('phone', 'Phone Number'),
    ('enum', 'ID Mapping'),
    ('late-flag', 'Late Flag'),
    ('invisible', 'Search Only'),
    ('address', 'Address (Android/CloudCare)'),
)

END_OF_FORM = (
    ('default', 'Home Screen'),
    ('module', 'Module'),
    ('previous_screen', 'Previous Screen'),
)
CASE_TYPE = (
    ('none', 'Does not use cases'),
    ('open', 'Registers a new case'),
    ('update', 'Updates or closes a case'),
    ('open-other', 'Registers a case (different module)'),
)


class Application(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    version = models.IntegerField(default=1)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.id:
            self.slug = self.name

        return super(Application, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                             update_fields=update_fields)

    def __unicode__(self):
        return self.name


class Module(models.Model):
    application = models.ForeignKey(Application, related_name='modules')

    index = models.PositiveIntegerField(null=True, default=0)
    name = models.CharField(max_length=100, blank=True, null=True)
    in_root = models.BooleanField(default=False)

    icon_xpath = models.CharField(max_length=200, blank=True, null=True)
    audio_xpath = models.CharField(max_length=200, blank=True, null=True)

    # case props
    case_type = models.CharField(max_length=100, blank=True, null=True)
    case_label = models.CharField(max_length=100, blank=True, null=True)

    case_menu_item = models.BooleanField(default=False)
    case_menu_item_label = models.CharField(max_length=100, blank=True, null=True)

    """
    Select Parent and Parent case is to allow the users to select from a list of parent cases before proceding for the child case
    """
    case_select_parent = models.BooleanField(default=False)
    case_parent_case = models.ForeignKey('self', blank=True, null=True, related_name='child_cases')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        if not self.id:
            if self.application:
                self.index = max([f.id for f in self.application.modules.all()] or [0]) + 1

        return super(Module, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                        update_fields=update_fields)

    def __unicode__(self):
        return self.name


class ModuleDisplayItem(models.Model):
    module = models.ForeignKey(Module, null=False, related_name='case_list_items')
    type = models.CharField(max_length=20, choices=(("case_short", "List"), ("case_long", "Details")))
    property = models.CharField(max_length=200, null=True, blank=True)
    label = models.CharField(max_length=200, null=True, blank=True)
    format = models.CharField(max_length=20, blank=True, null=True, choices=CASE_FORMAT)


class Form(models.Model):
    index = models.PositiveIntegerField(null=True, default=0)
    namespace = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    form_url = models.CharField(max_length=200, blank=True, null=True)
    submission_url = models.CharField(max_length=200, blank=True, null=True)
    icon_xpath = models.CharField(max_length=200, blank=True, null=True)
    audio_xpath = models.CharField(max_length=200, blank=True, null=True)

    display_condition = models.CharField(max_length=300, blank=True, null=True)

    end_of_form = models.CharField(max_length=20, blank=True, null=True, choices=END_OF_FORM)
    auto_capture_location = models.BooleanField(default=False)
    case_action = models.CharField(max_length=20, blank=True, null=True, choices=CASE_TYPE)

    close_case = models.BooleanField(default=False)

    module = models.ForeignKey(Module, null=True, related_name='forms')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        if not self.id:
            if self.module:
                self.index = max([f.id for f in self.module.forms.all()] or [0]) + 1
            self.namespace = str(uuid4())

        return super(Form, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                      update_fields=update_fields)

    def __unicode__(self):
        return "{} - {} - {}".format(self.module.application.name, self.module.index, self.index)


class FormCase(models.Model):
    form = models.ForeignKey(Form, related_name="cases")
    case_module = models.ForeignKey(Module, null=True, blank=True)
    case_filter = models.CharField(max_length=200, blank=True, null=True)

    def __unicode__(self):
        return "{} - {}".format((self.case_module or self.form.module).case_type, self.form.case_action)


class FormCaseMapping(models.Model):
    form_case = models.ForeignKey(FormCase, related_name='mapping')
    direction = models.IntegerField(blank=True, default=1, null=True, choices=((1, "From Case"), (2, "To Case")))
    origin = models.CharField(max_length=500, blank=True, null=True)
    destination = models.CharField(max_length=100, blank=True, null=True)


class ApplicationGroup(models.Model):
    application = models.ForeignKey(Application, related_name="groups")
    uuid = models.CharField(max_length=64, blank=True)
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.id:
            self.uuid = str(uuid4())

        return super(ApplicationGroup, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                                  update_fields=update_fields)


class ApplicationUser(models.Model):
    application = models.ForeignKey(Application, related_name="users")
    uuid = models.CharField(max_length=64, blank=True)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    group = models.ForeignKey(ApplicationGroup, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)

    def __unicode__(self):
        return self.username

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.id:
            self.uuid = str(uuid4())

        return super(ApplicationUser, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                                 update_fields=update_fields)


class ApplicationKey(models.Model):
    application = models.ForeignKey(Application, related_name="keys")
    uuid = models.CharField(max_length=64, blank=True)
    valid = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField()
    key = models.CharField(max_length=100)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.id:
            self.uuid = str(uuid4())
            self.expires = (self.valid or datetime.datetime.now()) + datetime.timedelta(2 * 365 / 12)
            self.key = str(base64.b64encode(os.urandom(32)))

        return super(ApplicationKey, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                                update_fields=update_fields)

