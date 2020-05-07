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


def getClosestScaredGhostDist(pos, ghostPosList, ghostTimerList, walls):
    """
    Find the distance (by a legal route) to the closest object.
    """
    if not ghostPosList:
        return 0, 0

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
        for index, p in enumerate(ghostPosList):
            if p == (pos_x, pos_y) and ghostTimerList[index] > dist:
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
    return 0, 0


def foodManhattanDistance(food_grid, next_pos):
    """
    Motivates agent to move towards state with lower overall MD, hence improving scores
    """
    total_MD = 0
    next_x, next_y = next_pos
    for food in food_grid:  # contains pos of food
        md = abs(food[0] - next_x) + abs(food[1] - next_y)
        total_MD += md
    return total_MD * 10


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
            return self.getLegalNeighbours(new_frontier_list, walls, n - 1)

    """
    Returns a 2-Element Tuple of ActiveGhostList positions and ScaredGhostList positions
    """

    def getGhostPositions(self, ghost_states, ghost_pos):
        active_ghost_pos = []
        scared_ghosts_pos = []
        scared_ghosts_timer = []
        # record positions of active and scared ghosts
        for index, state in enumerate(ghost_states):
            if state.scaredTimer > 0:
                scared_ghosts_pos.append(ghost_pos[index])
                scared_ghosts_timer.append(state.scaredTimer)
            else:
                active_ghost_pos.append(ghost_pos[index])

        return active_ghost_pos, scared_ghosts_pos, scared_ghosts_timer

    def getFeatures(self, state, action):
        # Initialize helper variables
        food = state.getFood()
        walls = state.getWalls()
        capsules = state.getCapsules()

        # ghosts
        ghost_states = state.getGhostStates()
        ghosts_pos = state.getGhostPositions()
        active_ghosts_pos, scared_ghosts_pos, scared_ghosts_timer = self.getGhostPositions(ghost_states, ghosts_pos)

        features = util.Counter()

        features["bias"] = 1.0

        # compute the location of pacman after he takes the action
        x, y = state.getPacmanPosition()
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)

        # count the number of ghosts 1-step away
        features["#-of-active-ghosts-1-step-away"] = sum(
            ((next_x, next_y) in Actions.getLegalNeighbors(g, walls))
            for g in active_ghosts_pos)

        features["#-of-scared-ghosts-1-step-away"] = sum(
            ((next_x, next_y) in Actions.getLegalNeighbors(g, walls))
            for g in scared_ghosts_pos)



        if not features["#-of-scared-ghosts-1-step-away"] and not features["#-of-active-ghosts-1-step-away"]:
            # count the number of active ghosts 2-steps away
            positions_two_steps_away = Actions.getLegalNeighbors((next_x, next_y), walls)

            glob_set = set()
            for g in scared_ghosts_pos:
               two_pos_away = set()
               for pos in Actions.getLegalNeighbors(g, walls):
                    for pos_2 in Actions.getLegalNeighbors(pos, walls):
                     two_pos_away.add(pos_2)
               for e in two_pos_away:
                   glob_set.add(e)

            two_count_active = 0
            for pos in positions_two_steps_away:
                if pos in glob_set:
                    two_count_active += 1
            features["#-of-scared-ghosts-2-steps-away"] = two_count_active

        # if there is no danger of ghosts then add the food feature

        dist = closestFood((next_x, next_y), food, walls)
        if dist is not None:
            # make the distance a number less than one otherwise the update
            # will diverge wildly
            features["closest-food"] = float(dist) / (walls.width * walls.height)

        if not features["#-of-active-ghosts-1-step-away"]:  # safe to hunt for food
            if food[next_x][next_y] and ((next_x, next_y) not in scared_ghosts_pos):  # food in next tile, no scared ghosts to prioritze
                features["eats-food"] = 1.0 - features["closest-food"]
            if (next_x, next_y) in capsules and not scared_ghosts_pos:
                features["eats-capsule"] = 1.0

        if not features["#-of-active-ghosts-1-step-away"] and len(scared_ghosts_pos) > 0:  # not in danger of nearby active ghosts
            distToClosestScaredGhost, index = getClosestScaredGhostDist((next_x, next_y), scared_ghosts_pos,
                                                                        scared_ghosts_timer, walls)
            features["closest-scared-ghost"] = 1.0 - (float(distToClosestScaredGhost) / (walls.width * walls.height))


        if not scared_ghosts_pos:  # only look for capsules if there are no scared ghosts
            distToClosestCapsule, index = closest((next_x, next_y), capsules, walls)
            if distToClosestCapsule is not None:
                features["closest-capsule"] = float(distToClosestCapsule) / (walls.width * walls.height)

        # features["food-md"] = foodManhattanDistance(food.asList(), (next_x, next_y)) / (
        #             (walls.width * walls.height) * (walls.width + walls.height))
        # Normalizing

        features.divideAll(10.0)

        return features