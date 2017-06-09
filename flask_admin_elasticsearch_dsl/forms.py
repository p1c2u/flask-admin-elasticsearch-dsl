from elasticsearch_dsl import Integer, Date, Boolean
from wtforms import fields

from flask_admin.form import BaseForm
from flask_admin.model.form import ModelConverterBase


def get_form(document, converter, base_class=BaseForm):
    field_dict = {}
    for field_name in document._doc_type.mapping:
        field = converter.convert(document, field_name)
        if field is not None:
            field_dict[field_name] = field
    return type(document.__name__ + 'Form', (base_class, ), field_dict)


class AdminDocumentConverter(ModelConverterBase):
    """
        Elasticsearch DSL document to form converter
    """
    def __init__(self, session, view):
        super(AdminDocumentConverter, self).__init__()

        self.session = session
        self.view = view

    def convert(self, document, field_name):
        prop = document._doc_type.mapping.properties[field_name]
        prop_type = type(prop)
        if prop_type == Boolean:
            return fields.BooleanField()
        if prop_type == Date:
            return fields.DateTimeField()
        return fields.StringField()
