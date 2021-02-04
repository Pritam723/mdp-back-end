from . import views
from django.urls import path,include







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

	# path('task-list/', views.taskList, name="task-list"),
	# path('task-detail/<str:pk>/', views.taskDetail, name="task-detail"),
	# path('task-create/', views.taskCreate, name="task-create"),

	# path('task-update/<str:pk>/', views.taskUpdate, name="task-update"),
	# path('task-delete/<str:pk>/', views.taskDelete, name="task-delete"),
]