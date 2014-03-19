# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tables

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.images.images import views

from openstack_dashboard.dashboards.admin.images import forms
from openstack_dashboard.dashboards.admin.images \
    import tables as project_tables

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = project_tables.AdminImagesTable
    template_name = 'admin/images/index.html'

    def has_prev_data(self, table):
        return self._prev

    def has_more_data(self, table):
        return self._more

    def get_data(self):
        images = []
        filters = self.get_filters()
        prev_marker = self.request.GET.get(
            project_tables.AdminImagesTable._meta.prev_pagination_param, None)

        if prev_marker is not None:
            sort_dir = 'asc'
            marker = prev_marker
        else:
            sort_dir = 'desc'
            marker = self.request.GET.get(
                project_tables.AdminImagesTable._meta.pagination_param, None)
        try:
            images, self._more, self._prev = api.glance.image_list_detailed(
                self.request,
                marker=marker,
                paginate=True,
                filters=filters,
                sort_dir=sort_dir)

            if prev_marker is not None:
                images = sorted(images, key=lambda image:
                                getattr(image, 'created_at'), reverse=True)

        except Exception:
            self._prev = False
            self._more = False
            msg = _('Unable to retrieve image list.')
            exceptions.handle(self.request, msg)
        return images

    def get_filters(self):
        filters = {'is_public': None}
        filter_field = self.table.get_filter_field()
        filter_string = self.table.get_filter_string()
        filter_action = self.table._meta._filter_action
        if filter_field and filter_string and (
                filter_action.is_api_filter(filter_field)):
            if filter_field in ['size_min', 'size_max']:
                invalid_msg = ('API query is not valid and is ignored: %s=%s'
                               % (filter_field, filter_string))
                try:
                    filter_string = long(float(filter_string) * (1024 ** 2))
                    if filter_string >= 0:
                        filters[filter_field] = filter_string
                    else:
                        LOG.warning(invalid_msg)
                except ValueError:
                    LOG.warning(invalid_msg)
            else:
                filters[filter_field] = filter_string
        return filters


class CreateView(views.CreateView):
    template_name = 'admin/images/create.html'
    form_class = forms.AdminCreateImageForm
    success_url = reverse_lazy('horizon:admin:images:index')


class UpdateView(views.UpdateView):
    template_name = 'admin/images/update.html'
    form_class = forms.AdminUpdateImageForm
    success_url = reverse_lazy('horizon:admin:images:index')


class DetailView(views.DetailView):
    """Admin placeholder for image detail view."""
    pass
