from . import views
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import url
from django.views.static import serve






# urlpatterns = [
#     path('', views.index, name='index'),
# ]


urlpatterns = [
	path('', views.apiOverview, name="api-overview"),
    path('test/', views.test, name="test"),
    path('addMasterData/', views.addMasterData, name="addMasterData"),
    path('fetchMD/', views.fetchMD, name="fetchMD"),
    path('addNewMeterFile/', views.addNewMeterFile, name="addNewMeterFile"),
    path('getAllMeterData/', views.getAllMeterData, name="getAllMeterData"),
	path('deleteNewMeterFile/<str:meter_id>', views.deleteNewMeterFile, name = "deleteNewMeterFile"),
	path('editNewMeterFile/<str:meter_id>', views.editNewMeterFile, name = "editNewMeterFile"),
	path('unzipMeterData/<str:meter_id>', views.unzipMeterData, name = "unzipMeterData"),
	path('getMeterData/<str:meter_id>', views.getMeterData, name = "getMeterData"),

    url(r'^download/(?P<path>.*)$',serve,{'document_root':settings.MEDIA_ROOT}),


	# path('task-list/', views.taskList, name="task-list"),
	# path('task-detail/<str:pk>/', views.taskDetail, name="task-detail"),
	# path('task-create/', views.taskCreate, name="task-create"),

	# path('task-update/<str:pk>/', views.taskUpdate, name="task-update"),
	# path('task-delete/<str:pk>/', views.taskDelete, name="task-delete"),
]
if settings.DEBUG:
	urlpatterns+=static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
	urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
