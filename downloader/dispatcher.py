# -*- coding:utf-8 -*-
import os
import traceback
import config
import api
import tools
from tools import WebDownloader


class TaskDispatcher:
    
    def __init__(self):
        self.saveTempFile = config.saveTempFile
        self.hlsThreadCnt = config.hlsThreadCnt
        self.fragThreadCnt = config.fragThreadCnt
        self.fragmentCnt = config.fragmentCnt
        self.correctTimestamp = config.correctTimestamp
        self.tempFilePath = tools.realPath(config.tempFilePath)
        self.videoFilePath = tools.realPath(config.videoFilePath)

        self.downloader = WebDownloader(self.saveTempFile)
        self.task = None

        tools.mkdirIfNotExists(self.tempFilePath)
        tools.mkdirIfNotExists(self.videoFilePath)
        tools.checkFFmpeg()
        tools.setupRequestLogger(config.logPath)
        tools.setupDebug(config.debug)


    # hls: Download all ts segments and merge
    def _downloadHls(self, urls, fileName, headers = {}, correct = False):
        print("-- dispatcher/downloadHls")

        tempFileBase = tools.join(self.tempFilePath, fileName)
        fileNames = tools.generateFileNames(urls, tempFileBase)
        targetFileName = tools.join(self.videoFilePath, fileName + '.mp4')

        self.downloader.downloadAll(urls, fileNames, headers, self.hlsThreadCnt)
        tools.mergePartialVideos(fileNames, targetFileName, correct=correct)

        self.saveTempFile or tools.removeFiles(fileNames)
        return targetFileName

    # dash: Download audio, video and merge
    def _downloadDash(self, audioUrls, videoUrls, fileName, headers = {}):
        print("-- dispatcher/downloadDash")

        tempAudioBase = tools.join(self.tempFilePath, fileName + '.audio')
        tempVideoBase = tools.join(self.tempFilePath, fileName + '.video')
        audioNames = tools.generateFileNames(audioUrls, tempAudioBase)
        videoNames = tools.generateFileNames(videoUrls, tempVideoBase)
        targetFileName = tools.join(self.videoFilePath, fileName + '.mp4')

        self.downloader.multiThreadDownloadAll(audioUrls, audioNames, headers, \
            self.fragThreadCnt, self.fragmentCnt)
        self.downloader.multiThreadDownloadAll(videoUrls, videoNames, headers, \
            self.fragThreadCnt, self.fragmentCnt)
        tools.mergeAudio2Video(audioNames, videoNames, targetFileName)

        self.saveTempFile or tools.removeFiles(audioNames + videoNames)
        return targetFileName

    # Ordinary segmented video: download and merge
    def _downloadPartialVideos(self, urls, fileName, headers = {}):
        print("-- dispatcher/downloadPartialVideos")

        tempFileBase = tools.join(self.tempFilePath, fileName)
        fileNames = tools.generateFileNames(urls, tempFileBase)
        suffix = tools.getSuffix(urls[0])
        targetFileName = tools.join(self.videoFilePath, fileName + suffix)

        for i, url in enumerate(urls):
            self.downloader.multiThreadDownload(url, fileNames[i], headers, \
                self.fragThreadCnt, self.fragmentCnt)
        tools.mergePartialVideos(fileNames, targetFileName)

        self.saveTempFile or tools.removeFiles(fileNames)
        return targetFileName

    # websocket video stream, save to local and merge
    def handleStream(self, fileName, audioFormat, videoFormat, **desc):
        print("-- dispatcher/handleStream")

        audioName = tools.join(self.tempFilePath, fileName + '.audio' + audioFormat)
        videoName = tools.join(self.tempFilePath, fileName + '.video' + videoFormat)
        targetFileName = tools.join(self.videoFilePath, fileName + '.mp4')

        self.downloader.saveStream(audioName, videoName, **desc)
        tools.mergeAudio2Video([audioName], [videoName], targetFileName)

        self.saveTempFile or tools.removeFiles([audioName, videoName])
        print('Finish %s\n' % targetFileName)
        return targetFileName

    # Download the bullet screen and integrate it into the video file
    def handleSubtitles(self, subtitles, fileName, videoName, headers = {}):
        subtitleUrls, subtitleNames = [], []
        subtitlesInfo = []

        for name, url in subtitles:
            subtitleUrls.append(url)
            subtitleName = tools.join(self.tempFilePath, '%s_%s%s' % \
                (fileName, name, tools.getSuffix(url)))
            subtitleNames.append(subtitleName)
            subtitlesInfo.append((name, subtitleName))

        self.downloader.downloadAll(subtitleUrls, subtitleNames, headers, self.hlsThreadCnt)

        for each in subtitleNames:
            tools.tryFixSrtFile(each)
        
        targetFileName = tools.integrateSubtitles(subtitlesInfo, videoName)
        self.saveTempFile or tools.removeFiles(subtitleNames)
        return targetFileName


    def download(self, url, fileName, data = None):
        fileName = tools.escapeFileName(fileName)
        videoType, headers, audioUrls, videoUrls, subtitles = api.parseSingleUrl(url, data)

        if audioUrls:
            print('Match to %d audio and %d video, start downloading' % (len(audioUrls), len(videoUrls)))
        else:
            print('Matched %d videos, start downloading' % len(videoUrls))

        targetFileName = ''
        if videoType == 'hls':
            # When subtitle files exist, use binary merge to correct the timestamp
            correct = self.correctTimestamp or bool(subtitles)
            targetFileName = self._downloadHls(videoUrls, fileName, headers, correct)
        elif videoType == 'dash':
            targetFileName = self._downloadDash(audioUrls, videoUrls, fileName, headers)
        elif videoType == 'partial':
            targetFileName = self._downloadPartialVideos(videoUrls, fileName, headers)

        if subtitles:
            print('%d subtitles are matched, start downloading' % len(subtitles))
            targetFileName = self.handleSubtitles(subtitles, fileName, targetFileName, headers)

        print('Finish: %s\n' % targetFileName)


    def downloadMultiParts(self, url, baseFileName, pRange):
        startP, endP, allPartInfo = api.parseMultiPartUrl(url, pRange)

        print('Ready to download %d-%dP\n' % (startP, endP))

        for i in range(startP-1, endP):
            partName, videoUrl = allPartInfo[i]['name'], allPartInfo[i]['videoUrl']
            fileName = 'P%03d__%s__%s' % (i + 1, baseFileName, partName)
            print('Start download %d P: %s' % (i + 1, fileName))
            self.download(videoUrl, fileName)

    def dispatch(self, **task):
        self.task = task
        task['type'] = task.get('type', 'link')
        print()

        try:
            if task['type'] == 'link':
                url, fileName = task.get('linksurl') or task['url'], task['fileName']
                data = task.get('data')
                if task.get('pRange'):
                    self.downloadMultiParts(url, fileName, task['pRange'])
                else:
                    self.download(url, fileName, data)
            elif task['type'] == 'stream':
                self.handleStream(**task)
        except Exception as e:
            print('-' * 100)
            traceback.print_exc()
            print('-' * 100)
        except KeyboardInterrupt:
            self.shutdown()
        finally:
            task['type'] == 'stream' and task['close']()
            self.task = None

    def shutdown(self):
        if self.task:
            task = self.task
            self.task = None

            if task['type'] == 'stream':
                task['dataQueue'].put(KeyboardInterrupt())
            self.downloader.shutdownAndClean()