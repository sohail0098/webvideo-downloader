# webvideo-downloader

![](https://img.shields.io/badge/platform-win%20%7C%20linux%20%7C%20osx-brightgreen) ![](https://img.shields.io/badge/python-%3E=%203.5.0-orange)

🚀 Video downloader, to download videos from streaming websites.

---

## Table of Contents

- [Supported websites](#Sites)
- [Features](#Features)
- [Quickstart](#Quickstart)
  - [Installation](#Installation)
  - [Running](#Running)
- [Changelog](#Changelog)

## Sites

| Site                                | URL                                                    | Normal Videos | VIP exclusive |
| ------------------------------------- | ------------------------------------------------------ | -------- | ------- |
| Bilibili (single Part/multiple Part)                   | [https://www.bilibili.com/](https://www.bilibili.com/) | ✓        | ✓       |
| IQIYI     | [https://www.iqiyi.com/](https://www.iqiyi.com/)                       | ✓        | ✓       |
| Tencent Video         | [https://v.qq.com/](https://v.qq.com/)                          | ✓        | ✓       |
| Mango TV       | [https://www.mgtv.com/](https://www.mgtv.com/)                        | ✓        | ✓       |
| WeTV             | [https://wetv.vip/](https://wetv.vip/)                              | ✓        | ✓ |
| IQiyi International   | [https://www.iq.com/](https://www.iq.com/)                    | ✓        | ✓       |

In addition, optional [CommonHlsDownloader](https://github.com/jaysonlong/webvideo-downloader/raw/master/violentmonkey/CommonHlsDownloader.user.js) scripting support is available, mostly based on HLS Streaming video sites, such as [Youtube](https://youtube.com/) or [LPL official website](https://lpl.qq.com/) etc.

## Features

#### *Download features*

- Cross-platform（Windows/Linux/Mac）
- Multi-threaded download (single file/multiple files parallel download)
- Subtitle download and merge (videos with merged subtitles need to be played with a player that supports internal subtitles, such as `MPV`, `MPC-HC`, `PotPlayer`，`VLC Player`, `MX Player` etc.）

#### *About VIP*

This project supports downloading **1080p, VIP exclusive, VIP on-demand, and paid video** content, provided that you are a using a VIP account.

> **Whatever you can watch can be downloaded.**
>
> You can only download the videos that you or your account can watch online. There is no VIP cracking/hacking function in this project.


## Quickstart

### Installation

##### *Required programs*

This project utilises [Python](https://www.python.org/)、[FFmpeg](https://ffmpeg.org/) and the browser extension [Violentmonkey](https://violentmonkey.github.io/)/[Tampermonkey](https://www.tampermonkey.net/)：

- [Python](https://www.python.org/) (3.5 or above)
- [FFmpeg](https://ffmpeg.org/) (Not required on windows, binary is already in the folder)
- [Violentmonkey](https://violentmonkey.github.io/) /  [Tampermonkey](https://www.tampermonkey.net/) (Choose any one of the two)

##### *Getting Started*

Download the repo zip or use git clone：

```
git clone https://github.com/jaysonlong/webvideo-downloader.git
```

##### *Project Installation*

Install any of the following Violentmonkey/Tampermonkey Scripts. Simply click the link to install:

- [WebVideoDownloader](https://github.com/jaysonlong/webvideo-downloader/raw/master/violentmonkey/WebVideoDownloader.user.js)

- [CommonHlsDownloader](https://github.com/jaysonlong/webvideo-downloader/raw/master/violentmonkey/CommonHlsDownloader.user.js)（Optional. Universal HLS download script, works on **all** websites that use HLS）

Install python dependencies：

```
cd webvideo-downloader/downloader
pip install -r requirements.txt
```

(Optional) Install an ad blocker in your browser:
- [AdGuard Ad-blocker](https://adguard.com/)

> If a website has ads in the video, the script will be delayed until the advertisement is about to end before the video link can be retrieved. Installing an ad-blocker will allow you to skip the advertisement therefore removing the need to wait.

### Running

> This project is divided into two parts. The javascript script in the **Violentmonkey** directory is used to extract video links in the browser, and the python script in the **Downloader** directory is used to download and merge videos.

First execute the python script：

```
python daemon.py
```

Then visit the video website and click on a video, you will be presented with a pop up download button, click the button to download.

Example：https://www.bilibili.com/video/BV1c741157Wb

![bilibili](img/bilibili.gif)

The download progress can be viewed in the command window of the python script：

```
$ python daemon.py
Listening on port 18888 for clients...

Receive: {
    "fileName": "Some File Name",
    "linksurl": "http://xxx",
    "type": "link"
}

Handle: "Some File Name"

Match 1 segment of audio, 1 segment of video, start downloading
-- dispatcher/downloadDash
Downloading E:\Workspace\Github\webvideo-downloader\temp\Some File Name.audio.m4s
Downloading 8 segments, 8 threads in parallel
Progress: [########################################] 100%    0.9/0.9MB  450KB/s 0s
Downloading E:\Workspace\Github\webvideo-downloader\temp\Some File Name.video.m4s
Downloading 8 segments, 8 threads in parallel
Progress: [########################################] 100%  11.2/11.2MB  5.2MB/s 2s
Merging Files
Finish.
```

> The download directory defaults to the videos folder under the project root directory, which can be configured in downloader/config.py.

Python script optional command line parameters:

```
$ python daemon.py -h
usage: daemon.py [-h] [-t:h N] [-t:f N] [-f N] [-p PORT] [-c] [-s] [-d] [-i]

optional arguments:
  -h, --help     show this help message and exit
  -t:h N         the thread count of hls download, default 8
  -t:f N         the thread count of fragments download, default 8
  -f N           the fragments count of each file, default 0 using the thread count
  -p PORT        the port that the backend server listens on, default 18888
  -c, --correct  correct the timestamp of hls video, merge fragments using binnary mode
  -s             if set, will save the temp files
  -d             debug mode, log more info and save the temp files (ignore -s)
  -i             interactive mode, get url and file name from the command line
```



## Changelog

### [v2.0] - 2020-11-09

#### Add

- Support Tencent video long segment download (video uploaded by the user)
- Support VIP download of iQiyi International Station, WeTV download without subtitles
- Add debug mode

#### Change

- Combine daemon mode and interactive mode into one python script
- Disable WebAssembly extension in iQiyi International Station (iq.com) to prevent subtitle encryption

### [v1.6] - 2020-09-12

#### Add

- Support iqiyi international station video download
- Support multiple subtitle files integrated into the video

### [v1.5] - 2020-09-01

#### Add

- Support WeTV, iQiyi Taiwan station video download
- Support part of the website subtitle files integrated into the video
- Download file integrity check

#### Change

- MP4 file moov box front for easy network transmission

### [v1.4] - 2020-06-30

#### Change

- Port reuse in daemon mode, and its listening mode supports both HTTP Server and WebSocket
- Violent monkey script can customize the remote call mode (HTTP or WebSocket)

### [v1.3] - 2020-06-27

#### Change

- Violent Monkey Script Refactoring & Interface Rewriting

### [v1.2] - 2020-06-18

#### Add

- Support iQIYI MPD format file analysis
- Support MSE video stream export via WebSocket (experimental)
- Two new violent monkey scripts: general hls download script and MSE video stream export script (experimental)
- Command line parameter support

#### Change

- The monitoring mode of the daemon mode is changed from HTTP Server to WebSocket 
- Bilibili multi-P download script merged into universal download script

### [v1.1] - 2020-05-29

#### Add

- Supports running in daemon mode based on HTTP Server, the browser clicks on the link to directly call the background download

#### Change

- Combine 4 website scripts into a single, easy to install and manage

### [v1.0] - 2020-05-26

#### Add

- Support Bilibili, iQiyi, Tencent Video, Mango TV video download (manually copy and paste the link)
  
[v2.0]: https://github.com/jaysonlong/webvideo-downloader/compare/v1.6...v2.0
[v1.6]: https://github.com/jaysonlong/webvideo-downloader/compare/v1.5...v1.6
[v1.5]: https://github.com/jaysonlong/webvideo-downloader/compare/v1.4...v1.5
[v1.4]: https://github.com/jaysonlong/webvideo-downloader/compare/v1.3...v1.4
[v1.3]: https://github.com/jaysonlong/webvideo-downloader/compare/v1.2...v1.3
[v1.2]: https://github.com/jaysonlong/webvideo-downloader/compare/v1.1...v1.2
[v1.1]: https://github.com/jaysonlong/webvideo-downloader/compare/v1.0...v1.1
[v1.0]: https://github.com/jaysonlong/webvideo-downloader/releases/tag/v1.0
