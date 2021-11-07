from django.urls import path
from django.views.generic.base import TemplateView
from . import views

urlpatterns = [ 
    path('manage', views.ManageLogs.as_view()),
    path('graph/<int:id>/', views.graph_example),
    path('logs', views.LogsJsonView.as_view()),
    path('select_comparisons',TemplateView.as_view(template_name='select_comparisons.html')),
    path('select_logs',views.SelectLogs.as_view()),
    path('compare', views.CompareLogs.as_view()),
    path('json/compare', views.CompareLogsJson.as_view())
]

