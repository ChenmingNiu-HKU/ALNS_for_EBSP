from calculationFuncs import *



def random_insert(evsp_ccs: EVSP_FCS, tripBank: list, schedule, enePenalty, capPenalty, chargeProb, is_degrade):
    '''
    insert trip and charging node randomly
    1. select a trip randomly
    2. insert it to a random position
    3. insert a charging node behind it randomly
    4. if infeasible, add a penalty to it
    '''

    #   initialize params and variables
    params = evsp_ccs
    new_schedule = copy(schedule)
    tripPool = copy(tripBank)



    #  insert trips
    while tripPool: # not empty
        trip, tc_idx, pos = randomPos(params, tripPool, new_schedule)
        if pos == -1:   # no position to insert
            kran = random.choice(params.K)
            tc = ['o', trip, 'd']
            idx_lst_schedule = list(new_schedule.keys())[-1][0] # last index of schedule
            new_schedule[(idx_lst_schedule+1, kran)] = tc
        else:

            new_schedule[tc_idx].insert(pos, trip)
            #   insert charging node randomly
            if chargeProb >= random.uniform(0, 1):
                trip_d = new_schedule[tc_idx][pos+1]
                r = randomChargingNode(params, trip, trip_d, tc_idx[1])
                if r == None:
                    pass
                else:
                    new_schedule[tc_idx].insert(pos+1, r)
        tripPool.remove(trip)


    #   remove charging node before 'd'
    for num, tc in new_schedule.items():
        sec_lst_node = tc[-2]
        if type(sec_lst_node) == str:
            if len(sec_lst_node) >= 2:
                new_schedule[num].remove(sec_lst_node)

    #   calculate cost
    eneFeasible, Y_idx = check_energy_feasibility(params, new_schedule)
    capFeasible = check_capacity_feasibility(params, new_schedule)
    new_cost = calScheduleCost(params, new_schedule, is_degrade)
    if not eneFeasible:
        new_cost += enePenalty
    if not capFeasible:
        new_cost += capPenalty
    isFeasible = eneFeasible and capFeasible

    return new_cost, new_schedule, isFeasible


def greedy_insert_1(evsp_ccs: EVSP_FCS, tripBank: list, schedule, enePenalty, capPenalty, chargeProb, is_degrade):
    '''
    insert trip and charging node randomly
    1. select a trip randomly
    2. insert it to a random position
    3. insert a charging node behind it randomly
    4. if infeasible, add a penalty to it
    '''

    #   initialize params and variables
    params = evsp_ccs
    new_schedule = copy(schedule)
    tripPool = copy(tripBank)



    #  insert trips
    while tripPool: # not empty
        trip, tc_idx, pos = randomPos(params, tripPool, new_schedule)

        if pos == -1:   # no position to insert
            kran = random.choice(params.K)
            tc = ['o', trip, 'd']
            idx_lst_schedule = list(new_schedule.keys())[-1][0] # last index of schedule
            new_schedule[(idx_lst_schedule+1, kran)] = tc
        else:

            new_schedule[tc_idx].insert(pos, trip)
            #   insert charging node randomly
            if chargeProb >= random.uniform(0, 1):
                trip_d = new_schedule[tc_idx][pos+1]
                r = STgreedyChargingNode(params, new_schedule, trip, trip_d, tc_idx, 10)
                if r == None:
                    pass
                else:
                    new_schedule[tc_idx].insert(pos+1, r)
        tripPool.remove(trip)


    #   remove charging node before 'd'
    for num, tc in new_schedule.items():
        sec_lst_node = tc[-2]
        if type(sec_lst_node) == str:
            if len(sec_lst_node) >= 2:
                new_schedule[num].remove(sec_lst_node)
    # optimize vehicle type
    new_schedule = findBestVehType(params, new_schedule)

    #   calculate cost
    eneFeasible, Y_idx = check_energy_feasibility(params, new_schedule)
    capFeasible = check_capacity_feasibility(params, new_schedule)
    new_cost = calScheduleCost(params, new_schedule, is_degrade)
    if not eneFeasible:
        new_cost += enePenalty
    if not capFeasible:
        new_cost += capPenalty
    isFeasible = eneFeasible and capFeasible

    return new_cost, new_schedule, isFeasible


def greedy_insert_2(evsp_ccs: EVSP_FCS, tripBank: list, schedule, enePenalty, capPenalty, chargeProb, is_degrade):
    '''
    insert trip and charging node randomly
    1. select a trip randomly
    2. insert it to a random position
    3. insert a charging node behind it randomly
    4. if infeasible, add a penalty to it
    '''

    #   initialize params and variables
    params = evsp_ccs
    new_schedule = copy(schedule)
    tripPool = copy(tripBank)



    #  insert trips
    while tripPool: # not empty
        trip, tc_idx, pos = randomPos(params, tripPool, new_schedule)

        if pos == -1:   # no position to insert
            kran = random.choice(params.K)
            tc = ['o', trip, 'd']
            idx_lst_schedule = list(new_schedule.keys())[-1][0] # last index of schedule
            new_schedule[(idx_lst_schedule+1, kran)] = tc
        else:

            new_schedule[tc_idx].insert(pos, trip)
            #   insert charging node randomly
            if chargeProb >= random.uniform(0, 1):
                trip_d = new_schedule[tc_idx][pos+1]
                r = STgreedyChargingNode(params, new_schedule, trip, trip_d, tc_idx, 20)
                if r == None:
                    pass
                else:
                    new_schedule[tc_idx].insert(pos+1, r)
        tripPool.remove(trip)


    #   remove charging node before 'd'
    for num, tc in new_schedule.items():
        sec_lst_node = tc[-2]
        if type(sec_lst_node) == str:
            if len(sec_lst_node) >= 2:
                new_schedule[num].remove(sec_lst_node)
    # optimize vehicle type
    new_schedule = findBestVehType(params, new_schedule)

    #   calculate cost
    eneFeasible, Y_idx = check_energy_feasibility(params, new_schedule)
    capFeasible = check_capacity_feasibility(params, new_schedule)
    new_cost = calScheduleCost(params, new_schedule, is_degrade)
    if not eneFeasible:
        new_cost += enePenalty
    if not capFeasible:
        new_cost += capPenalty
    isFeasible = eneFeasible and capFeasible

    return new_cost, new_schedule, isFeasible


def greedy_insert_3(evsp_ccs: EVSP_FCS, tripBank: list, schedule, enePenalty, capPenalty, chargeProb, is_degrade):
    '''
    insert trip and charging node randomly
    1. select a trip randomly
    2. insert it to a random position
    3. insert a charging node behind it randomly
    4. if infeasible, add a penalty to it
    '''

    #   initialize params and variables
    params = evsp_ccs
    new_schedule = copy(schedule)
    tripPool = copy(tripBank)



    #  insert trips
    while tripPool: # not empty
        trip, tc_idx, pos = randomPos(params, tripPool, new_schedule)

        if pos == -1:   # no position to insert
            kran = random.choice(params.K)
            tc = ['o', trip, 'd']
            idx_lst_schedule = list(new_schedule.keys())[-1][0] # last index of schedule
            new_schedule[(idx_lst_schedule+1, kran)] = tc
        else:

            new_schedule[tc_idx].insert(pos, trip)
            #   insert charging node randomly
            if chargeProb >= random.uniform(0, 1):
                trip_d = new_schedule[tc_idx][pos+1]
                r = STgreedyChargingNode(params, new_schedule, trip, trip_d, tc_idx, 30)
                if r == None:
                    pass
                else:
                    new_schedule[tc_idx].insert(pos+1, r)
        tripPool.remove(trip)


    #   remove charging node before 'd'
    for num, tc in new_schedule.items():
        sec_lst_node = tc[-2]
        if type(sec_lst_node) == str:
            if len(sec_lst_node) >= 2:
                new_schedule[num].remove(sec_lst_node)
    # optimize vehicle type
    new_schedule = findBestVehType(params, new_schedule)

    #   calculate cost
    eneFeasible, Y_idx = check_energy_feasibility(params, new_schedule)
    capFeasible = check_capacity_feasibility(params, new_schedule)
    new_cost = calScheduleCost(params, new_schedule, is_degrade)
    if not eneFeasible:
        new_cost += enePenalty
    if not capFeasible:
        new_cost += capPenalty
    isFeasible = eneFeasible and capFeasible

    return new_cost, new_schedule, isFeasible


def greedy_insert_4(evsp_ccs: EVSP_FCS, tripBank: list, schedule, enePenalty, capPenalty, chargeProb, is_degrade):
    '''
    insert trip and charging node randomly
    1. select a trip randomly
    2. insert it to a random position
    3. insert a charging node behind it randomly
    4. if infeasible, add a penalty to it
    '''

    #   initialize params and variables
    params = evsp_ccs
    new_schedule = copy(schedule)
    tripPool = copy(tripBank)



    #  insert trips
    while tripPool: # not empty
        trip, tc_idx, pos = randomPos(params, tripPool, new_schedule)

        if pos == -1:   # no position to insert
            kran = random.choice(params.K)
            tc = ['o', trip, 'd']
            idx_lst_schedule = list(new_schedule.keys())[-1][0] # last index of schedule
            new_schedule[(idx_lst_schedule+1, kran)] = tc
        else:

            new_schedule[tc_idx].insert(pos, trip)
            #   insert charging node randomly
            if chargeProb >= random.uniform(0, 1):
                trip_d = new_schedule[tc_idx][pos+1]
                r = STgreedyChargingNode(params, new_schedule, trip, trip_d, tc_idx, 40)
                if r == None:
                    pass
                else:
                    new_schedule[tc_idx].insert(pos+1, r)
        tripPool.remove(trip)


    #   remove charging node before 'd'
    for num, tc in new_schedule.items():
        sec_lst_node = tc[-2]
        if type(sec_lst_node) == str:
            if len(sec_lst_node) >= 2:
                new_schedule[num].remove(sec_lst_node)
    # optimize vehicle type
    new_schedule = findBestVehType(params, new_schedule)

    #   calculate cost
    eneFeasible, Y_idx = check_energy_feasibility(params, new_schedule)
    capFeasible = check_capacity_feasibility(params, new_schedule)
    new_cost = calScheduleCost(params, new_schedule, is_degrade)
    if not eneFeasible:
        new_cost += enePenalty
    if not capFeasible:
        new_cost += capPenalty
    isFeasible = eneFeasible and capFeasible

    return new_cost, new_schedule, isFeasible

def greedy_insert_5(evsp_ccs: EVSP_FCS, tripBank: list, schedule, enePenalty, capPenalty, chargeProb, is_degrade):
    '''
    insert trip and charging node randomly
    1. select a trip randomly
    2. insert it to a random position
    3. insert a charging node behind it randomly
    4. if infeasible, add a penalty to it
    '''

    #   initialize params and variables
    params = evsp_ccs
    new_schedule = copy(schedule)
    tripPool = copy(tripBank)



    #  insert trips
    while tripPool: # not empty
        trip, tc_idx, pos = randomPos(params, tripPool, new_schedule)

        if pos == -1:   # no position to insert
            kran = random.choice(params.K)
            tc = ['o', trip, 'd']
            idx_lst_schedule = list(new_schedule.keys())[-1][0] # last index of schedule
            new_schedule[(idx_lst_schedule+1, kran)] = tc
        else:

            new_schedule[tc_idx].insert(pos, trip)
            #   insert charging node randomly
            if chargeProb >= random.uniform(0, 1):
                trip_d = new_schedule[tc_idx][pos+1]
                r = STgreedyChargingNode(params, new_schedule, trip, trip_d, tc_idx, 50)
                if r == None:
                    pass
                else:
                    new_schedule[tc_idx].insert(pos+1, r)
        tripPool.remove(trip)


    #   remove charging node before 'd'
    for num, tc in new_schedule.items():
        sec_lst_node = tc[-2]
        if type(sec_lst_node) == str:
            if len(sec_lst_node) >= 2:
                new_schedule[num].remove(sec_lst_node)
    # optimize vehicle type
    new_schedule = findBestVehType(params, new_schedule)

    #   calculate cost
    eneFeasible, Y_idx = check_energy_feasibility(params, new_schedule)
    capFeasible = check_capacity_feasibility(params, new_schedule)
    new_cost = calScheduleCost(params, new_schedule, is_degrade)
    if not eneFeasible:
        new_cost += enePenalty
    if not capFeasible:
        new_cost += capPenalty
    isFeasible = eneFeasible and capFeasible

    return new_cost, new_schedule, isFeasible