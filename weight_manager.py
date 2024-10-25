import random





'''
@author: Chenming Niu
'''


_reject = 0
_accept = 1
_better = 2
_optimal = 3
scores_add= {
    0: 0,
    1: 5,
    2: 15,
    3: 30
}





class Weights():

    '''
    weights is a class to manage scores, weights of different operators
    and choose a proper one for one iteration
    '''

    def __init__(self,
                 r,
                 removeOps: dict,
                 insertOps: dict
                 ):
        # init operators
        self.r = r  # control params
        self.removeSele = 0
        self.insertSele = 0
        self.removeOp_dct = removeOps
        self.insertOp_dct = insertOps

        #   weigths, scores
        self.weightRem = {i: 1 for i in removeOps.keys()}
        self.weightIns = {i: 1 for i in insertOps.keys()}
        self.scoreRem = {i: 0 for i in removeOps.keys()}
        self.scoreIns = {i: 0 for i in insertOps.keys()}
        self.timeRem = {i: 0 for i in removeOps.keys()}
        self.timeIns = {i: 0 for i in insertOps.keys()}
        self.historyWeightRem = {i: [1] for i in removeOps.keys()}
        self.historyWeightIns = {i: [1] for i in insertOps.keys()}


    def updateTimeAndScores(self, result: int):
        self.scoreRem[self.removeSele] += scores_add[result]
        self.scoreIns[self.insertSele] += scores_add[result]
        self.timeRem[self.removeSele] += 1
        self.timeIns[self.insertSele] += 1

    def updateWeights(self):
        """
        Update weights after each segment.
        """
        for i in self.weightRem.keys():
            if self.timeRem[i] == 0:
                self.historyWeightRem[i].append(self.weightRem[i])
            else:
                self.weightRem[i] = self.weightRem[i] * (1 - self.r) + self.r * (
                            self.scoreRem[i] / self.timeRem[i])
                self.historyWeightRem[i].append(self.weightRem[i])

        for i in self.weightIns.keys():
            if self.timeIns[i] == 0:
                self.historyWeightIns[i].append(self.weightIns[i])
            else:
                self.weightIns[i] = self.weightIns[i] * (1 - self.r) + self.r * (
                            self.scoreIns[i] / self.timeIns[i])
                self.historyWeightIns[i].append(self.weightIns[i])

        self.scoreRem = {i: 0 for i in self.removeOp_dct.keys()}
        self.scoreIns = {i: 0 for i in self.insertOp_dct.keys()}
        self.timeRem = {i: 0 for i in self.removeOp_dct.keys()}
        self.timeIns = {i: 0 for i in self.insertOp_dct.keys()}

    def selectRemoveOperator(self):
        """
        Select operators according to weights.
        """
        cumWeights = {i: sum([self.weightRem[n] for n in self.weightRem.keys() if n <= i]) for i in
                      self.weightRem.keys()}  # cumulative probability
        rouletteValue = random.uniform(0, max(cumWeights.values()))  # roulette wheel number
        for k in self.weightRem.keys():
            if cumWeights[k] >= rouletteValue:
                operator = self.removeOp_dct[k]
                self.removeSele = k
                break
        return operator

    def selectInsertOperator(self):
        """
        Select operators according to weights.
        """
        cumWeights = {i: sum([self.weightIns[n] for n in self.weightIns.keys() if n <= i]) for i in
                      self.weightIns.keys()}  # cumulative probability
        rouletteValue = random.uniform(0, max(cumWeights.values()))  # roulette wheel number
        for k in self.weightIns.keys():
            if cumWeights[k] >= rouletteValue:
                operator = self.insertOp_dct[k]
                self.insertSele = k
                break
        return operator