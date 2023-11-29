# coding=utf-8
# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
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

from pacman import Directions
from game import Agent
import api
import random
import game
import util



# MDP Solver
class MDPAgent(Agent):
    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        self.gamma = 0.5  # Discount factor: reduces the utility values with each time step
        self.reward = -0.5  # Incentive for Pac-Man to keep moving

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        self.buildmap(state)
        self.Freespace()
        self.legalMoves()
        self.ghoststate = api.ghostStates(state)
        self.ghosttime = api.ghostStatesWithTimes(state)
        self.ghoststatus = self.ghostStatus()
        self.Utility(state)

        self.table_utility()
        self.policyInit()

    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"

    #
    # Data structures methods
    #

    # Map
    def buildmap(self, state):
        # Number of Rows
        wall = api.walls(state)
        w = wall[-1][0] + 1
        self.row = w
        # Number of Columns
        h = wall[-1][1] + 1
        self.column = h
        self.map = []
        while len(self.map) != self.row:
            self.map.append([0] * self.column)
        # Pacman location
        pac = api.whereAmI(state)
        self.map[pac[0]][pac[1]] = 'P'
        # Walls
        for x, y in wall:
            self.map[x][y] = '%'
        # Foods
        food = api.food(state)
        for x, y in food:
            self.map[x][y] = '*'
        # Capsules
        capsule = api.capsules(state)
        if capsule:
            for x, y in capsule:
                self.map[x][y] = 'C'
        # Ghosts
        ghost = api.ghosts(state)
        if ghost:
            for x, y in ghost:
                self.map[int(x)][int(y)] = 'G'

    # Utility array
    def Utility(self, state):
        self.utility = []
        foods = api.food(state)
        cap = api.capsules(state)
        ghosts = api.ghosts(state)
        f = self.freespace
        while len(self.utility) != self.row:
            self.utility.append([0] * self.column)
        for x, y in foods:
            self.utility[x][y] = 0.1
        for x, y in cap:
            self.utility[x][y] = 10
        # Hunting Mode change ghosts utility by checking EDIBLE status
        # mediumClassic
        if self.row > 8:
            status = self.ghoststatus
            # Keep yourself alive!
            if not status[1]:
                for x, y in ghosts:
                    x = int(x)
                    y = int(y)
                    self.utility[int(x)][int(y)] = -30
                    # Ghosts dangerous perimeters
                    # North
                    if (x, y + 1) in f:
                        self.utility[int(x)][int(y + 1)] = -30
                    if (x, y + 2) in f:
                        self.utility[int(x)][int(y + 2)] = -30
                    # NorthEast
                    if (x + 1, y + 1) in f:
                        self.utility[int(x + 1)][int(y + 1)] = -30
                    if (x + 1, y + 2) in f:
                        self.utility[int(x + 1)][int(y + 2)] = -30
                    if (x + 2, y + 1) in f:
                        self.utility[int(x + 2)][int(y + 1)] = -30
                    # East
                    if (x + 1, y) in f:
                        self.utility[int(x + 1)][int(y)] = -30
                    if (x + 2, y) in f:
                        self.utility[int(x + 2)][int(y)] = -30
                    # SouthEast
                    if (x + 1, y - 1) in f:
                        self.utility[int(x + 1)][int(y - 1)] = -30
                    if (x + 1, y - 2) in f:
                        self.utility[int(x + 1)][int(y - 2)] = -30
                    if (x + 2, y - 1) in f:
                        self.utility[int(x + 2)][int(y - 1)] = -30
                    # South
                    if (x, y - 1) in f:
                        self.utility[int(x)][int(y - 1)] = -30
                    if (x, y - 2) in f:
                        self.utility[int(x)][int(y - 2)] = -30
                    # SouthWest
                    if (x - 1, y - 1) in f:
                        self.utility[int(x - 1)][int(y - 1)] = -30
                    if (x - 1, y - 2) in f:
                        self.utility[int(x - 1)][int(y - 2)] = -30
                    if (x - 2, y - 1) in f:
                        self.utility[int(x - 2)][int(y - 1)] = -30
                    # West
                    if (x - 1, y) in f:
                        self.utility[int(x - 1)][int(y)] = -30
                    if (x - 2, y) in f:
                        self.utility[int(x - 2)][int(y)] = -30
                    # NorthWest
                    if (x - 1, y + 1) in f:
                        self.utility[int(x - 1)][int(y + 1)] = -30
                    if (x - 1, y + 2) in f:
                        self.utility[int(x - 1)][int(y + 2)] = -30
                    if (x - 2, y + 1) in f:
                        self.utility[int(x - 2)][int(y + 1)] = -30
            # Ghosts are scared!
            else:
                if self.ghosttime[0][1] > 3:
                    # Edible ghosts
                    for x, y in foods:
                        self.utility[x][y] = 0
                    for x, y in cap:
                        self.utility[x][y] = 0
                    for x, y in status[1]:
                        self.utility[int(x)][int(y)] = 30
                    # Dangerous ghosts
                    for x, y in status[0]:
                        self.utility[int(x)][int(y)] = -30
                        # Ghosts dangerous perimeters
                        # North
                        if (x, y + 1) in f:
                            self.utility[int(x)][int(y + 1)] = -30
                        if (x, y + 2) in f:
                            self.utility[int(x)][int(y + 2)] = -30
                        # NorthEast
                        if (x + 1, y + 1) in f:
                            self.utility[int(x + 1)][int(y + 1)] = -30
                        if (x + 1, y + 2) in f:
                            self.utility[int(x + 1)][int(y + 2)] = -30
                        if (x + 2, y + 1) in f:
                            self.utility[int(x + 2)][int(y + 1)] = -30
                        # East
                        if (x + 1, y) in f:
                            self.utility[int(x + 1)][int(y)] = -30
                        if (x + 2, y) in f:
                            self.utility[int(x + 2)][int(y)] = -30
                        # SouthEast
                        if (x + 1, y - 1) in f:
                            self.utility[int(x + 1)][int(y - 1)] = -30
                        if (x + 1, y - 2) in f:
                            self.utility[int(x + 1)][int(y - 2)] = -30
                        if (x + 2, y - 1) in f:
                            self.utility[int(x + 2)][int(y - 1)] = -30
                        # South
                        if (x, y - 1) in f:
                            self.utility[int(x)][int(y - 1)] = -30
                        if (x, y - 2) in f:
                            self.utility[int(x)][int(y - 2)] = -30
                        # SouthWest
                        if (x - 1, y - 1) in f:
                            self.utility[int(x - 1)][int(y - 1)] = -30
                        if (x - 1, y - 2) in f:
                            self.utility[int(x - 1)][int(y - 2)] = -30
                        if (x - 2, y - 1) in f:
                            self.utility[int(x - 2)][int(y - 1)] = -30
                        # West
                        if (x - 1, y) in f:
                            self.utility[int(x - 1)][int(y)] = -30
                        if (x - 2, y) in f:
                            self.utility[int(x - 2)][int(y)] = -30
                        # NorthWest
                        if (x - 1, y + 1) in f:
                            self.utility[int(x - 1)][int(y + 1)] = -30
                        if (x - 1, y + 2) in f:
                            self.utility[int(x - 1)][int(y + 2)] = -30
                        if (x - 2, y + 1) in f:
                            self.utility[int(x - 2)][int(y + 1)] = -30
        # smallGrid
        else:
            for x, y in ghosts:
                self.utility[int(x)][int(y)] = -30
                # Ghosts dangerous perimeters
                # North
                if (int(x), int(y + 1)) in f:
                    self.utility[int(x)][int(y + 1)] = -30
                # East
                if (int(x + 1), int(y)) in f:
                    self.utility[int(x + 1)][int(y)] = -30
                # South
                if (int(x), int(y - 1)) in f:
                    self.utility[int(x)][int(y - 1)] = -30
                # SouthWest
                if (int(x - 1), int(y - 1)) in f:
                    self.utility[int(x - 1)][int(y - 1)] = -30
                if (x - 1, y - 2) in f:
                    self.utility[int(x - 1)][int(y - 2)] = -30
                # West
                if (int(x - 1), int(y)) in f:
                    self.utility[int(x - 1)][int(y)] = -30

    # Free space
    def Freespace(self):
        self.freespace = []
        for x in range(self.row):
            for y in range(self.column):
                if self.map[x][y] != '%':
                    self.freespace.append((x, y))

    # Legal moves at each state
    def legalMoves(self):
        self.availMoves = {}
        m = self.map
        for x, y in self.freespace:
            self.availMoves[(x, y)] = []
            # NORTH
            if m[x][y + 1] != '%':  # and m[x][y + 1] != 'G'
                self.availMoves[(x, y)].append('North')
            # EAST
            if m[x + 1][y] != '%':  # and m[x + 1][y] != 'G'
                self.availMoves[(x, y)].append('East')
            # SOUTH
            if m[x][y - 1] != '%':  # and m[x][y - 1] != 'G'
                self.availMoves[(x, y)].append('South')
            # WEST
            if m[x - 1][y] != '%':  # and m[x - 1][y] != 'G':
                self.availMoves[(x, y)].append('West')

    # Table of Utility: legal moves utility & illegal moves 'still'
    def table_utility(self):
        # TABLE of UTILITY:
        self.tableUtility = {}
        # Create a table that retrieve the utility value of next move with the format
        # tu[location][action] -> utility value
        #
        # Adding elements to the Nested Dictionary
        # From https://www.programiz.com/python-programming/nested-dictionary
        #
        for x, y in self.freespace:
            self.tableUtility[(x, y)] = {}
            # NORTH
            if self.map[x][y + 1] != '%':
                self.tableUtility[(x, y)]['North'] = self.utility[x][y + 1]
            else:
                self.tableUtility[(x, y)]['North'] = self.utility[x][y]
            # EAST
            if self.map[x + 1][y] != '%':
                self.tableUtility[(x, y)]['East'] = self.utility[x + 1][y]
            else:
                self.tableUtility[(x, y)]['East'] = self.utility[x][y]
            # SOUTH
            if self.map[x][y - 1] != '%':
                self.tableUtility[(x, y)]['South'] = self.utility[x][y - 1]
            else:
                self.tableUtility[(x, y)]['South'] = self.utility[x][y]
            # WEST
            if self.map[x - 1][y] != '%':
                self.tableUtility[(x, y)]['West'] = self.utility[x - 1][y]
            else:
                self.tableUtility[(x, y)]['West'] = self.utility[x][y]

    # Global policy
    def policyInit(self):
        p = {}
        for x, y in self.freespace:
            p[(x, y)] = 'East'
        self.policy = p

    # Ghost Status
    def ghostStatus(self):
        status = {0: [], 1: []}
        for gh, st in self.ghoststate:
            status[st].append(gh)
        return status

    #
    # Data Update methods
    #
    def updateUtilityTable(self, nu):
        for x, y in self.freespace:
            if 'North' in self.availMoves[(x, y)]:
                self.tableUtility[(x, y)]['North'] = nu[x][y + 1]
            else:
                self.tableUtility[(x, y)]['North'] = nu[x][y]
            if 'East' in self.availMoves[(x, y)]:
                self.tableUtility[(x, y)]['East'] = nu[x + 1][y]
            else:
                self.tableUtility[(x, y)]['East'] = nu[x][y]
            if 'South' in self.availMoves[(x, y)]:
                self.tableUtility[(x, y)]['South'] = nu[x][y - 1]
            else:
                self.tableUtility[(x, y)]['South'] = nu[x][y]
            if 'West' in self.availMoves[(x, y)]:
                self.tableUtility[(x, y)]['West'] = nu[x - 1][y]
            else:
                self.tableUtility[(x, y)]['West'] = nu[x][y]

    #
    # Print methods
    #
    # Print map
    def printmap(self):
        print 'Current Environment: '
        for i in range(self.row):
            for j in range(self.column):
                print self.map[i][j],
            print '\n'

    # Print Utility
    def printutility(self):
        print "Utility: "
        for i in range(self.row):
            for j in range(self.column):
                print repr(round(self.utility[i][j], 3)).rjust(7),
            print '\n'

    # Print out free grids
    def printfreespace(self):
        print 'Freespace: ',
        print self.freespace

    #
    # Value Iteration methods
    #
    # Bellman function
    def bellman(self, ns):  # ns -> N States: tuple(x, y)
        tu = self.tableUtility
        u = {}
        # Loop over legal actions
        for action in self.availMoves[ns]:
            u[action] = 0.8 * tu[ns][action]
            if action == 'North' or action == 'South':
                u[action] += 0.1 * (tu[ns]['East'] + tu[ns]['West'])
            if action == 'East' or action == 'West':
                u[action] += 0.1 * (tu[ns]['North'] + tu[ns]['South'])
            u[action] = self.reward + self.gamma * u[action]
        v = list(u.values())
        k = list(u.keys())
        return max(v), k[v.index(max(v))]

    # Value iteration algorithm: return current optimal policy
    def valueIteration(self, state):
        u = self.utility
        p = self.policy
        foods = api.food(state)
        ghosts = api.ghosts(state)
        g = api.ghosts(state)
        cap = api.capsules(state)
        f = self.freespace
        # Ghosts dangerous perimeters
        # mediumClassic
        if self.row > 8:
            # Keep yourself alive!
            for x, y in g:
                x = int(x)
                y = int(y)
                # North
                if (x, y + 1) in f:
                    ghosts.append((x, y + 1))
                # East
                if (x + 1, y) in f:
                    ghosts.append((x + 1, y))
                # South
                if (x, y - 1) in f:
                    ghosts.append((x, y - 1))
                # West
                if (x - 1, y) in f:
                    ghosts.append((x - 1, y))
        # smallGrid
        else:
            for x, y in g:
                x = int(x)
                y = int(y)
                # North
                if (x, y + 1) in f:
                    ghosts.append((x, y + 1))
                # East
                if (x + 1, y) in f:
                    ghosts.append((x + 1, y))
                # South
                if (x, y - 1) in f:
                    ghosts.append((x, y - 1))
                # SouthWest
                if (x - 1, y - 1) in f:
                    ghosts.append((x - 1, y - 1))
                if (x - 1, y - 2) in f:
                    ghosts.append((x, y - 2))
                # West
                if (x - 1, y) in f:
                    ghosts.append((x - 1, y))
        c = 0
        # Algorithm body
        # Iterating until the maximum difference between iteration < delta(threshold)
        while True:
            # Iteration starts
            c += 1
            # Go through all states except foods, capsules & ghosts positions
            for s in f:
                if (s in foods) or (s in list(set(ghosts))) or (s in cap):
                    continue
                x = s[0]
                y = s[1]
                u[x][y], p[s] = self.bellman(s)
            self.updateUtilityTable(u)  # U_i+1 <- U_i
            self.utility = u
            self.policy = p
            if c > 20:
                break
        pacman = api.whereAmI(state)
        Legal = self.availMoves[pacman]
        x = pacman[0]
        y = pacman[1]
        #
        # Maximum Expected Utility
        #
        # mediumClassic
        if self.row > 8:
            radar = {}
            for direct in Legal:
                if direct == 'North':
                    radar['North'] = []
                    if (x, y + 1) in f:
                        radar['North'].append(u[x][y + 1])
                    if (x, y + 2) in f:
                        radar['North'].append(u[x][y + 2])
                    if (x, y + 3) in f:
                        radar['North'].append(u[x][y + 3])
                    # Corner Issue
                    if len(radar['North']) <= 1:
                        p = x
                        q = y + 1
                        safe = self.availMoves[(p, q)]
                        for sf in safe:
                            if sf == 'East':
                                if (p + 1, q) in f:
                                    radar['North'].append(u[p + 1][q])
                                if (p + 2, q) in f:
                                    radar['North'].append(u[p + 2][q])
                            if sf == 'West':
                                if (p - 1, q) in f:
                                    radar['North'].append(u[p - 1][q])
                                if (p - 2, q) in f:
                                    radar['North'].append(u[p - 2][q])
                        radar['North'] = float(sum(radar['North'])) / len(radar['North'])
                    else:
                        radar['North'] = float(sum(radar['North'])) / len(radar['North'])
                if direct == 'East':
                    radar['East'] = []
                    if (x + 1, y) in f:
                        radar['East'].append(u[x + 1][y])
                    if (x + 2, y) in f:
                        radar['East'].append(u[x + 2][y])
                    if (x + 3, y) in f:
                        radar['East'].append(u[x + 3][y])
                    # Corner Issue
                    if len(radar['East']) <= 1:
                        p = x + 1
                        q = y
                        safe = self.availMoves[(p, q)]
                        for sf in safe:
                            if sf == 'North':
                                if (p, q + 1) in f:
                                    radar['East'].append(u[p][q + 1])
                                if (p, q + 2) in f:
                                    radar['East'].append(u[p][q + 2])
                            if sf == 'South':
                                if (p, q - 1) in f:
                                    radar['East'].append(u[p][q - 1])
                                if (p, q - 2) in f:
                                    radar['East'].append(u[p][q - 2])
                        radar['East'] = float(sum(radar['East'])) / len(radar['East'])
                    else:
                        radar['East'] = float(sum(radar['East'])) / len(radar['East'])
                if direct == 'South':
                    radar['South'] = []
                    if (x, y - 1) in f:
                        radar['South'].append(u[x][y - 1])
                    if (x, y - 2) in f:
                        radar['South'].append(u[x][y - 2])
                    if (x, y - 3) in f:
                        radar['South'].append(u[x][y - 3])
                    # Corner Issue
                    if len(radar['South']) <= 1:
                        p = x
                        q = y - 1
                        safe = self.availMoves[(p, q)]
                        for sf in safe:
                            if sf == 'East':
                                if (p + 1, q) in f:
                                    radar['South'].append(u[p + 1][q])
                                if (p + 2, q) in f:
                                    radar['South'].append(u[p + 2][q])
                            if sf == 'West':
                                if (p - 1, q) in f:
                                    radar['South'].append(u[p - 1][q])
                                if (p - 2, q) in f:
                                    radar['South'].append(u[p - 2][q])
                        radar['South'] = float(sum(radar['South'])) / len(radar['South'])
                    else:
                        radar['South'] = float(sum(radar['South'])) / len(radar['South'])
                if direct == 'West':
                    radar['West'] = []
                    if (x - 1, y) in f:
                        radar['West'].append(u[x - 1][y])
                    if (x - 2, y) in f:
                        radar['West'].append(u[x - 2][y])
                    if (x - 3, y) in f:
                        radar['West'].append(u[x - 3][y])
                    # Corner Issue
                    if len(radar['West']) <= 1:
                        p = x - 1
                        q = y
                        safe = self.availMoves[(p, q)]
                        for sf in safe:
                            if sf == 'North':
                                if (p, q + 1) in f:
                                    radar['West'].append(u[p][q + 1])
                                if (p, q + 2) in f:
                                    radar['West'].append(u[p][q + 2])
                            if sf == 'South':
                                if (p, q - 1) in f:
                                    radar['West'].append(u[p][q - 1])
                                if (p, q - 2) in f:
                                    radar['West'].append(u[p][q - 2])
                        radar['West'] = float(sum(radar['West'])) / len(radar['West'])
                    else:
                        radar['West'] = float(sum(radar['West'])) / len(radar['West'])
            vr = list(radar.values())
            vk = list(radar.keys())
            return vk[vr.index(max(vr))]
        # smallGrid
        else:
            radar = {}
            for direct in Legal:
                if direct == 'North':
                    radar['North'] = []
                    if (x, y + 1) in f:
                        radar['North'].append(u[x][y + 1])
                    if (x, y + 2) in f:
                        radar['North'].append(u[x][y + 2])
                    radar['North'] = float(sum(radar['North'])) / len(radar['North'])
                if direct == 'East':
                    radar['East'] = []
                    if (x + 1, y) in f:
                        radar['East'].append(u[x + 1][y])
                    if (x + 2, y) in f:
                        radar['East'].append(u[x + 2][y])
                    radar['East'] = float(sum(radar['East'])) / len(radar['East'])
                if direct == 'South':
                    radar['South'] = []
                    if (x, y - 1) in f:
                        radar['South'].append(u[x][y - 1])
                    if (x, y - 2) in f:
                        radar['South'].append(u[x][y - 2])
                    radar['South'] = float(sum(radar['South'])) / len(radar['South'])
                if direct == 'West':
                    radar['West'] = []
                    if (x - 1, y) in f:
                        radar['West'].append(u[x - 1][y])
                    if (x - 2, y) in f:
                        radar['West'].append(u[x - 2][y])
                    radar['West'] = float(sum(radar['West'])) / len(radar['West'])
            vr = list(radar.values())
            vk = list(radar.keys())
            return vk[vr.index(max(vr))]

    #
    # Main function
    #
    def getAction(self, state):
        # Update Map & utility values after each runtime according to realtime environment
        self.registerInitialState(state)
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        action = self.valueIteration(state)
        return api.makeMove(action, legal)