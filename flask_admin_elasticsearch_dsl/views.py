from elasticsearch_dsl import Integer, Date

from flask_admin.model.base import BaseModelView

from flask_admin_elasticsearch_dsl.forms import (
    get_form, AdminDocumentConverter,
)


class DocumentView(BaseModelView):
    can_create = False
    can_edit = True
    can_delete = False

    sortable_doc_fields = [Integer, Date]
    model_form_converter = AdminDocumentConverter

    def __init__(self, document, session,
                 name=None, category=None, endpoint=None, url=None,
                 static_folder=None, menu_class_name=None, menu_icon_type=None,
                 menu_icon_value=None):
        self.session = session
        super(DocumentView, self).__init__(document, name, category, endpoint,
                                        url, static_folder,
                                        menu_class_name=menu_class_name,
                                        menu_icon_type=menu_icon_type,
                                        menu_icon_value=menu_icon_value)

    def scaffold_list_columns(self):
        return list(self.model._doc_type.mapping)

    def scaffold_sortable_columns(self):
        def is_sortable_doc_field(field_name):
            prop = self.model._doc_type.mapping.properties[field_name]
            return type(prop) in self.sortable_doc_fields

        sortable_columns = filter(
            is_sortable_doc_field, self.model._doc_type.mapping)
        return list(sortable_columns)

    def scaffold_form(self):
        converter = self.model_form_converter(self.session, self)
        return get_form(self.model, converter)

    def get_list(self, page, sort_field, sort_desc, search, filters,
                 page_size=None):
        query = self.model.search(using=self.session)

        if page_size is None:
            page_size = self.page_size

        if page is not None and page_size is not None:
            start = page*page_size
            query = query.extra(from_=start, size=page_size)

        if sort_field is None:
            order = self._get_default_order()
            if order is not None:
                sort_field, sort_desc = order

        if sort_field is not None:
            sort = "".join(['-' if sort_desc else '', sort_field])
            query = query.sort(sort)

        return query.count(), list(query)

    def get_one(self, document_id):
        return self.model.get(id=document_id, using=self.session)

    def get_pk_value(self, model):
        return model.meta.id
