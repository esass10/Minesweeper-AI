# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action
import random
import time

class MyAI( AI ):

	# Tile class for initializing our board
	class Tile():
		label = -1						# 0-8 for value of square, -1 = covered&unflagged, -2 = covered&flagged		
		effective = -1					# effective = label - number of adjacent marked tiles
		numAdjCoveredUnflagged = 8	
		mineProb = 0		

	# startX / startY is where you're randomly placed. you don't choose.
	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
		# initialize class variables
		self.__start = time.time()
		self.__rows = rowDimension
		self.__cols = colDimension
		self.__totalTiles = rowDimension*colDimension
		self.__totalMines = totalMines
		self.__flagCount = 0
		self.__moveCount = 0
		self.__startX = startX
		self.__startY = startY
		self.__curX = startX
		self.__curY = startY
		self.__uncoverCount = 1	
		self.__zeroQueue = []					# queue of zero tiles to uncover. mass uncovers!
		self.__frontierCov = []					# queue of covered tiles
		self.__frontierUnc = {}					# mapping of uncovered frontier tiles to their mine probabilities
		self.__hintTileCoords = []				# list of coordinates for hint tiles
		self.__uncoverAll = []

		# intialize board -> 2d array of tiles, then update startX / startY
		self.__board = [[self.Tile() for i in range(self.__cols)] for j in range(self.__rows)]
			
		# look at border tiles and change numAdjCoveredUnflagged
		for i in range(0, self.__rows):
			if i == 0 or i == self.__rows-1:
				for j in range(0, self.__cols):
					if j == 0 or j == self.__cols-1:
						self.__board[i][j].numAdjCoveredUnflagged = 3
					else:
						self.__board[i][j].numAdjCoveredUnflagged = 5
			else:
				self.__board[i][0].numAdjCoveredUnflagged = 5
				self.__board[i][self.__cols-1].numAdjCoveredUnflagged = 5
				


	# update the board, setting label, and calculating effective label
	def updateBoard(self, x:int, y:int, label:int):
		self.__board[x][y].label = label
		if label >= 0:
			self.__board[x][y].effective = self.getEffectiveLabel(x,y)
		else:
			self.__board[x][y].effective = label

	# print the board
	def printBoard(self):
		for r in self.__board:
			print("\n")
			for c in r:
				if c.label == -2:
					print('F', end = "\t")
				elif c.label == -1:
					print('?', end = "\t")
				else:
					print(c.label, end = "\t")
	
	def printEffectiveBoard(self):
		for r in self.__board:
			print("\n")
			for c in r:
				print(c.effective, end = "\t")
	
	def printBoardAdjCovUnf(self):
		for r in self.__board:
			print("\n")
			for c in r:
				print(c.numAdjCoveredUnflagged, end = "\t")

	# return valid neighbors (valid = in range)
	def getValidNeighbors(self, x:int, y:int):
		#print("x:", x, "\ty:", y)
		possibleNeighbors = [(x-1, y-1), (x, y-1), (x+1, y-1), (x-1, y), (x+1, y), (x-1, y+1), (x, y+1), (x+1, y+1)]
		returnNeighbors = []
		for neighbor in possibleNeighbors:
			if neighbor[0] >= 0 and neighbor[0] <= self.__rows-1 and neighbor[1] >= 0 and neighbor[1] <= self.__cols-1:			# if board is in valid range
				returnNeighbors.append(neighbor)
		return returnNeighbors

	# helper function that retrieves the effective label for a single
	def getEffectiveLabel(self, x:int, y:int) -> "Effective Label":
		effectiveLabel = self.__board[x][y].label - self.getNumAdjFlaggedTiles(x,y)
		return effectiveLabel
		
	# helper function that gets the number of adjacent flagged tiles
	def getNumAdjFlaggedTiles(self, x:int, y:int) -> "Adjacent Flagged Tiles Count":
		labels = self.getNeighborLabels(x,y)			
		adjFlagCount = 0
		for label in labels:
			if label == -2:
				adjFlagCount += 1
		return adjFlagCount

	# helper function that gets neighboring labels from a tile
	def getNeighborLabels(self, x:int, y:int) -> "List of Neighbor's Labels":
		neighborCoordinates = self.getValidNeighbors(x,y)						# get coordinates of all valid neighbors
		returnList = []															# return list of labels												
		for neighbor in neighborCoordinates:
			returnList.append(self.__board[neighbor[0]][neighbor[1]].label)		# look at label of all valid neighbors
		return returnList

	# helper function that decrements numAdjCoveredUnflagged of all neighboring tiles
	def decrementNumAdjCoveredUnflagged(self, x:int, y:int):
		neighborCoordinates = self.getValidNeighbors(x,y)						# get all neighboring tiles to x,y
		for neighbor in neighborCoordinates:
			self.__board[neighbor[0]][neighbor[1]].numAdjCoveredUnflagged -= 1  # go through all neighboring tiles, and decrement 

	# helper function when we're flagging
	def decrementAdjEffective(self, x:int, y:int):
		neighborCoordinates = self.getValidNeighbors(x,y)							# get all neighboring tiles to x,y
		for neighbor in neighborCoordinates:
			#print("neighbor: (", neighbor[0], ",", neighbor[1], ")")
			if self.__board[neighbor[0]][neighbor[1]].label > 0:
				#print("decrementing!!")
				self.__board[neighbor[0]][neighbor[1]].effective -= 1  				# go through all neighboring tiles, and decrement 


	def getAction(self, number: int) -> "Action Object":
		# print("move count: ", self.__moveCount)
		end = time.time()
		# print("time (s): ", end-self.__start)
		if (end-self.__start <= 300) and self.__totalTiles - self.__totalMines != self.__uncoverCount:
			if number >= 0:
				# print("updating tile: ", self.__curX, ", ", self.__curY, " to ", number)
				self.updateBoard(self.__curX, self.__curY, number)

			if self.__uncoverCount == 1:
				self.decrementNumAdjCoveredUnflagged(self.__curX, self.__curY)

		
			if self.__flagCount == self.__totalMines:
				#print("flagged all mines")
				for r in range(0, self.__rows):
					for c in range(0, self.__cols):
						if self.__board[r][c].effective == -1:
				#			print("appending to uncover all: (", r, ",", c, ")")
							self.__uncoverAll.append((r, c))

			# uncover all tiles if you've flagged every bomb
			if self.__uncoverAll:
				uncoverAllTile = self.__uncoverAll.pop()
				self.__curX = uncoverAllTile[0]
				self.__curY = uncoverAllTile[1]
				self.__moveCount += 1
				self.__uncoverCount += 1
				self.decrementNumAdjCoveredUnflagged(self.__curX, self.__curY)
				#print("1UNCOVER ON: ", self.__curX, ",", self.__curY)
				return Action(AI.Action.UNCOVER, self.__curX, self.__curY)

			# #PRINT LABELS
			# print("-----\n", "BOARD\n")
			# self.printBoard()
			# print("\n-----\n")

			# # PRINT EFFECTIVE LABELS
			# print("-----\n", "EFFECTIVE BOARD\n")
			# self.printEffectiveBoard()
			# print("\n-----\n")

			# # PRINT NUM ADJACENT COVERED UNFLAGGED
			# print("-----\n", "AdjCovUnfBOARD\n")
			# self.printBoardAdjCovUnf()
			# print("\n-----\n")

			# # check if we've flagged all bombs, and if so, uncover 
			# if self.__flagCount == self.__totalMines:
			# 	for r in self.__board:
			# 		for c in r:
			# 			if self.__board[r][c] == -1:
			# 				return Action(AI.Action.UNCOVER, r, c)

			# add to zero queue if after flagging the effective label becomes 0
			if self.__hintTileCoords: # if hint tiles are not empty
				for tile in self.__hintTileCoords:
					#print("looking at hint tile: ", tile[0], ", ", tile[1])
					if self.__board[tile[0]][tile[1]].effective == 0 and self.__board[tile[0]][tile[1]].numAdjCoveredUnflagged != 0:
						neighbors = self.getValidNeighbors(tile[0], tile[1])
						
						for neighbor in neighbors:
							if self.__board[neighbor[0]][neighbor[1]].label == -1 and (neighbor[0], neighbor[1]) not in self.__zeroQueue:
								#print("appending tile to zero queue:", neighbor[0], ", ", neighbor[1])
								self.__zeroQueue.append((neighbor[0], neighbor[1]))
					
			# if whatever you just uncovered is greater than zero, add to hintTileCoords
			if number > 0 and (self.__curX, self.__curY) not in self.__hintTileCoords:
				self.__hintTileCoords.append((self.__curX, self.__curY))
			
			# ZERO-CHAINING
			# if current tile is 0, uncover all neighboring tiles
			if number == 0:
				# get valid neighbors (valid means in range of board)
				neighbors = self.getValidNeighbors(self.__curX, self.__curY)
				#print("zero queuing on tile: ", self.__curX, ", ", self.__curY)
				#print("neighbors: ", neighbors)
				for neighbor in neighbors:
					#print("1queue: \n", self.__zeroQueue, "\n")
					#print("label:",self.__board[neighbor[0]][neighbor[1]].label)
					if self.__board[neighbor[0]][neighbor[1]].effective == -1 and (neighbor[0], neighbor[1]) not in self.__zeroQueue:		# if tile on board is covered:
						self.__zeroQueue.append((neighbor[0], neighbor[1]))	# append all covered tiles to zeroQueue to be uncovered
						#print("valid neighbor: \n", self.__zeroQueue, "\n")
				
				#print("queue: ", self.__zeroQueue, "\n")

			#print("totalTiles - totalMines: ", self.__totalTiles - self.__totalMines)
			#print("uncoverCount: ", self.__uncoverCount)
			# pop off the queue		
			if self.__zeroQueue: # if zeroQueue is not empty
				#print("zeroQueue: ", self.__zeroQueue)
				self.__curX = self.__zeroQueue[0][0]
				self.__curY = self.__zeroQueue[0][1]
				self.__zeroQueue.pop(0)
				self.__moveCount += 1
				self.__uncoverCount += 1
				#print("ACTION UNCOVER ON: (", self.__curX, ", ", self.__curY,")")
				self.decrementNumAdjCoveredUnflagged(self.__curX, self.__curY)			# whenever we uncover, decrement number of Adj+Covered+Unflagged for all neighbors
			#	print("2UNCOVER ON: ", self.__curX, ",", self.__curY)
				#print("1")
				return Action(AI.Action.UNCOVER, self.__curX, self.__curY)

			# test logic through hintTiles
			#print("hintTileCoords: ", self.__hintTileCoords)
			for tile in self.__hintTileCoords:
				#print("tile: (" , tile[0], ", ", tile[1], ")")
				# print("tile effective label: ", self.__board[tile[0]][tile[1]].effective)
				# print("tile numAdjCovUnf: ", self.__board[tile[0]][tile[1]].numAdjCoveredUnflagged)
				# rule of thumb #1: if effectiveLabel == NumUnmarkedNeighbors, then all UnmarkedNeighbors must be mines
				if self.__board[tile[0]][tile[1]].effective == self.__board[tile[0]][tile[1]].numAdjCoveredUnflagged:		
					neighbors = self.getValidNeighbors(tile[0], tile[1])
					#print("neighbors: ", neighbors)
					for neighbor in neighbors:
						if self.__board[neighbor[0]][neighbor[1]].label == -1:							# if neighbor is covered&unflagged
							self.decrementNumAdjCoveredUnflagged(neighbor[0], neighbor[1])				# whenever we uncover, decrement number of Adj+Covered+Unflagged for all neighbors
							self.decrementAdjEffective(neighbor[0], neighbor[1])
							self.__flagCount += 1
							self.__moveCount += 1
							# print("flagging: (", neighbor[0], ", ", neighbor[1], ")")
							self.updateBoard(neighbor[0], neighbor[1], -2)					# update board
							
							for tile in self.__hintTileCoords:
								# check that all hintTiles are valid
								if self.__board[tile[0]][tile[1]].numAdjCoveredUnflagged == 0:
									self.__hintTileCoords.remove(tile)
							#print("2")
							return Action(AI.Action.FLAG, neighbor[0], neighbor[1])			# then uncover it
							
			# NEXT PIECE OF LOGIC -- ZERO CHAINING / RULE OF THUMB OVER
			# GO THROUGH ENTIRE BOARD, FIND ALL FRONTIER HINT TILES, GET THE PROBABILITIES OF NEIGHBORING TILES TO BE MINE
			# print("start guessing logic")
			for r in range(0, self.__rows):
				for c in range(0, self.__cols):
					if self.__board[r][c].effective > 0 and float(self.__board[r][c].numAdjCoveredUnflagged) > 0:
						self.__frontierUnc[(r, c)] = float(self.__board[r][c].effective) / float(self.__board[r][c].numAdjCoveredUnflagged)		# map the frontier hint tile to its probability {(x,y) : probability}
			# print("got all frontier tiles + probability")
			# print("self.__frontierUnc: ", self.__frontierUnc)

			# GET THE TILE WITH THE LOWEST PROBABILITY OF BEING A MINE
			min_prob = 1
			min_coord = ()
			for coord, prob in self.__frontierUnc.items():
				if prob <= min_prob:
					min_prob = prob
					min_coord = coord
			if not self.__frontierUnc:
				return Action(AI.Action.LEAVE, self.__curX, self.__curY)

			# print("min_prob: ", min_prob)
			# print("min_coord: ", min_coord)
			# CHOOSE RANDOM TILE TO UNCOVER FROM LOWEST PROBABILITY, THEN UNCOVER
			covered_neighbors_to_guess = []
			valid_neighbors_of_coord = self.getValidNeighbors(min_coord[0], min_coord[1])
			for neighbor in valid_neighbors_of_coord:
				# print("in loop")
				if self.__board[neighbor[0]][neighbor[1]].label == -1:
					covered_neighbors_to_guess.append(neighbor)
			# print("reached here")
			random.seed()
			cover = random.randrange(0, len(covered_neighbors_to_guess)-1)
			coverTile = covered_neighbors_to_guess[cover]
			# print("guessing on tile: ", coverTile[0], ", ", coverTile[1], " : ", min_prob, " : ", min_coord)
			self.__curX = coverTile[0]
			self.__curY = coverTile[1]
			self.__uncoverCount += 1
			self.__moveCount += 1
			self.__frontierUnc.clear()
			self.decrementNumAdjCoveredUnflagged(self.__curX, self.__curY)
			#print("3GUESS UNCOVER ON: ", self.__curX, ",", self.__curY)
		#	print("4")
			return Action(AI.Action.UNCOVER, self.__curX, self.__curY)
		else:
			#print("LEAVING WORLD2")
			#print("5")
			return Action(AI.Action.LEAVE, 0, 0)

		#print("LEAVING WORLD3")
		#print("6")
		return Action(AI.Action.LEAVE, 0, 0)

	

	