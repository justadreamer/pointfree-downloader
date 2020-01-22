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

# global functions:
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

class Strategy:
    def loadCookies(self):
        cookieFilePath = os.path.join(os.getcwd(), self.cookieFileName)
        self.cookies = loadCookies(cookieFilePath)


class PointFreeStrategy(Strategy):
    def __init__(self):
        self.BASE_URL = 'https://www.pointfree.co/'
        self.VIDEOS_DIR = '~/Movies/PointFree'
        self.GDRIVE_PATH = 'Screencasts/PointFree'
        self.cookieFileName = 'cookies-pointfree.txt'
        self.loadCookies()

    def parseEpisodes(self):
        episodesPage = downloadTextContent(self.BASE_URL, self.cookies)
        soup = BeautifulSoup(episodesPage, "html.parser")
        episodes = []
        for h3 in soup.find_all('h1'):
            a = h3.find('a')
            if a is None:
                return None
            relativeURL = a['href']
            episode = Episode(self, relativeURL)
            episodes.append(episode)
        return episodes

    # this is an overridable method
    def makeEpisodeVideoURL(self, relativePageURL):
        pageURL = appendPathComponent(self.BASE_URL, relativePageURL)
        markup = downloadTextContent(pageURL, self.cookies)
        soup = BeautifulSoup(markup, "html.parser")
        iframe = soup.find("iframe")
        sourceURL = iframe["src"]
        return sourceURL

    # this is an overridable method
    def downloadCommand(self, url, outputFilePath):
        command = 'youtube-dl -c --no-check-certificate --add-header "Referer:https://www.pointfree.co/"  --output ' + outputFilePath + ' ' + url
        return command


class SwiftTalkStrategy(Strategy):
    def __init__(self):
        self.BASE_URL = 'https://talk.objc.io/'
        self.VIDEOS_DIR = '~/Movies/SwiftTalk'
        self.GDRIVE_PATH = 'Screencasts/SwiftTalk'
        self.cookieFileName = 'cookies-swifttalk.txt'
        self.loadCookies()

    def parseEpisodes(self):
        episodesPage = downloadTextContent(self.BASE_URL + '/episodes', self.cookies)
        soup = BeautifulSoup(episodesPage, "html.parser")
        episodes = []
        for h3 in soup.find_all('h3'):
            a = h3.find('a')
            if a is None:
                return None
            relativeURL = a['href']
            episode = Episode(self, relativeURL)
            episodes.append(episode)
        return episodes

    def makeEpisodeVideoURL(self, relativePageURL):
        pageURL = appendPathComponent(self.BASE_URL, relativePageURL)
        return pageURL

    def downloadCommand(self, url, outputFilePath):
        command = 'youtube-dl -c --no-check-certificate --cookies ' + self.cookieFileName + ' --output ' + outputFilePath + ' ' + url
        return command

class Episode:
    def __init__(self, strategy, relativeURL):
        # set from outside:
        self.strategy = strategy
        self.relativeURL = relativeURL
        self.ext = 'mp4'
        self.gdriveUpload = True # by default it is true
        self.removeLocal = False
        self.forceDownload = False
        self.forceUpload = False
        self.videoDir = strategy.VIDEOS_DIR

        # computed and cached:
        self.name = self.getEpisodeName()
        self.fileName = self.getFileNameMP4()

    def __str__(self):
        return "Episode: " + self.name

    def __repr__(self):
        return self.__str__()

    def getEpisodeName(self):
        components = self.relativeURL.split('/')
        return components[len(components)-1]

    def getFileNameMP4(self):
        return self.name + '.mp4'

    def getFileNameM2TS(self):
        return self.name + '.m2ts'

    def getVideoDir(self):
        videoDir = os.path.expanduser(self.videoDir)
        if not os.path.isabs(videoDir):
            videoDir = os.path.join(os.getcwd(), videoDir)
        if not os.path.exists(videoDir):
            os.makedirs(videoDir, exist_ok = True)
        return videoDir

    def getVideoFilePath(self):
        fullFileName = self.getFileNameMP4()
        fullFileName = os.path.join(self.getVideoDir(), fullFileName)
        return fullFileName

    def isDownloaded(self):
        return os.path.exists(self.getVideoFilePath())

    def gdriveUploadIfNeeded(self):
        if self.gdriveUpload:
            if not self.isGdriveAlreadyUploaded() or self.forceUpload:
                folder = Folder(PurePath(self.strategy.GDRIVE_PATH))
                print('Uploading to GDrive')
                if os.path.exists(self.getVideoFilePath()):
                    folder.upload(self.getVideoFilePath())
            else:
                print('Already uploaded to GDrive and no --force-upload flag provided')

    def removeLocalFileIfNeeded(self):
        if self.removeLocal:
            print('removing '+self.getVideoFilePath())
            os.remove(self.getVideoFilePath())

    def isGdriveAlreadyUploaded(self):
        folder = Folder(PurePath(self.strategy.GDRIVE_PATH))
        filemp4 = folder.fileForName(self.getFileNameMP4())
        filem2ts = folder.fileForName(self.getFileNameM2TS())
        return (filemp4 is not None) or (filem2ts is not None)

    # this method downloads the episode to the local folder, then uploads to Google Drive,
    # unless something else is specified
    def grab(self):
        print("Grabbing", self)
        url = self.strategy.makeEpisodeVideoURL(self.relativeURL)

        if self.isDownloaded() and (not self.forceDownload):
            print(self.name + ' is already downloaded locally')
        else:
            if self.gdriveUpload and self.isGdriveAlreadyUploaded() and not self.forceDownload:
                print(self.name + ' has already been uploaded to GDrive, not downloading locally since no --force-download flag provided')
            else:
                command = self.strategy.downloadCommand(url, self.getVideoFilePath())
                os.system(command)

        self.gdriveUploadIfNeeded()
        self.removeLocalFileIfNeeded()

def main():
    if '--swift-talk' in sys.argv:
        strategy = SwiftTalkStrategy()
    else:
        strategy = PointFreeStrategy()

    episodes = strategy.parseEpisodes()

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
    forceUpload = '--force-upload' in sys.argv  # by default we don't force reloading, if the file is already uploaded to gdrive f.e.
    forceDownload = '--force-download' in sys.argv  # by default we don't force reloading, if the file is already uploaded to gdrive f.e.

    # we formed the list of episodes to grab, now we specify the settings and grab them
    for episode in episodes:
        episode.gdriveUpload = gdriveUpload
        episode.removeLocal = removeLocal
        episode.forceUpload = forceUpload
        episode.forceDownload = forceDownload
        episode.grab()

if __name__ == "__main__":
    main()
