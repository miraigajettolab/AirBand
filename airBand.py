#!/usr/bin/env python
# coding: utf-8

# In[42]:


# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import pygame as pg
import numpy as np
import argparse
import cv2
import imutils
import time


# In[43]:


#resourse block
# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
alphaLower = (21, 88, 172)
alphaUpper = (56, 255, 255)
#second blob values
betaLower = (0, 120, 187)
betaUpper = (10, 255, 255)
#bools that keep track of channels
inCenterA = np.array([False] * 8)
inCenterB = np.array([False] * 8)
#used as switch between two instruments(drums by default)
pick = False
fired = False
#pygame audio mixer
pg.mixer.init()
pg.init()
#audio resourses
#notes
c6 = pg.mixer.Sound("./res/notes/c6.wav")
d6 = pg.mixer.Sound("./res/notes/d6.wav")
e6 = pg.mixer.Sound("./res/notes/e6.wav")
f6 = pg.mixer.Sound("./res/notes/f6.wav")
g6 = pg.mixer.Sound("./res/notes/g6.wav")
a6 = pg.mixer.Sound("./res/notes/a6.wav")
b6 = pg.mixer.Sound("./res/notes/b6.wav")
#drums
clHat = pg.mixer.Sound("./res/drums/clHat.wav")
crash = pg.mixer.Sound("./res/drums/crash.wav")
snare = pg.mixer.Sound("./res/drums/snare.wav")
kick = pg.mixer.Sound("./res/drums/kick.wav")
#setting the number of audio channels
pg.mixer.set_num_channels(50)


# In[44]:


def switch(pick, fired):
	x1 = 150
	x2 = 450
	y1 = 0
	y2 = 50
	cv2.rectangle(frame, (x1, y1),(x2, y2),(0,0,0), 2)
	if alphaCenter is not None and  betaCenter is not None:
		if ((alphaCenter[0] > x1 and alphaCenter[0] < x2) and (alphaCenter[1] > y1) and alphaCenter[1] < y2) and ((betaCenter[0] > x1 and betaCenter[0] < x2) and (betaCenter[1] > y1) and betaCenter[1] < y2):
			if not fired:
				cv2.rectangle(frame, (x1, y1),(x2, y2),(0,0,0), -1)
				return not pick, True
			else:
				return pick, fired
	return pick, False


# In[45]:


def drum(xDrum, yDrum, radDrum, colorDrum, sound, i):
	cv2.circle(frame, (xDrum, yDrum), radDrum,colorDrum, 3)
	if alphaCenter is not None:
		if ((alphaCenter[0] - xDrum)**2 + (alphaCenter[1]-yDrum)**2 < radDrum**2):
			if inCenterA[i] == False:
				sound.play()
				cv2.circle(frame, (xDrum, yDrum), radDrum, (colorDrum[0],colorDrum[1]/2,colorDrum[2]), -1)
			inCenterA[i] = True
		else:
			inCenterA[i] = False
	if betaCenter is not None:
		if ((betaCenter[0] - xDrum)**2 + (betaCenter[1]-yDrum)**2 < radDrum**2):
			if inCenterB[i] == False:
				sound.play()
				cv2.circle(frame, (xDrum, yDrum), radDrum, (colorDrum[0],colorDrum[1]/2,colorDrum[2]), -1)
			inCenterB[i] = True
		else:
			inCenterB[i] = False


# In[46]:


def note(x1, y1, x2, y2, colorDrum, sound, i):
	cv2.rectangle(frame, (x1, y1),(x2, y2),colorDrum, 2)
	if alphaCenter is not None:
		if ((alphaCenter[0] > x1 and alphaCenter[0] < x2) and (alphaCenter[1] > y1) and alphaCenter[1] < y2):
			if inCenterA[i] == False:
				sound.play()
				cv2.rectangle(frame, (x1, y1),(x2, y2),(colorDrum[0],colorDrum[1],colorDrum[2]/2), -1)      
			inCenterA[i] = True
		else:
			inCenterA[i] = False
	if betaCenter is not None:
		if ((betaCenter[0] > x1 and betaCenter[0] < x2) and (betaCenter[1] > y1) and betaCenter[1] < y2):
			if inCenterB[i] == False:
				sound.play()
				cv2.rectangle(frame, (x1, y1),(x2, y2),(colorDrum[0],colorDrum[1],colorDrum[2]/2), -1) 
			inCenterB[i] = True
		else:
			inCenterB[i] = False


# In[47]:


def drumSet():
	drum(180,480,150,(0, 51, 102),kick,0)
	drum(450,480,120,(0, 0, 0),snare,1)
	drum(-10,150,100,(0, 153, 255),clHat,2)
	drum(610,150,100,(0, 153, 255),crash,3)    


# In[48]:


def noteSet():
	noteWidth = 75
	spacer = 5
	yStart = 300
	yEnd = 450
	xStart = 20
	noteCol = (255,0,255)
	iterator = 0
	notes = [c6,d6,e6,f6,g6,a6,b6]
	for note6 in notes:
		note(xStart,yStart,xStart+noteWidth,yEnd,noteCol,note6,iterator)
		xStart = xStart + noteWidth + spacer
		iterator += 1


# In[49]:


#main loop
#start the vidio capture from the webcam
vs = cv2.VideoCapture(0)
# allow the camera or video file to warm up
time.sleep(1.0)
# keep looping
while True:
	# grab the current frame
	ret, frame = vs.read()
	frame = cv2.flip(frame, 1);
	# handle the frame from VideoCapture or VideoStream
	#frame = frame[1] if args.get("video", False) else frameq
 
	# if we are viewing a video and we did not grab a frame,
	# then we have reached the end of the video
	if frame is None:
		break
 
	# resize the frame, blur it, and convert it to the HSV
	# color space
	frame = imutils.resize(frame, width=600)
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
 
	# construct a alphaMask for the color "alpha", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the alphaMask
	alphaMask = cv2.inRange(hsv, alphaLower, alphaUpper)
	alphaMask = cv2.erode(alphaMask, None, iterations=2)
	alphaMask = cv2.dilate(alphaMask, None, iterations=2)

	#same for the beta one    
	betaMask = cv2.inRange(hsv, betaLower, betaUpper)
	betaMask = cv2.erode(betaMask, None, iterations=2)
	betaMask = cv2.dilate(betaMask, None, iterations=2)
	# find contours in the alphaMask and initialize the current
	# (x, y) center of the ball
	alphaCnts = cv2.findContours(alphaMask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	alphaCnts = imutils.grab_contours(alphaCnts)
	alphaCenter = None

	#same for the beta one
	betaCnts = cv2.findContours(betaMask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	betaCnts = imutils.grab_contours(betaCnts)
	betaCenter = None
    
	# only proceed if at least one contour was found
	if len(alphaCnts) > 0:
		# find the largest contour in the alphaMask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(alphaCnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		alphaCenter = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
 
		# only proceed if the radius meets a minimum size
		if radius > 10:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),
				(0, 0, 255), 2)
			cv2.circle(frame, alphaCenter, 5, (0, 0, 255), -1)
 
	#same for the beta one
	if len(betaCnts) > 0:
		c = max(betaCnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		betaCenter = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
 
		# only proceed if the radius meets a minimum size
		if radius > 10:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),
				(255, 0, 0), 2)
			cv2.circle(frame, betaCenter, 5, (255, 0, 0), -1)

	pick, fired = switch(pick, fired)
	if pick:
		noteSet()
	else:
		drumSet()

    
	# show the frame to our screen
	cv2.imshow("Drums", frame)
	key = cv2.waitKey(1) & 0xFF
	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break
        
vs.release();
# close all windows
cv2.destroyAllWindows()

