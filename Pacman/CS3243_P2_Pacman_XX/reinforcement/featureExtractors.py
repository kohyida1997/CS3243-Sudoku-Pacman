# featureExtractors.py
# --------------------
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


"Feature extractors for Pacman game states"

from game import Directions, Actions
import util


class FeatureExtractor:
    def getFeatures(self, state, action):
        """
          Returns a dict from features to counts
          Usually, the count will just be 1.0 for
          indicator functions.
        """
        util.raiseNotDefined()


class IdentityExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        feats = util.Counter()
        feats[(state, action)] = 1.0
        return feats


class CoordinateExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        feats = util.Counter()
        feats[state] = 1.0
        feats['x=%d' % state[0]] = 1.0
        feats['y=%d' % state[0]] = 1.0
        feats['action=%s' % action] = 1.0
        return feats


def closestFood(pos, food, walls):
    """
    closestFood -- this is similar to the function that we have
    worked on in the search project; here its all in one place
    """
    fringe = [(pos[0], pos[1], 0)]
    expanded = set()
    while fringe:
        pos_x, pos_y, dist = fringe.pop(0)
        if (pos_x, pos_y) in expanded:
            continue
        expanded.add((pos_x, pos_y))
        # if we find a food at this location then exit
        if food[pos_x][pos_y]:
            return dist
        # otherwise spread out from the location to its neighbours
        nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
        for nbr_x, nbr_y in nbrs:
            fringe.append((nbr_x, nbr_y, dist + 1))
    # no food found
    return None

def closest(pos, objectPosList, walls):
    """
    Find the distance (by a legal route) to the closest object. 
    """
    fringe = [(pos[0], pos[1], 0)]
    expanded = set()
    while fringe:
        pos_x, pos_y, dist = fringe.pop(0)
        if (pos_x, pos_y) in expanded:
            continue
        expanded.add((pos_x, pos_y))

        # if we find a ghost at this location then exit
        found = False
        foundIndex = -1
        for index, p in enumerate(objectPosList):
            if p == (pos_x, pos_y):
                found = True
                foundIndex = index
                break

        if found:
            return dist, foundIndex
        
        # otherwise spread out from the location to its neighbours
        nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
        for nbr_x, nbr_y in nbrs:
            fringe.append((nbr_x, nbr_y, dist + 1))
    # no ghost found 
    return None, None

def foodManhattanDistance(food_grid, next_pos):
    """
    Motivates agent to move towards state with lower overall MD, hence improving scores
    """
    total_MD = 0
    next_x, next_y = next_pos
    for food in food_grid: #contains pos of food
        md = abs(food[0] - next_x) + abs(food[1] - next_y)
        total_MD += md
    return total_MD*10

class SimpleExtractor(FeatureExtractor):
    """
    Returns simple features for a basic reflex Pacman:
    - whether food will be eaten
    - how far away the next food is
    - whether a ghost collision is imminent
    - whether a ghost is one step away
    """

    def getFeatures(self, state, action):
        # extract the grid of food and wall locations and get the ghost locations
        food = state.getFood()
        walls = state.getWalls()
        ghosts = state.getGhostPositions()

        features = util.Counter()

        features["bias"] = 1.0

        # compute the location of pacman after he takes the action
        x, y = state.getPacmanPosition()
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)

        # count the number of ghosts 1-step away
        features["#-of-ghosts-1-step-away"] = sum(
            (next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)

        # if there is no danger of ghosts then add the food feature
        if not features["#-of-ghosts-1-step-away"] and food[next_x][next_y]:
            features["eats-food"] = 1.0

        dist = closestFood((next_x, next_y), food, walls)
        if dist is not None:
            # make the distance a number less than one otherwise the update
            # will diverge wildly
            features["closest-food"] = float(dist) / (walls.width * walls.height)
        features.divideAll(10.0)
        return features


class NewExtractor(FeatureExtractor):
    """
    Design you own feature extractor here. You may define other helper functions you find necessary.
    """

    """
    Recursive function that finds all legal neighbours n distance away. Similar to BFS
    """
    def getLegalNeighbours(self, frontier_list, walls, n):
        # positions_two_steps_away = Actions.getLegalNeighbors((next_x, next_y), walls)
        if n == 0:
            return frontier_list
        else:
            new_frontier_list = []
            for pos in frontier_list:
                neighbours = Actions.getLegalNeighbors(pos, walls)
                new_frontier_list.extend(neighbours)
            return self.getLegalNeighbours(new_frontier_list, walls, n-1)
    
    """
    Returns a 2-Element Tuple of ActiveGhostList positions and ScaredGhostList positions
    """
    def getGhostPositions(self, ghost_states, ghost_pos):
        active_ghost_pos = []
        scared_ghosts_pos = []
        scared_ghosts_timer = []
        #record positions of active and scared ghosts
        for index, state in enumerate(ghost_states):
            if state.scaredTimer > 0: 
                scared_ghosts_pos.append(ghost_pos[index])
                scared_ghosts_timer.append(state.scaredTimer)
            else:
                active_ghost_pos.append(ghost_pos[index])
        
        return active_ghost_pos, scared_ghosts_pos, scared_ghosts_timer


    def getFeatures(self, state, action):
        #Initialize helper variables
        food = state.getFood()
        walls = state.getWalls()
        capsules = state.getCapsules()
        
        #ghosts
        ghost_states = state.getGhostStates()
        ghosts_pos = state.getGhostPositions()
        active_ghosts_pos, scared_ghosts_pos, scared_ghosts_timer = self.getGhostPositions(ghost_states, ghosts_pos)

        features = util.Counter()

        features["bias"] = 1.0

        # compute the location of pacman after he takes the action
        x, y = state.getPacmanPosition()
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)

        positions_two_steps_away = Actions.getLegalNeighbors((next_x, next_y), walls)
        # positions_two_steps_away = self.getLegalNeighbours([(x, y)],walls, 2) #inconclusive evidence it may be better than above

        # count the number of ghosts 1-step away
        features["#-of-active-ghosts-1-step-away"] = sum(
            ((next_x, next_y) in Actions.getLegalNeighbors(g, walls))
            for g in active_ghosts_pos)

        features["#-of-scared-ghosts-1-step-away"] = sum(
            ((next_x, next_y) in Actions.getLegalNeighbors(g, walls))
            for g in scared_ghosts_pos)

        # count the number of active ghosts 2-steps away
        two_count_active = 0
        for pos in positions_two_steps_away:
            two_count_active += sum(
                pos in Actions.getLegalNeighbors(g, walls) for g in active_ghosts_pos)
        features["#-of-active-ghosts-2-steps-away"] = two_count_active

        # if there is no danger of ghosts then add the food feature
        if not features["#-of-active-ghosts-1-step-away"]:
            if food[next_x][next_y]:
                features["eats-food"] = 1.0

        dist = closestFood((next_x, next_y), food, walls)
        if dist is not None:
            # make the distance a number less than one otherwise the update
            # will diverge wildly
            features["closest-food"] = float(dist) / (walls.width * walls.height)

        if scared_ghosts_pos: 
            distToClosestScaredGhost, index = closest((next_x, next_y), scared_ghosts_pos, walls)
            if distToClosestScaredGhost is not None:
                # closestScaredGhostTimeOut = scared_ghosts_timer[index]
                #it can catch it before ghost becomes active
                # if distToClosestScaredGhost < (closestScaredGhostTimeOut / 2):
                features["closest-scared-ghost"] = float(distToClosestScaredGhost)*4 / (walls.width * walls.height)

        if capsules:
            distToClosestCapsule, index = closest((next_x, next_y), capsules, walls)
            if distToClosestCapsule is not None:
                features["closest-capsule"] = float(distToClosestCapsule) / (2*(walls.width * walls.height))
        
        features["food-md"] = foodManhattanDistance(food.asList(), (next_x, next_y)) / ((walls.width * walls.height) * (walls.width + walls.height))
        # Normalizing
        features.divideAll(10.0)

        return features
