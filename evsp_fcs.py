import pandas as pd

'''
@ author: Chenming Niu
'''

class EVSP_FCS():
    """
    EVSP_CCS is a params class for electric vehicle scheduling problem
    considering charging strategy where charging time is a flexible variable;
    input params include timetables, time steps, battery safety level,
    and recharging station capacity
    """
    __slots__ = ['timetable', 'T', 'K', 'E_k', 'v_k', 'D', 'R', 'R_k',
                 'TN', 'u_r', 'v_p_1',
                 's_i', 's_r', 't_i', 't_r', 'e_i', 'e_r',
                 'A_k', 't_ij', 'e_ij',
                 't_TT', 't_TR', 'e_TT', 'e_TR',
                 'c_e', 'c_t', 'c_k', 'c_b', 'lf', 'zeta',
                 'a1', 'a2', 'a3', 'a4',
                 'beta', 'C', 'C_tn', 'alpha',
                 'u', 'b', 'a',
                 'c_kb', 'a_kb', 'm_k', 'B_k']

    def __init__(self,
                 timetable: pd.DataFrame,
                 alpha=0.2, # battery safety level
                 beta=10,   # time steps
                 capacity=10,    # recharging station capacity
                 char_time_max = 12):
        self.timetable = timetable
        #   trip node
        self.T = list(range(1, self.timetable.shape[0]+1))
        #   vehicle type
        self.K = [1, 2, 3]
        #   vehicle info
        self.E_k = {1: 100, 2: 170, 3: 258} # battery capacity
        self.v_k = 1   # charging rate, constant for 3 vehicle types
        #   depot nodes
        self.D = ['o', 'd']

        #   nonlinear charge function
        self.c_kb = {1: [0, 57.5, 70, 100], 2: [0, 97.7, 119, 170], 3: [0, 148, 180, 258]} # time break points
        self.a_kb = {1:[0.0, 0.88, 0.93, 1.0], 2:[0.0, 0.88, 0.93, 1.0], 3: [0.0, 0.88, 0.93, 1.0]}  # SOC for break points
        self.m_k = {1: len(self.c_kb[1]), 2: len(self.c_kb[2]), 3: len(self.c_kb[3])}   # number of break points
        self.B_k = {k:list(range(0,self.m_k[k])) for k in self.K}   # break point set
        self.v_p_1 = 1.53   # charging rate for phase 1
        #   recharging time node: r_t_n, t refers to the start time, n represents num of basic charging time division
        self.R = [f'r_{t}_{n}' for n in range(1, int(self.c_kb[3][-1]/beta)-int(self.E_k[3]*alpha/(self.v_p_1*beta))+1)
                        for t in range(1, 1440//beta - n + 1) if n <= char_time_max]
        self.R_k = {k: [f'r_{t}_{n}' for n in range(1, int(self.c_kb[k][-1]/beta)-int(self.E_k[k]*alpha/(self.v_p_1*beta))+1)
                        for t in range(1, 1440//beta - n + 1) if n <= char_time_max] for k in self.K}
        self.TN = [t for t in range(1, 1440//beta + 1)] # time node
        self.u_r = {r: list(range(int(r.split('_')[1]), int(r.split('_')[1])+int(r.split('_')[2]))) for r in self.R}    # charging time occupancy

        #   define start time
        self.s_i = {i: self.timetable['StartTimeMin'].iloc[i-1] for i in self.T}
        self.s_i['o'], self.s_i['d'] = 0, 24*60
        self.s_r = {r: 300+(int(r.split('_')[1])-1)*beta for r in self.R}

        #   define trip travel time
        self.t_i = {i: self.timetable['TravelTimeMin'].iloc[i-1] for i in self.T}
        self.t_r = {r: int(r.split('_')[2])*beta for r in self.R}
        self.t_i['o'] = 0

        #   define trip energy consumption
        self.e_i = {i: self.timetable['Consumption'].iloc[i-1] for i in self.T} # consumption amount
        self.e_r = {r: int(r.split('_')[2])*beta*self.v_k for r in self.R}   # charging amount
        self.e_i['d'] = 0
        #   arc
        basic_A = [('o', j) for j in self.T] \
                +[(i, 'd') for i in self.T] \
                +[(i, j) for i in self.T for j in self.T
                  if self.s_i[i]+self.t_i[i]<self.s_i[j]]
        self.A_k = {k: basic_A for k in self.K}
        for k in self.K:
            max_charging_time = int(self.E_k[k]*(1-alpha)//self.v_k)    # max charging timenode
            for i in self.T:
                for r in self.R_k[k]:
                    if self.s_i[i] + self.t_i[i] < self.s_r[r]:
                        if self.t_r[r] <= max_charging_time:
                            self.A_k[k].append((i, r))
                    if self.t_r[r] <= max_charging_time:
                        self.A_k[k].append((r, 'd'))
                        if self.s_r[r] + self.t_r[r] < self.s_i[i]:
                            self.A_k[k].append((r, i))
        #   main arcs
        A_all = list(self.A_k.values())
        A_all = list(set(sum(A_all, [])))   # merge three types of arcs

        #   deadhead time
        self.t_ij = {(i, j): None for i, j in A_all}
        for i,j in A_all:
            if i == 'o':
                self.t_ij[(i, j)] = 3
            if i in self.T:
                if j in self.T:
                    self.t_ij[(i, j)] = 2
                else:   # R & 'd'
                    self.t_ij[(i, j)] = 3
            if i in self.R:
                if j in self.T:
                    self.t_ij[(i, j)] = 3
                else:   # 'd'
                    self.t_ij[(i, j)] = 0
        self.t_TT, self.t_TR = 2, 3
        #   deadhead consumption
        self.e_ij = {(i, j): None for i, j in A_all}
        for i, j in A_all:
            if i == 'o':
                self.e_ij[(i, j)] = 0.075
            if i in self.T:
                if j in self.T:
                    self.e_ij[(i, j)] = 0.05
                else:  # R & 'd'
                    self.e_ij[(i, j)] = 0.075
            if i in self.R:
                if j in self.T:
                    self.e_ij[(i, j)] = 0.075
                else:  # 'd'
                    self.e_ij[(i, j)] = 0
        self.e_TT, self.e_TR = 0.05, 0.075

        #   remove arcs that violate time compatibility
        for i, j in A_all:
            if i != 'o' and j != 'd':
                if i in self.T:
                    if j in self.T:
                        if self.s_i[i] + self.t_i[i] + self.t_ij[(i,j)] > self.s_i[j]:
                            A_all.remove((i, j))
                    else:   # j in R
                        if self.s_i[i] + self.t_i[i] + self.t_ij[(i,j)] > self.s_r[j]:
                            A_all.remove((i, j))
                else:   # i in R
                    if self.s_r[i] + self.t_r[i] + self.t_ij[(i,j)] > self.s_i[j]:
                        A_all.remove((i, j))
        for k, arcs in self.A_k.items():
            self.A_k[k] = list(set(arcs)&set(A_all))



        #   cost rate
        self.c_e = 0.6414   #   electricity cost
        self.c_t = 0.5  # labor cost
        self.c_k = {1: 488.33, 2: 530.88, 3: 585.86}    # daily cost of vehicle investment except battery
        self.c_b = {1: 84000, 2: 142800, 3: 216720}    # battery cost
        self.lf = 12*360    # life cycle time (day)
        self.zeta = 0.2 # battery replacement standard
        self.a1, self.a2, self.a3, self.a4 = -0.0004092, -2.167, 0.00001408, 6.13


        #   battery degradation params
        self.u = 0.9    #   cycle efficiency
        self.b, self.a = 0.795, 694 # battery dependent params



        #   other params
        self.beta = beta    # time steps
        self.C = capacity   # charging station capacity
        self.C_tn = {tn: self.C for tn in self.TN}
        self.alpha = alpha  # battery safety level











