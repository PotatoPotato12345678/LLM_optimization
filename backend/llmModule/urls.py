from django.urls import path

from . import ED_views
from . import EE_views

urlpatterns = [
    path('ed/', ED_views.ED.as_view(), name='ed'),
    path('ee/', EE_views.EE.as_view(), name='ee'),
]