# mapAgents.py
# parsons/11-nov-2017
#
# Version 1.0
#
# A simple map-building to work with the PacMan AI projects from:
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

# The agent here is an extension of the above code written by Simon
# Parsons, based on the code in pacmanAgents.py

from pacman import Directions
from game import Agent
import api


class MDPAgent(Agent):

    def __init__(self):
        """The init method initialise the variable """
        self.ghostHub = []  # list of 8-tile ghost starting area on medium grid
        self.tenticles = - 10  # Sets Negative reward for Ghost Radius
        self.NSEW_Direct = ["North", "South", "East", "West"]  # All Directions/ Movements are based on this Index
        self.RottenFoodLength = 3  # Determine Range of Rotten Food Function
        self.grid = []  # Defines Dimensions of the Grid
        self.UDic = {}  # Resets iteration Dictionary
        self.blank_dictionary ={}
        self.hub = - 1  # Assigns Negative Reward to 8-tile ghost starting area on medium grid
        self.blank_list = []  # Initialises List that contains all blank (i.e non-fixed reward) states
        self.eaten_list = []  # List of all the consumed consumables
        self.tentacles_list = []  # Creates a list of the tentacle/ negative rewards radius
        print "The electric things have their life too. Paltry as those lives are"

    def final(self, state):
        """ The final method is used to resets all the list prior to every iteration of the program"""
        self.ghostHub = []  # list of 8-tile ghost starting area on medium grid
        self.tenticles = - 10  # Sets Negative reward for Ghost Radius
        self.NSEW_Direct = ["North", "South", "East", "West"]  # All Directions/ Movements are based on this Index
        self.RottenFoodLength = 3  # Determine Range of Rotten Food Function
        self.grid = []  # Defines Dimensions of the Grid
        self.UDic = {}  # Resets iteration Dictionary
        self.blank_dictionary ={}
        self.hub = -1  # Assigns Negative Reward to 8-tile ghost starting area on medium grid
        self.blank_list = []  # Initialises List that contains all blank (i.e non-fixed reward) states on the grid
        self.eaten_list = []  # List of all the consumed consumables
        self.tentacles_list = []  # Creates a list of the tentacle/ negative rewards radius
        print "Gerty, am I a clone?"

    def gridBuilder(self, state):
        """Generates a list of all the spaces on the grid; using the Height and Width"""
        for x in range(self.getLayoutWidth(api.corners(state)) - 1):
            for y in range(self.getLayoutHeight(api.corners(state)) - 1):
                if (x, y) not in self.wallcoord and (x, y) not in self.grid:
                    self.grid.append((x, y))
        return self.grid

    # Artificial Intelligence; Reasoning and Decision Making ; Tutorial 5; MapAgent
    def getLayoutHeight(self, corners):
        height = - 1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1

    # Artificial Intelligence; Reasoning and Decision Making ; Tutorial 5; MapAgent
    def getLayoutWidth(self, corners):
        width = - 1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1

    def rewardDictionary(self, state):
        """The Reward Method creates a rewards dictionary which assigns a reward to some key features on the grid (i.e.
        Food, Capsules, Ghosts, Ghost Hub and Backspaces) on the grid. The functionality of the Method varies
        for each grid. The reward for the ghost are assigned via a separate set of methods"""
        # Initialises a rewards dictionary
        RewardDic = {}  # Will contain Rewards/Values for Consumables, Ghosts, Rotten Food and Blank Spaces
        self.Fixed_Reward_Dic = {}  # Negative Rewards Dictionary; Contains Rewards for Ghost Radius and Ghost Hub
        # # Creates individual dictionaries for consumables using APIs; assigns respective rewards
        food_dictionary = {i: 1 for i in self.foodcoord}
        capsule_dictionary = {i: 2 for i in self.capsulecoord}
        # Adds consumables to Rewards Dictionary
        RewardDic.update(food_dictionary)
        RewardDic.update(capsule_dictionary)
        # Checks Grid Size via number of tiles on grid; Less Than 20 = Small; Greater Than 20 = Medium Classic
        if len(self.grid) < 20:
            # Iterates over all tiles on grid
            for i in self.grid:
                # Check for all non-key feature tiles; i.e tiles with No Consumables, Walls, and/or Ghosts.
                if i not in self.foodcoord and i not in self.wallcoord and i not in self.blank_list and i not in \
                        self.ghostcoord:
                    # Adds Blank Spaces to a list of all the space with no key feature; Blank Space List
                    self.blank_list.append(i)
            # # Creates a dictionaries of Blank Spaces; assigns a reward of zero i.e., initialises the iteration space
            self.blank_dictionary = {i: 0 for i in self.blank_list}
        else:
            # Creates a list of all the consumed consumables; only way to remove Ghost Starting Area on Medium Classic
            if self.pacmancoord not in self.eaten_list:
                # If pacman has been to a tile it has eaten the food
                self.eaten_list.append(self.pacmancoord)
            # Obtains coordinate for the Ghost Starting Area i.e 8 tiles @ Grid Centre; adds coordinates to Hub list
            for i in self.grid:
                #  Check for all non-key feature tiles; i.e tiles with No Consumables, Walls, and/or Ghosts.
                if i not in self.foodcoord and i not in self.capsulecoord and i not in self.eaten_list and \
                        i not in self.wallcoord and i not in self.ghostHub:
                    # Pacman sometimes gets stuck at entrance of Ghost Hub; Therefore GhostHub is created
                    self.ghostHub.append(i)
            # Iterates over all tiles on grid
            for i in self.grid:
                # Check for all non-key feature tiles; i.e tiles with No Consumables, Walls, and / or Ghosts
                if i not in self.foodcoord and i not in self.capsulecoord and i not in self.blank_list and \
                        i not in self.wallcoord and i not in self.ghostcoord:
                    # Adds Blank Spaces to a list of all the Blank Space with no key features
                    self.blank_list.append(i)
            # Creates Hub dictionary; assign a negative reward to the hub area; to stops pacman from getting stuck
            self.hub_dictionary = {i: self.hub for i in self.ghostHub}
            # Create iteration space; assigns zero value to Blank Space Tiles
            self.blank_dictionary = {i: 0 for i in self.blank_list}
        # Adds/updates Blank Spaces to Reward dictionary
        RewardDic.update(self.blank_dictionary)
        # Checks size of Grid again
        if len(self.grid) < 20:  # Small Grid
            # Assigns negative reward to Inky; Small Grid
            RewardDic.update(self.singleGhost(state))
        else:  # Grid => 20 = Medium Classic
            # Assigns negative reward to Inky and Clyde; Creates Negative Ghost Radius; Assigns Negative Integer to Food
            RewardDic.update(self.multiGhost(state))
            # Overrides Negative Reward when ghost in ghost starting area i.e Hub
            RewardDic.update(self.hub_dictionary)
            # Blank Spaces in Negative Ghost Radius + HUB will be assigned a Zero Reward IF not included in FR Dic;
            self.Fixed_Reward_Dic.update(self.ghost_tentacles_dictionary)
            self.Fixed_Reward_Dic.update(self.hub_dictionary)
        # Initialising Pacman Location to zero
        if self.pacmancoord in RewardDic.keys():
            RewardDic[self.pacmancoord] = 0
        return RewardDic

    def singleGhost(self, state):
        """Creates a dictionary that assigned a negative reward to the Inky's coordinates; Only used on the small grid"""
        # Initialise Inky's Negative Reward dictionary
        ghost_dictionary = {}
        # Check to see if Inky is scared
        if self.ghostStatus[0][1] == 0:  # 0 = Not Scared
            # If TRUE; Assigns a Negative Reward to Ink's Location
            ghost_dictionary[self.ghostStatus[0][0]] = - 1
        return ghost_dictionary

    def multiGhost(self, state):
        """Creates a dictionary of negative rewards for the Clyde and Inky. Create a radius of negative rewards
        surrounding ghosts i.e imaginary ghostly tentacles. Assigns a negative reward to food, one tile to the North,
        South, East and West of ghost tentacle radius"""
        # Initialises Inky and Clyde's Joint Dictionary; Imagine Inky and Clyde have ghost tentacles that infect area
        self.ghost_tentacles_dictionary = {}
        # Initialises Tentacle List i.e Ghost Radius; Lists are separated; in case one ghost has been eaten/respawns
        self.tentacles_list = []
        tentaclesClyde = []
        tentaclesInky = []
        # IInitialises Rotten Food List; Assigns a Negative Utility for Certain Consumables
        rotten_food_list = []
        rottenClyde = []
        rottenInky = []
        # Obtains Coordinates for Inky and Clyde
        Ghost_Coordinates = [self.ghostStatus[0][0], self.ghostStatus[1][0]]
        # Clyde's Ghost Tentacles; Initially checks to see if Clyde is scared; If TRUE start assigning reward
        if self.ghostStatus[0][1] == 0:  # 0 = Scared
            # If Clyde is scared; a negative reward is assigned its coordinate in the joint Ghost dictionary
            self.ghost_tentacles_dictionary[self.ghostStatus[1][0]] = -10
            # Creates a 1 tile radius surrounding Clyde; using the Corners and NSEW method; Tentacles
            tentaclesClyde = self.corners(self.ghostStatus[1][0]) + self.NSEW(self.ghostStatus[1][0])
            # Calls the Rotten Food method which generates a set of coordinates; one to the North, South, East and West;
            # The Rotten food method only inc. food pellets 1 tile to the NSEW of the Ghost Radius; Not Corners
            rottenClyde = self.rottenFood(self.ghostStatus[1][0])
        # Inky's Ghostly Tentacles; Same as above
        if self.ghostStatus[1][1] == 0:
            self.ghost_tentacles_dictionary[self.ghostStatus[0][0]] = -10
            tentaclesInky = self.corners(self.ghostStatus[0][0]) + self.NSEW(self.ghostStatus[0][0])
            rottenInky = self.rottenFood(self.ghostStatus[0][0])
        # Creates a joint list of the tiles 1 tile radius surrounding Clyde and Inky; Ghostly tentacles;
        temporay_tentacles = tentaclesInky + tentaclesClyde
        # Iterate over Tentacle List
        for i in temporay_tentacles:
            # Removes Tentacles/ Tiles outside of the Grid/ in Walls.
            if i not in self.wallcoord and i in self.grid and i not in self.tentacles_list:
                self.tentacles_list.append(i)
        # Assigns a Negative reward to the the Negative Tentacle Radi
        for i in self.tentacles_list:
            # Remove Ghost location
            if i not in Ghost_Coordinates:
                # Assign Fixed Negative Reward
                self.ghost_tentacles_dictionary[i] = self.tenticles
        # Checks; Do any food pellet exist in the rotten food region; If TRUE; Assign negative reward
        for i in rottenInky:
            if i in self.foodcoord and i not in rotten_food_list:
                rotten_food_list.append(i)
        for i in rottenClyde:
            if i in self.foodcoord and i not in rotten_food_list:
                rotten_food_list.append(i)
        # Check; Remove Rotten Food Locations in Ghost Tentacles; Avoids OverLap/ Over assignment
        for i in rotten_food_list:
            if i not in self.ghost_tentacles_dictionary:
                self.ghost_tentacles_dictionary[i] = - 10
        #  Returns Full Ghost Dictionary
        return self.ghost_tentacles_dictionary

    def NSEW(self, coordinates):
        """Creates a list of the states to the North, South, East and West of a given set of coordinates."""
        (x, y) = coordinates
        return [(x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y), (x, y)]  # N, S, E, W, Bounce

    def corners(self, coordinates):
        """Creates a list of the states to the NorthEast,NorthWest, SouthEast and SouthWest  of coordinates; Corners."""
        (x, y) = coordinates
        return [(x - 1, y + 1), (x + 1, y + 1), (x + 1, y - 1), (x - 1, y - 1)]  # NE, NW, SE, SW

    def rottenFood(self, coordinates):
        """The Rotten Food method creates a list of tiles one square to the North, South East and West of the
        negative tentacle ghost radius. Does not Include Radius itself. Only assigns negative rewards to food only not
        tiles"""
        RottenFood_List = [] # Intialise/Resets list after very timestep
        # Ghost's Location is take as the argument
        (x, y) = coordinates
        # Generates a list of coordinates; one tile to the NSEW of ghost radius; Does not include corners
        # Coordinates in Ghost Radius will be removed later
        # Negative Rewards will only be assigned to Food Pellets in Rotten Food Method Range; Not Blank Spaces
        for i in range(self.RottenFoodLength):
            RottenFood_List.append((x, y + i))
            RottenFood_List.append((x, y - i))
            RottenFood_List.append((x + i, y))
            RottenFood_List.append((x - i, y))
        return RottenFood_List

    def valueIteration(self, state):
        """The Value Iteration method contains the Bellman Update which is is used for value iteration. Value iteration
        commences on all the blank spaces on the grid ,therefore, all food pellets and ghosts are assumed to be fixed
        states. Additionally the ghost hub and ghost radius are assumed to be fixed value state. First a coordinate is
        passed through the NSEW method which generates the list of states, which is then used to Expected Utility of
        a particular state; which is the maximum expected utility given that the agent has selected the optimal action;
        Therefore the utility of a state, is equal to the highest utility of the surrounding state."""

        U = self.rewardDictionary(state) # Creates a reward dictionary;
        delta = 0 # Initialise Delta; Used to Check Convergence Condition
        # Creates an Infinite While loop; Continues until the convergence condition is met => Loop is broken
        while True:
            # Creates a Copy of the previously Rewards dictionary
            # Creates a variable the Utility Method can access; i.e to calculate the Expected Utility of a tile using
            # the iterated dictionary from the previous step.
            U.update(self.blank_dictionary) # Update the New Utility Values of iterated blank space
            self.UDic = U.copy() # Store Previous Delta values for convergence check
            # Allows Utility Method access
            delta_old = delta # Store Previous Delta
            if len(self.grid) < 20:  # Small
                for i in self.blank_dictionary.keys():  # Iterates Passes all Non-Fixed Reward States (i.e Blank Spaces)
                    # Commences value iteration over all the Non-Fixed Reward States (i.e Blank Spaces)
                    if i not in self.ghostcoord: # Removes Ghost = Fixed Reward State
                        # Create a list of the neighbouring coordinate; To Calculate Expected Utility
                        states = self.NSEW(i)
                        # Passes list though Utility Method; Selects Maximum Utility of neibouring states;
                        # assigns to center state in dic
                        self.UDic[states[4]] = max(self.utilityFunction((states)))
                        # Bellman Update; Assigns New utility value to Blank Space Dic
                        self.blank_dictionary[i] = -0.01 + 0.6 * self.UDic[states[4]]
                        # MAX(MIN)
                        # self.UDic[state[4]] = min(self.utilityFunction((states)))

            else:
                for i in self.blank_dictionary.keys():  # Iterates over all Blank Space states
                    if i not in self.Fixed_Reward_Dic.keys() and i not in self.ghostcoord:
                        # Only non - Fixed Reward States i.e Blank Spaces; The Ghost Radius is considered a
                        # Fixed Value. The blank space dictionary contains all the blank spaces inc. ones in the
                        # negative ghost radius, therefore,the negative radial rewards will be iterated over if not
                        # removed from the iteration space.
                        # A list of states surrounding a blank space state is obtained via the NSEW Method;
                        states = self.NSEW(i)
                        # The NSEW and Centre states are passed through the Utility Function; Which Generates a list
                        # containing the Utility of the neighbouring spaces
                        # Maximum Utility neighbouring states is obtained; assigns to the centre state.
                        self.UDic[states[4]] = max(self.utilityFunction((states)))
                        # Bellman Update; Assigns New utility value to Blank Space Dic
                        self.blank_dictionary[i] = -0.01 + 0.8 * self.UDic[states[4]]
            # Call convergence method; to check for convergence based on summation of dic utilities and rewards
            delta = self.convergence(self.UDic) - self.convergence(U)
            # If the utilities have converged; the while loop is broken; and the iterated reward dic is returned.
            if delta == delta_old:
                return U

    def convergence(self, Utls):
        """The Convergence method check to see if the utilities in the iterated utility dictionary have converged."""
        utls = []
        for i in Utls.values():
            if i not in utls:
                utls.append(i)
        return sum(utls)

    def utilityFunction(self, NSEWstates):
        """Calculates the utility of a state using the stocastic motion model"""
        # Creates a list to store states; if a state is in the wall it is reassigned the center state coordinate
        state = []  # n', 's', 'e', 'w'
        # Iterate over 4 states generated by NSEW Method; N, S, E, W and Bounce i.e Center Coordinate
        for i in range(4):
            # Checks to see if the coordinates are in a wall
            if NSEWstates[i] in self.wallcoord:
                # If a coordinate is in a wall; Pick center coordinate
                state.append(NSEWstates[4])
            else: # IF NOT; coordinate remains the same
                state.append(NSEWstates[i])
        # Next using the set of coordinates the corresponding utilities are calculated using the transition model
        n_val = (0.8 * self.UDic[state[0]]) + (0.1 * self.UDic[state[2]]) + (0.1 * self.UDic[state[3]])
        s_val = (0.8 * self.UDic[state[1]]) + (0.1 * self.UDic[state[2]]) + (0.1 * self.UDic[state[3]])
        e_val = (0.8 * self.UDic[state[2]]) + (0.1 * self.UDic[state[0]]) + (0.1 * self.UDic[state[1]])
        w_val = (0.8 * self.UDic[state[3]]) + (0.1 * self.UDic[state[0]]) + (0.1 * self.UDic[state[1]])
        # Generates a list of utilities
        return [n_val, s_val, e_val, w_val]

    def getAction(self, state):
        self.UDic ={}
        # Obtain information about the environment
        self.wallcoord = api.walls(state)
        self.foodcoord = api.food(state)
        self.capsulecoord = api.capsules(state)
        self.ghostcoord = api.ghosts(state)
        self.ghostStatus = api.ghostStates(state)
        self.pacmancoord = api.whereAmI(state)
        # Obtain List of Legal Actions
        legal = api.legalActions(state)
        # Build Grid
        self.gridBuilder(state)
        # Calls value iteration Method; which Generates an iterated Rewards dic; Resets variable to iterated dic
        self.UDic = self.valueIteration(state) # = iterated Utilities Dictionary
        # Maximum Expected Utility i.e Pol Selection
        # Generate a list of utilities of the states surrounding Pacman using the iterated reward dictionary
        values = self.utilityFunction(self.NSEW(api.whereAmI(state)))
        # Obtains Maximum Expected Utility from list generated via Utility Function
        MEU = max(values)
        # Obtains Index for MEU
        Index = values.index(MEU)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        # Pacman chooses optimal policy using Max/Max Regime
        for i in range(len(self.NSEW_Direct)):
            if self.NSEW_Direct[Index] == self.NSEW_Direct[i]:

                return api.makeMove(self.NSEW_Direct[i], legal)

