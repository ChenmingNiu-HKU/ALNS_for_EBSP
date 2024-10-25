from initial_solution import Initialize
from evsp_fcs import EVSP_FCS
from alns_evsp_fcs import ALNS_EVSP_FCS
import pandas as pd




if __name__ == '__main__':
    # capacity = 10   # define your own charging station capacity
    timetable_name = input('Your own timetable name (not include .csv): ')
    capacity = input('Specify the charging station capacity: ')
    timetable = pd.read_csv(f'timetable/{timetable_name}.csv')
    params = EVSP_FCS(timetable=timetable, capacity=int(capacity))
    init_schedule, init_r_trip = Initialize(params)
    solver = ALNS_EVSP_FCS(params, is_degrade=True) # choose if you wanna calculate battery degradation
    cost, schedule, historyBestCost, historyCurrentCost = solver.solve(init_schedule, init_r_trip)


