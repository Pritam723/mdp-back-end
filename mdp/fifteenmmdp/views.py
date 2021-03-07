from django.shortcuts import render
import json
from django.core import serializers
import os
import zipfile
from django.conf import settings
from datetime import datetime
import shutil

# Create your views here.
from django.core.files import File


from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response
# from .serializers import AllMeterFilesSerializer

from .models import AllMeterFiles,NpcFile,MergedFile,DateFilteredFile,ValidatedFile,RealMeterMWHFile,FictMeterMWHFile,FinalOutputFile
from .extract import dirJsonNPC
from .merge import mergeNPCs
from .dateFilter import dateFilterMergedFile
from .validate import validateFile
from .realMeterMWH import createRealMeterMWH
from .fictMeterMWH import createFictMeterMWH
from .finalOutput import createFinalOutput

# from .extract import extractMeterFile
from .supportingFunctions import *
from django.core.files.storage import FileSystemStorage

class OverwriteStorage(FileSystemStorage):
    def get_valid_name(self, name):
            # return get_valid_filename(name)
            return name
    def get_available_name(self, name,max_length=None):
        if self.exists(name):
            print(name)
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


######################### Testing ##########################################################################
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

####################### Zipped Meter Data ####################################################################
@csrf_exempt
def getAllMeterData(request):
    AllMeterFiles_json = AllMeterFiles.objects.all()
    AllMeterFiles_json = serializers.serialize("json", AllMeterFiles.objects.all())
    # data = {"data": AllMeterFiles_json}
    # return JsonResponse(data)
    return HttpResponse(AllMeterFiles_json, content_type="text/json-comment-filtered")

@csrf_exempt
def getMeterData(request, meter_id):   # Data of single meter
    meterData = AllMeterFiles.objects.filter(id=int(meter_id))
    meterData_json = serializers.serialize("json", meterData)
    # data = {"data": AllMeterFiles_json}
    # return JsonResponse(data)
    return HttpResponse(meterData_json, content_type="text/json-comment-filtered")

@csrf_exempt
def addNewMeterFile(request):
    print("I have request object")
    print(request.POST['year'])
    print(request.POST['month'])
    print(request.POST['startDate'])
    print(request.POST['endDate'])
    print(datetime.strptime(request.POST['startDate'], "%d-%m-%Y"))
    print(datetime.strptime(request.POST['endDate'], "%d-%m-%Y"))

    # print(request.POST['meterZippedFile'].name)

    year = request.POST['year']
    month = request.POST['month']
    startDate = datetime.strptime(request.POST['startDate'], "%d-%m-%Y")
    endDate = datetime.strptime(request.POST['endDate'], "%d-%m-%Y")
    meterZippedFile = request.FILES['meterZippedFile']

    meterData = AllMeterFiles.objects.create(year=year, month=month,status = "Uploaded", startDate=startDate, endDate=endDate)
    meterData.save()
    meterData.zippedMeterFile = meterZippedFile
    meterData.save()

    return HttpResponse(json.dumps({'id' : meterData.id, 'message': 'MeterFile added'}), content_type='application/json')

@csrf_exempt
def deleteNewMeterFile(request,meter_id):
    print(meter_id)
    AllMeterFiles.objects.get(id=int(meter_id)).delete()
    return HttpResponse({'message': 'Meter deleted'}, status=200)

###########################  Extract ##########################################################################

@csrf_exempt
def getNPCData(request, meter_id):   # Data of single meter

    print("inside getNPCData")
    print(meter_id)

    npcFiles = list(filter(lambda npcFile: (npcFile.npcFileMeterId() == meter_id),NpcFile.objects.all()))
    # npcFile = npcFiles[0]
    # npcDict = json.loads(npcFile.npcDictionary)
    # print(npcDict["1"])
    npcFiles_json = serializers.serialize("json", npcFiles , fields=('dirStructureNPC','meterFile'))
 
    return HttpResponse(npcFiles_json, content_type="text/json-comment-filtered")




@csrf_exempt
def extract(request,meter_id):
    
    try :
        print("inside extract")

        print("meter_id")
        print(meter_id)
        meterData = AllMeterFiles.objects.get(id=meter_id)
        print(meterData.zippedMeterFile)
        # zipFilePath = os.path.join("fifteenmmdp/media/",str(meterData.zippedMeterFile))
        npcFilesFolderPath = os.path.join("fifteenmmdp/media/meterFile/meterFile"+meter_id,'NPC Files',os.path.basename(str(meterData.zippedMeterFile)))
        # print(os.path.splitext(zipFilePath))   # ('fifteenmmdp/media/meterFile/meterFile29/test', '.zip')
        print(npcFilesFolderPath)
        print(os.path.splitext(npcFilesFolderPath)) # ('meterFile/meterFile29\\NPC Files\\test', '.zip')

        with zipfile.ZipFile('fifteenmmdp/media/'+ str(meterData.zippedMeterFile), 'r') as zip_ref:
            # zip_ref.extractall("fifteenmmdp/media/meterFile/meterFile"+ meter_id)
            zip_ref.extractall("fifteenmmdp/media/meterFile/meterFile"+ meter_id +"/NPC Files")

        if(not (meterData.status is None) and (statusCodes.index(meterData.status) == 0)) :
            print("Extract executed")

            npcDict = {'lastIndex' : 1}

            jsonOutput = dirJsonNPC(os.path.splitext(npcFilesFolderPath)[0],meterData,npcDict)
            print(json.dumps(jsonOutput))
            print(npcDict)

            npcFileObject = NpcFile.objects.create(npcDictionary = json.dumps(npcDict),dirStructureNPC=json.dumps(jsonOutput), meterFile = meterData)
            npcFileObject.save()

            AllMeterFiles.objects.filter(id = meter_id).update(status="Extracted")
        return HttpResponse({'message': 'Meter File Extracted'}, status=200)
    except Exception as e :
        return HttpResponse(json.dumps([str(e)]), content_type='application/json',status=500)



# @csrf_exempt
# def downloadNPCFile(request,npc_id):

    print("inside downloadNpcFile")
    print(npc_id)
    npcFile = NpcFile.objects.get(id=int(npc_id))


    outputFile_path = os.path.join(settings.MEDIA_ROOT,npcFile.filePath)
    print(outputFile_path)

    if(os.path.exists(outputFile_path)) :
        with open(outputFile_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="text/plain")
            response['Content-Disposition'] = 'attachment; filename=' + npcFile.fileName
            return response

    return HttpResponse("There is no NPC File to download")


@csrf_exempt
def downloadNPCFile(request,meter_id,npc_id):   # Single File only

    print("inside downloadNPCFile")
    print(npc_id)
    # npcFile = NpcFile.objects.get(id=int(npc_id))

    npcFiles = list(filter(lambda npcFile: (npcFile.npcFileMeterId() == meter_id),NpcFile.objects.all()))
    npcFile = npcFiles[0]
    npcDict = json.loads(npcFile.npcDictionary)

    outputFile_path = os.path.join(settings.MEDIA_ROOT,npcDict[npc_id])
    print(outputFile_path)

    if(os.path.exists(outputFile_path)) :
        with open(outputFile_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="text/plain")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(npcDict[npc_id])
            return response

    return HttpResponse("There is no NPC File to download")


# @csrf_exempt
# def changeNPCFile(request,npc_id):

    print("inside changeNPCFile")
    print(npc_id)

    print(request.FILES['fileToUpload'])
    # npcFileToChange = NpcFile.objects.get(id = npc_id)
    # npcFileToChange.npcFile = request.FILES['fileToUpload']
    # npcFileToChange.save()
    return HttpResponse({'message': 'NPC Changed'}, status=200)

@csrf_exempt
def changeNPCFile(request,meter_id,npc_id):

    print("inside changeNPCFile")
    print(npc_id)

    print(request.FILES['fileToUpload'])
    myfile = request.FILES['fileToUpload']

    print(myfile)
    print(myfile.name)
    npcFiles = list(filter(lambda npcFile: (npcFile.npcFileMeterId() == meter_id),NpcFile.objects.all()))
    npcFile = npcFiles[0]
    npcDict = json.loads(npcFile.npcDictionary)
    print(npcDict[npc_id])
    # useThisLoc = 'fifteenmmdp/media'+npcDict[npc_id]
    useThisLoc = npcDict[npc_id]

    fs = OverwriteStorage()
    fs.save(useThisLoc, myfile)
    # realMeterMWHFileToChange.npcFile = request.FILES['fileToUpload']
    # realMeterMWHFileToChange.save()
    return HttpResponse({'message': 'NPCFile Changed'}, status=200)

###########################  Merge ##########################################################################
@csrf_exempt
def merge(request,meter_id):
    print(meter_id)
    meterFile = AllMeterFiles.objects.get(id=int(meter_id))
    print(meterFile.status)
    mergeError = mergeNPCs(path = "meterFile"+meter_id, _meterData = meterFile)  #Path given
    if(len(mergeError) != 0) :
        return HttpResponse(json.dumps(mergeError), content_type='application/json',status=500)
    else :
        return HttpResponse({'message': 'NPCs Merged'}, status=200)
        

@csrf_exempt
def getMergedFile(request,meter_id):

    print("inside getMergedFile")
    print(meter_id)

    mergedFile = list(filter(lambda mergedFile: (mergedFile.mergedFileMeterId() == meter_id),MergedFile.objects.all()))
    
    mergedFile_json = serializers.serialize("json", mergedFile)
    # data = {"data": AllMeterFiles_json}
    # return JsonResponse(data)
    return HttpResponse(mergedFile_json, content_type="text/json-comment-filtered")


@csrf_exempt
def downloadMergedFile(request,mergedFile_id):

    print("inside downloadMergedFile")

    print(mergedFile_id)
    mergedFile = MergedFile.objects.get(id=int(mergedFile_id))


    outputFile_path = os.path.join(settings.MEDIA_ROOT,mergedFile.filePath)
    print(outputFile_path)

    if(os.path.exists(outputFile_path)) :
        with open(outputFile_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="text/plain")
            response['Content-Disposition'] = 'attachment; filename=' + mergedFile.fileName
            return response

    return HttpResponse("There is no Merged File to download")

@csrf_exempt
def changeMergedFile(request,mergedFile_id):

    print("inside changeMergedFile")

    print(request.FILES['fileToUpload'])
    mergedFileToChange = MergedFile.objects.get(id = mergedFile_id)
    mergedFileToChange.mergedFile = request.FILES['fileToUpload']
    mergedFileToChange.save()
    print(mergedFile_id)
    return HttpResponse({'message': 'Merged File Changed'}, status=200)

############################## Date Filter #####################################################################

@csrf_exempt
def dateFilter(request,meter_id):
    print(meter_id)
    meterFile = AllMeterFiles.objects.get(id=int(meter_id))
    print(meterFile.status)
    dateFilterError = dateFilterMergedFile(path = "meterFile"+meter_id, _meterData = meterFile)  #Path given
    if(len(dateFilterError) != 0) :
        return HttpResponse(json.dumps(dateFilterError), content_type='application/json',status=500)
    else :
    #Need to fix 
        return HttpResponse({'message': 'MergedFile DateFiltered'}, status=200)


@csrf_exempt
def getDateFilteredFile(request,meter_id):

    print("inside getDateFilteredFile")
    print(meter_id)

    dateFilteredFile = list(filter(lambda dateFilteredFile: (dateFilteredFile.dateFilteredFileMeterId() == meter_id),DateFilteredFile.objects.all()))
    
    dateFilteredFile_json = serializers.serialize("json", dateFilteredFile)
    # data = {"data": AllMeterFiles_json}
    # return JsonResponse(data)
    return HttpResponse(dateFilteredFile_json, content_type="text/json-comment-filtered")


@csrf_exempt
def downloadDateFilteredFile(request,dateFilteredFile_id):

    print("inside downloadDateFilteredFile")

    print(dateFilteredFile_id)
    dateFilteredFile = DateFilteredFile.objects.get(id=int(dateFilteredFile_id))


    outputFile_path = os.path.join(settings.MEDIA_ROOT,dateFilteredFile.filePath)
    print(outputFile_path)

    if(os.path.exists(outputFile_path)) :
        with open(outputFile_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="text/plain")
            response['Content-Disposition'] = 'attachment; filename=' + dateFilteredFile.fileName
            return response

    return HttpResponse("There is no DateFiltered File to download")

@csrf_exempt
def changeDateFilteredFile(request,dateFilteredFile_id):

    print("inside changeDateFiltered")

    print(request.FILES['fileToUpload'])
    dateFilteredFileToChange = DateFilteredFile.objects.get(id = dateFilteredFile_id)
    dateFilteredFileToChange.dateFilteredFile = request.FILES['fileToUpload']
    dateFilteredFileToChange.save()
    print(dateFilteredFile_id)
    return HttpResponse({'message': 'DateFiltered File Changed'}, status=200)

@csrf_exempt
def downloadNrxFile(request,meter_id):

    print("inside downloadNrxFile")

    print(meter_id)

    outputFile_path = os.path.join(settings.MEDIA_ROOT,'meterFile/meterFile'+meter_id+"/DateFiltered File/NRXFile.NRX")
    print(outputFile_path)

    if(os.path.exists(outputFile_path)) :
        with open(outputFile_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="text/plain")
            response['Content-Disposition'] = 'attachment; filename=' + 'NRXFile.NRX'
            return response

    return HttpResponse("There is no NRX File to download")

############################ Validate ##############################################################################

@csrf_exempt
def validate(request,meter_id):
    try :
        print(meter_id)
        meterFile = AllMeterFiles.objects.get(id=int(meter_id))
        print(meterFile.status)
        valiDateError = validateFile(path = "meterFile"+meter_id, _meterData = meterFile)  #Path given
        if(len(valiDateError) != 0) :
            return HttpResponse(json.dumps(valiDateError), content_type='application/json',status=500)
        else :
        #Need to fix 
            return HttpResponse({'message': 'MergedFile Validated'}, status=200)
    except Exception as e :
        return HttpResponse(json.dumps([str(e)]), content_type='application/json',status=500)


@csrf_exempt
def getValidatedFile(request,meter_id):

    print("inside getValidatedFile")
    print(meter_id)

    validatedFile = list(filter(lambda validatedFile: (validatedFile.validatedFileMeterId() == meter_id),ValidatedFile.objects.all()))
    
    validatedFile_json = serializers.serialize("json", validatedFile)
    # data = {"data": AllMeterFiles_json}
    # return JsonResponse(data)
    return HttpResponse(validatedFile_json, content_type="text/json-comment-filtered")


@csrf_exempt
def downloadValidatedFile(request,validatedFile_id):

    print("inside downloadValidatedFile")

    print(validatedFile_id)
    validatedFile = ValidatedFile.objects.get(id=int(validatedFile_id))


    outputFile_path = os.path.join(settings.MEDIA_ROOT,validatedFile.filePath)
    print(outputFile_path)

    if(os.path.exists(outputFile_path)) :
        with open(outputFile_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="text/plain")
            response['Content-Disposition'] = 'attachment; filename=' + validatedFile.fileName
            return response

    return HttpResponse("There is no Validated File to download")

@csrf_exempt
def changeValidatedFile(request,validatedFile_id):

    print("inside changeValidatedFile")

    print(request.FILES['fileToUpload'])
    validatedFileToChange = ValidatedFile.objects.get(id = validatedFile_id)
    validatedFileToChange.validatedFile = request.FILES['fileToUpload']
    validatedFileToChange.save()
    print(validatedFile_id)
    return HttpResponse({'message': 'Validated File Changed'}, status=200)


############################## Create Real Meter MWH #################################################################

@csrf_exempt
def getRealMeterMWHData(request, meter_id):   # Data of single meter

    print("inside getRealMeterMWHData")
    print(meter_id)

    realMeterMWHFiles = list(filter(lambda realMeterMWHFile: (realMeterMWHFile.realMeterMWHFileMeterId() == meter_id),RealMeterMWHFile.objects.all()))
    # realMeterMWHFile = realMeterMWHFiles[0]
    # mwhDict = json.loads(realMeterMWHFile.mwhDictionary)
    # print(mwhDict["1"])
    realMeterMWHFiles_json = serializers.serialize("json", realMeterMWHFiles , fields=('dirStructureRealMWH','meterFile'))
    # data = {"data": AllMeterFiles_json}
    # return JsonResponse(data)
    return HttpResponse(realMeterMWHFiles_json, content_type="text/json-comment-filtered")


@csrf_exempt
def realMeterMWH(request,meter_id):
    # try :
    print(meter_id)
    meterFile = AllMeterFiles.objects.get(id=int(meter_id))
    print(meterFile.status)
    createRealMeterMWH(path = "meterFile"+meter_id, _meterData = meterFile)  #Path given
    return HttpResponse({'message': 'Real Meter MWH Created'}, status=200)
    # except Exception as e :
    #     return HttpResponse(json.dumps([str(e)]), content_type='application/json',status=500)

@csrf_exempt
def downloadRealMeterMWHFile(request,meter_id,realMeterMWH_id):   # Single File only

    print("inside downloadRealMeterMWHFile")
    print(realMeterMWH_id)
    # realMeterMWHFile = RealMeterMWHFile.objects.get(id=int(realMeterMWH_id))

    realMeterMWHFiles = list(filter(lambda realMeterMWHFile: (realMeterMWHFile.realMeterMWHFileMeterId() == meter_id),RealMeterMWHFile.objects.all()))
    realMeterMWHFile = realMeterMWHFiles[0]
    mwhDict = json.loads(realMeterMWHFile.mwhDictionary)

    outputFile_path = os.path.join(settings.MEDIA_ROOT,mwhDict[realMeterMWH_id])
    print(outputFile_path)

    if(os.path.exists(outputFile_path)) :
        with open(outputFile_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="text/plain")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(mwhDict[realMeterMWH_id])
            return response

    return HttpResponse("There is no Real Meter MWH File to download")


@csrf_exempt
def changeRealMeterMWHFile(request,meter_id,realMeterMWH_id):

    print("inside changeRealMeterMWHFile")
    print(realMeterMWH_id)

    print(request.FILES['fileToUpload'])
    myfile = request.FILES['fileToUpload']
    # realMeterMWHFileToChange = RealMeterMWHFile.objects.get(id = realMeterMWH_id)
    print(myfile)
    print(myfile.name)
    realMeterMWHFiles = list(filter(lambda realMeterMWHFile: (realMeterMWHFile.realMeterMWHFileMeterId() == meter_id),RealMeterMWHFile.objects.all()))
    realMeterMWHFile = realMeterMWHFiles[0]
    mwhDict = json.loads(realMeterMWHFile.mwhDictionary)
    print(mwhDict[realMeterMWH_id])
    # useThisLoc = 'fifteenmmdp/media'+mwhDict[realMeterMWH_id]
    useThisLoc = mwhDict[realMeterMWH_id]

    fs = OverwriteStorage()
    fs.save(useThisLoc, myfile)
    # realMeterMWHFileToChange.npcFile = request.FILES['fileToUpload']
    # realMeterMWHFileToChange.save()
    return HttpResponse({'message': 'RealMeterMWHFile Changed'}, status=200)


def downLoadFullRealMeterMWHFiles(request,meter_id):
    print("inside downLoadFullRealMeterMWHFiles")
    print(meter_id)

    path = os.path.join(settings.MEDIA_ROOT,'meterFile/meterFile'+meter_id)
    inputFile_path = os.path.join(path,'Real Meter MWH Files')
    outputFile_path = os.path.join(path,'Real_Meter_MWH.zip')

    shutil.make_archive(os.path.splitext(outputFile_path)[0], 'zip', inputFile_path)

    if(os.path.exists(outputFile_path)) :
        with open(outputFile_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/force-download")
            response['Content-Disposition'] = 'attachment; filename=' + 'Real_Meter_MWH.zip'
            return response

    return HttpResponse("There is no Real Meter MWH File to download")
############################## Create Fictitious Meter MWH #################################################################

@csrf_exempt
def getFictMeterMWHData(request, meter_id):   # Data of single meter

    print("inside getFictMeterMWHData")
    print(meter_id)

    fictMeterMWHFiles = list(filter(lambda fictMeterMWHFile: (fictMeterMWHFile.fictMeterMWHFileMeterId() == meter_id),FictMeterMWHFile.objects.all()))
    # fictMeterMWHFile = fictMeterMWHFiles[0]
    # fictMwhDict = json.loads(fictMeterMWHFile.fictMwhDictionary)
    # print(fictMwhDict["1"])
    fictMeterMWHFiles_json = serializers.serialize("json", fictMeterMWHFiles , fields=('dirStructureFictMWH','meterFile'))
    # data = {"data": AllMeterFiles_json}
    # return JsonResponse(data)
    return HttpResponse(fictMeterMWHFiles_json, content_type="text/json-comment-filtered")


@csrf_exempt
def fictMeterMWH(request,meter_id):
    # try :
    print(meter_id)
    meterFile = AllMeterFiles.objects.get(id=int(meter_id))
    print(meterFile.status)
    createFictMeterMWH(path = "meterFile"+meter_id, _meterData = meterFile)  #Path given
    return HttpResponse({'message': 'Fict Meter MWH Created'}, status=200)
    # except Exception as e :
    #     return HttpResponse(json.dumps([str(e)]), content_type='application/json',status=500)

@csrf_exempt
def downloadFictMeterMWHFile(request,meter_id,fictMeterMWH_id):   # Single File only

    print("inside downloadFictMeterMWHFile")
    print(fictMeterMWH_id)
    # fictMeterMWHFile = FictMeterMWHFile.objects.get(id=int(fictMeterMWH_id))

    fictMeterMWHFiles = list(filter(lambda fictMeterMWHFile: (fictMeterMWHFile.fictMeterMWHFileMeterId() == meter_id),FictMeterMWHFile.objects.all()))
    fictMeterMWHFile = fictMeterMWHFiles[0]
    fictMwhDict = json.loads(fictMeterMWHFile.fictMwhDictionary)

    outputFile_path = os.path.join(settings.MEDIA_ROOT,fictMwhDict[fictMeterMWH_id])
    print(outputFile_path)

    if(os.path.exists(outputFile_path)) :
        with open(outputFile_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="text/plain")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(fictMwhDict[fictMeterMWH_id])
            return response

    return HttpResponse("There is no Fict Meter MWH File to download")


@csrf_exempt
def changeFictMeterMWHFile(request,meter_id,fictMeterMWH_id):

    print("inside changeFictMeterMWHFile")
    print(fictMeterMWH_id)

    print(request.FILES['fileToUpload'])
    myfile = request.FILES['fileToUpload']
    # realMeterMWHFileToChange = RealMeterMWHFile.objects.get(id = realMeterMWH_id)
    print(myfile)
    print(myfile.name)
    fictMeterMWHFiles = list(filter(lambda fictMeterMWHFile: (fictMeterMWHFile.fictMeterMWHFileMeterId() == meter_id),FictMeterMWHFile.objects.all()))
    fictMeterMWHFile = fictMeterMWHFiles[0]
    fictMwhDict = json.loads(fictMeterMWHFile.fictMwhDictionary)
    print(fictMwhDict[fictMeterMWH_id])
    # useThisLoc = 'fifteenmmdp/media'+fictMwhDict[fictMeterMWH_id]
    useThisLoc = fictMwhDict[fictMeterMWH_id]

    fs = OverwriteStorage()
    fs.save(useThisLoc, myfile)
    # realMeterMWHFileToChange.npcFile = request.FILES['fileToUpload']
    # realMeterMWHFileToChange.save()
    return HttpResponse({'message': 'FictMeterMWHFile Changed'}, status=200)

def downLoadFullFictMeterMWHFiles(request,meter_id):
    print("inside downLoadFullFictMeterMWHFiles")
    print(meter_id)

    path = os.path.join(settings.MEDIA_ROOT,'meterFile/meterFile'+meter_id)
    inputFile_path = os.path.join(path,'Fictitious Meter MWH Files')
    outputFile_path = os.path.join(path,'Fictitious_Meter_MWH.zip')

    shutil.make_archive(os.path.splitext(outputFile_path)[0], 'zip', inputFile_path)

    if(os.path.exists(outputFile_path)) :
        with open(outputFile_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/force-download")
            response['Content-Disposition'] = 'attachment; filename=' + 'Fictitious_Meter_MWH.zip'
            return response

    return HttpResponse("There is no Fictitious Meter MWH File to download")

############################## Create Final Output Files #################################################################



@csrf_exempt
def getRealMeterMWHData(request, meter_id):   # Data of single meter

    print("inside getRealMeterMWHData")
    print(meter_id)

    realMeterMWHFiles = list(filter(lambda realMeterMWHFile: (realMeterMWHFile.realMeterMWHFileMeterId() == meter_id),RealMeterMWHFile.objects.all()))
    # realMeterMWHFile = realMeterMWHFiles[0]
    # mwhDict = json.loads(realMeterMWHFile.mwhDictionary)
    # print(mwhDict["1"])
    realMeterMWHFiles_json = serializers.serialize("json", realMeterMWHFiles , fields=('dirStructureRealMWH','meterFile'))
    # data = {"data": AllMeterFiles_json}
    # return JsonResponse(data)
    return HttpResponse(realMeterMWHFiles_json, content_type="text/json-comment-filtered")


@csrf_exempt
def realMeterMWH(request,meter_id):
    # try :
    print(meter_id)
    meterFile = AllMeterFiles.objects.get(id=int(meter_id))
    print(meterFile.status)
    createRealMeterMWH(path = "meterFile"+meter_id, _meterData = meterFile)  #Path given
    return HttpResponse({'message': 'Real Meter MWH Created'}, status=200)
    # except Exception as e :
    #     return HttpResponse(json.dumps([str(e)]), content_type='application/json',status=500)

@csrf_exempt
def downloadRealMeterMWHFile(request,meter_id,realMeterMWH_id):   # Single File only

    print("inside downloadRealMeterMWHFile")
    print(realMeterMWH_id)
    # realMeterMWHFile = RealMeterMWHFile.objects.get(id=int(realMeterMWH_id))

    realMeterMWHFiles = list(filter(lambda realMeterMWHFile: (realMeterMWHFile.realMeterMWHFileMeterId() == meter_id),RealMeterMWHFile.objects.all()))
    realMeterMWHFile = realMeterMWHFiles[0]
    mwhDict = json.loads(realMeterMWHFile.mwhDictionary)

    outputFile_path = os.path.join(settings.MEDIA_ROOT,mwhDict[realMeterMWH_id])
    print(outputFile_path)

    if(os.path.exists(outputFile_path)) :
        with open(outputFile_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="text/plain")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(mwhDict[realMeterMWH_id])
            return response

    return HttpResponse("There is no Real Meter MWH File to download")


@csrf_exempt
def changeRealMeterMWHFile(request,meter_id,realMeterMWH_id):

    print("inside changeRealMeterMWHFile")
    print(realMeterMWH_id)

    print(request.FILES['fileToUpload'])
    myfile = request.FILES['fileToUpload']
    # realMeterMWHFileToChange = RealMeterMWHFile.objects.get(id = realMeterMWH_id)
    print(myfile)
    print(myfile.name)
    realMeterMWHFiles = list(filter(lambda realMeterMWHFile: (realMeterMWHFile.realMeterMWHFileMeterId() == meter_id),RealMeterMWHFile.objects.all()))
    realMeterMWHFile = realMeterMWHFiles[0]
    mwhDict = json.loads(realMeterMWHFile.mwhDictionary)
    print(mwhDict[realMeterMWH_id])
    # useThisLoc = 'fifteenmmdp/media'+mwhDict[realMeterMWH_id]
    useThisLoc = mwhDict[realMeterMWH_id]

    fs = OverwriteStorage()
    fs.save(useThisLoc, myfile)
    # realMeterMWHFileToChange.npcFile = request.FILES['fileToUpload']
    # realMeterMWHFileToChange.save()
    return HttpResponse({'message': 'RealMeterMWHFile Changed'}, status=200)


def downLoadFullRealMeterMWHFiles(request,meter_id):
    print("inside downLoadFullRealMeterMWHFiles")
    print(meter_id)

    path = os.path.join(settings.MEDIA_ROOT,'meterFile/meterFile'+meter_id)
    inputFile_path = os.path.join(path,'Real Meter MWH Files')
    outputFile_path = os.path.join(path,'Real_Meter_MWH.zip')

    shutil.make_archive(os.path.splitext(outputFile_path)[0], 'zip', inputFile_path)

    if(os.path.exists(outputFile_path)) :
        with open(outputFile_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/force-download")
            response['Content-Disposition'] = 'attachment; filename=' + 'Real_Meter_MWH.zip'
            return response

    return HttpResponse("There is no Real Meter MWH File to download")
############################## Create Fictitious Meter MWH #################################################################

@csrf_exempt
def getFinalOutputData(request, meter_id):   # Data of single meter

    print("inside getFinalOutputData")
    print(meter_id)

    finalOutputFiles = list(filter(lambda finalOutputFile: (finalOutputFile.finalOutputFileMeterId() == meter_id),FinalOutputFile.objects.all()))
   
    finalOutputFiles_json = serializers.serialize("json", finalOutputFiles , fields=('dirStructureFinalOutput','meterFile'))
    # data = {"data": AllMeterFiles_json}
    # return JsonResponse(data)
    return HttpResponse(finalOutputFiles_json, content_type="text/json-comment-filtered")


@csrf_exempt
def finalOutput(request,meter_id):
    # try :
    print(meter_id)
    meterFile = AllMeterFiles.objects.get(id=int(meter_id))
    print(meterFile.status)
    createFinalOutput(path = "meterFile"+meter_id, _meterData = meterFile)  #Path given
    return HttpResponse({'message': 'Final Output Created'}, status=200)
    # except Exception as e :
    #     return HttpResponse(json.dumps([str(e)]), content_type='application/json',status=500)

@csrf_exempt
def downloadFinalOutputFile(request,meter_id,finalOutput_id):   # Single File only

    print("inside downloadFinalOutputile")
    print(finalOutput_id)

    finalOutputFiles = list(filter(lambda finalOutputFile: (finalOutputFile.fianlOutputFileMeterId() == meter_id),FinalOutputFile.objects.all()))
    finalOutputFile = finalOutputFiles[0]
    finalOutputDict = json.loads(finalOutputFile.finalOutputDictionary)

    outputFile_path = os.path.join(settings.MEDIA_ROOT,finalOutputDict[finalOutput_id])
    print(outputFile_path)

    if(os.path.exists(outputFile_path)) :
        with open(outputFile_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="text/plain")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(finalOutputDict[finalOutput_id])
            return response

    return HttpResponse("There is no Final Output File to download")


@csrf_exempt
def changeFinalOutputFile(request,meter_id,finalOutput_id):

    print("inside changeFinalOutputFile")
    print(finalOutput_id)

    print(request.FILES['fileToUpload'])
    myfile = request.FILES['fileToUpload']

    print(myfile)
    print(myfile.name)

    finalOutputFiles = list(filter(lambda finalOutputFile: (finalOutputFile.fianlOutputFileMeterId() == meter_id),FinalOutputFile.objects.all()))
    finalOutputFile = finalOutputFiles[0]
    finalOutputDict = json.loads(finalOutputFile.finalOutputDictionary)
    print(finalOutputDict[finalOutput_id])
    # useThisLoc = 'fifteenmmdp/media'+finalOutputDict[finalOutput_id]
    useThisLoc = finalOutputDict[finalOutput_id]

    fs = OverwriteStorage()
    fs.save(useThisLoc, myfile)
    # realMeterMWHFileToChange.npcFile = request.FILES['fileToUpload']
    # realMeterMWHFileToChange.save()
    return HttpResponse({'message': 'Final Output File Changed'}, status=200)

@csrf_exempt
def downLoadFullFinalOutputFiles(request,meter_id):
    print("inside downLoadFullFinalOutputFiles")
    print(meter_id)

    path = os.path.join(settings.MEDIA_ROOT,'meterFile/meterFile'+meter_id)
    inputFile_path = os.path.join(path,'Final Output Files')
    outputFile_path = os.path.join(path,'Final_Output.zip')

    shutil.make_archive(os.path.splitext(outputFile_path)[0], 'zip', inputFile_path)

    if(os.path.exists(outputFile_path)) :
        with open(outputFile_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/force-download")
            response['Content-Disposition'] = 'attachment; filename=' + 'Final_Output.zip'
            return response

    return HttpResponse("There is no Final Output File to download")

@csrf_exempt
def getNecessaryFiles(request) :
    # necessaryFiles_json = serializers.serialize("json", necessaryFiles)
    return HttpResponse(json.dumps(necessaryFiles), content_type="application/json")
