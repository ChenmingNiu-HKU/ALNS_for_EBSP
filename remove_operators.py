from evsp_fcs import EVSP_FCS
from tqdm import tqdm
import random
from copy import deepcopy, copy
from calculationFuncs import split_T_byVehType

'''
@author: Chenming Niu
'''


def random_remove(evsp_ccs: EVSP_FCS, schedule, r_trip, n: int, is_rand_n,
                  split_ratio):  # n is the number of trips to remove
    '''
    remove n trips randomly from schedule
    '''
    #   initialize params
    params = evsp_ccs
    split_rate = split_ratio
    #   removed_schdule
    if is_rand_n == False:
        tripBank = list(random.sample(params.T, n))  # generate trip bank, storing trips to remove
    else:
        n_veh_min = int(n * split_rate)
        n_veh_other = n - n_veh_min
        T_veh_min, T_veh_other = split_T_byVehType(params, schedule)
        tripBank = list(random.sample(T_veh_min, n_veh_min)) + list(random.sample(T_veh_other, n_veh_other))

    removed_schedule = {}  # store new schedule after removal
    removed_idx_list = []  # store index of removed list
    rTrip = copy(r_trip)

    for num, tc in schedule.items():

        #   filter tripbank and chargingbank from original schedule
        trip_charging_Bank = list(set([i for i in tripBank if i in list(rTrip.keys()) if
                                       i in tc]))  # extract the trip node before charging node to remove
        new_tc = list(filter(lambda x: x not in tripBank, tc))
        if trip_charging_Bank:
            for i in trip_charging_Bank:
                new_tc.remove(rTrip[i])
                rTrip.pop(i)

        removed_schedule[num] = new_tc

        if len(new_tc) <= 4:  # trip chain too short
            tripBank.extend([i for i in new_tc[1:-1] if type(i) == int])  # remove trips in short trip chain
            removed_idx_list.append(num)

    for idx in removed_idx_list:
        removed_schedule.pop(idx)

    return tripBank, removed_schedule


def timeRelate_remove(evsp_ccs: EVSP_FCS, schedule, r_trip, n: int, is_rand_n, split_ratio):
    '''
    remove n trips from schedule by the time relation
    '''
    #   initialize params
    params = evsp_ccs
    #   removed_schdule
    removed_schedule = {}  # store new schedule after removal
    removed_idx_list = []  # store index of removed list
    rTrip = copy(r_trip)

    split_rate = split_ratio
    if is_rand_n == False:
        tripBank = []  # generate trip bank, storing trips to remove
        while len(tripBank) < n:
            unremoved = list(set(params.T) - set(tripBank))
            i = random.choice(unremoved)
            time_relation = {j: abs(params.s_i[i] - params.s_i[j]) + abs(params.t_i[i] - params.t_i[j]) for j in
                             unremoved}
            j = min(time_relation, key=time_relation.get)
            tripBank.append(j)
    else:
        n = n
        n_veh_min = int(n * split_rate)
        n_veh_other = n - n_veh_min
        T_veh_min, T_veh_other = split_T_byVehType(params, schedule)
        tripBank_veh_min, tripBank_veh_other = [], []
        while len(tripBank_veh_min) < n_veh_min:
            unremoved = list(set(T_veh_min) - set(tripBank_veh_min))
            i = random.choice(unremoved)
            time_relation = {j: abs(params.s_i[i] - params.s_i[j]) + abs(params.t_i[i] - params.t_i[j]) for j in
                             unremoved}
            j = min(time_relation, key=time_relation.get)
            tripBank_veh_min.append(j)
        while len(tripBank_veh_other) < n_veh_other:
            unremoved = list(set(T_veh_other) - set(tripBank_veh_other))
            i = random.choice(unremoved)
            time_relation = {j: abs(params.s_i[i] - params.s_i[j]) + abs(params.t_i[i] - params.t_i[j]) for j in
                             unremoved}
            j = min(time_relation, key=time_relation.get)
            tripBank_veh_other.append(j)
        tripBank = tripBank_veh_min + tripBank_veh_other

    # find
    # while len(tripBank) < n:
    #     unremoved = list(set(params.T)-set(tripBank))
    #     i = random.choice(unremoved)
    #     time_relation = {j:abs(params.s_i[i]-params.s_i[j])+abs(params.t_i[i]-params.t_i[j]) for j in unremoved}
    #     j = min(time_relation, key=time_relation.get)
    #     tripBank.append(j)

    for num, tc in schedule.items():
        #   filter tripbank and chargingbank from original schedule
        trip_charging_Bank = list(set([i for i in tripBank if i in list(rTrip.keys()) if
                                       i in tc]))  # extract the trip node before charging node to remove
        new_tc = list(filter(lambda x: x not in tripBank, tc))
        if trip_charging_Bank:
            for i in trip_charging_Bank:
                new_tc.remove(rTrip[i])
                rTrip.pop(i)

        removed_schedule[num] = new_tc

        if len(new_tc) <= 4:  # trip chain too short
            tripBank.extend([i for i in new_tc[1:-1] if type(i) == int])  # remove trips in short trip chain
            removed_idx_list.append(num)

    for idx in removed_idx_list:
        removed_schedule.pop(idx)

    return tripBank, removed_schedule


def neighbor_remove(evsp_ccs: EVSP_FCS, schedule, r_trip, n: int, is_rand_n, split_ratio):
    #   initialize params
    params = evsp_ccs
    #   removed_schdule
    removed_schedule = {}  # store new schedule after removal
    tripBank = list(random.sample(params.T, 1))  # generate initial trip bank, storing trips to remove
    removed_idx_list = []  # store index of removed list
    schedule_nocharge = {}
    rTrip = copy(r_trip)
    for num, tc in schedule.items():
        schedule_nocharge[num] = list(filter(lambda x: (type(x) == int or len(x) < 2), tc))
        # tc_charging = [i for i in tc if type(i)==str if len(i)>=2]
        # # for i in tc:
        # #     if type(i) == str:
        # #         if len(i)>=2:
        # #             tc_charging.append(i)
        # schedule_nocharge[num] = list(set(tc)-set(tc_charging)) # remove charging node

    while len(tripBank) < n:
        unremoved = list(set(params.T) - set(tripBank))
        i = random.choice(unremoved)
        tripBank.append(i)
        for tc in list(schedule_nocharge.values()):
            if i in tc:
                idx = tc.index(i, 1, -1)  # index(element, start, end)
                if idx - 1 != 0 and (tc[idx - 1] not in tripBank):
                    tripBank.append(tc[idx - 1])
                if idx + 1 != len(tc) - 1 and (tc[idx + 1] not in tripBank):
                    tripBank.append(tc[idx + 1])
                break

    for num, tc in schedule.items():
        #   filter tripbank and chargingbank from original schedule
        trip_charging_Bank = list(set([i for i in tripBank if i in list(rTrip.keys()) if
                                       i in tc]))  # extract the trip node before charging node to remove
        new_tc = list(filter(lambda x: x not in tripBank, tc))
        if trip_charging_Bank:
            for i in trip_charging_Bank:
                new_tc.remove(rTrip[i])
                rTrip.pop(i)

        removed_schedule[num] = new_tc

        if len(new_tc) <= 4:  # trip chain too short
            tripBank.extend([i for i in new_tc[1:-1] if type(i) == int])  # remove trips in short trip chain
            removed_idx_list.append(num)

    for idx in removed_idx_list:
        removed_schedule.pop(idx)

    return tripBank, removed_schedule



