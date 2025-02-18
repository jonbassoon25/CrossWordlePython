'''
Jonathan Hanson, Zac Young, Eric Lu

crossWordle.py

A game where you solve crossword puzzles by completing wordles.

3.30.23
'''
#allWords.txt is based on the word list from the site http://www.mieliestronk.com/corncob_lowercase.txt and is being used under the fair use copyright

#the following modules were not created by our team and are open source, preinstalled with python 3
import random
import json

#the pygame module was created by Pete Shinners and is being used under the GNU license
import pygame

#initalizes pygame
pygame.init()

#init game state
gameState = "start"

#init gameInstructions
global gameInstructions
gameInstructions = "Welcome to Crosswordle!\n    Crosswordle is a game that combines the newspaper sensation\nof the 20th century with the \"Word Game\" genre smash hit of 2022.\nTo play, simply solve the crossword by clicking on each empty\nword capsule. Clicking on a empty word capsule brings up a wordle\ngame, and upon winning the wordle, the word is added onto the\ncrossword. Don't worry! Unlike traditional wordles, you have\ninfinite tries. However, if you are looking to beat a friend's\nscore, try to be efficient with your guesses because each guess\nreduces your score.\n    Difficulty selection also impacts your score. Choosing a\nhigher difficulty will greatly increase your final score, but\nbeware: It is not for the faint of heart.\n    An example wordle game is provided. A feature worth noting\nis the letter dictionary to the left, which shows you the status\nof every letter by color. If a letter is brown, it means you have\nnot tried to use it yet. If a letter is gray, you have tried it,\nand it does not appear anywhere in the unknown word. If a letter\nis yellow, it is part of the target word, but you have not placed\nit in the correct position yet. Yellow letters also are displayed\nbelow your input, in the original column it was placed in, for\nreference. Finally, if a letter is green, it is in the target\nword and in the correct position! Green letters are also\ndisplayed above your input. In order to guess a word, just start\ntyping. Your guess will appear in the lower word capsule. Once\nyou have filled every position, press enter, and you will receive\nthe results. Just like in a normal crossword, solving one word\nmay give you an advantage when solving others. Upon the\ncompletion of the crossword, your score will be displayed.\n                         Good luck!"
gameInstructions = gameInstructions.split("\n")
#init keyPresses
keyPresses = []

#init hitboxes
hitboxes = []

#init button states
buttonStates = ["normal", "normal", "normal", "normal", "normal", "normal", "normal", "normal"]

#load and transform images
#gameExamplePng = pygame.image.load("gameExample.jpg")

#init playing state
playing = True

#init playerScore and baseScore
playerScore = 0
global baseScore
baseScore = 100000

#init crossword and dimensions
crosswordDimensions = [25, 25]
#how much to multiply by to get accurate size of tiles
crosswordMultipliers = [
 600 // crosswordDimensions[0], 600 // crosswordDimensions[1]
]

#max fails before aborting a word spawn
maxFails = 50000

#init game screen
screen = pygame.display.set_mode([600, 600])

#button colors for different states
buttonColors = {
 "normal": "#555555",
 "hovering": "#777777",
 "pressed": "#BBBBBB"
}

#constants for cleaner code
global min
global max
min = 0
max = 1
global x
global y
x = 0
y = 1

#loads all scores from sava data
def loadScores():
	#scores formatted as allScores = {"username": highscore, "username": highscore"}
	try:
		with open("allScores.json") as scoreFile:
			allScores = json.load(scoreFile)
	#if the file is not found
	except:
		allScores = {}

	return allScores

#saves all scores to save data
def saveScores(allScores):
	with open("allScores.json", "w") as scoreFile:
		json.dump(allScores, scoreFile)

#generates player score
def generateScore(guesses, words, difficulty):
	score = baseScore
	avgWordsPerGuess = words/guesses
	if difficulty == "easy":
		difficultyMultiplier = 0.5
	if difficulty == "medium":
		difficultyMultiplier = 1
	if difficulty == "hard":
		difficultyMultiplier = 4
	score = score * avgWordsPerGuess * difficultyMultiplier
	return round(score)
	
#generate a useable word list
def generateWordList(wordLength):
	#clear words list of words that are not within set wordLength boundaries
	with open("allWords.txt") as wordFile:
		allWords = wordFile.readlines()
	worthlessWordIndexes = []
	for i in range(len(allWords)):
		allWords[i] = allWords[i].strip()
		if len(allWords[i]) < wordLength[min] or len(allWords[i]) > wordLength[max]:
			worthlessWordIndexes.append(i)
	worthlessWordIndexes.sort()
	worthlessWordIndexes.reverse()
	for i in range(len(worthlessWordIndexes)):
		del allWords[worthlessWordIndexes[i]]
	with open("workingWords.txt", "w") as newFile:
		newFile.write('\n'.join(allWords))


#init crossword data
def initCrosswordData(crosswordDimensions):
	'''
	// means none
	-/ means blacklisted space (nothing can spawn in it)
	- {letter} means letter not shown
	+ {letter} means letter is shown
	'''
	crosswordData = []
	for i in range(crosswordDimensions[1]):
		xData = []
		for k in range(crosswordDimensions[0]):
			xData.append("//")
		crosswordData.append(xData)
	return crosswordData


#loops through crossword data, called only once per frame
def crosswordDataLoop(crosswordData, change, screen=False, crosswordMultipliers=[]):
	won = True
	#change is represented as [x position, y position, changed data]
	#for every y
	for i in range(len(crosswordData)):
		#for every x
		for k in range(len(crosswordData[i])):
			if screen:
				if crosswordData[i][k][1] != "/":
					pygame.draw.rect(screen, "#000000", (k * crosswordMultipliers[0], i * crosswordMultipliers[1], 600 / crosswordMultipliers[0], 600 / crosswordMultipliers[1]), 2)
					if crosswordData[i][k][0] == "+":
						font = pygame.font.SysFont("monospace",round(crosswordMultipliers[0]) - 3)
						sentence = font.render(crosswordData[i][k][1], True, "black")
						screen.blit(sentence, (k * crosswordMultipliers[0] + 5, i * crosswordMultipliers[1]))
					if crosswordData[i][k][0] == "-":
						won = False
			if change:
				if change[0] == k and change[1] == i:
					#print(f"Writing Over {crosswordData[i][k]} with {change[2]}")
					crosswordData[i][k] = change[2]
	return crosswordData, won

def updateCrossword(changesToAdd, crosswordData):
	for change in changesToAdd:
		crosswordData, p = crosswordDataLoop(crosswordData, change)
	return crosswordData, []


def collectKeyPresses(event, keyPresses):
	if event.type == pygame.KEYDOWN:
		if event.key == pygame.K_a:
			keyPresses.append("a")
		if event.key == pygame.K_b:
			keyPresses.append("b")
		if event.key == pygame.K_c:
			keyPresses.append("c")
		if event.key == pygame.K_d:
			keyPresses.append("d")
		if event.key == pygame.K_e:
			keyPresses.append("e")
		if event.key == pygame.K_f:
			keyPresses.append("f")
		if event.key == pygame.K_g:
			keyPresses.append("g")
		if event.key == pygame.K_h:
			keyPresses.append("h")
		if event.key == pygame.K_i:
			keyPresses.append("i")
		if event.key == pygame.K_j:
			keyPresses.append("j")
		if event.key == pygame.K_k:
			keyPresses.append("k")
		if event.key == pygame.K_l:
			keyPresses.append("l")
		if event.key == pygame.K_m:
			keyPresses.append("m")
		if event.key == pygame.K_n:
			keyPresses.append("n")
		if event.key == pygame.K_o:
			keyPresses.append("o")
		if event.key == pygame.K_p:
			keyPresses.append("p")
		if event.key == pygame.K_q:
			keyPresses.append("q")
		if event.key == pygame.K_r:
			keyPresses.append("r")
		if event.key == pygame.K_s:
			keyPresses.append("s")
		if event.key == pygame.K_t:
			keyPresses.append("t")
		if event.key == pygame.K_u:
			keyPresses.append("u")
		if event.key == pygame.K_v:
			keyPresses.append("v")
		if event.key == pygame.K_w:
			keyPresses.append("w")
		if event.key == pygame.K_x:
			keyPresses.append("x")
		if event.key == pygame.K_y:
			keyPresses.append("y")
		if event.key == pygame.K_z:
			keyPresses.append("z")
		if event.key == pygame.K_BACKSPACE and len(keyPresses) > 0:
			del keyPresses[-1]
		if event.key == pygame.K_RETURN:
			keyPresses.append("\n")
	return keyPresses


#generate an empty letter dictionary
def generateLetterDict():
	dictionary = {}
	for i in range(26):
		dictionary[chr(97 + i)] = "#964B00"

	return dictionary


#generate the wordle game
def wordleGame(screen, keyPresses, hitbox, letterDict, greens, yellows, crosswordData, guesses):
	with open("workingWords.txt") as workingFile:
		workingWords = workingFile.readlines()
	#derive the word from the hitbox
	word = hitbox[4]
	#check if the word is a real word
	if not workingWords.count("".join(keyPresses)) > 0 and len(keyPresses) > len(word):
		print("Either that is not a real word, or it has been deemed inappropriate.")
		keyPresses = []
	#create empty list greens to display green letters
	if len(greens) == 0:
		for letter in word:
			greens.append("")
	#create empty list of lists yellows to display yellow letters
	if len(yellows) == 0:
		for column in word:
			yellows.append([])
		#fetch the letters that are already revealed from crosswordData
		#if the hitbox is vertical
		if hitbox[2] == 1:
			for i in range(hitbox[3]):
				if crosswordData[hitbox[1] + i][hitbox[0]][0] == "+":
					greens[i] = word[i]
					letterDict[word[i]] = "green"
					#if there are more of that letter to be found
					if word.count(word[i]) > greens.count(word[i]):
						#add the letter to yellows
						yellows[i].append(word[i])
						letterDict[word[i]] = "yellow"
		#if the hitbox is horitontal
		if hitbox[3] == 1:
			for i in range(hitbox[2]):
				if crosswordData[hitbox[1]][hitbox[0] + i][0] == "+":
					#update all data values to show the letter being green
					greens[i] = word[i]
					letterDict[word[i]] = "green"
					#if there are more of that letter to be found
					if word.count(word[i]) > greens.count(word[i]):
						#add the letter to yellows
						yellows[i].append(word[i])
						letterDict[word[i]] = "yellow"
	#try is used in order to prevent "Index Out Of Range" error due to keyPresses being empty on the first iteration
	try:
		previousKeyPress = keyPresses[-1]
	except:
		previousKeyPress = ""
	#init wordGuessed
	wordGuessed = False
	#if the user has input too many characters or the user has inputted a word of insufficient length and pressed enter
	if (len(keyPresses) > len(word) and keyPresses[-1] != "\n") or (previousKeyPress == "\n" and len(keyPresses) <= len(word)):
		#remove the last keypress from keyPresses
		del keyPresses[-1]
	#if the user has inputted a full word and pressed enter
	if len(keyPresses) > len(word) and keyPresses[-1] == "\n":
		#remove the enter from keyPresses
		del keyPresses[-1]
		#for each letter in keyPresses
		for i in range(len(keyPresses)):
			#if the letter is shared by the word and in the right position
			if keyPresses[i] == word[i] and greens[i] != word[i]:
				#update all data values to show the letter being green
				greens[i] = word[i]
				letterDict[keyPresses[i]] = "green"
				#if there are more of that letter to be found
				if word.count(keyPresses[i]) > greens.count(keyPresses[i]):
					#add the letter to yellows
					if yellows[i].count(keyPresses[i]) == 0: #prevents duplicates
						yellows[i].append(keyPresses[i])
					letterDict[keyPresses[i]] = "yellow"
				else: #there are no more of that letter to be found, so remove any of its appearances from yellows
					for n in range(len(yellows)):
						yellowsToDel = []
						for l in range(len(yellows[n])):
							if yellows[n][l] == keyPresses[i]:
								yellowsToDel.append(l)
						yellowsToDel.reverse()
						for u in range(len(yellowsToDel)):
							del yellows[n][yellowsToDel[u]]
			#if the letter is shared by the word, but not in the right position
			elif word.count(keyPresses[i]) > 0:
				#update all data values to show the letter being yellow
				#prevent the yellow from spawning if we have already found every one of that letter
				if greens.count(keyPresses[i]) < word.count(keyPresses[i]):
					if yellows[i].count(keyPresses[i]) == 0: #prevents duplicates
						yellows[i].append(keyPresses[i])
				#should override green in letterDict in the case of the word having repeated letters, but not if there are none of that letter left to find
				if greens.count(keyPresses[i]) < word.count(keyPresses[i]):
					letterDict[keyPresses[i]] = "yellow"
			#else (the word does not contain the letter)
			else:
				#update all data values to show the letter being gray
				letterDict[keyPresses[i]] = "#333333"
		'''
		print("Greens: " + str(greens))
		print("Yellows: " + str(yellows))
		'''
		if word == "".join(keyPresses):
			wordGuessed = True
		#clear keyPresses in preparation for the user's next guess
		guesses += 1
		keyPresses = []
	return keyPresses, letterDict, greens, yellows, wordGuessed, guesses

	
#generates crossword map
def generateCrossword(crosswordDimensions, wordCount):
	crosswordData = initCrosswordData(crosswordDimensions)
	changesToAdd = []
	possiblePositions = []
	#init hitboxes
	hitboxes = []
	with open("workingWords.txt") as workingFile:
		workingWords = workingFile.readlines()
	baseWord = workingWords[random.randint(0, len(workingWords) - 1)].strip()
	# plant the base word in the center of the crossword
	basePosition = [
	 round(crosswordDimensions[x] / 2) - round(len(baseWord) / 2),
	 round(crosswordDimensions[y] / 2)
	]
	for i in range(len(baseWord)):
		#baseword spawned
		changesToAdd.append([basePosition[x] + i, basePosition[y], "-" + baseWord[i]])
		possiblePositions.append([basePosition[x] + i, basePosition[y]])
	#print("Base Word: " + baseWord)
	#blacklist the spots on each end of the base word
	changesToAdd.append([basePosition[x] - 1, basePosition[y], "-/"])
	changesToAdd.append([basePosition[x] + len(baseWord), basePosition[y], "-/"])
	#add the hitbox of the base word to the hitboxes list
	#hitboxes [[x, y, width, height, word]]
	hitboxes.append([basePosition[x], basePosition[y], len(baseWord), 1, baseWord])
	#repeatedly create a new random word, and if it is compatible with a word that is already there, add it to the crossword, and add the coordinates of each letter to usedLocations and edit crossword data
	crosswordData, changesToAdd = updateCrossword(changesToAdd, crosswordData)
	#for every word as many times as words are needed
	failCount = 0
	while wordCount > 0:
		found = False
		#while there are no possible positions
		while not found:
			#choose a new random word
			newWord = workingWords[random.randint(0, len(workingWords) - 1)].strip()
			#for every letter in the new word
			for i in range(len(newWord)):
				#for every reference letter
				for k in range(len(possiblePositions)):
					#if the reference letter is equal to the current letter in the new word (meaning that the new word shares a letter with any of the previous words)
					if newWord[i] == crosswordData[possiblePositions[k][y]][possiblePositions[k][x]][1]:
						found = True
		#for every position in possible positions
		broken = False
		wordFound = False
		for position in possiblePositions:
			wordCountAdded = False
			if broken:
				break
			#try to spawn the word vertically on the position
			sharedLetter = crosswordData[position[y]][position[x]][1]
			for i in range(len(newWord)):
				if broken:
					break
				#sometimes these positions go out of the boundaries of the screen, so we put them into a try loop
				try:
					test1 = crosswordData[position[y] + len(newWord) - i][position[x]] == "//"
					test2 = crosswordData[position[y] - i - 1][position[x]] == "//"
				except:
					#the word does not work in that position so try a different one
					continue
				#if the current letter is the shared letter and the spawn is not inturupted by spawning directly perpendicular to another word
				if newWord[i] == sharedLetter and test1 and test2:
					#now that we know the sharedLetter's position, check the positions VERTICAL to the sharedLetter in order to see if the spawn is compatible
					for k in range(len(newWord)):
						#if the position of the new letter is not outside the borders and is over an empty tile or one of the same letter
						if ((position[y] - i + k > 0) and (position[y] - i + k + 1 + len(newWord) < crosswordDimensions[y]) and (crosswordData[position[y] - i + k][position[x]] == "//" or crosswordData[position[y] - i + k][position[x]][1] == newWord[i])):
							#if every position is correct (the for loop has reached the end without breaking)
							if k == (len(newWord) - 1):
								#spawn the word vertically
								#print(newWord + " Spawned")
								#set fails to 0
								failCount = 0
								for j in range(len(newWord)):
									#prevents duplicates in possiblePositions
									if possiblePositions.count([position[x], position[y] - i + j]) == 0:
										possiblePositions.append([position[x], position[y] - i + j])
									#if there is an intersection, blacklist the squares around it
									if crosswordData[position[y] - i + j][position[x]] != "//":
										#if there is something above
										if i != 0:
											#if there is something to the right
											if crosswordData[position[y] - i + j][position[x] + 1][1] != "/":
												#spawn right and up
												changesToAdd.append([position[x] + 1, position[y] - i + j - 1, "-/"])
											#if there is something to the left
											if crosswordData[position[y] - i + j][position[x] - 1][1] != "/":
												#spawn left and up
												changesToAdd.append([position[x] - 1, position[y] - i + j - 1, "-/"])
										#if there is something below
										if i != len(newWord):
											#if there is something to the right
											if crosswordData[position[y] - i + j][position[x] + 1][1] != "/":
												#spawn right and down
												changesToAdd.append([position[x] + 1, position[y] - i + j + 1, "-/"])
											#if there is something to the left
											if crosswordData[position[y] - i + j][position[x] - 1][1] != "/":
												changesToAdd.append([position[x] - 1, position[y] - i + j + 1, "-/"])
									#if it is the first letter
									if j - i == 0:
										pass
										#possiblePositions.remove([position[x], position[y] - i + j])
									#spawn each letter of the word with "-" dictating that they are hidden
									changesToAdd.append([position[x], position[y] - i + j, "-" + newWord[j]])
								#add hitbox of word to hitboxes
								hitboxes.append([position[x], position[y] - i, 1, len(newWord), newWord])
								#add blacklisted locations to crosswordData to predetermined positions based on the kind of spawn. Used to prevent words spawning directly next to one another
								changesToAdd.append([position[x], position[y] - i - 1, "-/"])
								changesToAdd.append([position[x], position[y] - i + len(newWord), "-/"])
								#update the crossword
								crosswordData, changesToAdd = updateCrossword(changesToAdd, crosswordData)
								broken = True
								wordFound = True
								workingWords.remove(newWord + "\n")
								failCount = 0
								break
						else:
							#the word failed to spawn vertically, so try spawning horizontally instead
							broken = True
							break
			#try to spawn the word

			broken = False
			if wordFound:
				broken = True
			for i in range(len(newWord)):
				if broken:
					break
				#sometimes these positions go out of the boundaries of the screen, so we put them into a try loop
				try:
					test1 = crosswordData[position[y]][position[x] - i + len(newWord)] == "//"
					test2 = crosswordData[position[y]][position[x] - i - 1] == "//"
				except:
					#the word does not work in the current position so try a different one
					continue
				#if the letter i is shared letter and there is space on each end of the word
				if newWord[i] == sharedLetter and test1 and test2:
					#now that we know the sharedLetter's position, check the positions HORIZONTAL to the sharedLetter in order to see if the spawn is compatible
					for k in range(len(newWord)):
						#if the position of the new letter is not outside the borders and is over an empty tile or one of the same letter
						if (position[x] - i + k >= 0) and (position[x] - i + k + 1 + len(newWord) < crosswordDimensions[x]) and (crosswordData[position[y]][position[x] - i + k] == "//" or crosswordData[position[y]][position[x] - i + k][1] == newWord[i]):
							#if every position is correct (the for loop has reached the end without breaking)
							if k == (len(newWord) - 1):
								#spawn the word vertically
								#print(newWord + " Spawned")
								#set failCount to 0
								failCount = 0
								for j in range(len(newWord)):
									#prevents duplicates in possiblePositions
									if possiblePositions.count([position[x] - i + j, position[y]]) == 0:
										possiblePositions.append([position[x] - i + j, position[y]])
									#if there is an intersection, check and blacklist the squares around it
									if crosswordData[position[y]][position[x] - i + j] != "//":
										#if there is something to the left
										if i != 0:
											#if there is something above
											if crosswordData[position[y] - 1][position[x] - i + j][1] != "/":
												#spawn left and up
												changesToAdd.append(
												 [position[x] - i + j - 1, position[y] - 1, "-/"])
											#if there is something below
											if crosswordData[position[y] + 1][position[x] - i + j][1] != "/":
												#spawn left and below
												changesToAdd.append(
												 [position[x] - i + j - 1, position[y] + 1, "-/"])
										#if there is something to the right
										if i != len(newWord):
											#if there is something above
											
											if crosswordData[position[y] - 1][position[x] - i + j][1] != "/":
												#spawn right and above
												changesToAdd.append([position[x] - i + j + 1, position[y] - 1, "-/"])
											#if there is something below
											
											if crosswordData[position[y] + 1][position[x] - i + j][1] != "/":
												#spawn right and below
												changesToAdd.append([position[x] - i + j + 1, position[y] + 1, "-/"])
									#spawn each letter of the word with "-" dictating that they are hidden
									if j - i == 0:
										pass
										#possiblePositions.remove([position[x] - i + j, position[y]])
									changesToAdd.append([position[x] - i + j, position[y], "-" + newWord[j]])
									crosswordData, changesToAdd = updateCrossword(changesToAdd, crosswordData)
								hitboxes.append([position[x] - i, position[y], len(newWord), 1, newWord])
								#add blacklisted locations to crosswordData to predetermined positions based on the kind of spawn. Used to prevent words spawning directly next to one another
								changesToAdd.append([position[x] - i - 1, position[y], "-/"])
								changesToAdd.append([position[x] - i + len(newWord), position[y], "-/"])
								crosswordData, changesToAdd = updateCrossword(changesToAdd,crosswordData)
								broken = True
								workingWords.remove(newWord + "\n")
								failCount = 0
								break
						else:
							#the word failed, so break the for loop and get a new random word
							wordCount += 1
							wordCountAdded = True
							failCount += 1
							broken = True
							break
			try:
				if possiblePositions.index(position) == len(possiblePositions) - 1 and not wordCountAdded:
					wordCount += 1
			except:
				pass
		wordCount -= 1
		if failCount >= maxFails:
			print("too many fails")
			crosswordData = "fail"
			break
	#keep at end of program
	return crosswordData, hitboxes



def displayText(screen, x, y, text, textSize):
	font = pygame.font.SysFont("monospace", textSize)
	sentence = font.render(text, True, "black")
	screen.blit(sentence, (x, y))



def drawButton(screen, rect, state, buttonColors):
	if state == "normal":
		pygame.draw.rect(screen, buttonColors["normal"], (rect[0], rect[1], rect[2], rect[3]))
	if state == "hovering":
		pygame.draw.rect(screen, buttonColors["hovering"], (rect[0], rect[1], rect[2], rect[3]))
	if state == "pressed":
		pygame.draw.rect(screen, buttonColors["pressed"],
				 (rect[0], rect[1], rect[2], rect[3]))

#draws all greens
def drawGreens(screen, greens):
	for i in range(len(greens)):
		if greens[i] != "":
			pygame.draw.rect(screen, "#55FF00", (200 + (i * 25), 75, 25, 25))
		pygame.draw.rect(screen, "#000000", ((i * 25) + 200, 75, 25, 25), 2)
		font = pygame.font.SysFont("monospace", 25)
		letter = font.render(greens[i], True, "black")
		screen.blit(letter, ((i * 25) + 203, 97 - 25))

#draws player input below greens
def drawInput(screen, keyPresses, greens):
	for i in range(len(greens)):
		pygame.draw.rect(screen, "#000000", ((i * 25) + 200, 125, 25, 25), 2)
	for i in range(len(keyPresses)):
		font = pygame.font.SysFont("monospace", 25)
		letter = font.render(keyPresses[i], True, "black")
		screen.blit(letter, ((i * 25) + 203, 97 + 25))

#draws all yellow markers
def drawYellows(screen, yellows):
	for i in range(len(yellows)):
		for k in range(len(yellows[i])):
			pygame.draw.rect(screen, "#000000", (200 + (i * 25), 175 + (k * 25), 25, 25), 2)
			pygame.draw.rect(screen, "#FFFF00", (200 + (i * 25), 175 + (k * 25), 25, 25))
			font = pygame.font.SysFont("monospace", 25)
			letter = font.render(yellows[i][k], True, "black")
			screen.blit(letter, ((i * 25) + 203, 147 + 25 + (k * 25)))

#draws alphabet on left side of screen
def drawLetterDict(screen, letterDict):
	#for 24 letters (a - x)
	for i in range(6):
		for k in range(4):
			pygame.draw.rect(screen, "#000000", (25 + (k * 25), 100 + (i * 25), 25, 25), 2)
			pygame.draw.rect(screen, letterDict[chr(k * 6 + i + 97)], (25 + (k * 25), 100 + (i * 25), 25, 25))
			font = pygame.font.SysFont("monospace", 25)
			letter = font.render(chr(k * 6 + i + 97), True, "black")
			screen.blit(letter, ((k * 25) + 28, 97 + (i * 25)))
	#for y
	pygame.draw.rect(screen, "#000000", (25 + (4 * 25), 100 + (0 * 25), 25, 25), 2)
	pygame.draw.rect(screen, letterDict["y"], (25 + (4 * 25), 100 + (0 * 25), 25, 25))
	font = pygame.font.SysFont("monospace", 25)
	letter = font.render("y", True, "black")
	screen.blit(letter, ((4 * 25) + 28, 97 + (0 * 25)))
	#for z
	pygame.draw.rect(screen, "#000000", (25 + (4 * 25), 100 + (1 * 25), 25, 25), 2)
	pygame.draw.rect(screen, letterDict["z"], (25 + (4 * 25), 100 + (1 * 25), 25, 25))
	font = pygame.font.SysFont("monospace", 25)
	letter = font.render("z", True, "black")
	screen.blit(letter, ((4 * 25) + 28, 97 + (1 * 25)))
			


	
	


'''
generateLetterDict()
generateWordList(wordLength)
crossword, hitboxes = generateCrossword(crosswordDimensions, wordCount)
crossword = centerCrossword(crossword, crosswordDimensions)
'''
while playing:
	#happens for every event in pygame
	for event in pygame.event.get():
		#if the esc key is pressed or the quit event is recieved
		if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
			playing = False
			break
		if gameState == "wordle" or gameState == "save":
			keyPresses = collectKeyPresses(event, keyPresses)
		if event.type == pygame.MOUSEBUTTONDOWN:
			if mouseX > 175 and mouseX < 425 and mouseY > 150 and mouseY < 250 and buttonStates[0] != "pressed":
				buttonStates[0] = "pressed"

			if mouseX > 175 and mouseX < 425 and mouseY > 300 and mouseY < 400 and buttonStates[1] != "pressed":
				buttonStates[1] = "pressed"

			if mouseX > 175 and mouseX < 425 and mouseY > 450 and mouseY < 550 and buttonStates[2] != "pressed":
				buttonStates[2] = "pressed"
			if mouseX > 0 and mouseX < 100 and mouseY > 450 and mouseY < 500 and buttonStates[3] != "pressed":
				buttonStates[3] = "pressed"
			if mouseX > 125 and mouseX < 275 and mouseY > 400 and mouseY < 450 and buttonStates[4] != "pressed":
				buttonStates[4] = "pressed"

			if mouseX > 325 and mouseX < 475 and mouseY > 400 and mouseY < 450 and buttonStates[5] != "pressed":
				buttonStates[5] = "pressed"
				
			if mouseX > 0 and mouseX < 100 and mouseY > 0 and mouseY < 50 and buttonStates[6] != "pressed":
				buttonStates[6] = "pressed"
			if mouseX > 100 and mouseX < 500 and mouseY > 550 and mouseY < 590 and buttonStates[7] != "pressed":
				buttonStates[7] = "pressed"
				
		if event.type == pygame.MOUSEBUTTONUP:
			buttonStates = ["normal", "normal", "normal", "normal", "normal", "normal", "normal", "normal"]
			if mouseX > 175 and mouseX < 425 and mouseY > 150 and mouseY < 250 and buttonStates[0] != "pressed":
				if gameState == "difficultySelect":
					difficulty = "easy"
				if gameState == "start":
					gameState = "difficultySelect"
				
			if mouseX > 175 and mouseX < 425 and mouseY > 300 and mouseY < 400 and buttonStates[1] != "pressed":
				if gameState == "start":
					gameState = "leaderboard"
				if gameState == "difficultySelect":
					difficulty = "medium"

			if mouseX > 175 and mouseX < 425 and mouseY > 450 and mouseY < 550 and buttonStates[2] != "pressed":
				if gameState == "start":
					gameState = "help"
				if gameState == "difficultySelect":
					difficulty = "hard"
			if mouseX > 0 and mouseX < 100 and mouseY > 450 and mouseY < 500 and buttonStates[3] != "pressed" and gameState == "wordle":
				gameState = "crossword"

			if mouseX > 125 and mouseX < 275 and mouseY > 400 and mouseY < 450 and buttonStates[4] != "pressed" and gameState == "win":
				gameState = "start"

			if mouseX > 325 and mouseX < 475 and mouseY > 400 and mouseY < 450 and buttonStates[5] != "pressed" and gameState == "win":
				gameState = "save"
				
			if mouseX > 0 and mouseX < 100 and mouseY > 0 and mouseY < 50 and buttonStates[6] != "pressed" and (gameState == "leaderboard" or gameState == "help" or gameState == "difficultySelect" or gameState == "exampleGame"):
				if gameState == "exampleGame":
					gameState = "help"
				else:
					gameState = "start"
			if mouseX > 100 and mouseX < 500 and mouseY > 550 and mouseY < 590 and gameState == "help":
				gameState = "exampleGame"

			for hitbox in hitboxes:
				if mouseX > hitbox[0] * crosswordMultipliers[0] and mouseX < (hitbox[0] + hitbox[2]) * crosswordMultipliers[0] and mouseY > hitbox[1] * crosswordMultipliers[1] and mouseY < (hitbox[1] + hitbox[3]) * crosswordMultipliers[1]:
					wordleHitbox = hitbox
					gameState = "initWordle"


	#gets mouse coordinates
	mouseX, mouseY = pygame.mouse.get_pos()
	if gameState == "start" or gameState == "difficultySelect":
		#is the mouse over any buttons, if so change the button state
		if mouseX > 175 and mouseX < 425 and mouseY > 150 and mouseY < 250 and buttonStates[0] != "pressed":
			buttonStates[0] = "hovering"
		elif buttonStates[0] != "pressed":
			buttonStates[0] = "normal"
		if mouseX > 175 and mouseX < 425 and mouseY > 300 and mouseY < 400 and buttonStates[1] != "pressed":
			buttonStates[1] = "hovering"
		elif buttonStates[1] != "pressed":
			buttonStates[1] = "normal"
		if mouseX > 175 and mouseX < 425 and mouseY > 450 and mouseY < 550 and buttonStates[2] != "pressed":
			buttonStates[2] = "hovering"
		elif buttonStates[2] != "pressed":
			buttonStates[2] = "normal"
	if gameState == "wordle":
		if mouseX > 0 and mouseX < 100 and mouseY > 450 and mouseY < 500 and buttonStates[3] != "pressed":
			buttonStates[3] = "hovering"
		elif buttonStates[3] != "pressed":
			buttonStates[3] = "normal"
	screen.fill("light gray")
	if gameState == "win":#125, 400, 150, 50
		if mouseX > 125 and mouseX < 275 and mouseY > 400 and mouseY < 450 and buttonStates[4] != "pressed":
			buttonStates[4] = "hovering"
		elif buttonStates[4] != "pressed":
			buttonStates[4] = "normal"
		if mouseX > 325 and mouseX < 475 and mouseY > 400 and mouseY < 450 and buttonStates[5] != "pressed":
			buttonStates[5] = "hovering"
		elif buttonStates[5] != "pressed":
			buttonStates[5] = "normal"
	if gameState == "leaderboard" or gameState == "help" or gameState == "difficultySelect" or gameState == "exampleGame":
		if mouseX > 0 and mouseX < 100 and mouseY > 0 and mouseY < 50 and buttonStates[6] != "pressed":
			buttonStates[6] = "hovering"
		elif buttonStates[6] != "pressed":
			buttonStates[6] = "normal"
	if gameState == "help":
		#[100, 550, 400, 40]
		if mouseX > 100 and mouseX < 500 and mouseY > 550 and mouseY < 590 and buttonStates[7] != "pressed":
			buttonStates[7] = "hovering"
		elif buttonStates[7] != "pressed":
			buttonStates[7] = "normal"
	#if gameState is start draw menu screen
	if gameState == "start":
		drawButton(screen, [175, 150, 250, 100], buttonStates[0], buttonColors)
		drawButton(screen, [175, 300, 250, 100], buttonStates[1], buttonColors)
		drawButton(screen, [175, 450, 250, 100], buttonStates[2], buttonColors)
		displayText(screen, 65, 40, "CROSSWORDLE", 75)
		displayText(screen, 240, 175, "PLAY", 50)
		displayText(screen, 185, 330, "LEADERBOARD", 35)
		displayText(screen, 210, 450, "How To", 50)
		displayText(screen, 240, 490, "Play", 50)
		difficulty = ""

	if gameState == "difficultySelect":
		#difficulty = input("What is the difficulty?\n").lower()
		drawButton(screen, (0, 0, 100, 50), buttonStates[6], buttonColors)
		displayText(screen, 3, 3, "Back", 30)
		displayText(screen, 25, 50, "Select a Difficulty", 50)
		drawButton(screen, [175, 150, 250, 100], buttonStates[0], buttonColors)
		drawButton(screen, [175, 300, 250, 100], buttonStates[1], buttonColors)
		drawButton(screen, [175, 450, 250, 100], buttonStates[2], buttonColors)
		displayText(screen, 240, 175, "EASY", 50)
		displayText(screen, 200, 330, "MEDIUM", 50)
		displayText(screen, 240, 480, "HARD", 50)
		
		
		if difficulty == "easy":
			#max word length is 22, min max word length is 4
			#min word length is 2
			wordLength = [3,5]  #min, max
			#init wordCount for number of words in crossword
			wordCount = 4
		if difficulty == "medium":
			#max word length is 22, min max word length is 4
			#min word length is 2
			wordLength = [4, 8]  #min, max
			#init wordCount for number of words in crossword
			wordCount = 8
		if difficulty == "hard":
			#max word length is 22, min max word length is 4
			#min word length is 2
			wordLength = [5, 15]  #min, max
			#init wordCount for number of words in crossword
			wordCount = 12
		if difficulty != "":
			gameState = "initgame"


		
	#if gamestate is initgame generate the crossword
	if gameState == "initgame":
		crosswordData = "fail"
		while crosswordData == "fail":
			generateWordList(wordLength)
			crosswordData, hitboxes = generateCrossword(crosswordDimensions, wordCount)
		#crosswordData = centerCrossword(crosswordData, crosswordDimensions)
		change = None
		guesses = 0
		gameState = "crossword"
	#if gameState is crossword allow the user to play and show the crossword portion of the game
	if gameState == "crossword":
		#shows game data and allows it to be edited
		crosswordData, won = crosswordDataLoop(crosswordData, change, screen, crosswordMultipliers)
		#hitbox is [x, y, width, height, word]
		for hitbox in hitboxes:
			if mouseX > hitbox[0] * crosswordMultipliers[0] and mouseX < (hitbox[0] + hitbox[2]) * crosswordMultipliers[0] and mouseY > hitbox[1] * crosswordMultipliers[1] and mouseY < (hitbox[1] + hitbox[3]) * crosswordMultipliers[1]:
				pygame.draw.rect(screen, "#FFFFFF", (hitbox[0] * crosswordMultipliers[0], hitbox[1] * crosswordMultipliers[1], hitbox[2] * crosswordMultipliers[0], hitbox[3] * crosswordMultipliers[1]), 3)
		change = None
		if won:
			gameState = "win"

	#if gameState is worlde allow the user to play and show the wordle portion of the game
	if gameState == "initWordle":
		greens = []
		yellows = []
		letterDict = generateLetterDict()
		gameState = "wordle"
		#print(wordleHitbox[4])
	if gameState == "wordle":
		keyPresses, letterDict, greens, yellows, hasWon, guesses = wordleGame(screen, keyPresses, wordleHitbox, letterDict, greens, yellows, crosswordData, guesses)
		drawGreens(screen, greens)
		drawYellows(screen, yellows)
		drawLetterDict(screen, letterDict)
		drawInput(screen, keyPresses, greens)
		drawButton(screen, [0, 450, 100, 50], buttonStates[3], buttonColors)
		displayText(screen, 15, 460, "Back", 25)
		if hasWon:
			print("Wordle won")
			keyPresses = []
			hitboxes.remove(wordleHitbox)
			#if the hitbox is vertical
			changesToAdd = []
			if wordleHitbox[2] == 1:
				#replace the -s with +s in order to show the completed word on the crossword
				for i in range(len(wordleHitbox[4])):
					changesToAdd.append([wordleHitbox[0], wordleHitbox[1] + i, "+" + wordleHitbox[4][i]])
			#if the hitbox is horitontal
			if wordleHitbox[3] == 1:
				#replace the -s with +s in order to show the completed word on the crossword
				for i in range(len(wordleHitbox[4])):
					changesToAdd.append([wordleHitbox[0] + i, wordleHitbox[1], "+" + wordleHitbox[4][i]])
			changesToAdd, crossword = updateCrossword(changesToAdd, crosswordData)
			#if the game has been won (all letters have been revealed)
			gameState = "crossword"
	if gameState == "win":
		#player has won. Display celabratory messages and allow them to return to title screen
		#random number for random message
		randomNumber = random.randint(0, 2)
		if difficulty == "easy":
			displayText(screen, 175, 100, "GOOD JOB!", 50)
		if difficulty == "medium":
			displayText(screen, 175, 100, "CONGRATS!", 50)
		if difficulty == "hard":
			displayText(screen, 125, 100, "AMAZING WORK!", 50)
		finalScore = generateScore(guesses, wordCount, difficulty)
		displayText(screen, 115, 250, f"Your Score Was {finalScore}!", 30)
		drawButton(screen, [125, 400, 150, 50], buttonStates[4], buttonColors)
		drawButton(screen, [325, 400, 150, 50], buttonStates[5], buttonColors)
		displayText(screen, 125, 415, "<- Back to Menu", 15)
		displayText(screen, 335, 415, "Save   Score ->", 15)
	#if the player has clicked the "help" button
	if gameState == "help":
		drawButton(screen, (0, 0, 100, 50), buttonStates[6], buttonColors)
		displayText(screen, 3, 3, "Back", 30)
		displayText(screen, 193, 50, "INSTRUCTIONS", 30)
		#display the formatted game instructions
		for i in range(len(gameInstructions)):
			displayText(screen, 10, 90 + i * 15, gameInstructions[i], 15)
		drawButton(screen, [100, 550, 400, 40], buttonStates[7], buttonColors)
		displayText(screen, 160, 550, "Example Game", 36)
	if gameState == "exampleGame":
		drawButton(screen, (0, 0, 100, 50), buttonStates[6], buttonColors)
		displayText(screen, 3, 3, "Back", 30)
		#draw game example picture
		#screen.blit(gameExamplePng, (50, 150))
	if gameState == "save":
		#12 char max for save name
		#if enter is pressed
		if len(keyPresses) > 1 and keyPresses[-1] == "\n":
			#add to all scores
			del keyPresses[-1]
			allScores = loadScores()
			allScores[''.join(keyPresses)] = finalScore
			saveScores(allScores)
			keyPresses = []
			gameState = "start"
			
		if len(keyPresses) > 12:
			del keyPresses[-1]
			
		pygame.draw.rect(screen, "#000000", (150, 200, 300, 25), 2)
		for i in range(len(keyPresses)):
			font = pygame.font.SysFont("monospace", 25)
			letter = font.render(keyPresses[i], True, "black")
			screen.blit(letter, ((i * 25) + 153, 198))
		displayText(screen, 150, 150, "Enter Username:", 35)
	if gameState == "leaderboard":
		displayText(screen, 185, 30, "Leaderboard", 35)
		drawButton(screen, (0, 0, 100, 50), buttonStates[6], buttonColors)
		displayText(screen, 3, 3, "Back", 30)
		allScores = loadScores()
		yOffset = 0
		names = []
		scores = []
		for k, v in allScores.items():
			names.append(k)
			scores.append(v)
		allScores = {}
		for k in range(len(names)):
			highestScore = 0
			for i in range(len(scores)):
				if scores[i] > highestScore:
					highestScoreIndex = i
					highestScore = scores[i]
			allScores[names[highestScoreIndex]] = highestScore
			del names[highestScoreIndex]
			del scores[highestScoreIndex]
		for k, v in allScores.items():
			displayText(screen, 150, yOffset + 100, f"{k}:{' '  * (12 - len(k))} {v}", 25)
			yOffset += 30
	pygame.display.flip()
pygame.quit()
