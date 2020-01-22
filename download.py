# python3 script
# put your cookie.txt next to the script and launch it from that working dir
#

import requests
from bs4 import BeautifulSoup
import os
import sys
from GoogleDriveWrapper import Folder
from cookies import loadCookies
from pathlib import PurePath

BASE_URL = 'https://www.pointfree.co/'
VIDEOS_DIR = 'videos'
GDRIVE_PATH = 'Screencasts/PointFree'

def appendPathComponent(base,addition):
    if not base[len(base)-1] == '/':
        base += '/'
    if addition[0]=='/':
        addition = addition[1:]
    base+=addition
    return base

def downloadTextContent(url, cookies):
    resp = requests.get(url, cookies=cookies)
    return resp.text

class Episode:
    def __init__(self,baseURL,relativeURL):
        # set from outside:
        self.baseURL = baseURL
        self.relativeURL = relativeURL
        self.ext = 'mp4'
        self.gdriveUpload = True # by default it is true
        self.removeLocal = False
        self.forceReload = False
        self.videoDir = VIDEOS_DIR

        # computed and cached:
        self.name = self.getEpisodeName()
        self.fileName = self.getFileName()

    def __str__(self):
        return "Episode: " + self.name

    def __repr__(self):
        return self.__str__()

    def getEpisodeName(self):
        components = self.relativeURL.split('/')
        return components[len(components)-1]

    def getBaseURL(self,url):
        lastslashpos = url.rfind('/')
        if lastslashpos == len(url)-1:
            lastsplashpos = url.rfind('/',0,len(url)-2)
        return url[0:lastslashpos]

    def getFileName(self):
        return self.name + '.' + self.ext

    def getVideoDir(self):
        videoDir = os.path.expanduser(self.videoDir)
        if os.path.isabs(videoDir):
            return videoDir
        return os.path.join(os.getcwd(), videoDir)

    def getVideoFilePath(self):
        fullFileName = self.getFileName()
        fullFileName = os.path.join(self.getVideoDir(), fullFileName)
        return fullFileName

    def isDownloaded(self):
        return os.path.exists(self.getVideoFilePath())

    def gdriveUploadIfNeeded(self):
        if self.gdriveUpload:
            if not self.isGdriveAlreadyUploaded():
                folder = Folder(PurePath(GDRIVE_PATH))
                print('Uploading to gdrive')
                folder.upload(self.getVideoFilePath())
            else:
                print('Already uploaded to gdrive')

    def removeLocalFileIfNeeded(self):
        if self.removeLocal:
            print('removing '+self.getVideoFilePath())
            os.remove(self.getVideoFilePath())

    def isGdriveAlreadyUploaded(self):
        folder = Folder(PurePath(GDRIVE_PATH))
        file = folder.fileForName(self.getFileName())
        return file is not None

    # this method downloads the episode to the local folder, then uploads to Google Drive,
    # unless something else is specified
    def grab(self, cookies):
        print("Grabbing", self)
        url = self.makeEpisodeVideoURL(cookies)

        if self.isDownloaded() and (not self.forceReload):
            print(self.name + ' is already downloaded')
        else:
            if self.gdriveUpload and self.isGdriveAlreadyUploaded() and (not self.forceReload):
                print(self.name + ' has already been uploaded to GDrive')
            else:
                command = self.downloadCommand(url)
                os.system(command)

        self.gdriveUploadIfNeeded()
        self.removeLocalFileIfNeeded()

    # this is an overridable method
    def makeEpisodeVideoURL(self, cookies):
        pageURL = appendPathComponent(self.baseURL,self.relativeURL)
        markup = downloadTextContent(pageURL,cookies)
        soup = BeautifulSoup(markup, "html.parser")
        iframe = soup.find("iframe")
        sourceURL = iframe["src"]
        return sourceURL

    # this is an overridable method
    def downloadCommand(self, url):
        command = 'youtube-dl --no-check-certificate --add-header "Referer:https://www.pointfree.co/"  --output ' + self.getVideoFilePath() + ' ' + url
        return command

def parseEpisodesPointFree(cookies):
    baseURL = BASE_URL
    episodesPage = downloadTextContent(baseURL,cookies)
    soup = BeautifulSoup(episodesPage, "html.parser")
    episodes = []
    for h3 in soup.find_all('h1'):
        a = h3.find('a')
        if a is None:
            return None
        relativeURL = a['href']
        episode = Episode(baseURL,relativeURL)
        episodes.append(episode)
    return episodes

def main():
    cookieFileName = os.path.join(os.getcwd(), 'cookies.txt')
    cookies = loadCookies(cookieFileName)
    episodes = parseEpisodesPointFree(cookies)

    if episodes is None or len(episodes) == 0:
        print("Error parsing episodes, check your cookies")
        return

# TODO: use some nice argument parsing lib, like getopt
    # now we form the list of episodes to attempt to grab:
    if '--last' in sys.argv or '--latest' in sys.argv:
        print("Downloading last episode only")
        episodes = episodes[:1]  # only the most recent one
    elif '-e' in sys.argv:
        argInd = sys.argv.index('-e')
        ep = sys.argv[argInd+1]
        print("Downloading episode",ep)
        for episode in episodes:
            if ep in episode.name:
                episodes = [episode]  # this single one to grab
                break

    gdriveUpload = not ('--no-gdrive-upload' in sys.argv)  # by default we upload to gdrive
    removeLocal = '--remove-local' in sys.argv  # by default we leave the local files as is
    forceReload = '--force-reload' in sys.argv  # by default we don't force reloading, if the file is already uploaded to gdrive f.e.

    # we formed the list of episodes to grab, now we specify the settings and grab them
    for episode in episodes:
        episode.gdriveUpload = gdriveUpload
        episode.removeLocal = removeLocal
        episode.forceReload = forceReload
        episode.grab(cookies)

if __name__ == "__main__":
    main()
