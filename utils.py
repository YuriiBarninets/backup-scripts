import os
from datetime import datetime


def deleteFilesOlderThanExpirationDays(filesList, filesDir, expirationDays, fileSystemModule):
    nowTime = datetime.now()
    for fileName in filesList:
        pathToFile = os.path.join(filesDir, fileName)
        fileModifyTime = datetime.fromtimestamp(
            fileSystemModule.stat(pathToFile).st_mtime)
        timeSinceLastModify = nowTime - fileModifyTime

        if timeSinceLastModify.days >= expirationDays:
            fileSystemModule.remove(pathToFile)
            filesList.remove(fileName)
