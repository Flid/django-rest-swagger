# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import rest_framework_swagger as rfs
from .compat import import_string
from formencode.api import NoDefault


def get_class_form_args(method, view_class, version):
    return _process_form(view_class.form_class)



def _split_docstring(docstring):
    """
    Parse docstring, search
    """
    split_lines = trim_docstring(docstring).split('\n')

    try:
        index = map(unicode.strip, split_lines).index('---')
    except ValueError:
        return '\n'.join(split_lines), None

    return '\n'.join(split_lines[:index]), '\n'.join(split_lines[index + 1:])


FIELD_TYPE_MAP = {
    b'Number': b'integer',
    b'StringBool': b'boolean',
    b'JSONValidator': b'json',
    b'Set': b'list',
    b'URL': b'url',
    b'OneOf': b'choice',
    b'OrderingValidator': b'choice',
}


def _update_description(field_info, to_add):
    descr = field_info.get('description') or ''
    descr += ' ' if descr else ''
    field_info['description'] = descr + to_add


def get_field_specific_data(field_info, field):
    field_class_name = field.__class__.__name__

    if field_class_name == b'OneOf':
        field_info[b'enum'] = field.list

    elif field_class_name == b'OrderingValidator':
        options = []
        for item in field.options:
            options.append(item)
            options.append('-' + item)

        field_info[b'enum'] = options

    elif field_class_name == b'CommaSeparatedSet':
        _update_description(
            field_info,
            'Acceptable values: {%s}' % ', '.join(field.allowed_values),
        )


def _get_field_type(field):
    return FIELD_TYPE_MAP.get(field.__class__.__name__, b'string')


def _get_field_description(field):
    if hasattr(field, b'get_description'):
        return field.get_description()

    return field.description or getattr(field, b'default_description', '')


def _get_default_value(field):
    if field.if_missing is NoDefault:
        return

    return field.if_missing


def _process_form(form):
    params = []

    for field_name, field in form.fields.iteritems():
        field_info = {
            b'name': field_name,
            b'description': _get_field_description(field),
            b'required': field.if_missing is NoDefault,
            b'type': _get_field_type(field),
            b'paramType': b'query',
        }

        default_value = _get_default_value(field)
        if default_value:
            # None is not allowed here
            field_info[b'defaultValue'] = default_value

        get_field_specific_data(field_info, field)

        params.append(field_info)

    return params
