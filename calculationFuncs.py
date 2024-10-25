import time

from evsp_fcs import EVSP_FCS
import random
from copy import deepcopy, copy
import math
from scipy import integrate


'''
@author: Chenming Niu
'''



### Insert Operator Functions

## random position finder

#  random position func1
def randomPos(EVSP_FCS: EVSP_FCS, tripBank: list, schedule):
    '''
    find trip and position to insert randomly
    '''

    trip, tc_idx, pos = None, -1, -1    # trip to insert, tripChain index, position of tripChain
    tripPool = copy(tripBank)
    params = EVSP_FCS

    while tripPool:
        trip = random.choice(tripPool)
        tc_idx, pos = findPosInSchedule(params, schedule, trip)
        if pos == -1:
            tripPool.remove(trip)
            continue
        else:
            break
    return trip, tc_idx, pos


#  random position func2
def findPosInSchedule(EVSP_FCS: EVSP_FCS, schedule, trip):
    tc_idx, pos = -1, -1
    schedule_idx_list = list(schedule.keys())

    while schedule_idx_list:    # not empty
        tc_idx = random.choice(schedule_idx_list)
        tc = schedule[tc_idx]
        pos = findPosInTC(EVSP_FCS, tc, trip)
        if pos == -1:
            schedule_idx_list.remove(tc_idx)
            continue
        else:
            break
    return tc_idx, pos


#  random position func3
def findPosInTC(EVSP_FCS: EVSP_FCS, tc, trip):

    pos= -1

    for idx, node_o in enumerate(tc[:-1]):
        node_d = tc[idx+1]  # node_o: node origin, node_d: node destination

        if check_time_feasibility(EVSP_FCS, node_o, trip):
            if check_time_feasibility(EVSP_FCS, trip, node_d):
                pos = idx + 1
                break
        else:
            break

    return pos




## regret-k position finder
#   regret-1 func1
def regret1Pos(EVSP_FCS: EVSP_FCS, tripBank: list, schedule):
    '''
    find trip and position to insert randomly
    '''

    trip, tc_idx, pos = None, -1, -1    # trip to insert, tripChain index, position of tripChain
    tripPool = copy(tripBank)
    params = EVSP_FCS

    while tripPool:
        trip = random.choice(tripPool)
        tc_idx, pos = findBestPosInSchedule(params, schedule, trip)
        if pos == -1:
            tripPool.remove(trip)
            continue
        else:
            break
    return trip, tc_idx, pos

#   regret-1 func2
def findBestPosInSchedule(EVSP_FCS: EVSP_FCS, schedule, trip):
    tc_idx, pos, cost_add = -1, -1, 10000

    for idx, tc in schedule.items():
        pos_cur, cost_add_cur =  findBestPosInTC(EVSP_FCS, tc, idx[1], trip)
        if cost_add_cur < cost_add:
            cost_add = cost_add_cur
            pos = pos_cur
            tc_idx = idx

    return tc_idx, pos



#   regret-1 func3
def findBestPosInTC(EVSP_FCS: EVSP_FCS, tc, k, trip):
    params = EVSP_FCS
    pos, cost_new = -1, 10000

    for idx in range(len(tc)-1):
        if check_time_feasibility(params, tc[idx], trip):
            if check_time_feasibility(params, trip, tc[idx+1]):
                tc_new = copy(tc)
                tc_new.insert(idx+1, trip)

                cost_cur = caltcCost(params, tc_new, k)
                if cost_cur < cost_new:
                    cost_new = cost_cur
                    pos = idx+1
    return pos, cost_new




### calculate trip chain cost
def caltcCostByType(EVSP_FCS: EVSP_FCS, tc, k):
    params = EVSP_FCS
    Y = copy(params.E_k[k])
    cost_e, cost_t, cost_bd = 0, 0, 0
    for idx, node_o in enumerate(tc[:-1]):
        node_d = tc[idx + 1]
        if node_d == 'd':
            cost_bd += calBatDeg((Y-params.e_TR)/params.E_k[k], Y/params.E_k[k], params, k)*params.E_k[k]   # battery degradadtion
            Y = Y - params.e_TR
            cost_bd += calBatDeg(Y/params.E_k[k], 1, params, k)*params.E_k[k] # battery degradation
            cost_e += params.c_e*(params.E_k[k]-Y)  # electricity
            cost_t += params.c_t*params.t_TR  # labor cost
            Y = params.E_k[k]
        else:
            if node_o in params.T:
                if node_d in params.T:
                    cost_bd += calBatDeg((Y-params.e_TT-params.e_i[node_d])/params.E_k[k], Y/params.E_k[k], params, k)*params.E_k[k]
                    Y = Y - params.e_TT - params.e_i[node_d]
                    cost_t += params.c_t*(params.t_TT+params.t_i[node_d])
                else:  # node_d in R
                    cost_bd += calBatDeg((Y-params.e_TR)/params.E_k[k], Y/params.E_k[k], params, k)*params.E_k[k]
                    Y = Y - params.e_TR
                    energy_charge = nonlinear_Charge(params, k, Y, params.t_r[node_d])
                    cost_bd += calBatDeg(Y/params.E_k[k], (Y+energy_charge)/params.E_k[k], params, k)*params.E_k[k]
                    cost_e += params.c_e*(energy_charge)
                    cost_t += params.c_t * params.t_TR
                    Y = Y + energy_charge
            else:  # node_o in R
                if node_o != 'o':
                    cost_bd += calBatDeg((Y-params.e_TR-params.e_i[node_d])/params.E_k[k], Y/params.E_k[k], params, k)*params.E_k[k]
                    Y = Y - params.e_TR - params.e_i[node_d]
                    cost_t += params.c_t*(params.t_TR+params.t_i[node_d])
        if node_o == 'o':
            cost_bd += calBatDeg((Y - params.e_TR - params.e_i[node_d]) / params.E_k[k], Y / params.E_k[k], params, k)*params.E_k[k]
            Y = Y - params.e_TR - params.e_i[node_d]
            cost_t += params.c_t * (params.t_TR + params.t_i[node_d])


    # return cost_t+cost_e+cost_bd+params.c_k[k]
    return cost_bd, cost_t, cost_e, params.c_k[k]

### calculate schdule cost
def calScheduleCostByType(EVSP_FCS: EVSP_FCS, schedule):
    params = EVSP_FCS
    cost_bd, cost_t, cost_e, cost_k = 0, 0, 0, 0
    for idx, tc in schedule.items():
        tc_cost_bd, tc_cost_t, tc_cost_e, tc_cost_k = caltcCostByType(params, tc, idx[1]) # idx[1] is k, vehicle type
        cost_bd += tc_cost_bd
        cost_t += tc_cost_t
        cost_e += tc_cost_e
        cost_k += tc_cost_k
    return cost_bd, cost_t, cost_e, cost_k

def caltcCost(EVSP_FCS: EVSP_FCS, tc, k, is_degrade):
    params = EVSP_FCS
    Y = copy(params.E_k[k])
    Y_last = copy(params.E_k[k])
    cost = 0
    if is_degrade == True:
        for idx, node_o in enumerate(tc[:-1]):
            node_d = tc[idx + 1]
            if node_d == 'd':
                Y = Y - params.e_TR
                cost += calBatDeg(Y/params.E_k[k], Y_last/params.E_k[k], params, k)*params.E_k[k] + calBatDeg(Y/params.E_k[k], 1, params, k)*params.E_k[k] \
                    + params.c_t*params.t_TR + params.c_e*params.e_TR

                Y, Y_last = params.E_k[k], params.E_k[k]
            else:
                if node_o in params.T:
                    if node_d in params.T:
                        Y = Y - params.e_TT - params.e_i[node_d]
                        cost += params.c_t*(params.t_TT+params.t_i[node_d]) + params.c_e*(params.e_TT+params.e_i[node_d])
                    else:  # node_d in R
                        Y = Y - params.e_TR
                        cost += calBatDeg(Y/params.E_k[k], Y_last/params.E_k[k], params, k)*params.E_k[k]
                        energy_charge = nonlinear_Charge(params, k, Y, params.t_r[node_d])
                        cost += calBatDeg(Y/params.E_k[k], (Y+energy_charge)/params.E_k[k], params, k)*params.E_k[k]
                        cost += params.c_t*params.t_TR + params.c_e*params.e_TR
                        Y = Y + energy_charge
                        Y_last = copy(Y)
                else:  # node_o in R
                    if node_o != 'o':
                        Y = Y - params.e_TT - params.e_i[node_d]
                        cost += params.c_t*(params.t_TR+params.t_i[node_d]) + params.c_e*(params.e_TR+params.e_i[node_d])
            if node_o == 'o':
                Y = Y - params.e_TT - params.e_i[node_d]
                cost += params.c_t*(params.t_TR+params.t_i[node_d]) + params.c_e*(params.e_TR+params.e_i[node_d])
    else:
        for idx, node_o in enumerate(tc[:-1]):
            node_d = tc[idx + 1]
            if node_d == 'd':
                Y = Y - params.e_TR
                cost += params.c_t * params.t_TR + params.c_e * params.e_TR

                Y, Y_last = params.E_k[k], params.E_k[k]
            else:
                if node_o in params.T:
                    if node_d in params.T:
                        Y = Y - params.e_TT - params.e_i[node_d]
                        cost += params.c_t * (params.t_TT + params.t_i[node_d]) + params.c_e * (
                                    params.e_TT + params.e_i[node_d])
                    else:  # node_d in R
                        Y = Y - params.e_TR
                        energy_charge = nonlinear_Charge(params, k, Y, params.t_r[node_d])
                        cost += params.c_t * params.t_TR + params.c_e * params.e_TR
                        Y = Y + energy_charge
                        Y_last = copy(Y)
                else:  # node_o in R
                    if node_o != 'o':
                        Y = Y - params.e_TT - params.e_i[node_d]
                        cost += params.c_t * (params.t_TR + params.t_i[node_d]) + params.c_e * (
                                    params.e_TR + params.e_i[node_d])
            if node_o == 'o':
                Y = Y - params.e_TT - params.e_i[node_d]
                cost += params.c_t * (params.t_TR + params.t_i[node_d]) + params.c_e * (
                            params.e_TR + params.e_i[node_d])
    cost += params.c_k[k]
    return cost

def calScheduleCost(EVSP_FCS: EVSP_FCS, schedule, is_degrade):
    params = EVSP_FCS
    cost = 0
    for idx, tc in schedule.items():
        tc_cost = caltcCost(params, tc, idx[1], is_degrade) # idx[1] is k, vehicle type
        cost += tc_cost
    return cost

### calculate r_trip
def calRTrip(schedule):
    r_trip = {}
    for tc in list(schedule.values()):
        for idx in range(len(tc)):
            if type(tc[idx]) == str:
                if len(tc[idx]) >= 2:
                    if type(tc[idx-1]) == int:
                        r_trip[tc[idx-1]] = tc[idx]
    return r_trip


##  random charging time finder

def randomChargingNode(EVSP_FCS: EVSP_FCS, i, j, k):
    params = EVSP_FCS
    chargingNode_ava = [r for r in params.R_k[k] if check_time_feasibility(params, i, r) and
                        check_time_feasibility(params, r, j)]
    if chargingNode_ava:
        r = random.choice(chargingNode_ava)
    else:
        r = None
    return r


def STgreedyChargingNode(EVSP_FCS: EVSP_FCS, schedule,  i, j, idx, char_time):
    k = idx[1]
    tripchain = schedule[idx]
    params = EVSP_FCS
    chargingNode_ava = [r for r in params.R_k[k] if check_time_feasibility(params, i, r) and
                        check_time_feasibility(params, r, j)]
    if chargingNode_ava:
        possible_R = []
        C_rest = calCapRest(params, schedule)
        for r in chargingNode_ava:
            tn_lst = params.u_r[r]
            cap_feasible = True
            for tn in tn_lst:
                if C_rest[tn]-1>=0:
                    cap_feasible = False
            if cap_feasible:
                possible_R.append(r)
        if possible_R:
            chargingNode_t = {r: params.s_r[r] for r in possible_R if params.t_r[r]==char_time} # choose shortest charging time
            if chargingNode_t:
                r = min(chargingNode_t, key=chargingNode_t.get)
            else:
                r = random.choice(chargingNode_ava)
        else:
            r = random.choice(chargingNode_ava)
    else:
        r = None

    return r


###   check time feasiblity for any two nodes
def check_time_feasibility(EVSP_FCS: EVSP_FCS, i, j):
    params = EVSP_FCS
    if i == 'o' or j == 'd':
        return True
    if i in params.T:
        if j in params.T:
            if params.s_i[i]+params.t_i[i]+params.t_TT <= params.s_i[j]:
                return True
            else:
                return False

        else:   # j in R
            if params.s_i[i]+params.t_i[i]+params.t_TR <= params.s_r[j]:
                return True
            else:
                return False
    if i in params.R:
        if j in params.T:
            if params.s_r[i]+params.t_r[i]+params.t_TR <= params.s_i[j]:
                return True
            else:
                return False
        else:   # j in R
            return False


###     check energy feasibility
def check_energy_feasibility(evep_ccs: EVSP_FCS, schedule):
    params = evep_ccs
    Y_idx = {}
    feasibility = True
    for num, tc in schedule.items():
        Y = copy(params.E_k[num[1]])
        for idx, node_o in enumerate(tc[:-1]):
            node_d = tc[idx+1]
            if node_o == 'o' or node_d == 'd':
                Y = Y - params.e_ij[(node_o, node_d)] - params.e_i[node_d]
            else:
                if node_o in params.T:
                    if node_d in params.T:
                        Y = Y - params.e_ij[(node_o, node_d)] - params.e_i[node_d]
                    else:   # node_d in R
                        Y = Y - params.e_ij[(node_o, node_d)]
                        energy_charge = nonlinear_Charge(params, num[1], Y, params.t_r[node_d])
                        Y = Y + energy_charge
                else:   # node_o in R
                    Y = Y - params.e_ij[(node_o, node_d)] - params.e_i[node_d]
            if Y < params.alpha*params.E_k[num[1]] or Y > params.E_k[num[1]]:
                feasibility = False
        Y_idx[num] = Y  # store the last battery of every tc

    return feasibility, Y_idx


###     check capacity feasibility
def check_capacity_feasibility(EVSP_FCS: EVSP_FCS, schedule):
    params = EVSP_FCS
    C_tn = deepcopy(params.C_tn)
    for num, tc in schedule.items():
        for node in tc:
            if type(node) == str:
                if len(node) >= 2:
                    for tn in params.u_r[node]:
                        C_tn[tn] = C_tn[tn] - 1
                        if C_tn[tn] < 0:
                            return False
    return True


###     calculate cost of schedule
def calCost(EVSP_FCS: EVSP_FCS, schedule, Y):
    params = EVSP_FCS
    cost = 0
    for num, tc in schedule.items():
        cost += params.c_k[num[1]]
        for idx, node_o in enumerate(tc[:-1]):
            node_d = tc[idx + 1]
            if node_d == 'd':
                cost += params.c_t*params.t_ij[(node_o, node_d)]
            else:
                if node_o in params.T or node_o == 'o':
                    if node_d in params.T:
                        cost += params.c_t*(params.t_ij[(node_o, node_d)] + params.t_i[node_d])
                    else:  # node_d in R
                        cost +=  params.c_t*params.t_ij[(node_o, node_d)] +params.c_e*params.e_r[node_d]
                else:  # node_o in R
                    cost += params.c_t * (params.t_ij[(node_o, node_d)] + params.t_i[node_d])
        cost += params.c_e*(params.E_k[num[1]]-Y[num])
    return cost


###     calculate rest capacity
def calCapRest(EVSP_FCS: EVSP_FCS, schedule):
    params = EVSP_FCS
    C_rest = copy(params.C_tn)
    for tc in list(schedule.values()):
        for node in tc:
            if type(node) == str:
                if len(node) >= 2:
                    for tn in params.u_r[node]:
                        C_rest[tn] = C_rest[tn] - 1
    return C_rest


###     find best vehicle type to replace
def findBestVehType(EVSP_FCS: EVSP_FCS, schedule):
    params = EVSP_FCS
    new_schedule = {}
    for num, tc in schedule.items():
        k_feasible = []
        for k in params.K:
            isfeasible, Y = check_energy_feasibility(params, {(num[0], k): tc})
            if isfeasible:
                k_feasible.append(k)
        if k_feasible:
            new_schedule[(num[0], min(k_feasible))] = tc
        else:
            new_schedule[num] = tc
    return new_schedule


def checkVehType(EVSP_FCS: EVSP_FCS, schedule):
    vehtype_num = {k: 0 for k in EVSP_FCS.K}
    for idx in list(schedule.keys()):
        vehtype_num[idx[1]] += 1
    return vehtype_num


def split_T_byVehType(evsp: EVSP_FCS, schedule):
    T_veh_min = []
    T_veh_other = []
    k_min = min(evsp.K)
    for idx, tc in schedule.items():
        if idx[1] == k_min:
            for node in tc:
                if type(node) == int:
                    T_veh_min.append(node)
        else:
            for node in tc:
                if type(node) == int:
                    T_veh_other.append(node)
    return T_veh_min, T_veh_other


def nonlinear_Charge(evsp, k, y0, t0):
    params = evsp
    if y0 <= 0 or y0 >= 100:
        return params.v_k*t0
    else:
        E = copy(params.E_k[k])
        a_b = copy(params.a_kb[k])
        c_b = copy(params.c_kb[k])
        B = copy(params.B_k[k])
        a0 = y0/E
        # if a0 in a_b:
        #     c0 = [c_b[i] for i in B if a_b[i] == a0][0]  # origin time
        # else:
        rate = [(a_b[i + 1] - a_b[i]) / (c_b[i + 1] - c_b[i]) for i in B[:-1]]
        interval = [i for i in B[:-1] if a_b[i] <= a0 < a_b[i + 1]][0]
        c0 = (a0 - a_b[interval]) / rate[interval] + c_b[interval]
        c1 = c0 + t0
        interval = [i for i in B[:-1] if c_b[i] <= c1 < c_b[i + 1]]
        if interval:
            interval = interval[0]
            a1 = (c1 - c_b[interval]) * rate[interval] + a_b[interval]
            charged_ene = (a1 - a0) * E
            return charged_ene
        else:
            if c1 == c_b[-1]:
                return E
            else:
                return E+1

def calDegradation(evsp: EVSP_FCS, k, Y_tc):
    params = evsp
    degradation = 0
    for idx, y_o in enumerate(Y_tc[:-1]):
        y_o = y_o/params.E_k[k]
        y_d = Y_tc[idx+1]/params.E_k[k]
        #   y variation
        y_var = (y_d - y_o)/2
        y_var = abs(y_var)
        #   y average
        y_ave = (y_d + y_o)/2
        gamma = params.a1*y_var*math.exp(params.a2*y_ave) + params.a3*math.exp(params.a4*y_var)
        deg_y = gamma*y_var*2/params.zeta
        degradation += float(deg_y)
    Y_last = Y_tc[-1]
    y_var = (1-Y_last/params.E_k[k])/2
    y_ave = (1+Y_last/params.E_k[k])/2
    gamma = params.a1*y_var*math.exp(params.a2*y_ave) + params.a3*math.exp(params.a4*y_var)
    deg_y = gamma*y_var*2/params.zeta
    degradation += float(deg_y)

    battery_deg_daily = degradation*params.c_b[k]

    return battery_deg_daily

def WDF(x, params, k):
    return (params.c_b[k]*params.b*((1-x)**(params.b-1)))/(2*params.E_k[k]*(params.u**2)*params.a)


def calBatDeg(SOC_lower, SOC_upper, params, k):
    try:
        value, err = integrate.quad(WDF, SOC_lower, SOC_upper, args=(params, k))
    except:
        value = 0
    return value


