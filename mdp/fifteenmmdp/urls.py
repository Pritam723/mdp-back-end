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
    # path('test/', views.test, name="test"),
    # path('addMasterData/', views.addMasterData, name="addMasterData"),
    # path('fetchMD/', views.fetchMD, name="fetchMD"),

    path('addNewMeterFile/', views.addNewMeterFile, name="addNewMeterFile"),
    path('getAllMeterData/', views.getAllMeterData, name="getAllMeterData"),
	path('getMeterData/<str:meter_id>', views.getMeterData, name = "getMeterData"),
	path('deleteNewMeterFile/<str:meter_id>', views.deleteNewMeterFile, name = "deleteNewMeterFile"),
	# path('editNewMeterFile/<str:meter_id>', views.editNewMeterFile, name = "editNewMeterFile"),
    
	path('getNPCData/<str:meter_id>', views.getNPCData, name ="getNPCData"),
	path('extract/<str:meter_id>', views.extract, name = "extract"),
	path('changeNPCFile/<str:meter_id>/<str:npc_id>', views.changeNPCFile, name ="changeNPCFile"),
	path('downloadNPCFile/<str:meter_id>/<str:npc_id>', views.downloadNPCFile, name ="downloadNPCFile"),

	
	path('merge/<str:meter_id>', views.merge, name = "merge"),
	path('getMergedFile/<str:meter_id>', views.getMergedFile, name ="getMergedFile"),
	path('downloadMergedFile/<str:mergedFile_id>', views.downloadMergedFile, name ="downloadMergedFile"),
	path('changeMergedFile/<str:mergedFile_id>', views.changeMergedFile, name ="changeMergedFile"),

	path('dateFilter/<str:meter_id>', views.dateFilter, name = "dateFilter"),
	path('getDateFilteredFile/<str:meter_id>', views.getDateFilteredFile, name ="getDateFilteredFile"),
	path('downloadDateFilteredFile/<str:dateFilteredFile_id>', views.downloadDateFilteredFile, name ="downloadDateFilteredFile"),
	path('changeDateFilteredFile/<str:dateFilteredFile_id>', views.changeDateFilteredFile, name ="changeDateFilteredFile"),
	path('downloadNrxFile/<str:meter_id>', views.downloadNrxFile, name ="downloadNrxFile"),

	path('validate/<str:meter_id>', views.validate, name = "validate"),
	path('getValidatedFile/<str:meter_id>', views.getValidatedFile, name ="getValidatedFile"),
	path('downloadValidatedFile/<str:validatedFile_id>', views.downloadValidatedFile, name ="downloadValidatedFile"),
	path('changeValidatedFile/<str:validatedFile_id>', views.changeValidatedFile, name ="changeValidatedFile"),

    path('getRealMeterMWHData/<str:meter_id>', views.getRealMeterMWHData, name ="getRealMeterMWHData"),
	path('realMeterMWH/<str:meter_id>', views.realMeterMWH, name = "realMeterMWH"),
	path('changeRealMeterMWHFile/<str:meter_id>/<str:realMeterMWH_id>', views.changeRealMeterMWHFile, name ="changeRealMeterMWHFile"),
	path('downloadRealMeterMWHFile/<str:meter_id>/<str:realMeterMWH_id>', views.downloadRealMeterMWHFile, name ="downloadRealMeterMWHFile"),
	path('downLoadFullRealMeterMWHFiles/<str:meter_id>', views.downLoadFullRealMeterMWHFiles, name ="downLoadFullRealMeterMWHFiles"),


	path('getFictMeterMWHData/<str:meter_id>', views.getFictMeterMWHData, name ="getFictMeterMWHData"),
	path('fictMeterMWH/<str:meter_id>', views.fictMeterMWH, name = "fictMeterMWH"),
	path('changeFictMeterMWHFile/<str:meter_id>/<str:fictMeterMWH_id>', views.changeFictMeterMWHFile, name ="changeFictMeterMWHFile"),
	path('downloadFictMeterMWHFile/<str:meter_id>/<str:fictMeterMWH_id>', views.downloadFictMeterMWHFile, name ="downloadFictMeterMWHFile"),
	path('downLoadFullFictMeterMWHFiles/<str:meter_id>', views.downLoadFullFictMeterMWHFiles, name ="downLoadFullFictMeterMWHFiles"),


	path('getFinalOutputData/<str:meter_id>', views.getFinalOutputData, name ="getFinalOutputData"),
	path('finalOutput/<str:meter_id>', views.finalOutput, name = "finalOutput"),
	path('changeFinalOutputFile/<str:meter_id>/<str:finalOutput_id>', views.changeFinalOutputFile, name ="changeFinalOutputFile"),
	path('downloadFinalOutputFile/<str:meter_id>/<str:finalOutput_id>', views.downloadFinalOutputFile, name ="downloadFinalOutputFile"),
	path('downLoadFullFinalOutputFiles/<str:meter_id>', views.downLoadFullFinalOutputFiles, name ="downLoadFullFinalOutputFiles"),
    
	path('getNecessaryFiles', views.getNecessaryFiles, name ="getNecessaryFiles"),

    url(r'^download/(?P<path>.*)$',serve,{'document_root':settings.MEDIA_ROOT}),

]
if settings.DEBUG:
	urlpatterns+=static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
	urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
