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

#Kwame Owusu Boahene
from pacman import Directions
from game import Agent
import api
import random
import game


class MDPAgent(Agent):

    
    def __init__(self):
        """
            __init__(self,state) called at the start of first game to set global variables
            

           for parameters:
           return:
        """

        # list to keep track of capsules
        self.capsules=[]
        #keeps the value of the maximum width of the map
        self.maxX = 0
        #keeps the value of the maximum height of the map
        self.maxY = 0
        #keeps track of all food locations in map
        self.foodlist = []
        #keeps track of all walls in map
        self.wall = []
        # the discount factor
        self.discount = 0.9
        #reward for a location with food
        self.rewardfood = 10
        #reward for location with capsule
        self.rewardcapsule = 20
        #reward for location around ghost
        self.rewardaghost = -30
        #reward for location with ghost
        self.rewardghost = -50
        #reward for wall
        self.rewardwall = 0
        # reward map keeps track of reward for all locations
        self.rewardmap = None
        # keeps track of the number of states
        self.states = 0
        #reward for no food
        self.rewardnofood = 0
        #keeps track of locations around 
        self.aroundghost = []
        #keeps track of utility of each location
        self.utilitiesmap = None
        # has iteration converged or not
        self.converge = False
        #returns utility dictionary in MEU function if set to true
        self.returnutility = False
        #threshold for convergence
        self.threshold = 0.01
        

 

    def final(self, state):
        """
            final(self,state) called at the end of everygame to reset global variables
            

           for parameters:
           state: the current state of the game 
        """


        # list to keep track of capsules
        self.capsules=[]
        #keeps the value of the maximum width of the map
        self.maxX = 0
        #keeps the value of the maximum height of the map
        self.maxY = 0
        #keeps track of all food locations in map
        self.foodlist = []
        #keeps track of all walls in map
        self.wall = []
        # the discount factor
        self.discount = 0.9
        #reward for a location with food
        self.rewardfood = 10
        #reward for location with capsule
        self.rewardcapsule = 20
        #reward for location around ghost
        self.rewardaghost = -30
        #reward for location with ghost
        self.rewardghost = -50
        #reward for wall
        self.rewardwall = 0
        # reward map keeps track of reward for all locations
        self.rewardmap = None
        # keeps track of the number of states
        self.states = 0
        #reward for no food
        self.rewardnofood = 0
        #keeps track of locations around 
        self.aroundghost = []
        #keeps track of utility of each location
        self.utilitiesmap = None
        # has iteration converged or not
        self.converge = False
        #returns utility dictionary in MEU function if set to true
        self.returnutility = False
        #threshold for convergence
        self.threshold = 0.01




    
    def initializeMap(self,state):
        """
            InitializeMap(self,state) function serves two purposes

            1. create a reward map if the game has just began (i.e self.states == 0) 
            and assign the map to the global reward and utilities map (i.e self.rewardmap and self.utilities map) 
            or 
            2. update the global reward map(self.rewardmap) with the changes in coordinate value that has occured after pacman has change location

            and is based on instructions from lab 5-7

           for parameters:
           state: the current state of the game 

            InitializeMap(self,state) function serves two purposes
            1. create a reward map if the game has just began (i.e self.states == 0) 
            and assign the map to the global reward and utilities map (i.e self.rewardmap and self.utilities map) 
            or 
            2. update the global reward map(self.rewardmap) with the changes in coordinate value that has occured after pacman has change location

           for parameters:
           state: the current state of the game 
        """
      
        pacman = api.whereAmI(state)
        food = api.food(state)
        walls = api.walls(state)
        ghosts = api.ghosts(state)
        capsules = api.capsules(state)
        corners = api.corners(state)
        


        #if states == 0 this means a new game has began
        #therefore we create a reward map and to the global reward map and utilities map 
        if self.states == 0:

            
                    
            #Find the maximum width and height of the grid
            for i in range(0,len(corners)):

                if corners[i][0] > self.maxX:
                    self.maxX = corners[i][0] 
                if corners[i][1] > self.maxY:
                    self.maxY = corners[i][1] 


            #stores coordinates with no food and capsules and aren't walls
            NoFoodCoord=[]

            #using the maximum with and height find all posible coordinates in the grid
            # for each coordinate (x, y) check if coordinate is has a wall, capsule, food or nothing
            # place coordinate in respective list i.e wall, capsule, food or nofood list
            for x in range(0,self.maxX+1):
                for y in range(0,self.maxY+1):

                    #add coordinate to wall and set utility for wall to 0
                    if(x, y) in walls:
                        self.wall.append((x, y))

                    #add coordinate to food list
                    if(x, y) in food:
                        self.foodlist.append((x, y))

                    #add coordinate to capsule list
                    if (x, y) in capsules:
                        self.capsules.append((x, y))

                    #add coordinate that has no food, capsule and walls to NoFoodCoord list
                    if (x, y) not in walls and (x, y) not in food and (x, y) not in capsules:
                        NoFoodCoord.append((x, y))


            #create a dictionary
            rewardmap = {}
            #combine all created dictionaries into one to form a reward map of every cordinate and its reward
            rewardmap.update(dict.fromkeys(self.foodlist,self.rewardfood))
            rewardmap.update(dict.fromkeys(self.capsules,self.rewardcapsule))
            rewardmap.update(dict.fromkeys(NoFoodCoord,self.rewardnofood))
            rewardmap.update(dict.fromkeys(self.wall,self.rewardwall))

            # for each ghost in the map
            for ghost in ghosts:
                
                #change the reward value of ghost cordinate to reward for ghost location 
                rewardmap[(int(ghost[0]), int(ghost[1]))] = self.rewardghost
                
                #find the coordinates around each ghost
                self.aroundghost = self.aroundGhost(ghost)
                
                #for each coordinate around ghost
                for cord in self.aroundghost:
                #change the reward value of cordinates around ghost to reward for location around ghost
                    rewardmap[cord] = self.rewardaghost

                

            #assign reward map to global reward map
            self.rewardmap = rewardmap


            #assign reward map to global utilites map
            self.utilitiesmap = rewardmap

            #print self.utilitiesmap

            #increase the number of game states by 1
            self.states += 1

            #print "state is " + str(self.states)




        #if number of game states >= 1
        else:

            #check if pacman's current location is in the foodlist and remove it
            if pacman in self.foodlist:
                self.foodlist.remove(pacman)

            #check if pacman's current location is in the capsule list and remove it
            if pacman in self.capsules:
                self.capsules.remove(pacman)

            # set the reward of pacman's location to reward for no food
            self.rewardmap[pacman] = self.rewardnofood

            #increase the game state by 1
            self.states += 1

            #for each location
            for (x, y) in self.rewardmap:

                if(x, y) in walls:
                    self.rewardmap[(x, y)] = self.rewardwall

                if(x, y) in food:
                    self.rewardmap[(x, y)] = self.rewardfood

                #add coordinate to capsule list
                if (x, y) in capsules:
                    self.rewardmap[(x, y)] = self.rewardcapsule

                #add coordinate that have no food and capsule and walls
                if (x, y) not in walls and (x, y) not in food and (x, y) not in capsules:
                    self.rewardmap[(x, y)] = self.rewardnofood


            #get the ghost location and whether ghost is scared or not
            ghosts = api.ghostStates(state)

            # for each ghost location set the reward at location to rewar value for ghost
            for ghost in ghosts:

                self.rewardmap[(int(ghost[0][0]), int(ghost[0][1]))] = self.rewardghost


            #ghost with tiimes provide location of ghost and tells how long ghost would stay scared for if ghost is scared 
            ghosts = api.ghostStatesWithTimes(state)

            #For each ghost
            for  ghost in ghosts:
                #if ghost is scared and time left is > 5 and ghost is in a foodlocation
                if ghost[1] >= 6 and (int(ghost[0][0]), int(ghost[0][1])) in self.foodlist:

                    #set reward value for ghost to reward for food
                    self.rewardmap[(int(ghost[0][0]), int(ghost[0][1]))] = self.rewardfood

                    #find the coordinates around each ghost
                    self.aroundghost = self.aroundGhost(ghost[0])
                    
                    #for each coordinate around ghost
                    for cord in self.aroundghost:
                        #if coordinate has food
                        if cord in self.foodlist:
                            #set reward for coordinate to reward for food
                            self.rewardmap[cord] = self.rewardfood

                        else:
                            # set reward for cordinate to no food
                            self.rewardmap[cord] = self.rewardnofood


                else:
                    #set reward value for ghost location to reward for ghost
                    self.rewardmap[(int(ghost[0][0]), int(ghost[0][1]))] = self.rewardghost

                    #find the coordinates around each ghost
                    self.aroundghost = self.aroundGhost(ghost[0])

                     #for each coordinate around ghost
                    for cord in self.aroundghost:

                        # set reward for cordinate to value around ghost
                        self.rewardmap[cord] = self.rewardaghost



        

    def maxEU(self, walls, location):
        """
            this implementation is based on instructions specified in lab 5-7

            the implementation is also partly inspired by 
            https://github.com/leyankoh/pacman-mdp-solver/blob/master/mdpAgents.py lines 240-330

            maxEU(self, walls, location) serves two purposes
            1. maxEU takes a location and finds the direction(i.e north,south,east or west) with the maximum expected utility and return the value of that direction 
            or 
            2. maxEU takes a location and finds the expected utility of each direction(i.e north,south,east or west) of the location  and return a dictionary containing the expected utility 
            each direction
            
            To Calculate the Maximum Expected Utility of Location
            1. we take all the possible directions of a location (north,south,east and west)
            
            2. we find the expected utility of each direction
                    To find the Expected Utility of a Direction
                a. we find the 0.8 * the current utility of that direction 
                    if the direction is in a wall we find 0.8 * current utility location since we cant go into a wall
                    eg say we want to find the utility of direction east we take the current utility of east of the location and multiple by 0.8 
                        if east of the lcoation is in wall we would find 0.8 * current utility of the location
                b. Next, we take the current utility of going to the left and right of the direction i.e (perpendicular to the direction)  and multiply by 0.1 and sum them together
                     If north or south of the location is in a wall we would find 0.1 * current utility of the location and sum them together
                                                                    north
                                                                west     east
                                                                    south    
                eg for the utility of direction east we multipy the current utility of north and south of the location by 0.1 respectively
            
                c. We sum the results of a and b to get the expected utility of the direction

            3.we find the maximum amongst the expected utilities of the directions and that is the MEU of the location



            for parameters:
            walls: a list containing the walls in the map
            location: coordinate where maximum utility is going to be calculated

            return:  maximum expected utilitiy or list contains expected utilities for directions around given location
        """

        #take the x and y values of the location
        x = location[0]
        y = location[1]

        #print walls

        current = (x, y)
        # find the cordinates to the north,south, east and west of the location
        east = (x+1, y)
        west = (x-1, y)
        south =(x, y-1)
        north = (x, y+1)


        
        #create a dictionary to store utilities for these coordinates i.e north,south, east and west
        utility = {"north_util": 0.0, "east_util": 0.0, "south_util": 0.0, "west_util": 0.0}

        eastutility = 0
        westutility = 0
        northutility = 0
        southutility =0




        
        # find  utility in direction west of current location

        if  west not in walls: 

            westutility= self.utilitiesmap[west]

        #if wall pacman cannot move hence utility would be current location
        else:
            westutility= self.utilitiesmap[current]


         # find  utility in direction north of current location

        if   north not in walls:

            northutility =  self.utilitiesmap[north]

        #if wall pacman cannot move hence utility would be current location
        else:
            northutility =  self.utilitiesmap[current]


         # find  utility in direction south of current location
        if   south not in walls:

            southutility= self.utilitiesmap[south]
        #if wall pacman cannot move hence utility would be current location
        else:
            southutility = self.utilitiesmap[current]
        

          # find  utility in direction west of current location
        if  east not in walls:

            eastutility = self.utilitiesmap[east]
        #if wall pacman cannot move hence utility would be current location
        else:
            eastutility = self.utilitiesmap[current]



        utility["east_util"] = (0.8 * eastutility) + (0.1 * northutility) + (0.1 * southutility)
        utility["west_util"] = (0.8 * westutility) + (0.1 * northutility) + (0.1 * southutility)
        utility["north_util"] = (0.8 * northutility) + (0.1 * eastutility) + (0.1 * westutility)
        utility["south_util"] = (0.8 * southutility) + (0.1 * eastutility) + (0.1 * westutility)

        

        #when function is called by valueIteration()
        if self.returnutility == False:

            #print utility
            #return the maximum expected utility amongst all the directions
            return utility[max(utility, key=utility.get)]

        #when  when function called by PacmanMEU()
        else:
            #return the  expected utility for all the directions
            return utility
        

    def valueIteration(self,gamma):
        """
            valueIteration(self,gamma) 
            This value iteration function is based on the procedure specified in lecture 4.4 slides given by Frederick Mallmann-Trenn
            https://keats.kcl.ac.uk/pluginfile.php/6245956/mod_folder/content/0/lect04-4%20Bellman%20and%20Value%20Iteration.pdf?forcedownload=1

            instructions provided in lab 5-7

            it was also partly inspired by reading 
            Ashraf, Mohammad. Reinforcement Learning Demystified: Markov Decision Processes (Part 1). Medium, Towards Data Science, 11 Apr. 2018, towardsdatascience.com/reinforcement-learning-demystified-markov-decision-processes-part-1-bf00dda41690. 
            Ashraf, Mohammad. Reinforcement Learning Demystified: Markov Decision Processes (Part 2).Medium, Towards Data Science, 20 Apr. 2018, towardsdatascience.com/reinforcement-learning-demystified-markov-decision-processes-part-2-b209e8617c5a. 
            Ashraf, Mohammad. Reinforcement Learning Demystified: Solving MDPs with Dynamic Programming. Medium, Towards Data Science, 17 Dec. 2018, towardsdatascience.com/reinforcement-learning-demystified-solving-mdps-with-dynamic-programming-b52c8093c919. 

            the purpose of this function is to utilize iteration on bellman equation to find the optimal policy and value for the states in the environment(cordinates in map) 
            bellman equation = reward at cordinate(x, y) + discount factor * maximum expected utility at cordinate(x, y)

            the function converges when convergencevalue is below the threshold specified

            for parameters:
            gamma: the discount factor for bellman equation
        """ 
        # set discount factors and convergence values
        if self.maxX < 11:

            self.discount = 0.7
            selfthreshold = 0.1
            #print "here"
        #sets converge to false
        self.converge = False

        # while converge  is false(repeats process till converge becomes true)
        while self.converge == False:

            #set value to change convergence to 0
            convergencevalue = 0.0
            #make a copy of the current utilities map      
            newutilities = self.utilitiesmap.copy()

            #for every cordinate(x, y) in map
            for x in range(1,self.maxX):

                for y in range(1,self.maxY):

                    #if cordinate(x, y) is not a wall 
                    if  (x, y) not in self.wall :
                        #set the utility of cordinate to reward at cordinate(x, y) + discount factor * maximum expected utility at cordinate(x, y)
                        newutilities[(x, y)] = self.rewardmap[(x, y)] + gamma * self.maxEU(self.wall, (x, y))
                        
                        #set covergencevalue to sum of itself + absolute value of the difference between new utility at(x, y) and old utility at (x, y)
                        convergencevalue += abs(newutilities[(x, y)] - self.utilitiesmap[(x, y)])
            
            #set utilities map to newutilities calculated
            self.utilitiesmap = newutilities

            # if convergence value is less than threshold of 0.01
            if convergencevalue <=  self.threshold:
                # set converge to true
                self.converge = True
                break

            #iterations +=1



    def aroundGhost(self,ghosts):
        """
            aroundGhost(self,ghosts) the purpose of this function is to take the location of ghost and find all locations around it that arent walls

            for parameters:
            ghosts: the location of ghost

            returns: list with locations around ghost
        """

        #list to store coordinates
        coord = []

        #print ghosts

        #east of ghost
        if ( int(ghosts[0]) +1 , int(ghosts[1])) not in coord:
                if (int(ghosts[0])+ 1 , int(ghosts[1])) not in self.wall:
                    coord.append((int(ghosts[0])+ 1 , int(ghosts[1])))
        #west of ghost
        if (int(ghosts[0])- 1 , int(ghosts[1])) not in coord:
                if (int(ghosts[0])- 1, int(ghosts[1])) not in self.wall:
                    coord.append((int(ghosts[0])- 1, int(ghosts[1])))
        #south of ghost
        if (int(ghosts[0]), int(ghosts[1])-1) not in coord:
            if (int(ghosts[0]) , int(ghosts[1])-1) not in self.wall:
                coord.append((int(ghosts[0]) , int(ghosts[1]-1)) )
        
        #north of ghost
        if (int(ghosts[0]) , int(ghosts[1])+1) not in coord:
            if (int(ghosts[0]) , int(ghosts[1])+1) not in self.wall:
                coord.append( (int(ghosts[0]) , int(ghosts[1]+1)) )

        #northeast of ghost
        if ( int(ghosts[0]) +1 , int(ghosts[1])+1) not in coord:
                if ( int(ghosts[0]) +1 , int(ghosts[1])+1) not in self.wall:
                    coord.append(( int(ghosts[0]) +1 , int(ghosts[1])+1))
        #northwest of ghost
        if (int(ghosts[0])- 1 , int(ghosts[1]) + 1) not in coord:
                if (int(ghosts[0])- 1 , int(ghosts[1]) + 1) not in self.wall:
                    coord.append((int(ghosts[0])- 1 , int(ghosts[1]) + 1))
        #southeast of ghost
        if (int(ghosts[0]) + 1, int(ghosts[1])-1) not in coord:
            if (int(ghosts[0]) + 1, int(ghosts[1])-1) not in self.wall:
                coord.append((int(ghosts[0]) + 1, int(ghosts[1])-1) )
        
        #southwest of ghost
        if (int(ghosts[0]) -1, int(ghosts[1])-1) not in coord:
            if (int(ghosts[0]) -1, int(ghosts[1])-1) not in self.wall:
                coord.append( (int(ghosts[0]) -1, int(ghosts[1])-1) )

        return coord



    def PacmanEU(self,pacman,legal):
        """
            PacmanEU(self,pacman,legal) the purpose of this function is to take the location of pacman and find the best legal direction pacman should go to

            for parameters:
            pacman: the coordinate of pacman
            legal: legal directions pacman can go to

            returns: where direction pacman should go to
        """


        #when set to turn MaxEU function returns dictionary containing expected utilities for all directions around pacman
        self.returnutility = True

        utility = self.maxEU(self.wall, pacman)

        self.returnutility = False

        #print self.utilitiesmap

        #set initial maximum expected utility to large negative number
        maxeu = -100000000
        direct = None

        # if stop is in legal remove it
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        #for every legaldirection  
        for direction in legal:
            #if direction is north 
            if direction == Directions.NORTH:
                # and north expected utility is greater than maxeu, set maxeu to north expected utility and set direction to north
                if utility["north_util"] > maxeu:
                    maxeu = utility["north_util"] 
                    direct = "north"

            #if direction is south 
            if direction == Directions.SOUTH:
                 # and south expected utility is greater than maxeu, set maxeu to south expected utility and set direction to south
                if utility["south_util"] > maxeu:
                    maxeu = utility["south_util"] 
                    direct = "south"

            #if direction is east 
            if direction == Directions.EAST:
                # and east expected utility is greater than maxeu, set maxeu to east expected utility and set direction to east
                if utility["east_util"] > maxeu:
                    maxeu = utility["east_util"] 
                    direct = "east"

            #if direction is west 
            if direction == Directions.WEST:
            # and west expected utility is greater than maxeu, set maxeu to west expected utility and set direction to west
                if utility["west_util"] > maxeu:
                    maxeu = utility["west_util"] 
                    direct = "west"

        
        #print maxeu
        #print utility
        #print direct

        return direct


    def registerInitialState(self, state):
        """    
            registerInitialState(self, state) runs at the start of a new game

            for parameters:
            state: current state of the game

            returns: 
        """

        print "New Game"



    def getAction(self,state):
        """    
            getAction(self,state) the purpose of this function is to find initialize the map, run value iteration over the states(coordinates)
            find the optimum policy and return the direction in which pacman should go based in the optimum policy

            for parameters:
            state: current state of the game

            returns: direction pacman should go to
        """

        #get location of pacman
        pacman = api.whereAmI(state) 

        #print pacman
        #creates  reward and utility map if the game just began or updates reward map if game state isnt 0
        self.initializeMap(state)

        #peforms value iteration to find utility for all map coordinates
        self.valueIteration(self.discount)

        #legal actions pacman can make
        legal = api.legalActions(state)
        #remove stop from legal actions
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        #gets direction pacman should go
        direction = self.PacmanEU(pacman,legal)

        #excutes direction pacman should go
        if  direction == "north":
            #print "north"
            return api.makeMove(Directions.NORTH, legal)

        elif direction == "south":
            #print "south"
            return api.makeMove(Directions.SOUTH, legal)

        elif direction == "east":
            #print "east"
            return api.makeMove(Directions.EAST, legal)

        else: 
            #print "west"
            return api.makeMove(Directions.WEST, legal)


