from pydrive.auth import GoogleAuth
from pydrive.auth import RefreshError
from pydrive.drive import GoogleDrive
import os

class Drive:
    def __init__(self):
        self.drive = GoogleDrive(self.auth)

    @property
    def auth(self):
        credentialsFileName = 'credentials.json'
        gauth = GoogleAuth()
        gauth.LoadCredentialsFile(credentialsFileName)

        if gauth.access_token_expired:
            try:
                gauth.Refresh()
            except RefreshError:
                gauth.CommandLineAuth()
                gauth.SaveCredentialsFile(credentialsFileName)

        return gauth

    def fileListFrom(self,root):
        q = "'" + root + "' in parents"
        fileList = self.drive.ListFile({'q': q}).GetList()
        return fileList

    def printFileList(self,fileList):
        for file in fileList:
            print("title:", file['title'], "id:", file['id'])

class File:
    def __init__(self,file):
        self.file = file

    @property
    def fileSize(self):
        return int(self.file['fileSize'])

    @property
    def title(self):
        return self.file['title']

    @property
    def id(self):
        return self.file['id']


class Folder:
    def __init__(self, name):
        self.driveWrapper = Drive()
        self.name = name
        self.folder = self.folder()
        self.files = self.files()

    def folder(self):
        fileList = self.driveWrapper.fileListFrom('root')
        filtered = list(filter(lambda f: f['title']==self.name, fileList))
        if len(filtered)>0:
            return filtered[0]
        return None

    def files(self):
        fileList = self.driveWrapper.fileListFrom(self.folder['id'])
        return fileList

    def downloadAll(self,path):
        for f in self.files:
            filePath = os.path.join(path,f['title'])

            needsDownload = True
            if os.path.exists(filePath):
                upSize = int(f['fileSize'])
                downSize = os.stat(filePath).st_size
                if upSize == downSize:
                    print(f['title'] + " already downloaded")
                    needsDownload = False

            if needsDownload:
                print("Downloading "+f['title'])
                f.GetContentFile(filePath)

    def fileForName(self,name):
        for f in self.files:
            if f['title']==name:
                return File(f)
        return None

    def upload(self,path):
        fileName = os.path.basename(path)
        serverFile = self.fileForName(fileName)
        if serverFile is not None:
            if serverFile.fileSize == os.stat(path).st_size:
                print(serverFile.title + " already uploaded")
                return

        metadata = { 'parents': [ {"kind": "drive#fileLink", "id": self.folder['id'] } ], 'title': fileName }
        file = self.driveWrapper.drive.CreateFile(metadata=metadata)
        file.Upload()
        file.SetContentFile(path)
        file.Upload()
