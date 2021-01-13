"""Structs"""

import re
import cc
import bubbling

class videoData:
    videoUrl = ""
    videoId = ""
    transcript = []
    transcriptRaw = ""
    length = 0.0
    path = ""
    frames = 0
    context = ""
    clips = []
    cover = ""
    def __init__(self):
        self.videoUrl = promptVideoUrl()
        self.videoId = getVideoId(self.videoUrl)
        self.transcript = cc.fetchTranscript(self.videoId)
        self.transcriptRaw = cc.fetchTranscriptRaw(self.transcript)
        self.length = getVideoLength(self.transcript)
        self.path = bubbling.fetchVideo(self.videoUrl, self.videoId)
        self.frames = bubbling.getFrames(self.path, self.videoId)
        self.context = cc.determineContext(self.transcriptRaw)
        self.clips = [self.fetchInterval(i[0], i[1]) for i in getClipIntervals(self.length)]
        self.cover = bubbling.getRandomFrame()
    def fetchInterval(self, a, b):
        return videoClipData(
            start = a,
            end = b,
            transcript = cc.fetchInterval(self.transcript, a, b),
            transcriptRaw = cc.fetchIntervalRaw(self.transcript, a, b),
            length = b - a,
            frames = bubbling.getFramesInInterval(a, b, self.length, self.frames),
        )

class videoClipData:
    start = 0
    end = 0
    transcript = []
    transcriptRaw = ""
    length = 0.00
    frame = ""
    context = ""
    def __init__(self, start, end, transcript, transcriptRaw, length, frames):
        self.start = start
        self.end = end
        self.transcript = transcript
        self.transcriptRaw = transcriptRaw
        self.length = length
        self.context = cc.determineContext(self.transcriptRaw)
        self.frame = bubbling.getRandomFrame(frames)

def promptVideoUrl():
    txt = "Video url: "
    url = input(txt)
    while ("http" not in url) and ("youtube" not in url):
        print("Something like 'https://www.youtube.com/watch?v=o3_XAksahQA'")
        url = input(txt)
    return url

def getVideoId(url):
    m = re.search("watch\?v=(.*)&?", url).group(1).strip()
    print(f"[info] {m}")
    return m

def getVideoLength(transcript):
    startAndDuration = [(i["start"], i["duration"]) for i in transcript ]
    t = 0.00
    for i in startAndDuration:
        if i[0] > t:
            t = i[0] + i[1]
    if t <= 30:
        raise ValueError("Video must be longer than 30 seconds")
    return t

def getClipIntervals(videoLength):
    step = 15
    current = 0
    intervals = []
    while current < videoLength:
        intervals.append((current, current + step))
        current += step
    return intervals
    
# DEBUG: these videos work
# https://www.youtube.com/watch?v=qMKD_b0eGSA
# https://www.youtube.com/watch?v=buKpcZOYuJc
