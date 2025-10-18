from django.urls import path
from . import parse_views
from . import optimizer_views

urlpatterns = [
    path('dataParse/', parse_views.parseViews.as_view(), name='parse_views'),
    path('optimize/', optimizer_views.optimizerviews.as_view(), name='optimizer_views'),
]