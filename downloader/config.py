# -*- coding:utf-8 -*-
import tools


args = tools.getArguments({
    'name': '-t:h',
    'metavar': 'N',
    'type': int,
    'default': 8,
    'help': 'the thread count of hls download, default 8',
}, {
    'name': '-t:f',
    'metavar': 'N',
    'type': int,
    'default': 8,
    'help': 'the thread count of fragments download, default 8',
}, {
    'name': '-f',
    'metavar': 'N',
    'type': int,
    'default': 0,
    'help': 'the fragments count of each file, default 0 using the thread count',
}, {
    'name': '-p',
    'metavar': 'PORT',
    'type': int,
    'default': 18888,
    'help': 'the port that the backend server listens on, default 18888',
}, {
    'name': ['-c', '--correct'],
    'action': 'store_true', 
    'help': 'correct the timestamp of hls video, merge fragments using binnary mode',
}, {
    'name': '-s',
    'action': 'store_true', 
    'help': 'if set, will save the temp files',
}, {
    'name': '-d',
    'action': 'store_true', 
    'help': 'debug mode, log more info and save the temp files (ignore -s)',
}, {
    'name': '-i',
    'action': 'store_true', 
    'help': 'interactive mode, get url and file name from the command line',
})


# hls download thread count
hlsThreadCnt = getattr(args, 't:h')

# Number of segmented download threads
fragThreadCnt = getattr(args, 't:f')

# Number of segments downloaded in segments
fragmentCnt = getattr(args, 'f')

# The port that the server listens to in daemon mode
port = getattr(args, 'p')

# Whether to correct the hls video timestamp
correctTimestamp = getattr(args, 'correct')

# Debug mode
debug = getattr(args, 'd')

# Whether to keep downloaded temporary files (option ignored in debug mode)
saveTempFile = debug or getattr(args, 's')

# Interactive mode
interactive = getattr(args, 'i')

# Temporary file save path
tempFilePath = "../temp/"

# Video file save path
videoFilePath = "../videos/"

# Log file save path
logPath = './logs/'
