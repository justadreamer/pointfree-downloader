from unittest import TestCase
from download import *


class TestEpisode(TestCase):
    def setUp(self):
        self.episode = Episode(baseURL, '/episodes/S01E01-good')

    def test_fullName(self):
        self.assertEqual(self.episode.fullName, 'S01E01-good')

    def test_shortName(self):
        self.assertEqual(self.episode.shortName, 'S01E01')

    def test_getFullFileName(self):
        shortFilename = self.episode.getFileName(self.episode.shortName)
        self.assertEqual(shortFilename, 'S01E01.m2ts')
        fullFilename = self.episode.getFileName(self.episode.fullName)
        self.assertEqual(fullFilename, 'S01E01-good.m2ts')

    def test_getFullFilePath(self):
        fullFilePath = self.episode.getVideoFilePath()
        self.assertEqual(fullFilePath, os.path.join(os.getcwd(),VIDEOS_DIR,'S01E01-good.m2ts'))

    def test_getChunksDir(self):
        self.assertEqual(self.episode.getChunksDir(),os.path.join(os.getcwd(),CHUNKS_DIR,'S01E01-good'))
