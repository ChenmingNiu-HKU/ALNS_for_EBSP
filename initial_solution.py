import random
import joblib as jl
import pandas as pd
from evsp_fcs import EVSP_FCS
from copy import copy
from tqdm import tqdm
from random import choice
import numpy as np
from copy import copy, deepcopy
from calculationFuncs import calScheduleCost
'''
@ author: Chenming Niu
'''


#   greedy constructive: construct solution based on local optimum


def Initialize(evsp_ccs: EVSP_FCS):

    params = evsp_ccs
    #   initialze vehicle type
    K = deepcopy(params.K)

    k_init = max(params.E_k, key=params.E_k.get)    # initialize vehicle type with largest battery capacity
    T = copy(params.T)  # create a temp trip node
    tc = ['o'] # trip chain, storing depots, trip node and charging node
    schedule = {(1, k_init): copy(tc)}    # store trip chains by labeling num and vehicle type
    r_trip = {} # store the r behind trips
    Y = {(1, k_init): params.E_k[k_init]} # store battery amount
    C = copy(params.C_tn)
    cost = copy(params.c_k[k_init])   # initialize cost
    #   insert trip node
    for i in T:  # insert trip one by one
        cost_add, num_insert, r_insert, num_insert_r = 10000, None, None, None  # initialize cost_add and the tc to insert
        #   check if there are tc to insert
        for num, tc_cur in schedule.items():
            i_cur, Y_cur = tc_cur[-1], Y[num]  # extract current node
            if (i_cur, i) in params.A_k[num[1]]:  # check connection:
                if Y_cur - params.e_i[i] - params.e_ij[(i_cur, i)] >= params.E_k[num[1]]*params.alpha:  # check energy
                    cost_add_cur = cal_addcost(params, i_cur, None, i)
                    if cost_add_cur < cost_add:
                        cost_add = cost_add_cur
                        num_insert = num
                else:
                    r = choose_r(params, i_cur, i, C, Y_cur, num[1])
                    if r:
                        cost_add_cur = cal_addcost(params, i_cur, r, i)
                        if cost_add_cur < cost_add:
                            cost_add = cost_add_cur
                            num_insert_r = num
                            r_insert = r
                    else:   # r doesn't exist
                        continue
            else:
                continue

        if num_insert:  # find a tc to insert
            if r_insert:    # need to insert a r first
                Y[num_insert_r] = cal_batteramout(params, schedule[num_insert_r][-1], r_insert, i, Y[num_insert_r])
                r_trip[schedule[num_insert_r][-1]] = r_insert
                schedule[num_insert_r].append(r_insert)
                schedule[num_insert_r].append(i)
                cost += cost_add
                for tn in params.u_r[r_insert]:
                    C[tn] = C[tn] - 1
            else:   # insert trip only
                Y[num_insert] = cal_batteramout(params, schedule[num_insert][-1], None, i, Y[num_insert])
                schedule[num_insert].append(i)
                cost += cost_add
        else:   # no tc to insert
            num_cur = list(schedule.keys())[-1] # find the lastest insert num
            #   k_cur = random.choice(K)
            schedule[(num_cur[0]+1, k_init)] = copy(tc)+[i]
            cost += cal_addcost(params, 'o', None, i) + params.c_k[k_init]
            Y[(num_cur[0]+1, k_init)] = cal_batteramout(params, 'o', None, i, params.E_k[k_init])


    #   add 'd' and  cost of charging, complete schedule
    schedule_comp, cost_comp = complete_schedule(params, schedule, Y, cost)
    return schedule_comp, r_trip


def choose_r(params, i, j, C, Y, k):

    #   check time feasibility
    R_ij = [r for r in params.R_k[k] if params.s_i[i] + params.t_i[i] + params.t_TR <= params.s_r[r]
            and params.s_r[r] + params.t_r[r] + params.t_TR <= params.s_i[j]]


    #   check capacity constraint
    if not R_ij:
        return None
    R_ij_cp = copy(R_ij)
    for r in R_ij_cp:
        for tn in params.u_r[r]:
            if C[tn] == 0:
                if r in R_ij:
                    R_ij.remove(r)
    #   check energy feasibility
    if R_ij:
        R_ij = [r for r in R_ij if Y - params.e_ij[(i, r)] + params.e_r[r] - params.e_ij[(r, j)] - params.e_i[j] >= params.E_k[k]*params.alpha]
    else:
        return None
    #   R exists
    if R_ij:    # R_ij is not empty
        R_ij = sorted(R_ij, key=params.t_r.get) # ascending sequence
        # R_ij_t = [params.t_r[r] for r in R_ij]
        # prob = np.divide(R_ij_t, sum(R_ij_t))   # shorter charing time with higher probability
        # prob = prob[::-1]   # reverse
        r_chosen = np.random.choice(R_ij)
        return str(r_chosen)    # extract the r with min charging time
    else:
        return None



def cal_batteramout(params, i, r, j, Y):
    if r:   # r is not None, there is a charging between i and j
        return Y - params.e_ij[(i, r)] + params.e_r[r] - params.e_ij[(r, j)] - params.e_i[j]
    else:
        return Y - params.e_ij[(i, j)] - params.e_i[j]




def cal_addcost(params, i, r, j):
    if r:   # r is not None
        elec_cost = params.c_e*params.e_r[r]
        labor_cost = params.c_t*(params.t_ij[(i, r)] + params.t_r[r] + params.t_ij[(r, j)] + params.t_i[j])
        return elec_cost + labor_cost
    else:   # r is None
        elec_cost = 0
        labor_cost = params.c_t*(params.t_ij[(i, j)] + params.t_i[j])
        return elec_cost + labor_cost


def complete_schedule(params, schedule, Y, cost):
    schedule_full = {}
    cost_full = cost
    for num, tc in schedule.items():
        schedule_full[num] = tc + ['d']
        cost_full += params.c_e*(params.E_k[num[1]]-Y[num])
    return schedule_full, cost_full












