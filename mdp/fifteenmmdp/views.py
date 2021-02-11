from django.shortcuts import render
import json
from django.core import serializers
import os
import zipfile
from django.conf import settings

# Create your views here.
from django.core.files import File


from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import AllMeterFilesSerializer

from .models import AllMeterFiles,NpcFile





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
    import os
    # print(os.getcwdb())
    # def path_to_dict(path):
    #     d = {'name': os.path.basename(path)}
    #     if os.path.isdir(path):
    #         d['type'] = "directory"
    #         d['children'] = [path_to_dict(os.path.join(path,x)) for x in os.listdir(path)]
    #     else:
    #         d['type'] = "file"
    #     return d

    # print(json.dumps(path_to_dict('./Test')))

    # listIWantToStore = json.dumps(path_to_dict('./media/dateFilter'))
 
    # AllMeterFiles.objects.filter(id = 1).update(dirStructure = json.dumps(listIWantToStore))

@csrf_exempt
def fetchMD(request):
    jsonDec = json.decoder.JSONDecoder()
    ml = jsonDec.decode(AllMeterFiles.objects.all())
    return(JsonResponse(ml))

@csrf_exempt
def getAllMeterData(request):
    AllMeterFiles_json = AllMeterFiles.objects.all()
    AllMeterFiles_json = serializers.serialize("json", AllMeterFiles.objects.all() , fields=('id','year' , 'month','zippedMeterFile','dirStructure'))
    # data = {"data": AllMeterFiles_json}
    # return JsonResponse(data)
    return HttpResponse(AllMeterFiles_json, content_type="text/json-comment-filtered")

@csrf_exempt
def getMeterData(request, meter_id):   # Data of single meter
    meterData = AllMeterFiles.objects.filter(id=int(meter_id))
    meterData_json = serializers.serialize("json", meterData , fields=('id','year' , 'month','zippedMeterFile','dirStructure'))
    # data = {"data": AllMeterFiles_json}
    # return JsonResponse(data)
    return HttpResponse(meterData_json, content_type="text/json-comment-filtered")

@csrf_exempt
def addNewMeterFile(request):
    print("I have request object")
    print(request.POST['year'])
    print(request.POST['month'])

    # print(request.POST['meterZippedFile'].name)
    year = request.POST['year']
    month = request.POST['month']
    meterZippedFile = request.FILES['meterZippedFile']

    meterData = AllMeterFiles.objects.create(year=year, month=month, zippedMeterFile = meterZippedFile )
    meterData.save()
    return HttpResponse(json.dumps({'id' : meterData.id, 'message': 'MeterFile added'}), content_type='application/json')



@csrf_exempt
def editNewMeterFile(request,meter_id):
    print("Edit : I have request object id :" + meter_id)

    print(request.POST['year'])
    print(request.POST['month'])

    # # print(request.POST['meterZippedFile'].name)

    # year = request.POST['year']
    # month = request.POST['month']
    # meterZippedFile = request.FILES['meterZippedFile']

    # meterData = AllMeterFiles.objects.create(year=year, month=month, zippedMeterFile = meterZippedFile )
    # meterData.save()
    # return HttpResponse(json.dumps({'id' : meterData.id, 'message': 'MeterFile added'}), content_type='application/json')



@csrf_exempt
def deleteNewMeterFile(request,meter_id):
    print(meter_id)
    AllMeterFiles.objects.get(id=int(meter_id)).delete()
    return HttpResponse({'message': 'Meter deleted'}, status=200)

@csrf_exempt
def unzipMeterData(request,meter_id):

    def dirJson(path0,nPath,_meterData):
        d = {'name': os.path.basename(nPath)}
        d['size'] = str("{0:.2f}".format((os.stat(path0).st_size / 1024)) + "KB")
        if os.path.isdir(path0):
            d['type'] = "folder"
            d['path'] = nPath
            d['files'] = [dirJson(os.path.join(path0, x),os.path.join(nPath, x),_meterData) for x in os.listdir(path0)]
        else:
            if(os.path.splitext(path0)[1] == '.npc') :
                print(os.path.basename(nPath))
                local_file = open(path0,"rb")  #Open file from path0 i.e. extracted first path.
                npcFileObject = NpcFile.objects.create(fileName = os.path.basename(nPath), filePath = nPath, meterFile = _meterData)
                npcFileObject.npcFile.save(os.path.basename(nPath),  File(local_file))
                npcFileObject.save()
                local_file.close()
                d['id'] = npcFileObject.id
                d['type'] = "file"
                d['path'] = nPath
            else : 
                pass
        return d




    print("meter_id")
    print(meter_id)
    meterData = AllMeterFiles.objects.get(id=meter_id)
    print(meterData.zippedMeterFile)
    zipFilePath = (os.path.join(settings.MEDIA_ROOT,str(meterData.zippedMeterFile)))
    npcFilesFolderPath = os.path.join(settings.MEDIA_ROOT,'meterFile',meterData.year,meterData.month,'NPC Files',os.path.basename(zipFilePath))
    print(os.path.splitext(zipFilePath))
    print(npcFilesFolderPath)
    print(os.path.splitext(npcFilesFolderPath))

    jsonOutput = dirJson(os.path.splitext(zipFilePath)[0],os.path.splitext(npcFilesFolderPath)[0],meterData)
    print(json.dumps(jsonOutput))
    AllMeterFiles.objects.filter(id = meter_id).update(dirStructure = json.dumps(jsonOutput))

    # with zipfile.ZipFile('fifteenmmdp/media/'+ str(meterData.zippedMeterFile), 'r') as zip_ref:
    #     zip_ref.extractall("fifteenmmdp/media/meterFile/"+ meterData.year + "/" + meterData.month)
    #     zip_ref.extractall("fifteenmmdp/media/meterFile/"+ meterData.year + "/" + meterData.month +"/NPC Files")



# def home(request):
# 	context={'file':filtered_Meter(request.user)}
# 	return render(request,'fiveminutemeter/home.html',context)



# relativePath = 'F1'
# outputFile = 'myOutput.json'
# currDir = os.getcwd()
# absPath = os.path.join(currDir,relativePath)
# print(currDir)
# # outjson = path_to_dict("D:\\mdp\\reference\\Amrit\\F1")
# outjson = path_to_dict(os.path.join(currDir,relativePath))

# with  open(os.path.join(currDir,outputFile), "w") as outfile:
#     json.dump(outjson,outfile,indent = 6)


    # def dirJson(path0,nPath,_meterData):
    #     d = {'name': os.path.basename(path0)}
    #     d['size'] = str("{0:.2f}".format((os.stat(path0).st_size / 1024)) + "KB")
    #     if os.path.isdir(path0):
    #         d['type'] = "folder"
    #         d['path'] = path0
    #         d['files'] = [dirJson(os.path.join(path0, x),_meterData) for x in os.listdir(path0)]
    #     else:
    #         if(os.path.splitext(path0)[1] == '.npc') :
    #             print(os.path.basename(path0))
    #             local_file = open(path0,"rb")
    #             # npcFileObject.npcFile.save(os.path.basename(path),  File(local_file))
    #             local_file.close()
    #             npcFileObject = NpcFile.objects.create(fileName = os.path.basename(path0), filePath = path0, meterFile = _meterData,npcFile = (os.path.basename(path0),  File(local_file)))
    #             npcFileObject.save()
    #             d['id'] = npcFileObject.id
    #             d['type'] = "file"
    #             d['path'] = path0
    #         else : 
    #             pass
    #     return d
