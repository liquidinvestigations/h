# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from h.schemas.base import JSONSchema, ValidationError
from h.models.group import (
    GROUP_NAME_MIN_LENGTH,
    GROUP_NAME_MAX_LENGTH,
    GROUP_DESCRIPTION_MAX_LENGTH,
)
from h.util.group import GROUPID_PATTERN, split_groupid
from h.i18n import TranslationString as _


class CreateGroupAPISchema(JSONSchema):
    """Validates a JSON payload for creating a new group via API"""
    schema = {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'minLength': GROUP_NAME_MIN_LENGTH,
                'maxLength': GROUP_NAME_MAX_LENGTH,
            },
            'description': {
                'type': 'string',
                'maxLength': GROUP_DESCRIPTION_MAX_LENGTH,
            },
            'groupid': {
                'type': 'string',
                'pattern': GROUPID_PATTERN,
            },
        },
        'required': [
            'name'
        ],
    }

    def __init__(self, group_authority=None, default_authority=None):
        """
        The ``group_authority`` and ``default_authority`` properties are used
        to validate a ``groupid`` field in data. If the caller does not intend
        to pass any data dicts that contain a ``groupid`` entry, these
        properties are optional.

        :param group_authority:   The authority that is be associated with the group
        :param default_authority: The service's default authority; if it is the same as
                                  ``group_authority``, then this is considered a
                                  "first-party" group
        """
        super(CreateGroupAPISchema, self).__init__()
        self.group_authority = group_authority
        self.default_authority = default_authority

    def validate(self, data):
        """
        Validate against the JSON schema and also valid any groupid present

        :raises ValidationError: if any part of validation fails
        """
        appstruct = super(CreateGroupAPISchema, self).validate(data)
        self._validate_groupid(appstruct)

        return appstruct

    def _validate_groupid(self, appstruct):
        """
        Validate the groupid property on appstruct and return its constituent
        parts if successful. A non-None groupid is only allowed if the authority
        the group will be associated with is not the default authority
        (i.e. third-party authority only).


        :raises ValidationError: * if ``groupid`` is not allowed for the applied authority
                                 * if ``groupid`` is not in proper format
                                 * if the ``authority`` part of ``groupid`` does not match
                                   the group (client) authority
        """
        groupid = appstruct.get('groupid', None)
        if groupid is None:
            return None

        if (self.group_authority is None) or (self.group_authority == self.default_authority):
            raise ValidationError(
                "{err_msg} '{authority}'".format(
                    err_msg=_("groupid may only be set on groups oustide of the default authority"),
                    authority=self.default_authority
                ))

        groupid_parts = split_groupid(groupid)

        if groupid_parts['authority'] != self.group_authority:
            raise ValidationError("{err_msg} '{groupid}'".format(
                err_msg=_("Invalid authority specified in groupid"),
                groupid=groupid))
