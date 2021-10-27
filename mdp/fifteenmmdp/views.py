from django.shortcuts import render
import json
from django.core import serializers
import os
import zipfile
from django.conf import settings
from datetime import datetime
import shutil
import pandas as pd
# Create your views here.
from django.core.files import File

from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response
# from .serializers import AllMeterFilesSerializer

from .models import *
from .extract import dirJsonNPC
from .merge import mergeNPCs
from .dateFilter import dateFilterMergedFile
from .validate import validateFile
from .realMeterMWH import createRealMeterMWH
from .frequencyGraphData import frequencyGraphData
from .fictMeterMWH import createFictMeterMWH
from .finalOutput import createFinalOutput
from .analyseData import fetchData
from .changeMeterDataAnalyse import changeMeterEndDataWithEquation,revertMeterEndChanges,zeroFillMeter
from .componentWiseAnalysis import componentWiseMeterAnalysis
from .specialReports import specialReport1


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

def meterChangeLog(file_name, text_to_append):
    """Append given text as a new line at the end of file"""
    # Open the file in append & read mode ('a+')
    with open(file_name, "a+") as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)
        # If file is not empty then append '\n'
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        # Append text at the end of file
        file_object.write(text_to_append)

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
    # AllMeterFiles_json = AllMeterFiles.objects.all()
    AllMeterFiles_json = serializers.serialize("json", AllMeterFiles.objects.all().order_by('-id'))
    
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
        # npcFilesFolderPath = os.path.join("fifteenmmdp/media/meterFile/meterFile"+meter_id,'NPC Files',os.path.basename(str(meterData.zippedMeterFile)))
        npcFilesFolderPath = os.path.join("fifteenmmdp/media/meterFile/meterFile"+meter_id,'NPC Files')

        # print(os.path.splitext(zipFilePath))   # ('fifteenmmdp/media/meterFile/meterFile29/test', '.zip')
        print(npcFilesFolderPath)
        print(os.path.splitext(npcFilesFolderPath)) # ('meterFile/meterFile29\\NPC Files\\test', '.zip')

        with zipfile.ZipFile('fifteenmmdp/media/'+ str(meterData.zippedMeterFile), 'r') as zip_ref:
            # zip_ref.extractall("fifteenmmdp/media/meterFile/meterFile"+ meter_id)
            zip_ref.extractall("fifteenmmdp/media/meterFile/meterFile"+ meter_id +"/NPC Files")


        if(not (meterData.status is None) and (statusCodes.index(meterData.status) == 0)) :
            shutil.copytree('fifteenmmdp/media/necessaryFiles', "fifteenmmdp/media/meterFile/meterFile"+ meter_id +"/NPC Files/Necessary Files Local Copy")


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
def realMeterMWH(request,meter_id,overWrite):
    # try :
    print(meter_id)
    if(overWrite == "false") :
        print("Keep file as it is")
    else :
        shutil.rmtree(os.path.join("fifteenmmdp/media/meterFile","meterFile"+meter_id,"Real Meter MWH Files(Copy)"))
        print("overwrite the files")
    print(type(overWrite))
    meterFile = AllMeterFiles.objects.get(id=int(meter_id))
    print(meterFile.status)
    createRealMeterMWH(path = "meterFile"+meter_id, _meterData = meterFile, overWrite = overWrite)  #Path given
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

@csrf_exempt
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

@csrf_exempt
def fetchFrequencyGraphData(request, meter_id) :
    print("i am in fetchFrequencyGraphData")

    frequencyGraphDataToSend = frequencyGraphData(path = "meterFile"+meter_id) 
    # print(frequencyGraphDataToSend)
    return HttpResponse(json.dumps(frequencyGraphDataToSend))
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
    try :
        print(meter_id)
        meterFile = AllMeterFiles.objects.get(id=int(meter_id))
        print(meterFile.status)
        createFinalOutput(path = "meterFile"+meter_id, _meterData = meterFile)  #Path given
        return HttpResponse({'message': 'Final Output Created'}, status=200)
    except Exception as e :
        return HttpResponse(json.dumps([str(e)]), content_type='application/json',status=500)

@csrf_exempt
def downloadFinalOutputFile(request,meter_id,finalOutput_id):   # Single File only

    print("inside downloadFinalOutputile")
    print(finalOutput_id)

    finalOutputFiles = list(filter(lambda finalOutputFile: (finalOutputFile.finalOutputFileMeterId() == meter_id),FinalOutputFile.objects.all()))
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

    finalOutputFiles = list(filter(lambda finalOutputFile: (finalOutputFile.finalOutputFileMeterId() == meter_id),FinalOutputFile.objects.all()))
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

############################## Analyse data #################################################################
@csrf_exempt
def analyseData(request,meter_id):
    try :
        print("Analyse data")

        with open("fifteenmmdp/media/meterFile/meterFile" + str(meter_id) +"/NPC Files/Necessary Files Local Copy/GraphConfiguration.xlsx", "rb") as f: # input the .xlsx
            data = pd.read_excel(f,sheet_name=None,engine='openpyxl')
            f.close()

        stateWiseFeederDetails = {}

        print(len(data.keys()))
        for key in data.keys() :
            data[key] = data[key].fillna("Meter not specified")
            stateWiseFeederDetails[key] = []
            # print(data[key])

        # stateWiseFeederDetails = {'BIHAR' : [] , 'WEST BENGAL' : [] , 'GRIDCO' : [] , 'DVC' : [] , 'SIKKIM' : [] , 'JHARKHAND' : []}
        entities = stateWiseFeederDetails.keys()

        for entity in entities :
            for index, row in data[entity].iterrows():
                feederObject = {'id' : row['SL NO'] , 'Feeder Name' : row['Feeder Name'] , 'End1' : row['End1'], 'End2' : row['End2'] }
                stateWiseFeederDetails[entity].append(feederObject)
        
        # with open(r'fifteenmmdp/media/necessaryFiles/Graph Configuration.xlsx', "rb") as f: # input the .xlsx
        #     data = pd.read_excel(f,sheet_name="WEST BENGAL",engine='openpyxl')
        #     f.close()
        # print(data)

        
        # for index, row in data.iterrows():
        #     feederObject = {'id' : row['SL NO'] , 'Feeder Name' : row['Feeder Name'] , 'End1' : row['End1'], 'End2' : row['End2'] }
        #     stateWiseFeederDetails['WEST BENGAL'].append(feederObject)

        # print(stateWiseFeederDetails)
        return HttpResponse(json.dumps(stateWiseFeederDetails), content_type="application/json")

        # return HttpResponse({'message': 'ANALYSE DATA'}, status=200)
    except Exception as e :
        print(str(e))
        return HttpResponse(json.dumps([str(e)]), content_type='application/json',status=500)

@csrf_exempt
def fetchGraphData(request,meter_id,end1,end2,polarity):
    print(meter_id)
    print(end1)
    print(end2)
    print(polarity)
    graphData = fetchData(meter_id,end1,end2,polarity)
    return HttpResponse(json.dumps(graphData), content_type='application/json') 

@csrf_exempt
def fetchGraphDataExcel(request,meter_id,end1,end2,polarity):
    print(meter_id)
    print(end1)
    print(end2)
    print(polarity)
    graphData = fetchData(meter_id,end1,end2,polarity)
    # return HttpResponse(json.dumps(graphData), content_type='application/json')
    # graphData = {'end1Data' : end1Data ,'end2Data' : end2Data , 'xAxisData' : xAxisData , 'diff' : endDifference(end2Data,end1Data), 'diffPercentage' : endDifferencePercentage(end2Data,end1Data)}

    
    meterFileMainFolder = os.path.join(settings.MEDIA_ROOT,"meterFile","meterFile"+meter_id)

    print("inside fetchGraphDataExcel")

    graphDataExcel = {}

    graphDataExcel['Date'] = [item.split()[0] for item in graphData['xAxisData']]
    graphDataExcel['Timestamp'] = [item.split()[1] for item in graphData['xAxisData']]

    graphDataExcel[end1] = graphData['end1Data']
    graphDataExcel[end2] = graphData['end2Data']
    graphDataExcel['Difference'] = graphData['diff']
    graphDataExcel['Difference Percentage'] = graphData['diffPercentage']


    dfExcel = pd.DataFrame.from_dict(graphDataExcel)

    if(not os.path.exists(meterFileMainFolder + '/Pair Comparison')) :
        os.mkdir(meterFileMainFolder + '/Pair Comparison')

    outputFile_path = os.path.join(meterFileMainFolder,'Pair Comparison',end1 +" vs " + end2 +".xlsx")

    dfExcel.to_excel(outputFile_path)

    if(os.path.exists(outputFile_path)) :
        with open(outputFile_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/force-download")
            response['Content-Disposition'] = 'attachment; filename=' + end1 + " vs " + end2 +".xlsx"
            return response

    return HttpResponse("There is no File to download")

@csrf_exempt
def fetchMeterChangeLog(request,meter_id):
    print(meter_id)
  
    meterFileMainFolder = os.path.join(settings.MEDIA_ROOT,"meterFile","meterFile"+meter_id)

    print("inside fetchMeterChangeLog")
    
    outputFile_path = os.path.join(meterFileMainFolder,'ChangeLog.txt')

    if(os.path.exists(outputFile_path)) :
        with open(outputFile_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type='application/text charset=utf-8')
            response['Content-Disposition'] = 'attachment; filename= "ChangeLog.txt"'
            return response

    return HttpResponse("No change has been done yet.")



@csrf_exempt
def fetchDateInfo(request,meter_id):
    print("this is fetchDateInfo")
    print(meter_id)

    meterData = AllMeterFiles.objects.get(id=int(meter_id))

    # One day is substracted because Real Meter MWH Files only got created for these days.
    dateInformation = {'startDate' : str(meterData.startDate) , 'endDate' : str(meterData.endDate - timedelta(days=1))}
 
    return HttpResponse(json.dumps(dateInformation), content_type="text/json-comment-filtered")

@csrf_exempt
def zeroFillMeterEndData(request,meter_id):
    print("inside zeroFillMeterEndData")

    meterEndToZeroFill = request.POST['meterEndToReplace']
    print(meterEndToZeroFill)
    print(meter_id)

    meterFile = AllMeterFiles.objects.get(id=int(meter_id))

    zeroFillMeterError = zeroFillMeter("meterFile"+meter_id ,meterFile ,meterEndToZeroFill)
    changeLog =  "Unavailable data for " + meterEndToZeroFill + " is filled with Zero"

    meterChangeLog('fifteenmmdp\media\meterFile\meterFile129\ChangeLog.txt', changeLog)

    return HttpResponse("Success")



@csrf_exempt
def changeMeterEndData(request,meter_id):
    startDate = request.POST['startDate']
    endDate = request.POST['endDate']
    meterEndToReplace = request.POST['meterEndToReplace']
    equationToReplaceWith = request.POST['equationToReplaceWith']
    changeMeterError = changeMeterEndDataWithEquation("meterFile"+meter_id ,startDate,endDate,meterEndToReplace,equationToReplaceWith)
    print(startDate)
    changeLog =  meterEndToReplace + " is replaced with " + equationToReplaceWith + " from timestamp "  + startDate + " to timestamp " + endDate

    meterChangeLog('fifteenmmdp\media\meterFile\meterFile129\ChangeLog.txt', changeLog)
    return HttpResponse("Success")


@csrf_exempt
def revertMeterEndData(request,meter_id):
    meterEndToReplace = request.POST['meterEndToReplace']
    print(meterEndToReplace)
    print(meter_id)
    print("inside revertMeterEndData")
    revertMeterEndChangesError = revertMeterEndChanges("meterFile"+meter_id ,meterEndToReplace)
    changeLog =  "All the changes done on " + meterEndToReplace + " has been Reverted Back."

    meterChangeLog('fifteenmmdp\media\meterFile\meterFile129\ChangeLog.txt', changeLog)
    return HttpResponse("Success")

@csrf_exempt
def componentWiseAnalysis(request,meter_id):
    meterEndToAnalyse = request.POST['meterEndToAnalyse']
    print(meterEndToAnalyse)
    print(meter_id)
    print("inside componentWiseAnalysis")
    componentWiseGraphData = componentWiseMeterAnalysis("meterFile"+meter_id ,meterEndToAnalyse)

    return HttpResponse(json.dumps(componentWiseGraphData), content_type='application/json')

@csrf_exempt
def componentWiseExcelData(request,meter_id,meterEndToExcelData):
    
    meterFileMainFolder = os.path.join(settings.MEDIA_ROOT,"meterFile","meterFile"+meter_id)

    # meterEndToExcelData = request.POST['meterEndToExcelData']
    print(meterEndToExcelData)
    print(meter_id)
    print("inside componentWiseAnalysis")
    componentWiseGraphData = componentWiseMeterAnalysis("meterFile"+meter_id ,meterEndToExcelData)

    downloadExcelData = {}

    downloadExcelData['Date'] = [item.split()[0] for item in componentWiseGraphData[0]['x']]
    downloadExcelData['Timestamp'] = [item.split()[1] for item in componentWiseGraphData[0]['x']]

    for componentData in componentWiseGraphData :
        downloadExcelData[componentData['name']] = componentData['y']

    dfExcel = pd.DataFrame.from_dict(downloadExcelData)

    if(not os.path.exists(meterFileMainFolder + '/Component-Wise Excel Data')) :
        os.mkdir(meterFileMainFolder + '/Component-Wise Excel Data')

    outputFile_path = os.path.join(meterFileMainFolder,'Component-Wise Excel Data',meterEndToExcelData+".xlsx")

    dfExcel.to_excel(outputFile_path)

    if(os.path.exists(outputFile_path)) :
        with open(outputFile_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/force-download")
            response['Content-Disposition'] = 'attachment; filename=' + meterEndToExcelData+".xlsx"
            return response

    return HttpResponse("There is no File to download")

############################## Special Reports #################################################################

@csrf_exempt
def specialReports(request,meter_id):
    print(meter_id)
    print("inside specialReports")
    threshold = request.POST['threshold']
    print(threshold)
    if(not isFloat(threshold)) :
        threshold = 0.5
    specialReport1Data = specialReport1("meterFile"+meter_id,meter_id, float(threshold))

    return HttpResponse(json.dumps(specialReport1Data), content_type='application/json')

############################## Necessary Files #################################################################

@csrf_exempt
def getNecessaryFiles(request) :
    # necessaryFiles_json = serializers.serialize("json", necessaryFiles)
    # return HttpResponse(json.dumps(necessaryFiles), content_type="application/json")

    NecessaryFiles_json = serializers.serialize("json", NecessaryFile.objects.all())

    return HttpResponse(NecessaryFiles_json, content_type="text/json-comment-filtered")


@csrf_exempt
def downLoadNecessaryFile(request,necessaryFileId_id):
    print("inside downLoadNecessaryFile")
    print(necessaryFileId_id)

    necessaryFile = NecessaryFile.objects.get(id=int(necessaryFileId_id))

    outputFile_path = os.path.join(settings.MEDIA_ROOT,necessaryFile.filePath)

    if(os.path.exists(outputFile_path)) :
        with open(outputFile_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/force-download")
            response['Content-Disposition'] = 'attachment; filename=' + necessaryFile.fileName
            return response

    return HttpResponse("There is no File to download")

@csrf_exempt
def changeNecessaryFile(request,necessaryFileId_id):
    print("does work")
    print(request.POST['subTitle'])
    print(request.POST['description'])
    print(request.FILES['necessaryFile'])
    necessaryFile = NecessaryFile.objects.get(id=int(necessaryFileId_id))
    necessaryFile.subTitle = request.POST['subTitle']
    necessaryFile.description = request.POST['description']
    necessaryFile.necessaryFile = request.FILES['necessaryFile']
    necessaryFile.save()
    return HttpResponse({'message': 'Necessary File updated '}, status=200)




    