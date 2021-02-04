from django.shortcuts import render

# Create your views here.


from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import AllMeterFilesSerializer

from .models import AllMeterFiles

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@api_view(['GET'])
def apiOverview(request):
	api_urls = {
		'List':'/task-list/',
		'Detail View':'/task-detail/<str:pk>/',
		'Create':'/task-create/',
		'Update':'/task-update/<str:pk>/',
		'Delete':'/task-delete/<str:pk>/',
		}

	return Response(api_urls)

@api_view(['GET'])
def test(request):
    print("I am printing")
    return HttpResponse("I am test")

def addMasterData(request):
    import json
    import os
    print(os.getcwdb())
    def path_to_dict(path):
        d = {'name': os.path.basename(path)}
        if os.path.isdir(path):
            d['type'] = "directory"
            d['children'] = [path_to_dict(os.path.join(path,x)) for x in os.listdir(path)]
        else:
            d['type'] = "file"
        return d

    print(json.dumps(path_to_dict('./Test')))

    listIWantToStore = json.dumps(path_to_dict('./media/dateFilter'))
 
    AllMeterFiles.objects.filter(id = 1).update(dirStructure = json.dumps(listIWantToStore))

@csrf_exempt
def fetchMD(request):
    import json
    import os
    jsonDec = json.decoder.JSONDecoder()
    ml = jsonDec.decode(AllMeterFiles.objects.all())
    return(JsonResponse(ml))


@csrf_exempt
def addNewMeterFile(request):
    print("I have request object")
    print(request.POST['year'])
    print(request.POST['month'])

    # print(request.POST['meterZippedFile'].name)
    year = request.POST['year']
    month = request.POST['month']
    meterZippedFile = request.FILES['meterZippedFile']

    AllMeterFiles.objects.create(year=year, month=month, zippedMeterFile = meterZippedFile )
    return HttpResponse({'message': 'AllMeterFiles created'}, status=200)

@csrf_exempt
def getAllMeterData(request):
    from django.core import serializers
    AllMeterFiles_json = AllMeterFiles.objects.all()
    AllMeterFiles_json = serializers.serialize("json", AllMeterFiles.objects.all() , fields=('id','year' , 'month','zippedMeterFile'))
    # data = {"data": AllMeterFiles_json}
    # return JsonResponse(data)
    return HttpResponse(AllMeterFiles_json, content_type="text/json-comment-filtered")
