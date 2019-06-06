from scipy.spatial import distance as dist
import numpy as np
import cv2
from matplotlib import pyplot as plt
import argparse
import glob

# movie1 = [cv2.imread(file) for file in glob.glob("movie1/*.png")]

def createHistograms(image):
    color_values = ('b','g','r')
    random_x = np.random.rand(1000)
    for i,col in enumerate(color_values):
        histogram = cv2.calcHist([image],[i],None,[256],[0,256])
        plt.plot(histogram, color = col)
        plt.xlim([0,256])
        plt.hist(random_x, bins=20)
    plt.show()

def createHistogram_blue(image):
    histogram = cv2.calcHist([image],[0],None,[256],[0,256])
    return histogram

def createHistogram_green(image):
    histogram = cv2.calcHist([image],[1],None,[256],[0,256])
    return histogram

def createHistogram_red(image):
    histogram = cv2.calcHist([image],[2],None,[256],[0,256])
    return histogram

def HistogramComparitor(histogram1,histogram2):
    distance = cv2.compareHist(histogram1,histogram2,cv2.HISTCMP_BHATTACHARYYA)
    #print "distance"
    #print distance
    return distance

def histogramList(image):
    redHistogram = createHistogram_red(image)
    blueHistogram = createHistogram_blue(image)
    greenHistogram = createHistogram_green(image)
    histograms = []
    histograms.append(redHistogram)
    histograms.append(blueHistogram)
    histograms.append(greenHistogram)
    return histograms

def averageHistogramPoint(image1,image2):
    blueHistogram = createHistogram_blue(image1)
    blueHistogram2 = createHistogram_blue(image2)
    greenHistogram = createHistogram_green(image1)
    greenHistogram2 = createHistogram_green(image2)
    redHistogram = createHistogram_red(image1)
    redHistogram2 = createHistogram_red(image2)
    blue_point = HistogramComparitor(blueHistogram,blueHistogram2)
    #print blue_point
    green_point = HistogramComparitor(greenHistogram,greenHistogram2)
    #print green_point
    red_point = HistogramComparitor(redHistogram,redHistogram2)
    #print red_point
    #print "\n"
    average_point = np.median([blue_point,green_point,red_point])
    #print "average distance"
    #print average_point
    return average_point
    
def averageRGB(image):
    average_color_row = np.average(image, axis=0)
    average_color = np.average(average_color_row, axis=0)
    #print average_color
    return average_color

def convertToHSV(b,g,r):
    b,g,r = r/255.0, g/255.0, b/255.0
    max_colors = max(b,g,r)
    min_colors = min(b,g,r)
    difference = max_colors - min_colors
    if max_colors == min_colors:
        h = 0
    elif max_colors == r:
        h = (60* ((g-b)/difference)+360) % 360
    elif max_colors == g:
        h = (60* ((b-r)/difference)+120) % 360
    elif max_colors == b:
        h = (60* ((r-g)/difference)+240) % 360
        
    if max_colors == 0:
        s =0
    else:
        s = difference/max_colors
    v = max_colors
    weightedH = round((h/360)*100,2)
    #print h,s,v
    return weightedH#,s,v

def convertToPlot(h):
    if h<=80.0 or (h>=330.0 and h<=360.0):
        print "warm color"
    else:
        print "cold color"

def videoToFrames(video):
    success,image = video.read()
    count = 0
    success = True
    while success:
        success,image = video.read()
        cv2.imwrite("frame%d.jpg" %count, image)
        count +=1

def compareFrames(frames):
    print len(frames)
    averagePoints = []
    for frame in range(0,len(frames)-1):
        averagePoint = averageHistogramPoint(frames[frame],frames[frame+1])
        averagePoints.append(averagePoint)
    return averagePoints

def getSegments(averagePoints):
    segmentIndex = []
    for point in range(len(averagePoints)-1):
        median = np.median([averagePoints[point],averagePoints[point+1]])
        if median >= 0.5 or point == 0:
            segmentIndex.append(point)
    return segmentIndex

def chooseKeyframes(segmentIndexes,frameCount):
    keyframeIndex = []
    for point in range(len(segmentIndexes)):
        keyframe = 0
        if point == (len(segmentIndexes)-1):
            keyframe = int(round((segmentIndexes[point]+frameCount)/2))
            #print keyframe
        else:
            keyframe = int(round((segmentIndexes[point]+segmentIndexes[point+1])/2))
            #print keyframe
        keyframeIndex.append(keyframe)
    return keyframeIndex           

def getValueofFrame(keyframeIndexes,frames):
    averageRGBS = []
    for frameIndex in range(0,len(keyframeIndexes)):
        averageColor = averageRGB(frames[keyframeIndexes[frameIndex]])
        averageRGBS.append(convertToHSV(averageColor[0],averageColor[1],averageColor[2]))
    return averageRGBS

def getAverageHSV(HSVValues):
    averageHSV = sum(HSVValues)/len(HSVValues)
    #print averageHSV
    return averageHSV

def getTimes(keyframeIndexes,frameCount):
    times = []
    for index in range(0,len(keyframeIndexes)):
        if index != len(keyframeIndexes)-1:
            time = ((keyframeIndexes[index+1]-keyframeIndexes[index])/3.30)
            times.append(time)
        else:
            time = ((frameCount - keyframeIndexes[index])/3.30)
            times.append(time)
    return times

def totalTime(frameCount):
    time = (frameCount)/3.30
    return time
    

def keyframeAlgorithm(frames):
    print len(frames)
    averagePoints = compareFrames(frames)
    print len(averagePoints)
    segments = getSegments(averagePoints)
    print len(segments)
    keyframeIndexes = chooseKeyframes(segments,len(frames))
    print len(keyframeIndexes)
    #print keyframeIndexes
    averages = getValueofFrame(keyframeIndexes,frames)
    print len(averages)
    times = getTimes(segments,len(frames))
    #print(times)
    totalTimes = totalTime(len(frames))
    f = open("keyframes_real.txt", "a+")
    f.write(str(len(keyframeIndexes)))
    f.write("\n")

    f.write(str(totalTimes))

    f.write("\n")

    for time in range(len(times)):
        f.write(str(times[time]) + " ")

    f.write("\n")

    for average in range(len(averages)):
        f.write(str(averages[average]) + " ")

    f.write("\n")

    f.close()


def manualKeyframe(indexes,frames):
    keyframeIndexes = chooseKeyframes(indexes,len(frames))
    averages = getValueofFrame(keyframeIndexes,frames)
    times = getTimes(indexes,len(frames))
    totalTimes = totalTime(len(frames))
    f = open("keyframes_manual_withframeindexes.txt", "a+")
    f.write(str(len(keyframeIndexes)))
    f.write("\n")

    f.write(str(totalTimes))

    f.write("\n")

    for time in range(len(times)):
        f.write(str(times[time]) + " ")

    f.write("\n")

    for average in range(len(averages)):
        f.write(str(averages[average]) + " ")

    f.write("\n")


    f.close()


