from PIL import Image, ImageDraw, ImageFont, ImageColor
import os
from random import randint, choice
from textwrap import wrap
from datetime import datetime

PAGE = (1600, 2064)
RATIO = PAGE[1] / PAGE[0]
PADDING = 15
PAGECOLOR = (255, 255, 255)
FONTCOLOR = (255, 255, 255)
COMICBOOKDIR = "comic/"
R = randint(0, 100)
G = randint(0, 100)
B = randint(0, 100)

class font():
    ratio = 0.0
    face = ""
    def __init__(self, path, ratio):
        self.face = path
        self.ratio = ratio
    
TITLEFONT = font("comtube/fonts/modeseven.ttf", .63)
BODYFONT = font("comtube/fonts/zig.ttf", .81)

def createComicBook(videoData):
    path = makeComicBookDir()
    createTitlePage(videoData.videoId, videoData.cover)
    i = 1
    # n must be divisible by three (my preference)
    for clips in yieldEveryN(videoData.clips, 6):
        createPage(i, clips)
        i += 1
    createConclusionPage(i, videoData.videoUrl, videoData.cover)
    print(f"[log] {path}")

def createTitlePage(videoId, cover):
    page = Image.new("RGB", PAGE, PAGECOLOR)
    coverImg = Image.open(cover)
    coverImg = cropAndResizeWithinBoundaries(coverImg, PAGE[0], PAGE[1])
    coverImg = comicize(coverImg)
    page.paste(coverImg, (0, 0))
    page = addText(page, videoId, ["center", "center"], 150, font=TITLEFONT)
    page = addText(page, f"a YouTube Comic\n-\n{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ["center", "bottom"], 72)
    path = COMICBOOKDIR + "0.png"
    page.save(path)
    print(f"[log] {path}")

def createPage(pageNumber, clips):
    page = Image.new("RGB", PAGE, PAGECOLOR)
    w, h = page.size
    innerWidth = int(w - (PADDING * 2))
    innerHeight = int(h - (PADDING * 2))
    rowWidth = innerWidth
    rowHeight = int((innerHeight - (PADDING * 2)) / 3)
    currentX = PADDING
    currentY = PADDING
    for rowClips in yieldEveryN(clips, int(len(clips) / 3) if len(clips) > 1 else 1):
        page.paste(createRow(rowClips, rowWidth, rowHeight), (currentX, currentY))
        currentY += (rowHeight + PADDING)
    # FIXME: test this to make sure the page numbers have enough room
    page = addText(page, str(pageNumber), ["center", "page-number"], 20, fill=(0, 0, 0))
    path = f"{COMICBOOKDIR}{pageNumber}.png"
    page.save(path)
    print(f"[log] {path}")

def createRow(clips, w, h):
    print(f"[trace] createRow(clips: {len(clips)} ...))")
    if len(clips) > 4:
        raise ValueError("At most, 4 pictures per row are possible")
    row = Image.new("RGB", (w, h), PAGECOLOR)
    realEstate = w
    currentX = 0
    currentY = 0
    i = 0
    for clip in clips:
        idealWidth = int(realEstate / len(clips[i:]))
        if i + 1 < len(clips):
            frameWidth = randint(int(idealWidth * .8), idealWidth)
        else:
            frameWidth = idealWidth
        frameHeight = h
        row.paste(createFrame(clip, frameWidth, frameHeight), (currentX, currentY))
        realEstate = w - currentX
        currentX += (frameWidth + PADDING)
        i += 1
    return row

# https://dzone.com/articles/image-processing-in-python-with-pillow
def createFrame(clip, w, h):
    print(f"[trace] createFrame({clip.frame} ...)")
    frame = Image.open(clip.frame)
    frame = cropAndResizeWithinBoundaries(frame, w, h)
    frame = comicize(frame)
    textImg = Image.new("RGBA", (int(w * .8), int(h * .8)), (255, 255, 255, 0))
    textImgWidth, textImgHeight = textImg.size
    point = int(textImgHeight * .05)
    textImg = addText(textImg, clip.context, ["random", "random"], point, int((textImgWidth * .75) / (BODYFONT.ratio * point)))
    theta = randint(-15, 15)
    textImg = textImg.rotate(theta)
    frame.paste(textImg, (randint(int(textImgWidth * .05), int(w - textImgWidth - (w * .05))), randint(int(textImgHeight * .05), h - textImgHeight)), textImg)
    return frame

def createConclusionPage(pageNumber, videoUrl, cover):
    page = Image.open(cover)
    page = cropAndResizeWithinBoundaries(page, PAGE[0], PAGE[1])
    page = comicize(page)
    page = addText(page, f"The End\n-\n{videoUrl}", ["center", "center"], 40, font=TITLEFONT)
    page = addText(page, str(pageNumber), ["center", "page-number"], 20)
    path = f"{COMICBOOKDIR}{pageNumber}.png"
    page.save(path)
    print(f"[log] {path}")

def comicize(img):
    print(f"[trace] comicize({img})")
    # NOTE: expiremental
    j = 100
    data = img.getdata()
    r1 = avg([i[0] for i in data if i[0] >= j])
    r2 = avg([i[0] for i in data if (i[0] < j)])
    g1 = avg([i[1] for i in data if i[1] >= j])
    g2 = avg([i[1] for i in data if (i[1] < j)])
    b1 = avg([i[2] for i in data if i[2] >= j])
    b2 = avg([i[2] for i in data if (i[2] < j)])
    newData = []
    for item in data:
        r = 0
        g = 0
        b = 0
        if item[0] >= j:
            r = r1
        else:
            r = r2
        if item[1] >= j:
            g = g1
        else:
            g = g2
        if item[2] >= j:
            b = b2
        else:
            b = b2
        newData.append((r + R, g + G, b + B))
    img.putdata(newData)
    return img

def tupleAvg(t):
    return (avg(t[0]), avg(t[1]), avg(t[2]))

def avg(l):
    return int(sum(l) / len(l)) if len(l) > 0 else randint(0, 255)

def cropAndResizeWithinBoundaries(img, desiredW, desiredH):
    height = img.size[1]
    width = img.size[0]
    ratio = desiredH / desiredW
    newWidth, newHeight = getWidthAndHeightViaRatio(height, ratio)
    i = 0
    while (newWidth > width) and (i <= height):
        newWidth, newHeight = getWidthAndHeightViaRatio(height - i, ratio)
        i += 1
    x0 = randint(0, width - newWidth)
    y0 = randint(0, height - newHeight)
    x = x0 + newWidth
    y = y0 + newHeight
    cropped = img.crop((x0, y0, x, y))
    return cropped.resize((desiredW, desiredH))

def getWidthAndHeightViaRatio(h, r):
    newHeight = randint(int(h * .9), h)
    newWidth = int(newHeight / r)
    return (newWidth, newHeight)

def addText(img, text, align, point, width=0, fill=FONTCOLOR, font=BODYFONT):
    if width == 0:
        width = max(len(l) for l in text.split("\n"))
    w, h = img.size
    x = 0
    y = 0
    breadth = int(point * width * font.ratio)
    height = int(point * len(text.split("\n")))
    draw = ImageDraw.Draw(img)
    if align[0] == "center":
        x = int((w - breadth) * .5)
    elif align[0] == "right":
        x = int(w - breadth)
    elif align[0] == "left":
        x = 0
    elif align[0] == "random":
        x = randint(0, w - breadth)
    if align[1] == "center":
        y = int(h * .5) - (height)
    elif align[1] == "top":
        y = int(0) + (point)
    elif align[1] == "bottom":
        y = int(h) - (height) - (point)
    elif align[1] == "random":
        y = randint(height, h - (height))
    elif align[1] == "page-number":
        y = int(h) - int(((PADDING - height) * .5) + height)
    thisFont = ImageFont.truetype(font.face, point)
    draw.text((x, y), wrapText(text, width, align[0]), font=thisFont, fill=fill)
    return img

def wrapText(text, width, align):
    ret = ""
    for blob in text.split("\n"):
        blobtext = wrap(blob, width)
        for line in blobtext:
            if align == "center":
                line = f"{line : ^{width}}"
            if align == "right":
                line = f"{line : >{width}}"
            if align == "left":
                line = f"{line : <{width}}"
            ret += line + "\n"
    return ret

# preserves old comic books
def makeComicBookDir():
    global COMICBOOKDIR
    path = COMICBOOKDIR
    i = 0
    while os.path.isdir(path):
        i += 1
        path = COMICBOOKDIR.replace("/", str(i)) + "/"
    os.mkdir(path)
    COMICBOOKDIR = path
    return path

def yieldEveryN(l, n):
    count = len(l)
    i = 0
    ret = []
    while i < count:
        ret.append(l[i])
        i += 1
        if i % n == 0:
            yield ret
            ret = []
    if len(ret) > 0:
        yield ret
