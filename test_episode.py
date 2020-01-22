from unittest import TestCase
from grab import *

class TestEpisode(TestCase):
    def setUp(self):
        baseURL = 'http://base.com/'
        self.episode = Episode(baseURL, '/episodes/S01E01-good')

    def test_fullName(self):
        self.assertEqual(self.episode.name, 'S01E01-good')

    def test_shortName(self):
        self.assertEqual(self.episode.shortName, 'S01E01')

    def test_getFullFileName(self):
        shortFilename = self.episode.getFileNameMP4(self.episode.shortName)
        self.assertEqual('S01E01.mp4', shortFilename)
        fullFilename = self.episode.getFileNameMP4(self.episode.name)
        self.assertEqual('S01E01-good.mp4', fullFilename)

    def test_getFullFilePath(self):
        fullFilePath = self.episode.getVideoFilePath()
        expected = os.path.join(os.getcwd(),VIDEOS_DIR,'S01E01-good.mp4')
        self.assertEqual(expected, fullFilePath)

    def test_getVideoDir(self):
        dir = '~/Movies' # absolute path but with a user home dir
        self.episode.videoDir = dir
        expected = os.path.expanduser(dir)
        self.assertEqual(expected, self.episode.getVideoDir())

        dir = '/Library/Movies' # absolute path
        self.episode.videoDir = dir
        expected = dir
        self.assertEqual(expected, self.episode.getVideoDir())

        dir = 'relative' #relative path
        self.episode.videoDir = dir
        expected = os.path.abspath(dir)
        self.assertEqual(expected, self.episode.getVideoDir())