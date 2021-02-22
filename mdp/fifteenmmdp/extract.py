import os
from .models import NpcFile
from django.core.files import File


def dirJsonNPC(path0,nPath,_meterData):
    d = {'name': os.path.basename(nPath)}
    # d['size'] = str("{0:.2f}".format((os.stat(path0).st_size / 1024)) + "KB")
    if os.path.isdir(path0):
        d['type'] = "folder"
        # d['path'] = nPath
        d['files'] = [dirJsonNPC(os.path.join(path0, x),os.path.join(nPath, x),_meterData) for x in os.listdir(path0)]
    else:
        if(os.path.splitext(path0)[1].lower() == '.npc') :
            print(os.path.basename(nPath))
            local_file = open(path0,"rb")  #Open file from path0 i.e. extracted first path.
            npcFileObject = NpcFile.objects.create(fileName = os.path.basename(nPath), filePath = nPath, meterFile = _meterData)
            npcFileObject.npcFile.save(os.path.basename(nPath),  File(local_file))
            npcFileObject.save()
            local_file.close()
            d['id'] = npcFileObject.id
            d['type'] = "file"
            # d['path'] = nPath
        else : 
            pass
    return d