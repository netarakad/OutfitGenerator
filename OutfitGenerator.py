##########################################################################
# This file is the bulk of my TermProject. It allows users to pick image
# files from their computer and upload them, cycle through outfits to 
# create and store. There is a rating that will be displayed which takes
# into account weather data as well as color preference and colors of the 
# season, which for winter happen to be red and blue. It also saves the 
# data of each user so when they sign out their data is still stored.
##########################################################################

from tkinter import *
from tkinter.filedialog import askopenfilename
from PIL import Image

#Copied with changes from cmu_112_graphics.py at https://www.cs.cmu.edu/~notes/hw11.html
from cmu_112_graphics import *

import requests
import cv2
import numpy as np
import imutils
import os.path

#Copied from: https://www.pyimagesearch.com/2014/08/04/opencv-python-color-detection/
import pickle

#This class creates a new clothing item object when an image is imported
#Had to make this object global in order to use the pickle module
class ClothingItem(object):
		def __init__(self, filename, app, clothingChoices, clothesItems):
			self.filename = filename
			self.clothingChoices = clothingChoices
			self.clothesItems = clothesItems
			self.image1 = app.loadImage(self.filename)
			self.image2 = app.scaleImage(self.image1, 1/4)
			self.width, self.height = self.image2.size
			self.clothingChoices[self.filename] = ""

		def drawItem(self, canvas, x, y):
			canvas.create_image(x + self.width//2, y + self.height//2, 
								image=ImageTk.PhotoImage(self.image2))

		def tagFileWithLabel(self, label):
			self.clothingChoices[self.filename] = label


		def tagFileWithItem(self, item):
			self.clothesItems[self.filename] = item

		#Uses open cv to detect red in an image
		#Adapted from: https://www.pyimagesearch.com/2014/08/04/opencv-python-color-detection/
		def contains_red(self):
			base = os.path.basename(self.filename)
			img = cv2.imread(self.filename)
			hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
			hsv_l = np.array([170,50,50])
			hsv_h = np.array([180, 255, 255])
			return 255 in cv2.inRange(hsv, hsv_l, hsv_h)

		#Uses open cv to detect blue in an image
		#Adapted from: https://www.pyimagesearch.com/2014/08/04/opencv-python-color-detection/
		def contains_blue(self):
			base = os.path.basename(self.filename)
			img = cv2.imread(self.filename)
			hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
			hsv_l = np.array([110,50,50])
			hsv_h = np.array([130,255,255])
			return 255 in cv2.inRange(hsv, hsv_l, hsv_h)

def runOutfits():

	#This class creates my first splashcreen that displays instructions
	class Help(Mode):
		def appStarted(mode):
			mode.image = mode.loadImage("fashion.jpg")
			mode.background = mode.scaleImage(mode.image, 1)
			mode.imgX = mode.width // 2
			mode.imgY = mode.height // 2
			mode.buttonR = 30
			mode.buttonX = 560
			mode.buttonY = 360
			mode.margin = 75
			mode.spacing = 40

		def redrawAll(mode, canvas):
			canvas.create_image(mode.imgX, mode.imgY, 
								image = ImageTk.PhotoImage(mode.background))
			canvas.create_rectangle(mode.margin, mode.margin,
									mode.width - mode.margin, mode.height - mode.margin,
									fill = "light blue", outline = "light blue")
			canvas.create_text(mode.width//2, mode.height//4,
								text = "Welcome to your personal outfit generator!",
								fill = "black", font = "Noteworthy 20")
			canvas.create_text(mode.width//2, mode.height//4 + mode.spacing,
								text = "Plan your outfits based on the weather",
								fill = "black", font = "Noteworthy 20")
			canvas.create_text(mode.width//2, mode.height//4 + 2*mode.spacing,
								text = "Save your generated outfits",
								fill = "black", font = "Noteworthy 20")
			canvas.create_text(mode.width//2, mode.height//4 + 3*mode.spacing,
								text = "Learn what's in for the season",
								fill = "black", font = "Noteworthy 20")
			canvas.create_text(mode.width//2, mode.height//4 + 4*mode.spacing,
								text = "Click start to begin!",
								fill = "black", font = "Noteworthy 20")
			canvas.create_oval(mode.buttonX - mode.buttonR, mode.buttonY - mode.buttonR,
								mode.buttonX + mode.buttonR, mode.buttonY + mode.buttonR,
								fill = "black")
			canvas.create_text(mode.buttonX, mode.buttonY,
								text = "START", font = "Noteworthy", 
								fill = "white")

		def mousePressed(mode, event):
			if mode.pressedButton(event.x, event.y):
				mode.app.setActiveMode(mode.app.welcome)

		def pressedButton(mode, x, y):
			return (mode.buttonX - mode.buttonR <= x <= mode.buttonX + mode.buttonR) and \
					(mode.buttonY - mode.buttonR <= y <= mode.buttonY + mode.buttonR)

	#This class creates the options to log in and register
	class WelcomeScreen(Mode):
		def appStarted(mode):
			mode.image = mode.loadImage("fashion.jpg")
			mode.background = mode.scaleImage(mode.image, 1)
			mode.imgX = mode.width // 2
			mode.imgY = mode.height // 2
			mode.margin = 20
			mode.topBar = 40
			mode.buttonW = 80

		def mousePressed(mode, event):
			if mode.pressedLogIn(event.x, event.y):
				mode.app.setActiveMode(mode.app.login)
			if mode.pressedRegister(event.x, event.y):
				mode.app.setActiveMode(mode.app.register)

		def pressedLogIn(mode, x, y):
			return (mode.width//2 - mode.buttonW <= x <= mode.width//2 + mode.buttonW) and \
					(mode.height//3 <= y <= mode.height//3 + mode.buttonW//2)

		def pressedRegister(mode, x, y):
			return (mode.width//2 - mode.buttonW <= x <= mode.width//2 + mode.buttonW) and \
					(2*mode.height//3 <= y <= 2*mode.height//3 + mode.buttonW//2)

		def redrawAll(mode, canvas):
			canvas.create_image(mode.imgX, mode.imgY, 
								image = ImageTk.PhotoImage(mode.background))
			canvas.create_rectangle(mode.margin, mode.margin, 
									mode.width - mode.margin, mode.height - mode.margin,
									fill = "light blue")
			canvas.create_rectangle(mode.margin, mode.margin,
									mode.width - mode.margin, mode.margin + mode.topBar,
									fill = "black")
			canvas.create_text(mode.width//2, mode.topBar,
								text = "Welcome",
								fill = "white", font = "Noteworthy 15")
			canvas.create_rectangle(mode.width//2 - mode.buttonW, mode.height//3,
									mode.width//2 + mode.buttonW, mode.height//3 + mode.buttonW//2,
									fill = "white")
			canvas.create_text(mode.width//2, mode.height//3 + mode.buttonW//4,
								text = "LOG IN", font = "Noteworthy 30")
			canvas.create_rectangle(mode.width//2 - mode.buttonW, 2*mode.height//3,
									mode.width//2 + mode.buttonW, 2*mode.height//3 + mode.buttonW//2,
									fill = "white")
			canvas.create_text(mode.width//2, 2*mode.height//3 + mode.buttonW//4,
								text = "REGISTER",font = "Noteworthy 30")

	#This class takes care of logging a user in
	class Login(Mode):
		def appStarted(mode):
			mode.image = mode.loadImage("fashion.jpg")
			mode.background = mode.scaleImage(mode.image, 1)
			mode.imgX = mode.width // 2
			mode.imgY = mode.height // 2
			mode.margin = 20
			mode.topBar = 40
			mode.buttonW = 80
			mode.spacing = 10
			mode.usernameBoxColor = "white"
			mode.passwordBoxColor = "white"
			mode.isTypingUsername = False
			mode.isTypingPassword = False
			mode.correctUsername = True
			mode.correctPassword = True
			mode.username = []
			mode.displayUsername = ""
			mode.password = []
			mode.displayPassword = ""

		def mousePressed(mode, event):
			if mode.pressedBackButton(event.x, event.y):
				mode.app.setActiveMode(mode.app.welcome)
			if mode.pressedGoButton(event.x, event.y):
				listFiles = os.listdir()
				if mode.displayUsername in listFiles:
					contents = mode.readFile(mode.displayUsername)
					newContents = contents.splitlines()
					if mode.displayPassword in newContents:
						#Sets new username and password
						MyModalApp.username = mode.displayUsername
						MyModalApp.password = mode.displayPassword
						#Pickle usage copied from: https://stackoverflow.com/questions/4529815/saving-an-object-data-persistence
						#Saves information of clothing type and object to a file labeled by username
						if (mode.displayUsername + "Clothes") in listFiles:
							pickle_in = open(MyModalApp.username + "Clothes", "rb")
							MyModalApp.clothes = pickle.load(pickle_in)
						else:
							mode.writeFile(MyModalApp.username + "Clothes", "")
							MyModalApp.clothes = []
						if (mode.displayUsername + "ClothingChoices") in listFiles:
							pickle_in = open(MyModalApp.username + "ClothingChoices", "rb")
							MyModalApp.clothingChoices = pickle.load(pickle_in)
						else:
							mode.writeFile(MyModalApp.username + "ClothingChoices", "")
							MyModalApp.clothingChoices = {}
						if (mode.displayUsername + "ClothesItems") in listFiles:
							pickle_in = open(MyModalApp.username + "ClothesItems", "rb")
							MyModalApp.clothesItems = pickle.load(pickle_in)
						else:
							mode.writeFile(MyModalApp.username + "ClothesItems", "")
							MyModalApp.clothesItems = {}
						mode.app.setActiveMode(mode.app.closet)
					else:
						mode.correctPassword = False
				else:
					mode.correctUsername = False
				
			if mode.pressedUsername(event.x, event.y):
				mode.usernameBoxColor = "grey"
				mode.isTypingUsername = True
			else:
				mode.usernameBoxColor = "white"
				mode.isTypingUsername = False
			if mode.pressedPassword(event.x, event.y):
				mode.passwordBoxColor = "grey"
				mode.isTypingPassword = True
			else:
				mode.passwordBoxColor = "white"
				mode.isTypingPassword = False

		def keyPressed(mode, event):
			if mode.isTypingUsername:
				if event.key == "Delete":
					mode.username.pop()
				elif event.key == "Space":
					mode.username.append(" ")
				elif event.key == "Enter":
					mode.isTypingUsername = False
				else:
					mode.username.append(event.key)
				mode.displayUsername = "".join(mode.username) 
			if mode.isTypingPassword:
				if event.key == "Delete":
					mode.password.pop()
				elif event.key == "Space":
					mode.password.append(" ")
				elif event.key == "Enter":
					mode.isTypingPassword = False
				else:
					mode.password.append(event.key)
				mode.displayPassword = "".join(mode.password) 

		def pressedBackButton(mode, x, y):
			return (mode.margin + mode.spacing <= x <= mode.margin + mode.spacing + mode.buttonW) and \
					(mode.topBar - mode.margin + mode.spacing <= y <= mode.topBar + mode.spacing)

		def pressedUsername(mode, x, y):
			return (mode.width//2 - mode.buttonW <= x <= mode.width//2 + mode.buttonW) and \
					(mode.height//3 <= y <= mode.height//3 + mode.buttonW//2)

		def pressedPassword(mode, x, y):
			return (mode.width//2 - mode.buttonW <= x <= mode.width//2 + mode.buttonW) and \
					(2*mode.height//3 <= y <= 2*mode.height//3 + mode.buttonW//2)

		def pressedGoButton(mode, x, y):
			return (mode.width - mode.margin - mode.buttonW - mode.spacing <= x <= mode.width - mode.margin - mode.spacing) and \
					(mode.topBar - mode.margin + mode.spacing <= y <= mode.topBar + mode.spacing)

		#Copied from: https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
		@staticmethod
		def readFile(path):
			with open(path, "rt") as f:
				return f.read()

		#Copied from: https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
		@staticmethod
		def writeFile(path, contents):
			with open(path, "wt") as f:
				f.write(contents)

		def createUsernameBox(mode, canvas, color):
			canvas.create_rectangle(mode.width//2 - mode.buttonW, mode.height//3,
									mode.width//2 + mode.buttonW, mode.height//3 + mode.buttonW//2,
									fill = color)
		def createPasswordBox(mode, canvas, color):
			canvas.create_rectangle(mode.width//2 - mode.buttonW, 2*mode.height//3,
									mode.width//2 + mode.buttonW, 2*mode.height//3 + mode.buttonW//2,
									fill = color)

		def redrawAll(mode, canvas):
			canvas.create_image(mode.imgX, mode.imgY, 
								image = ImageTk.PhotoImage(mode.background))
			canvas.create_rectangle(mode.margin, mode.margin, 
									mode.width - mode.margin, mode.height - mode.margin,
									fill = "light blue")
			canvas.create_rectangle(mode.margin, mode.margin,
									mode.width - mode.margin, mode.margin + mode.topBar,
									fill = "black")
			canvas.create_text(mode.width//2, mode.topBar,
								text = "Log In",
								fill = "white", font = "Noteworthy 15")
			canvas.create_rectangle(mode.margin + mode.spacing,
									mode.topBar - mode.margin + mode.spacing,
									mode.margin + mode.spacing + mode.buttonW,
									mode.topBar + mode.spacing,
									fill = "light blue", outline = "light pink")
			canvas.create_text(mode.buttonW - mode.spacing, mode.topBar,
								text = "BACK", font = "Noteworthy 10")
			canvas.create_rectangle(mode.width - mode.margin - mode.buttonW - mode.spacing,
									mode.topBar - mode.margin + mode.spacing, 
									mode.width - mode.margin - mode.spacing, 
									mode.topBar + mode.spacing,
									fill = "light blue", outline = "light pink")
			canvas.create_text(mode.width - mode.buttonW + mode.spacing, mode.topBar,
								text = "GO", font = "Noteworthy 10")
			mode.createUsernameBox(canvas, mode.usernameBoxColor)
			mode.createPasswordBox(canvas, mode.passwordBoxColor)
			canvas.create_text(mode.width//2, mode.height//3 - 2*mode.spacing,
								text = "USERNAME", font = "Noteworthy 15")
			if mode.correctUsername == False:
				canvas.create_text(mode.width//2, mode.height//2 - mode.spacing,
								text = "USERNAME NOT FOUND", font = "Noteworthy 15",
								fill = "red")
			canvas.create_text(mode.width//2, 
								mode.height//3 + mode.buttonW//4,
								text = mode.displayUsername, font = "Noteworthy 15")
			canvas.create_text(mode.width//2, 2*mode.height//3 - 2*mode.spacing,
								text = "PASSWORD", font = "Noteworthy 15")
			if mode.correctPassword == False:
				canvas.create_text(mode.width//2, 3*mode.height//4 + 2*mode.spacing,
								text = "INCORRECT PASSWORD", font = "Noteworthy 15",
								fill = "red")
			canvas.create_text(mode.width//2, 
								2*mode.height//3 + mode.buttonW//4,
								text = mode.displayPassword, font = "Noteworthy 15")

	#This class takes care of registering a user
	class Register(Mode):
		def appStarted(mode):
			mode.image = mode.loadImage("fashion.jpg")
			mode.background = mode.scaleImage(mode.image, 1)
			mode.imgX = mode.width // 2
			mode.imgY = mode.height // 2
			mode.margin = 20
			mode.topBar = 40
			mode.buttonW = 80
			mode.spacing = 10
			mode.usernameBoxColor = "white"
			mode.passwordBoxColor = "white"
			mode.colorBoxColor = "white"
			mode.isTypingUsername = False
			mode.isTypingPassword = False
			mode.isTypingColor = False
			mode.username = []
			mode.displayUsername = ""
			mode.password = []
			mode.displayPassword = ""
			mode.color = []
			mode.displayColor = ""

		def mousePressed(mode, event):
			if mode.pressedBackButton(event.x, event.y):
				mode.app.setActiveMode(mode.app.welcome)
			if mode.pressedFinishButton(event.x, event.y):
				#Creates the file that just has username, password, and color preference file
				contents = open(mode.displayUsername, "w")
				contents.write(mode.displayUsername + "\n")
				contents.write(mode.displayPassword + "\n")
				contents.write(mode.displayColor)
				MyModalApp.color = mode.displayColor
				mode.app.setActiveMode(mode.app.login)
			if mode.pressedUsername(event.x, event.y):
				mode.usernameBoxColor = "grey"
				mode.isTypingUsername = True
			else:
				mode.usernameBoxColor = "white"
				mode.isTypingUsername = False
			if mode.pressedPassword(event.x, event.y):
				mode.passwordBoxColor = "grey"
				mode.isTypingPassword = True
			else:
				mode.passwordBoxColor = "white"
				mode.isTypingPassword = False
			if mode.pressedColor(event.x, event.y):
				mode.colorBoxColor = "grey"
				mode.isTypingColor = True
			else:
				mode.colorBoxColor = "white"
				mode.isTypingColor = False

		def keyPressed(mode, event):
			if mode.isTypingUsername:
				if event.key == "Delete":
					mode.username.pop()
				elif event.key == "Space":
					mode.username.append(" ")
				elif event.key == "Enter":
					mode.isTypingUsername = False
				else:
					mode.username.append(event.key)
				mode.displayUsername = "".join(mode.username) 
			if mode.isTypingPassword:
				if event.key == "Delete":
					mode.password.pop()
				elif event.key == "Space":
					mode.password.append(" ")
				elif event.key == "Enter":
					mode.isTypingPassword = False
				else:
					mode.password.append(event.key)
				mode.displayPassword = "".join(mode.password) 
			if mode.isTypingColor:
				if event.key == "Delete":
					mode.color.pop()
				elif event.key == "Space":
					mode.color.append(" ")
				elif event.key == "Enter":
					mode.isTypingColor = False
				else:
					mode.color.append(event.key)
				mode.displayColor = "".join(mode.color) 

		def pressedBackButton(mode, x, y):
			return (mode.margin + mode.spacing <= x <= mode.margin + mode.spacing + mode.buttonW) and \
					(mode.topBar - mode.margin + mode.spacing <= y <= mode.topBar + mode.spacing)

		def pressedUsername(mode, x, y):
			return (mode.width//2 - mode.buttonW <= x <= mode.width//2 + mode.buttonW) and \
					(mode.height//4 <= y <= mode.height//4 + mode.buttonW//2)

		def pressedPassword(mode, x, y):
			return (mode.width//2 - mode.buttonW <= x <= mode.width//2 + mode.buttonW) and \
					(mode.height//2 <= y <= mode.height//2 + mode.buttonW//2)

		def pressedColor(mode, x, y):
			return (mode.width//2 - mode.buttonW <= x <= mode.width//2 + mode.buttonW) and \
					(3*mode.height//4 <= y <= 3*mode.height//4 + mode.buttonW//2)

		def pressedFinishButton(mode, x, y):
			return (mode.width - mode.margin - mode.buttonW - mode.spacing <= x <= mode.width - mode.margin - mode.spacing) and \
					(mode.topBar - mode.margin + mode.spacing <= y <= mode.topBar + mode.spacing)

		#Copied from: https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
		@staticmethod
		def readFile(path):
			with open(path, "rt") as f:
				return f.read()

		#Copied from: https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
		@staticmethod
		def writeFile(path, contents):
			with open(path, "wt") as f:
				f.write(contents)

		def createUsernameBox(mode, canvas, color):
			canvas.create_rectangle(mode.width//2 - mode.buttonW, mode.height//4,
									mode.width//2 + mode.buttonW, mode.height//4 + mode.buttonW//2,
									fill = color)
		def createPasswordBox(mode, canvas, color):
			canvas.create_rectangle(mode.width//2 - mode.buttonW, mode.height//2,
									mode.width//2 + mode.buttonW, mode.height//2 + mode.buttonW//2,
									fill = color)
		def createColorBox(mode, canvas, color):
			canvas.create_rectangle(mode.width//2 - mode.buttonW, 3*mode.height//4,
									mode.width//2 + mode.buttonW, 3*mode.height//4 + mode.buttonW//2,
									fill = color)

		def redrawAll(mode, canvas):
			canvas.create_image(mode.imgX, mode.imgY, 
								image = ImageTk.PhotoImage(mode.background))
			canvas.create_rectangle(mode.margin, mode.margin, 
									mode.width - mode.margin, mode.height - mode.margin,
									fill = "light blue")
			canvas.create_rectangle(mode.margin, mode.margin,
									mode.width - mode.margin, mode.margin + mode.topBar,
									fill = "black")
			canvas.create_text(mode.width//2, mode.topBar,
								text = "Register",
								fill = "white", font = "Noteworthy 15")
			canvas.create_rectangle(mode.margin + mode.spacing,
									mode.topBar - mode.margin + mode.spacing,
									mode.margin + mode.spacing + mode.buttonW,
									mode.topBar + mode.spacing,
									fill = "light blue", outline = "light pink")
			canvas.create_text(mode.buttonW - mode.spacing, mode.topBar,
								text = "BACK", font = "Noteworthy 10")
			canvas.create_rectangle(mode.width - mode.margin - mode.buttonW - mode.spacing,
									mode.topBar - mode.margin + mode.spacing, 
									mode.width - mode.margin - mode.spacing, 
									mode.topBar + mode.spacing,
									fill = "light blue", outline = "light pink")
			canvas.create_text(mode.width - mode.buttonW + mode.spacing, mode.topBar,
								text = "FINISH", font = "Noteworthy 10")
			mode.createUsernameBox(canvas, mode.usernameBoxColor)
			mode.createPasswordBox(canvas, mode.passwordBoxColor)
			mode.createColorBox(canvas, mode.colorBoxColor)
			canvas.create_text(mode.width//2, mode.height//4 - 2*mode.spacing,
								text = "USERNAME", font = "Noteworthy 15")
			canvas.create_text(mode.width//2, 
								mode.height//4 + mode.buttonW//4,
								text = mode.displayUsername, font = "Noteworthy 15")
			canvas.create_text(mode.width//2, mode.height//2 - 2*mode.spacing,
								text = "PASSWORD", font = "Noteworthy 15")
			canvas.create_text(mode.width//2, 
								mode.height//2 + mode.buttonW//4,
								text = mode.displayPassword, font = "Noteworthy 15")
			canvas.create_text(mode.width//2, 3*mode.height//4 - 2*mode.spacing,
								text = "FAVORITE COLOR", font = "Noteworthy 15")
			canvas.create_text(mode.width//2, 
								3*mode.height//4 + mode.buttonW//4,
								text = mode.displayColor, font = "Noteworthy 15")

	#This class takes care of generating tops and bottoms for user to select outfit from
	class GenerateOutfit(Mode):
		def appStarted(mode):
			mode.topBar = 40
			mode.margin = 20
			mode.buttonW = 80
			mode.spacing = 10
			mode.imgX = mode.width // 2
			mode.imgY = mode.height // 2
			mode.image = mode.loadImage("fashion.jpg")
			mode.background = mode.scaleImage(mode.image, 1)
			mode.curBottom = 0
			mode.curTop = 0
			mode.createShirts()
			mode.createPants()

		def mousePressed(mode, event):
			if mode.pressedLikedButton(event.x, event.y):
				mode.app.setActiveMode(mode.app.savedOutfits)
			if mode.pressedClosetButton(event.x, event.y):
				mode.app.setActiveMode(mode.app.closet)
			if mode.pressedNextTopButton(event.x, event.y):
				mode.curTop += 1
			if mode.pressedNextBottomButton(event.x, event.y):
				mode.curBottom += 1
			if mode.pressedLikeButton(event.x, event.y):
				MyModalApp.likedTops.append(MyModalApp.tops[mode.curTop])
				MyModalApp.likedBottoms.append(MyModalApp.bottoms[mode.curBottom])

		#Tagging images to clothing types
		@staticmethod
		def createPants():
			for file in MyModalApp.clothingChoices:
				if MyModalApp.clothingChoices[file] == "pant":
					MyModalApp.bottoms.append(MyModalApp.clothesItems[file])
					MyModalApp.pants.append(MyModalApp.clothesItems[file])
				elif MyModalApp.clothingChoices[file] == "shorts":
					MyModalApp.bottoms.append(MyModalApp.clothesItems[file])
					MyModalApp.shorts.append(MyModalApp.clothesItems[file])

		@staticmethod
		def createShirts():
			for file in MyModalApp.clothingChoices:
				if MyModalApp.clothingChoices[file] == "shirt":
					MyModalApp.tops.append(MyModalApp.clothesItems[file])
					MyModalApp.shirts.append(MyModalApp.clothesItems[file])
				elif MyModalApp.clothingChoices[file] == "tee":
					MyModalApp.tops.append(MyModalApp.clothesItems[file])
					MyModalApp.tees.append(MyModalApp.clothesItems[file])
				elif MyModalApp.clothingChoices[file] == "pants":
					MyModalApp.pants.append(MyModalApp.clothesItems[file])
				elif MyModalApp.clothingChoices[file] == "shorts":
					MyModalApp.shorts.append(MyModalApp.clothesItems[file])
				elif MyModalApp.clothingChoices[file] == "dresses":
					MyModalApp.dresses.append(MyModalApp.clothesItems[file])

		def pressedLikedButton(mode, x, y):
			return (mode.width - mode.margin - mode.buttonW - mode.spacing <= x <= mode.width - mode.margin - mode.spacing) and \
					(mode.topBar - mode.margin + mode.spacing <= y <= mode.topBar + mode.spacing)

		def pressedClosetButton(mode, x, y):
			return (mode.margin + mode.spacing <= x <= mode.margin + mode.spacing + mode.buttonW) and \
					(mode.topBar - mode.margin + mode.spacing <= y <= mode.topBar + mode.spacing)

		def pressedNextTopButton(mode, x, y):
			return (mode.width//5 + 2*mode.margin <= x <= mode.width//5 + 2*mode.margin + mode.buttonW) and \
					(mode.margin + mode.topBar + mode.spacing <= y <= 2*mode.margin + mode.topBar + mode.spacing)

		def pressedNextBottomButton(mode, x, y):
			return (3*mode.width//5 + mode.margin <= x <= 3*mode.width//5 + mode.margin + mode.buttonW) and \
					(mode.margin + mode.topBar + mode.spacing <= y <= 2*mode.margin + mode.topBar + mode.spacing)

		def pressedLikeButton(mode, x, y):
			return (mode.margin + 2*mode.spacing + mode.buttonW <= x <= mode.margin + mode.spacing + 1.5*mode.buttonW) and \
					(mode.topBar - mode.margin + mode.spacing <= y <= mode.topBar + mode.spacing)

		def redrawAll(mode, canvas):
			canvas.create_image(mode.imgX, mode.imgY, 
								image = ImageTk.PhotoImage(mode.background))
			canvas.create_rectangle(mode.margin, mode.margin, 
									mode.width - mode.margin, mode.height - mode.margin,
									fill = "light blue")
			canvas.create_rectangle(mode.margin, mode.margin,
									mode.width - mode.margin, mode.margin + mode.topBar,
									fill = "black")
			canvas.create_text(mode.width//2, mode.topBar,
								text = "Create an Outfit",
								fill = "white", font = "Noteworthy 15")
			canvas.create_rectangle(mode.width - mode.margin - mode.buttonW - mode.spacing,
									mode.topBar - mode.margin + mode.spacing, 
									mode.width - mode.margin - mode.spacing, 
									mode.topBar + mode.spacing,
									fill = "light pink", outline = "light pink")
			canvas.create_text(mode.width - mode.buttonW + mode.spacing, mode.topBar,
								text = "LIKED", font = "Noteworthy 10")
			canvas.create_rectangle(mode.margin + mode.spacing,
									mode.topBar - mode.margin + mode.spacing,
									mode.margin + mode.spacing + mode.buttonW,
									mode.topBar + mode.spacing,
									fill = "light pink", outline = "light pink")
			canvas.create_text(mode.buttonW - mode.spacing, mode.topBar,
								text = "CLOSET", font = "Noteworthy 10")
			canvas.create_rectangle(mode.width//5 + 2*mode.margin,
									mode.margin + mode.topBar + mode.spacing,
									mode.width//5 + 2*mode.margin + mode.buttonW,
									2*mode.margin + mode.topBar + mode.spacing,
									fill = "light pink", outline = "light pink")
			canvas.create_text(mode.width//5 + mode.buttonW, 
								mode.margin + mode.topBar + 2*mode.spacing,
								text = "NEXT", font = "Noteworthy 10")
			canvas.create_rectangle(3*mode.width//5 + mode.margin,
									mode.margin + mode.topBar + mode.spacing,
									3*mode.width//5 + mode.margin + mode.buttonW,
									2*mode.margin + mode.topBar + mode.spacing,
									fill = "light pink", outline = "light pink")
			canvas.create_text(3*mode.width//5 + mode.buttonW - mode.margin, 
								mode.margin + mode.topBar + 2*mode.spacing,
								text = "NEXT", font = "Noteworthy 10")
			canvas.create_rectangle(mode.margin + 2*mode.spacing + mode.buttonW,
									mode.topBar - mode.margin + mode.spacing,
									mode.margin + mode.spacing + 1.5*mode.buttonW,
									mode.topBar + mode.spacing,
									fill = "light yellow", outline = "light pink")
			canvas.create_text(2*mode.buttonW - 2.5*mode.spacing, mode.topBar,
								text = "LIKE", font = "Noteworthy 10")
			if ((mode.curBottom > len(MyModalApp.bottoms) - 1) or \
				(mode.curTop > len(MyModalApp.tops) - 1)):
				mode.curBottom = 0
				mode.curTop = 0
			if len(MyModalApp.bottoms) > 0:
				MyModalApp.bottoms[mode.curBottom].drawItem(canvas, 3*mode.width//5, 1.5*mode.height//5)
			if len(MyModalApp.tops) > 0:
				MyModalApp.tops[mode.curTop].drawItem(canvas, mode.width//5, 1.5*mode.height//5)

	#This class takes care of importing images by the user
	class Closet(Mode):
		def appStarted(mode):
			mode.topBar = 40
			mode.margin = 20
			mode.buttonW = 80
			mode.spacing = 10
			mode.imgX = mode.width // 2
			mode.imgY = mode.height // 2
			mode.image = mode.loadImage("fashion.jpg")
			mode.background = mode.scaleImage(mode.image, 1)
			mode.selectedImage = False
			mode.newClothingItem = None
			mode.contents = ""
			mode.filename = ""

		#Copied from: https://www.pyimagesearch.com/2014/08/04/opencv-python-color-detection/
		#Allows for the saving of an object list to a file
		@staticmethod
		def save_object(obj, filename):
			with open(filename, 'wb') as output:  # Overwrites any existing file.
				pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

		def mousePressed(mode, event):
			if mode.pressedGenerateButton(event.x, event.y):
				mode.app.setActiveMode(mode.app.generateOutfit)
			if mode.pressedExitButton(event.x, event.y):
				#Saves lists that program depends on for image display for each user
				mode.save_object(MyModalApp.clothes, MyModalApp.username + "Clothes")
				mode.save_object(MyModalApp.clothingChoices, MyModalApp.username + "ClothingChoices")
				mode.save_object(MyModalApp.clothesItems, MyModalApp.username + "ClothesItems")
				mode.app.setActiveMode(mode.app.welcome)
			#Creates new instance of Clothing item when user imports an image
			if mode.pressedImportButton(event.x, event.y):
				mode.filename = askopenfilename()
				mode.newClothingItem = ClothingItem(mode.filename, mode, 
													MyModalApp.clothingChoices, MyModalApp.clothesItems)
				mode.newClothingItem.tagFileWithItem(mode.newClothingItem)
				MyModalApp.clothes.append(mode.newClothingItem)

			for i in range(len(MyModalApp.clothesItems)):
				if mode.chooseImage(i, event.x, event.y):
					mode.selectedImage = True
					mode.newClothingItem = MyModalApp.clothes[i]
			#Tags clothing article to image
			if mode.selectedImage == True:
				if mode.pressedShirtButton(event.x, event.y):
					mode.newClothingItem.tagFileWithLabel("shirt")
					print(mode.contents)
					mode.selectedImage = False
				elif mode.pressedTeeButton(event.x, event.y):
					mode.newClothingItem.tagFileWithLabel("tee")
					mode.selectedImage = False
				elif mode.pressedPantButton(event.x, event.y):
					mode.newClothingItem.tagFileWithLabel("pant")
					mode.selectedImage = False
				elif mode.pressedShortsButton(event.x, event.y):
					mode.newClothingItem.tagFileWithLabel("shorts")
					mode.selectedImage = False
				elif mode.pressedDressButton(event.x, event.y):
					mode.newClothingItem.tagFileWithLabel("dress")
					mode.selectedImage = False

		#Copied from: https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
		@staticmethod
		def readFile(path):
			with open(path, "rt") as f:
				return f.read()

		#Copied from: https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
		@staticmethod
		def writeFile(path, contents):
			with open(path, "wt") as f:
				f.write(contents)

		def pressedGenerateButton(mode, x, y):
			return (mode.width - mode.margin - mode.buttonW - mode.spacing <= x <= mode.width - mode.margin - mode.spacing) and \
					(mode.topBar - mode.margin + mode.spacing <= y <= mode.topBar + mode.spacing)

		def pressedImportButton(mode, x, y):
			return (mode.margin + mode.spacing <= x <= mode.margin + mode.spacing + mode.buttonW) and \
					(mode.topBar - mode.margin + mode.spacing <= y <= mode.topBar + mode.spacing)

		def pressedShirtButton(mode, x, y):
			return (mode.margin + mode.spacing <= x <= mode.margin + mode.spacing + mode.buttonW) and \
					(mode.height - 1.5*mode.margin <= y <= mode.height)

		def pressedTeeButton(mode, x, y):
			return (mode.margin + mode.spacing + 1.5*mode.buttonW <= x <= mode.margin + mode.spacing + 2.5*mode.buttonW) and \
					(mode.height - 1.5*mode.margin <= y <= mode.height)

		def pressedPantButton(mode, x, y):
			return (mode.margin + mode.spacing + 3*mode.buttonW <= x <= mode.margin + mode.spacing + 4*mode.buttonW) and \
					(mode.height - 1.5*mode.margin <= y <= mode.height)

		def pressedShortsButton(mode, x, y):
			return (mode.margin + mode.spacing + 4.5*mode.buttonW<= x <= mode.margin + mode.spacing + 5.5*mode.buttonW) and \
					(mode.height - 1.5*mode.margin <= y <= mode.height)

		def pressedDressButton(mode, x, y):
			return (mode.margin + mode.spacing + 6*mode.buttonW <= x <= mode.margin + mode.spacing + 7*mode.buttonW) and \
					(mode.height - 1.5*mode.margin <= y <= mode.height)

		def chooseImage(mode, i, x, y):
			mode.newClothingItem = MyModalApp.clothes[i]
			return (mode.margin + i*150 - MyModalApp.clothes[i].width <= x <= mode.margin + i*150 + MyModalApp.clothes[i].width) and \
					(mode.margin + mode.topBar <= y <= mode.margin + mode.topBar + MyModalApp.clothes[i].height)

		def pressedExitButton(mode, x, y):
			return (mode.margin + 2*mode.spacing + mode.buttonW <= x <= mode.margin + mode.spacing + 1.5*mode.buttonW) and \
					(mode.topBar - mode.margin + mode.spacing <= y <= mode.topBar + mode.spacing)


		def redrawAll(mode, canvas):
			canvas.create_image(mode.imgX, mode.imgY, 
								image = ImageTk.PhotoImage(mode.background))
			canvas.create_rectangle(mode.margin, mode.margin, 
									mode.width - mode.margin, mode.height - 2*mode.margin,
									fill = "lavender")
			canvas.create_rectangle(mode.margin + mode.spacing,
									mode.height - 1.5*mode.margin,
									mode.margin + mode.spacing + mode.buttonW,
									mode.height,
									fill = "light blue", outline = "light blue")
			canvas.create_text(mode.buttonW - mode.spacing, mode.height - mode.margin,
								text = "SHIRT", font = "Noteworthy 10")
			canvas.create_rectangle(mode.margin + mode.spacing + 1.5*mode.buttonW,
									mode.height - 1.5*mode.margin,
									mode.margin + mode.spacing + 2.5*mode.buttonW,
									mode.height,
									fill = "light blue", outline = "light blue")
			canvas.create_text(mode.margin + 5*mode.spacing + 1.5*mode.buttonW, mode.height - mode.margin,
								text = "TEE", font = "Noteworthy 10")
			canvas.create_rectangle(mode.margin + mode.spacing + 3*mode.buttonW,
									mode.height - 1.5*mode.margin,
									mode.margin + mode.spacing + 4*mode.buttonW,
									mode.height,
									fill = "light blue", outline = "light blue")
			canvas.create_text(mode.margin + 5*mode.spacing + 3*mode.buttonW, mode.height - mode.margin,
								text = "PANT", font = "Noteworthy 10")
			canvas.create_rectangle(mode.margin + mode.spacing + 4.5*mode.buttonW,
									mode.height - 1.5*mode.margin,
									mode.margin + mode.spacing + 5.5*mode.buttonW,
									mode.height,
									fill = "light blue", outline = "light blue")
			canvas.create_text(mode.margin + 5*mode.spacing + 4.5*mode.buttonW, mode.height - mode.margin,
								text = "SHORTS", font = "Noteworthy 10")
			canvas.create_rectangle(mode.margin + mode.spacing + 6*mode.buttonW,
									mode.height - 1.5*mode.margin,
									mode.margin + mode.spacing + 7*mode.buttonW,
									mode.height,
									fill = "light blue", outline = "light blue")
			canvas.create_text(mode.margin + 5*mode.spacing + 6*mode.buttonW, mode.height - mode.margin,
								text = "DRESS", font = "Noteworthy 10")
			canvas.create_rectangle(mode.margin, mode.margin,
									mode.width - mode.margin, mode.margin + mode.topBar,
									fill = "black")
			canvas.create_text(mode.width//2, mode.topBar,
								text = f"My Closet",
								fill = "white", font = "Noteworthy 15")
			canvas.create_rectangle(mode.width - mode.margin - mode.buttonW - mode.spacing,
									mode.topBar - mode.margin + mode.spacing, 
									mode.width - mode.margin - mode.spacing, 
									mode.topBar + mode.spacing,
									fill = "light blue", outline = "light blue")
			canvas.create_text(mode.width - mode.buttonW + mode.spacing, mode.topBar,
								text = "GENERATE", font = "Noteworthy 10")
			canvas.create_rectangle(mode.margin + mode.spacing,
									mode.topBar - mode.margin + mode.spacing,
									mode.margin + mode.spacing + mode.buttonW,
									mode.topBar + mode.spacing,
									fill = "light blue", outline = "light blue")
			canvas.create_text(mode.buttonW - mode.spacing, mode.topBar,
								text = "IMPORT", font = "Noteworthy 10")
			canvas.create_rectangle(mode.margin + 2*mode.spacing + mode.buttonW,
									mode.topBar - mode.margin + mode.spacing,
									mode.margin + mode.spacing + 1.5*mode.buttonW,
									mode.topBar + mode.spacing,
									fill = "light yellow", outline = "light blue")
			canvas.create_text(2*mode.buttonW - 2.5*mode.spacing, mode.topBar,
								text = "EXIT", font = "Noteworthy 10")
			for i in range(len(MyModalApp.clothesItems)):
				MyModalApp.clothes[i].drawItem(canvas, mode.margin + i*150, 
					mode.margin + mode.topBar)

	#This class takes care of all the liked outfits created by user
	class SavedOutfits(Mode):
		def appStarted(mode):
			mode.cols = 6
			mode.topBar = 40
			mode.margin = 20
			mode.buttonW = 80
			mode.spacing = 10
			mode.imgX = mode.width // 2
			mode.imgY = mode.height // 2
			mode.image = mode.loadImage("fashion.jpg")
			mode.background = mode.scaleImage(mode.image, 1)
			mode.curTop = 0
			mode.curBottom = 0
			mode.rating = 10
			mode.recommendation = ""

			#Learned API from https://openweathermap.org/api?source=post_page-----d49dfc66e6bc----------------------
			mode.city = "Pittsburgh"  
			mode.url = (f"http://api.openweathermap.org/data/2.5/weather?" + 
						f"q={mode.city}&appid=6c05a60d6c1b07e322c9213e2f189973")
			mode.res = requests.get(mode.url)
			mode.data = mode.res.json()
			mode.temp = round(( mode.data["main"]["temp"] - 273.15) * 9/5) + 32 #Kelvin
			
			mode.description = mode.data["weather"][0]["description"]
			mode.rating = 10
			mode.recommendation = ""
			mode.likedOutfit = True
			if (mode.curBottom <= len(MyModalApp.likedBottoms) - 1) and (mode.curTop <= len(MyModalApp.likedTops) - 1):
				outfit = MyModalApp.likedTops[mode.curTop], MyModalApp.likedBottoms[mode.curBottom]
				mode.rating, mode.recommendation = mode.createRating(outfit, 10, "", mode.temp, MyModalApp.color)
			else:
				mode.likedOutfit = False


		def createGrid(mode, canvas):
			gridWidth = mode.width // mode.cols

		def mousePressed(mode, event):
			if mode.pressedClosetButton(event.x, event.y):
				mode.app.setActiveMode(mode.app.closet)
			if mode.pressedGenerateButton(event.x, event.y):
				mode.app.setActiveMode(mode.app.generateOutfit)
			if mode.pressedNextOutfitButton(event.x, event.y):
				mode.curBottom += 1
				mode.curTop += 1
				if (mode.curBottom <= len(MyModalApp.likedBottoms) - 1) and (mode.curTop <= len(MyModalApp.likedTops) - 1):
					outfit = MyModalApp.likedTops[mode.curTop], MyModalApp.likedBottoms[mode.curBottom]
					mode.rating, mode.recommendation = mode.createRating(outfit, 10, "", mode.temp, MyModalApp.color)
				else:
					mode.curTop = 0
					mode.curBottom = 0
					outfit = MyModalApp.likedTops[mode.curTop], MyModalApp.likedBottoms[mode.curBottom]
					mode.rating, mode.recommendation = mode.createRating(outfit, 10, "", mode.temp, MyModalApp.color)

		#Creates a rating based on temp and color preference
		@staticmethod
		def createRating(outfit, rating, recommendation, temp, color):
			top, bottom = outfit
			#Red and Blue colors are in this winter
			if top.contains_red() or top.contains_blue():
				pass
			else:
				rating -= 2
				print("here")
				recommendation += "Lacking seasonal colors in top "
			if bottom.contains_red() or bottom.contains_blue():
				pass
			else:
				rating -= 2 
				recommendation += "Lacking seasonal colors in bottom "
			#Weather in PIT is always below 60 for now so select from shirts and pants
			if temp < 60:
				if top not in MyModalApp.shirts:
					rating -= 2
					recommendation += "Need shirt or more layers "
				if bottom not in MyModalApp.pants:
					rating -= 2
					recommendation += "Need pants "
			#Color preference isn't seasonal (aka not blue or red)
			if color not in ["blue", "red"]:
				rating -= 1
				recommendation += "Color preference not seasonal "
			return (rating, recommendation)
				
		def pressedClosetButton(mode, x, y):
			return (mode.width - mode.margin - mode.buttonW - mode.spacing <= x <= mode.width - mode.margin - mode.spacing) and \
					(mode.topBar - mode.margin + mode.spacing <= y <= mode.topBar + mode.spacing)

		def pressedGenerateButton(mode, x, y):
			return (mode.margin + mode.spacing <= x <= mode.margin + mode.spacing + mode.buttonW) and \
					(mode.topBar - mode.margin + mode.spacing <= y <= mode.topBar + mode.spacing)

		def pressedNextOutfitButton(mode, x, y):
			return (mode.width//2 - mode.buttonW <= x <= mode.width//2 + mode.buttonW) and \
					(mode.margin + mode.topBar + mode.spacing <= y <= 2*mode.margin + mode.topBar + mode.spacing)


		def redrawAll(mode, canvas):
			canvas.create_image(mode.imgX, mode.imgY, 
								image = ImageTk.PhotoImage(mode.background))
			canvas.create_rectangle(mode.margin, mode.margin, 
									mode.width - mode.margin, mode.height - mode.margin,
									fill = "light yellow")
			canvas.create_rectangle(mode.margin, mode.margin,
									mode.width - mode.margin, mode.margin + mode.topBar,
									fill = "black")
			canvas.create_text(mode.width//2, mode.topBar,
								text = f"Saved Outfits",
								fill = "white", font = "Noteworthy 15")
			canvas.create_rectangle(mode.width - mode.margin - mode.buttonW - mode.spacing,
									mode.topBar - mode.margin + mode.spacing, 
									mode.width - mode.margin - mode.spacing, 
									mode.topBar + mode.spacing,
									fill = "lavender", outline = "lavender")
			canvas.create_text(mode.width - mode.buttonW + mode.spacing, mode.topBar,
								text = "CLOSET", font = "Noteworthy 10")
			canvas.create_rectangle(mode.margin + mode.spacing,
									mode.topBar - mode.margin + mode.spacing,
									mode.margin + mode.spacing + mode.buttonW,
									mode.topBar + mode.spacing,
									fill = "lavender", outline = "lavender")
			canvas.create_text(mode.buttonW - mode.spacing, mode.topBar,
								text = "GENERATE", font = "Noteworthy 10")
			if mode.likedOutfit == True:
				canvas.create_rectangle(mode.width//2 - mode.buttonW,
										mode.margin + mode.topBar + mode.spacing,
										mode.width//2 + mode.buttonW,
										2*mode.margin + mode.topBar + mode.spacing,
										fill = "lavender", outline = "lavender")
				canvas.create_text(mode.width//2, mode.margin + mode.topBar + 2*mode.spacing,
									text = "NEXT OUTFIT", font = "Noteworthy 10")
				canvas.create_rectangle(mode.width//6, 3*mode.height//4 + mode.spacing,
										5*mode.width//6, 3*mode.height//4 + 7*mode.spacing,
										fill = "lavender")
				canvas.create_text(mode.width//2, 3*mode.height//4 + 2*mode.spacing,
									text = f"Rating for this outfit: {mode.rating}",
									font = "Noteworthy 10")
				if mode.recommendation == "":
					canvas.create_text(mode.width//2, 3*mode.height//4 + 4*mode.spacing,
									text = "Looking good!", font = "Noteworthy 10")
				else:
					canvas.create_text(mode.width//2, 3*mode.height//4 + 4*mode.spacing,
										text = mode.recommendation, font = "Noteworthy 10")
				canvas.create_text(mode.width//2, 3*mode.height//4 + 6*mode.spacing,
									text = f"Weather in Pittsburgh: " + 
									f"{mode.temp}ºF, {mode.description}",
									font = "Noteworthy 10")
				if len(MyModalApp.likedBottoms) > 0:
					MyModalApp.likedBottoms[mode.curBottom].drawItem(canvas, 3*mode.width//5, 1.5*mode.height//5)
				if len(MyModalApp.likedTops) > 0:
					MyModalApp.likedTops[mode.curTop].drawItem(canvas, mode.width//5, 1.5*mode.height//5)
			else:
				canvas.create_rectangle(mode.width//6, 3*mode.height//4 + mode.spacing,
										5*mode.width//6, 3*mode.height//4 + 7*mode.spacing,
										fill = "lavender")
				canvas.create_text(mode.width//2, 3*mode.height//4 + 4*mode.spacing,
										text = "No liked outfits to show!", font = "Noteworthy 10")

	class MyModalApp(ModalApp):
		clothingChoices = {}
		clothesItems = {}
		clothes = []
		savedOutfits = []
		bottoms = []
		shirts = []
		likedTops = []
		tops = []
		tees = []
		shirts = []
		pants = []
		shorts = []
		likedBottoms = []
		dresses = []
		username = ""
		password = ""
		contents = ""
		color = ""
		def appStarted(app):
	            app.help = Help()
	            app.savedOutfits = SavedOutfits()
	            app.generateOutfit = GenerateOutfit()
	            app.closet = Closet()
	            app.welcome = WelcomeScreen()
	            app.login = Login()
	            app.register = Register()
	            app.setActiveMode(app.help)
	            app.timerDelay = 50

	app = MyModalApp(width=600, height=400)

runOutfits()
