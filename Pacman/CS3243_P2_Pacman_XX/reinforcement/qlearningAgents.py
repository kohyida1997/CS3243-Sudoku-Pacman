# qlearningAgents.py
# ------------------
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


from game import *
from learningAgents import ReinforcementAgent
from featureExtractors import *

import random, util, math


class QLearningAgent(ReinforcementAgent):
    """
      Q-Learning Agent

      Functions you should fill in:
        - computeValueFromQValues
        - computeActionFromQValues
        - getQValue
        - getAction
        - update

      Instance variables you have access to
        - self.epsilon (exploration prob)
        - self.alpha (learning rate)
        - self.discount (discount rate)

      Functions you should use
        - self.getLegalActions(state)
          which returns legal actions for a state
    """

    def __init__(self, **args):
        "You can initialize Q-values here..."
        ReinforcementAgent.__init__(self, **args)

        self.q_values = util.Counter()

    def getQValue(self, state, action):
        """
          Returns Q(state,action)
          Should return 0.0 if we have never seen a state
          or the Q node value otherwise
        """
        return self.q_values[(state, action)]

    def computeValueFromQValues(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        legal_actions = self.getLegalActions(state)

        if len(legal_actions) == 0:
            return 0.0
        else:
            curr_max = -sys.maxint
            for a in legal_actions:
                if self.getQValue(state, a) >= curr_max:
                    curr_max = self.getQValue(state, a)
            return curr_max

    def computeActionFromQValues(self, state):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        if len(self.getLegalActions(state)) == 0:
            return None

        legal_actions = self.getLegalActions(state)
        curr_max = -sys.maxint
        tied_actions = []
    
        for a in legal_actions:
            curr_q_value = self.getQValue(state, a)
            if curr_q_value == curr_max: #add to tied list to break ties randomly later
                tied_actions.append(a)

            if curr_q_value > curr_max: #Better Q Value found, reset
                curr_max = curr_q_value
                del tied_actions[:] #reset list
                tied_actions.append(a) #add curr

        return random.choice(tied_actions)

    def getAction(self, state):
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.

          HINT: You might want to use util.flipCoin(prob)
          HINT: To pick randomly from a list, use random.choice(list)
        """

        legal_actions = self.getLegalActions(state)

        if len(legal_actions) == 0:
            return None

        if util.flipCoin(self.epsilon):
            return random.choice(legal_actions)
        else:
            return self.computeActionFromQValues(state)

    def update(self, state, action, nextState, reward):
        """
          The parent class calls this to observe a
          state = action => nextState and reward transition.
          You should do your Q-Value update here
          NOTE: You should never call this function,
          it will be called on your behalf
        """
        curr_q_value = self.getQValue(state, action)
        next_state_best_q_value = self.computeValueFromQValues(nextState)
        new_q_value = (1 - self.alpha) * curr_q_value + self.alpha * (reward + self.discount * next_state_best_q_value)
        self.q_values[(state, action)] = new_q_value

    def getPolicy(self, state):
        return self.computeActionFromQValues(state)

    def getValue(self, state):
        return self.computeValueFromQValues(state)


class PacmanQAgent(QLearningAgent):
    "Exactly the same as QLearningAgent, but with different default parameters"

    def __init__(self, epsilon=0.05, gamma=0.8, alpha=0.2, numTraining=0, **args):
        """
        These default parameters can be changed from the pacman.py command line.
        For example, to change the exploration rate, try:
            python pacman.py -p PacmanQLearningAgent -a epsilon=0.1

        alpha    - learning rate
        epsilon  - exploration rate
        gamma    - discount factor
        numTraining - number of training episodes, i.e. no learning after these many episodes
        """
        args['epsilon'] = epsilon
        args['gamma'] = gamma
        args['alpha'] = alpha
        args['numTraining'] = numTraining
        self.index = 0  # This is always Pacman
        QLearningAgent.__init__(self, **args)

    def getAction(self, state):
        """
        Simply calls the getAction method of QLearningAgent and then
        informs parent of action for Pacman.  Do not change or remove this
        method.
        """
        action = QLearningAgent.getAction(self, state)
        self.doAction(state, action)
        return action


class ApproximateQAgent(PacmanQAgent):
    """
       ApproximateQLearningAgent

       You should only have to overwrite getQValue
       and update.  All other QLearningAgent functions
       should work as is.
    """

    def __init__(self, extractor='IdentityExtractor', **args):
        self.featExtractor = util.lookup(extractor, globals())()
        PacmanQAgent.__init__(self, **args)
        self.weights = util.Counter()

    def getWeights(self):
        return self.weights

    def getQValue(self, state, action):
        """
          Should return Q(state,action) = w * featureVector
          where * is the dotProduct operator
        """

        feature_vector = self.featExtractor.getFeatures(state, action)
        res = 0
        for key in feature_vector:
            res += self.weights[key] * feature_vector[key]

        return res

    def update(self, state, action, nextState, reward):
        """
           Should update your weights based on transition
        """
        next_state_best_q_value = self.getValue(nextState)
        feature_vector = self.featExtractor.getFeatures(state, action)
        difference = (reward + self.discount * next_state_best_q_value) - self.getQValue(state, action)
        for key in feature_vector:
            curr_weight = self.weights[key]
            self.weights[key] = curr_weight + self.alpha * difference * feature_vector[key]

    def final(self, state):
        "Called at the end of each game."
        # call the super-class final method
        PacmanQAgent.final(self, state)

        features_to_check = ["#-of-scared-ghosts-1-step-away",  "#-of-active-ghosts-1-step-away",
                             "#-of-scared-ghosts-2-steps-away", "eats-food", "closest-scared-ghost", "closest-capsule",
                             "closest-food", "#-of-scared-ghosts-2-steps-away", "eats-capsule"]

        string_to_print = ""
        # did we finish training?
        if self.episodesSoFar <= self.numTraining:
            for key in features_to_check:
                string_to_print += key[5:] + "--> " + str(self.weights[key]) + "\n"
            print(string_to_print)
            pass
