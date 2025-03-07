# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""URLs."""

from django.urls import path
from machado.history.views import AuthenticatedUserActions, AdminUserActions


urlpatterns = [
    #path('', AuthenticatedUserActions.as_view({'post': 'create', 'get': 'listMyHistory'}), name='authenticated_history_functions'),
    path('', AuthenticatedUserActions.as_view({'get': 'listMyHistory'}), name='authenticated_history_functions'),
    path('all', AdminUserActions.as_view({'get': 'listAllHistory'}), name='admin_history_functions'),
]
