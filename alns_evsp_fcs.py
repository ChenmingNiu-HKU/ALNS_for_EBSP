from evsp_fcs import EVSP_FCS
from weight_manager import Weights
from repair_operators import *
from remove_operators import random_remove, timeRelate_remove, neighbor_remove
from calculationFuncs import calScheduleCost, calRTrip
import math
import time
from copy import copy, deepcopy
from tqdm import tqdm
import random



'''
@author: Chenming Niu
'''


_reject = 0
_accept = 1
_better = 2
_optimal = 3


class ALNS_EVSP_FCS():

    def __init__(self,
                 evsp_fcs: EVSP_FCS,
                 is_degrade,
                 iterMax = 30000,   # max iteration
                 nMax = 12, # max remove num
                 nMin = 1,  # min remove num
                 diversify_length = 2000,   # not used in this code
                 diversify_n = 100, # not used in this code
                 T0 = 100, # init temperature set for simulate annealing
                 alpha=0.9997,  # cooling rate set for simulate annealing
                 r=0.5,  # balance rate of weights
                 min_veh_n = 18,    # no used in this code
                 rand_n = 5, # not used in this code
                 split_n = 0.2, # the proportion of nodes to remove for e-bus of smallest capacity
                 enePenalty=700,    # energy violate penalty
                 capPenalty=700,    # capacity violate penalty
                 chargeProb=0.9,    # probability of insert a charging node
                 diversifyProb=0.05, # probability to diversify
                 segLength=100,     # how long to adjust weights
                 terminate=True,
                 terminateLength=5000,  # terminate condition
                 unchangedLength=1000,  # iter times to restart
                 ):
        self.params = evsp_fcs
        self.is_degrade = is_degrade
        self.iterMax = iterMax
        self.T0 = T0
        self.nMax = nMax
        self.nMin = nMin
        self.diversify_length = diversify_length
        self.diversify_n = diversify_n
        self.min_veh_n = min_veh_n
        self.rand_n = rand_n
        self.split_n = split_n
        self.alpha = alpha
        self.enePenalty = enePenalty
        self.capPenalty = capPenalty
        self.chargeProb = chargeProb
        self.diversifyProb = diversifyProb
        self.segLength = segLength
        self.terminate = terminate
        self.unchangedLength = unchangedLength
        if self.terminate is True:
            self.terminateLength = terminateLength
        else:
            self.terminateLength = self.iterMax

        self.removeOperators = {
            1: random_remove,
            2: timeRelate_remove,
            3: neighbor_remove
        }
        # test to choose best greedy insert
        self.insertOperators = {
            1: random_insert,
            2: greedy_insert_2,
            3: greedy_insert_3,
            4: greedy_insert_4
        }
        self.weights = Weights(r, self.removeOperators, self.insertOperators)

        self.bestSchedule = None
        self.bestCost = 0
        self.historyCurCost = []
        self.historyBestCost = []

        self.runTime = 0
        self.totalIter = 0


    def solve(self, initial_schedule, initial_r_trip):
        print('---------- start ALNS_EVSP_CCS ----------')

        start_time = time.time()

        # self.bestSchedule, r_trip, self.bestCost = Initialize(self.params)
        # self.bestSchedule, r_trip, self.bestCost = initialize(self.params)
        self.bestSchedule, r_trip = initial_schedule, initial_r_trip
        self.bestCost = calScheduleCost(self.params, self.bestSchedule, self.is_degrade)

        curSchedule = deepcopy(self.bestSchedule)
        curCost = deepcopy(self.bestCost)
        curRTrip = deepcopy(r_trip)

        #   initialize temperature
        T = self.T0
        is_rand_veh_type = False

        # iterate
        with tqdm(total=self.iterMax) as pbar:
            for iter in range(self.iterMax):

                num_to_rem = random.randint(self.nMin, self.nMax)

                remove_op = self.weights.selectRemoveOperator()
                insert_op = self.weights.selectInsertOperator()

                # remove and insert

                tripBank, removedSchedule = remove_op(self.params, curSchedule, curRTrip, num_to_rem, is_rand_veh_type, self.split_n)
                newCost, newSchedule, isFeasible = insert_op(self.params, tripBank, removedSchedule,
                                                             self.enePenalty, self.capPenalty, self.chargeProb, self.is_degrade)
                new_rTrip = calRTrip(newSchedule)

                #   if vehicle_type_num[min(self.params.K)] >= self.rand_n:


                #   acceptance
                result = _reject
                if isFeasible and (newCost<self.bestCost):
                    result = _optimal
                    self.bestSchedule, self.bestCost = newSchedule, newCost
                    curSchedule, curCost, curRTrip = newSchedule, newCost, new_rTrip
                elif newCost < curCost:
                    result = _better
                    curSchedule, curCost, curRTrip = newSchedule, newCost, new_rTrip
                elif math.exp((self.bestCost - newCost)/ T) >= random.random():
                    result = _accept
                    curSchedule, curCost, curRTrip = newSchedule, newCost, new_rTrip
                else:
                    pass

                self.historyCurCost.append(curCost)
                self.historyBestCost.append(self.bestCost)
                self.weights.updateTimeAndScores(result)
                T = T * self.alpha
                pbar.update(1)
                # update weights
                if (iter+1)%self.segLength == 0:    # every 100 times
                    self.weights.updateWeights()
                    # no improvement termination
                    if self.terminate is False:
                        pass
                    else:
                        if ((iter+1) >= self.terminateLength) and (self.historyBestCost[-1] == self.historyBestCost[-self.terminateLength]):
                            self.totalIter = iter + 1
                            print(f"--- Terminate at {iter+1} Iteration")
                            break
                if iter+1 >= self.unchangedLength and self.historyBestCost[-1] == self.historyBestCost[-self.unchangedLength]:
                    curSchedule, curCost, curRTrip = self.bestSchedule, self.bestCost, calRTrip(self.bestSchedule)
        #         print(f'current best cost: {self.bestCost}')
        # end_time = time.time()
        # solve_time = end_time - start_time
        # print(f'solve time: {solve_time}')
        # print(f'best cost: {self.bestCost}')
        # print(f'best schedule: {self.bestSchedule}')
        return self.bestCost, self.bestSchedule, self.historyBestCost, self.historyCurCost