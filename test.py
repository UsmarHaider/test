# mdpAgents.py
# parsons/20-nov-2017
#
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py
#
# The agent here was then modified by Dariana Agape.
#
import math

from pacman import Directions
from game import Agent
import api
import random
import game
import util


class MDPAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"

        # define rewards
        self.wallReward = None
        self.foodReward = 1
        self.capsuleReward = 10
        self.blankReward = -0.04
        self.ghostReward = -800
        self.dangerZoneReward = -600
        self.edibleGhostReward = 20

        self.probabilityRightAction = 0.8
        self.probabilityWrongAction = 0.1

        self.discountFactor = 0.9

        self.width = 0
        self.height = 0

        self.map = None

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"
        print api.whereAmI(state)
        corners = api.corners(state)
        self.height = corners[1][0] + 1
        self.width = corners[2][1] + 1
        self.map = self.createMap(state)

    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"
        # define rewards
        self.wallReward = None
        self.foodReward = 1
        self.capsuleReward = 10
        self.blankReward = -0.04
        self.ghostReward = -800
        self.dangerZoneReward = -600
        self.edibleGhostReward = 20

        self.probabilityRightAction = 0.8
        self.probabilityWrongAction = 0.1

        self.discountFactor = 0.9

        self.width = 0
        self.height = 0

        self.map = None

    # Creates and returns an initial map containing only the walls
    def createMap(self, state):
        map = []
        for i in range(self.height):
            map.append([])
            for j in range(self.width):
                map[i].append("  ")

        walls = api.walls(state)
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) in walls:
                    map[i][j] = self.wallReward
                else:
                    map[i][j] = self.blankReward

        return map

    # Creates and returns the reward map of the world
    # reward map acts as the reward function used in Bellmann update
    def createRewardMap(self, state):
        # creates empty reward map - only has walls
        rewardMap = self.createMap(state)
        food = api.food(state)
        capsules = api.capsules(state)
        walls = api.walls(state)
        ghosts = api.ghosts(state)

        # populate map with reward values for food, capsules, ghosts and empty spaces
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) in food:
                    rewardMap[i][j] = self.foodReward
                elif (i, j) in capsules:
                    rewardMap[i][j] = self.capsuleReward
                elif (i, j) in ghosts:
                    rewardMap[i][j] = self.ghostReward
                elif (i, j) in walls:
                    rewardMap[i][j] = self.wallReward
                else:
                    rewardMap[i][j] = self.blankReward

        return rewardMap

    # Updates the map with values for ghosts and dangerous zones
    def updateRewardMap(self, ghosts, map, state):
        # Dictionary having ghost location as key, and value as timer until the ghost's edible state ends
        edibleGhostDictionary = dict(api.ghostStatesWithTimes(state))

        for ghost in ghosts:
            # compute the danger zone for every ghost
            dangerArea = self.getGhostArea(ghost, map)

            # check if ghost is edible for long enough to make a move
            if edibleGhostDictionary[ghost] >= 4:
                # check if agent is near the edible ghost
                if self.getDistanceToGhost(ghost, api.whereAmI(state)) < 5:
                    map[int(ghost[0])][int(ghost[1])] = self.edibleGhostReward
            # else edible state is almost finished and ghost becomes terrifying again
            else:
                # update danger locations in utility map according to position of ghosts
                for pos in dangerArea:
                    if pos == ghost:
                        map[int(pos[0])][int(pos[1])] = self.ghostReward
                    else:
                        map[int(pos[0])][int(pos[1])] = self.dangerZoneReward

    # Computes distance between the two ghosts using Euclidean distance
    def getDistanceBetweenGhosts(self, state):
        ghosts = api.ghosts(state)
        ghost1 = ghosts[0]
        ghost2 = ghosts[1]
        return math.sqrt(math.pow(ghost1[0] - ghost2[0], 2) + math.pow(ghost1[1] - ghost2[1], 2))

    # Computes distance between agent and given ghost using Euclidean distance
    def getDistanceToGhost(self, ghost, pacman):
        return math.sqrt(math.pow(pacman[0] - ghost[0], 2) + math.pow(pacman[1] - ghost[1], 2))

    # Determine dangerous area for a ghost
    # It is defined as a 2 rows x 3 columns matrix with the next possible cells for a given direction
    def getGhostArea(self, ghost, rewardMap):
        dangerCoordinates = set()
        dangerCoordinates.add((int(ghost[0]), int(ghost[1])))

        # define danger area - ghost can move up, down, east, west
        # if a ghost can go up, the up, up-right and up-left become dangerous locations
        # if the ghost can go up once more, the next up, next up-right and next up-left become dangerous locations

        # if ghost can go up (there is no wall)
        if rewardMap[int(ghost[0])][int(ghost[1]) + 1] != self.wallReward:
            dangerCoordinates.add((int(ghost[0]), int(ghost[1]) + 1))
            # add right and left up cells to danger locations if there are no walls
            try:
                if rewardMap[int(ghost[0]) + 1][int(ghost[1]) + 1] != self.wallReward:
                    dangerCoordinates.add(([int(ghost[0]) + 1][int(ghost[1]) + 1]))
            except:
                pass
            try:
                if rewardMap[int(ghost[0]) - 1][int(ghost[1]) + 1] != self.wallReward:
                    dangerCoordinates.add(([int(ghost[0]) - 1][int(ghost[1]) + 1]))
            except:
                pass

            try:
                # if possible add next up location of the ghost to the danger locations
                if rewardMap[int(ghost[0])][int(ghost[1]) + 2] != self.wallReward:
                    dangerCoordinates.add(([int(ghost[0])][int(ghost[1]) + 2]))
            except:
                pass
            # add next right and left up locations to danger locations if there is no wall
            try:
                if rewardMap[int(ghost[0]) + 1][int(ghost[1]) + 2] != self.wallReward:
                    dangerCoordinates.add(([int(ghost[0]) + 1][int(ghost[1]) + 2]))
            except:
                pass
            try:
                if rewardMap[int(ghost[0]) - 1][int(ghost[1]) + 2] != self.wallReward:
                    dangerCoordinates.add(([int(ghost[0]) - 1][int(ghost[1]) + 2]))
            except:
                pass

        # if ghost can go down
        if rewardMap[int(ghost[0])][int(ghost[1]) - 1] != self.wallReward:
            dangerCoordinates.add((int(ghost[0]), int(ghost[1]) - 1))
            # add right and left down cells to danger locations if there are no walls
            try:
                if rewardMap[int(ghost[0]) + 1][int(ghost[1]) - 1] != self.wallReward:
                    dangerCoordinates.add(([int(ghost[0]) + 1][int(ghost[1]) - 1]))
            except:
                pass
            try:
                if rewardMap[int(ghost[0]) - 1][int(ghost[1]) - 1] != self.wallReward:
                    dangerCoordinates.add(([int(ghost[0]) - 1][int(ghost[1]) - 1]))
            except:
                pass

            try:
                # if possible add next up location of the ghost to the danger locations
                if rewardMap[int(ghost[0])][int(ghost[1]) - 2] != self.wallReward:
                    dangerCoordinates.add(([int(ghost[0])][int(ghost[1]) - 2]))
            except:
                pass
            # add next right and left up locations to danger locations if there are no walls
            try:
                if rewardMap[int(ghost[0]) + 1][int(ghost[1]) - 2] != self.wallReward:
                    dangerCoordinates.add(([int(ghost[0]) + 1][int(ghost[1]) - 2]))
            except:
                pass
            try:
                if rewardMap[int(ghost[0]) - 1][int(ghost[1]) - 2] != self.wallReward:
                    dangerCoordinates.add(([int(ghost[0]) - 1][int(ghost[1]) - 2]))
            except:
                pass

        # if ghost can go right
        if rewardMap[int(ghost[0]) + 1][int(ghost[1])] != self.wallReward:
            dangerCoordinates.add((int(ghost[0] + 1), int(ghost[1])))
            # add up and down right cells to danger locations if there are no walls
            try:
                if rewardMap[int(ghost[0]) + 1][int(ghost[1]) + 1] != self.wallReward:
                    dangerCoordinates.add(([int(ghost[0]) + 1][int(ghost[1]) + 1]))
            except:
                pass
            try:
                if rewardMap[int(ghost[0]) + 1][int(ghost[1]) - 1] != self.wallReward:
                    dangerCoordinates.add(([int(ghost[0]) + 1][int(ghost[1]) - 1]))
            except:
                pass

            try:
                # if possible add next right location of the ghost to the danger locations
                if rewardMap[int(ghost[0]) + 2][int(ghost[1])] != self.wallReward:
                    dangerCoordinates.add(([int(ghost[0]) + 2][int(ghost[1])]))
            except:
                pass
            # add next up and down right locations to danger locations if there are no walls
            try:
                if rewardMap[int(ghost[0]) + 2][int(ghost[1]) + 1] != self.wallReward:
                    dangerCoordinates.add(([int(ghost[0]) + 2][int(ghost[1]) + 1]))
            except:
                pass
            try:
                if rewardMap[int(ghost[0]) + 2][int(ghost[1]) - 1] != self.wallReward:
                    dangerCoordinates.add(([int(ghost[0]) + 2][int(ghost[1]) - 1]))
            except:
                pass

        # if ghost can go left
        if rewardMap[int(ghost[0]) - 1][int(ghost[1])] != self.wallReward:
            dangerCoordinates.add((int(ghost[0] - 1), int(ghost[1])))
            # add up and down left cells to danger locations if there are no walls
            try:
                if rewardMap[int(ghost[0]) - 1][int(ghost[1]) + 1] != self.wallReward:
                    dangerCoordinates.add(([int(ghost[0]) - 1][int(ghost[1]) + 1]))
            except:
                pass
            try:
                if rewardMap[int(ghost[0]) - 1][int(ghost[1]) - 1] != self.wallReward:
                    dangerCoordinates.add(([int(ghost[0]) - 1][int(ghost[1]) - 1]))
            except:
                pass

            try:
                # if possible add next left location of the ghost to the danger locations
                if rewardMap[int(ghost[0]) - 2][int(ghost[1])] != self.wallReward:
                    dangerCoordinates.add(([int(ghost[0]) - 2][int(ghost[1])]))
            except:
                pass
            # add next up and down left locations to danger locations if there are no walls
            try:
                if rewardMap[int(ghost[0]) - 2][int(ghost[1]) + 1] != self.wallReward:
                    dangerCoordinates.add(([int(ghost[0]) - 2][int(ghost[1]) + 1]))
            except:
                pass
            try:
                if rewardMap[int(ghost[0]) - 2][int(ghost[1]) - 1] != self.wallReward:
                    dangerCoordinates.add(([int(ghost[0]) - 2][int(ghost[1]) - 1]))
            except:
                pass

        return dangerCoordinates

    # Computes and returns the updated value of a cell using the Bellman equation.
    def bellmann(self, utilityMap, cell, cellRewardValue):
        x = cell[0]
        y = cell[1]

        if cellRewardValue == self.wallReward:
            return self.wallReward

        east = west = north = south = None
        currentReward = utilityMap[x][y]

        # checks if agent can go to the adjacent cells and retrieve their utility
        if x < self.width - 1:
            east = utilityMap[x + 1][y]
        if x > 0:
            west = utilityMap[x - 1][y]
        if y < self.height - 1:
            north = utilityMap[x][y + 1]
        if y > 0:
            south = utilityMap[x][y - 1]

        # if adjacent cell is wall, discard chances of going in that direction
        if east is None:
            east = -1
        if west is None:
            west = -1
        if north is None:
            north = -1
        if south is None:
            south = -1

        # compute probabilities of going in each direction
        if north is not None:  # no wall
            north_val = north * 0.8 + (east + west) * 0.1
        else:
            north_val = currentReward * 0.8 + (east + west) * 0.1

        if south is not None:
            south_val = south * 0.8 + (east + west) * 0.1
        else:
            south_val = currentReward * 0.8 + (east + west) * 0.1

        if east is not None:
            east_val = east * 0.8 + (north + south) * 0.1
        else:
            east_val = currentReward * 0.8 + (north + south) * 0.1

        if west is not None:
            west_val = west * 0.8 + (north + south) * 0.1
        else:
            west_val = currentReward * 0.8 + (north + south)

        # take max utility for a direction and compute the new utility value
        max_val = max([north_val, south_val, east_val, west_val])
        return float(float(cellRewardValue) + float(self.discountFactor) * float(max_val))

    # Apply value iteration algorithm on the given map
    # Returns the expected utility map
    def valueIteration(self, utilityMap, state):
        ghosts = api.ghosts(state)
        epsilon = 0.001

        # reward map - acting as the reward function having the reward value for each cell
        rewardMap = self.createRewardMap(state)
        self.updateRewardMap(ghosts, rewardMap, state)

        while True:
            Ucopy = self.createMap(state)  # only has walls
            delta = 0

            # for evry state, computes utility value for that cell using bellman equation
            for i in range(self.height):
                for j in range(self.width):
                    r = rewardMap[i][j]
                    Ucopy[i][j] = self.bellmann(utilityMap, (i, j), r)
                    try:
                        delta = max(delta, abs(Ucopy[i][j] - utilityMap[i][j]))
                    except:
                        pass
            utilityMap = Ucopy

            # checks for convergence
            # stops once the value function changes by only a small amount
            if delta < epsilon * (1 - self.discountFactor) / self.discountFactor:
                return utilityMap

    # Maps the value of a cell to an action (direction of action)
    def getActionUtility(self, legal, pacman_map, x, y):
        # dictionary having action as key and utility of the action as value
        toReturn = dict()
        for action in legal:
            value = None
            if action is Directions.NORTH:
                value = pacman_map[x][y + 1]
            elif action is Directions.SOUTH:
                value = pacman_map[x][y - 1]
            elif action is Directions.EAST:
                value = pacman_map[x + 1][y]
            elif action is Directions.WEST:
                value = pacman_map[x - 1][y]
            if value is not None:
                toReturn[action] = value

        return toReturn

    def getAction(self, state):
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        # get agent current location
        pacman = api.whereAmI(state)

        # value iteration algorithm on the initial empty map
        self.map = self.valueIteration(self.map, state)

        # computes max utility and make the corresponding action
        actionUtilityDictionary = self.getActionUtility(legal, self.map, pacman[0], pacman[1])
        all_values = actionUtilityDictionary.values()
        max_value = max(all_values)
        action = actionUtilityDictionary.keys()[actionUtilityDictionary.values().index(max_value)]

        return api.makeMove(action, legal)
