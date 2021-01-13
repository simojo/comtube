import cv2 as cv
import youtube_dl
from cc import getNouns
from random import choice
import os
from re import findall

FRAMESDIR = "frames/"

# NOTE: returns path to video (no way am I gonna let python hold a video in memory)
def fetchVideo(url, vidId):
    path = vidId + ".mp4"
    if os.path.exists(path):
        print(f"[info] {path} already downloaded")
        return path
    ydl_opts = {
        "restrictfilenames": True,
        "outtmpl": "%(id)s.mp4"
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return path

# https://www.geeksforgeeks.org/detect-an-object-with-opencv-python/
def getRandomFrame(frames = []):
    if len(frames) == 0:
        return FRAMESDIR + choice(os.listdir(FRAMESDIR))
    else:
        return FRAMESDIR + choice(frames)

def getFramesInInterval(start, end, totalLength, totalFrames):
    startRatio = start / totalLength
    endRatio = end / totalLength
    validFrames = []
    for i in range(1, totalFrames + 1):
        if (i / totalFrames > startRatio) and (i / totalFrames < endRatio):
            validFrames.append(f"{i}.png")
    return validFrames

# https://www.tutorialexample.com/python-capture-images-from-video-by-frames-using-opencv-a-complete-guide/
def getFrames(path, videoId):
    global FRAMESDIR
    FRAMESDIR = FRAMESDIR.replace("/", videoId + "/")
    if os.path.isdir(FRAMESDIR) and len(os.listdir(FRAMESDIR)) > 10:
        print(f"[info] {FRAMESDIR} already downloaded")
        fnames = []
        for i in os.listdir(FRAMESDIR):
            m = findall(r"\d+", i)
            if len(m) > 0:
                fnames.append(int(m[0]))
        return max(fnames)
    createFramesFolder()
    cap = cv.VideoCapture(path)
    if not cap.isOpened():
        raise SystemError("VideoCapture failed to open")
    frameFrequency = 60
    total_frame = 0
    index = 0
    while True:
        ret, frame = cap.read()
        if ret is False:
            break
        total_frame += 1
        if total_frame%frameFrequency == 0:
            index += 1
            image_name = FRAMESDIR + str(index) + ".png"
            cv.imwrite(image_name, frame)
            print(f"[log] {image_name}", end="\r")
    print()
    cap.release()
    return index

def createFramesFolder():
    global FRAMESDIR
    if not os.path.isdir(FRAMESDIR):
        os.mkdir(FRAMESDIR)
    else:
        for f in os.listdir(FRAMESDIR):
            os.remove(os.path.join(FRAMESDIR, f))

def removeFramesFolder():
    global FRAMESDIR
    if os.path.isdir(FRAMESDIR):
        for f in os.listdir(FRAMESDIR):
            os.remove(os.path.join(FRAMESDIR, f))
        os.remove(FRAMESDIR)
