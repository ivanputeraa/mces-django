# -*- coding: utf-8 -*-
"""
Created on Sat Oct 21 20:34:15 2017
@author: Prof. Chang and Dr.Ho
""" 
import numpy as np 
import pandas as pd
import scipy.stats
import scipy.optimize
import time

np.set_printoptions(suppress=True)

def micro_crack_esimator(datafile,ReportPath):
    print("Start ReadCSV", time.time())
    df = pd.read_csv(datafile, encoding='big5')
    df.sort_values(by=['Lot', 'Final'], inplace=True)
    n = df.shape[0]
    lot_name                  = df['Lot'].values.copy()
    current_total_piece               = df['CurrentTotalNum'].values.copy()
    total_piece       = df['TotalNum'].values.copy()
    ng_piece = df['BadNum'].values.copy()
    final = df['Final'].values.copy()
    final_idx                 = np.argwhere(final==-1).ravel()             # final_idx represents a serious number of last station  [-1  1  2  3 -1  1  2  3]  找出現-1下標的地方  [0 4]
    notfinal_idx              = np.argwhere(final!=-1).ravel()
    current_total_piece[notfinal_idx] = ng_piece[notfinal_idx]
    lot_begin = [];lot_end = []
    number_of_lot = len(final_idx) 
    for i in range (0, number_of_lot):#根据-1作为起始下标寻找一个lot数据段 
        lot_begin.append(final_idx[i]) 
    for i in range (0, number_of_lot-1):#排除第一个lot，即将下一个lot开始作为上一个的结束 
        lot_end.append(final_idx[i+1])
    lot_end.append(n)#最后一个lot   
    #grpary_badpiece  
    grpary_badpiece = [] 
    for i in range (0, number_of_lot):           #分割坏片對應的數量以及總數量
       a = lot_begin[i]
       b = lot_end[i]
       grp_badpiece = ng_piece[a:b]
       grpary_badpiece.append(grp_badpiece) 
    raw_data_lot_yieldrate_tmp = [];raw_data_lot_yieldrate = [] 
    for i in range(0, number_of_lot):                                 #原始數據良片生產率 [[-0.011505940186202065], [-0.00473117437590144]]
        badpieces_sum = sum(grpary_badpiece[i])                      #纍加某個個lot坏片總數   
        tmp_calculation = badpieces_sum / total_piece[lot_begin[i]]
        tmp_calculation = 1 - tmp_calculation                          #良片 
        if (tmp_calculation == 0):
            tmp_calculation = 0.001
        tmp_calculation = np.log(tmp_calculation)
        raw_data_lot_yieldrate_tmp.append(tmp_calculation)
        raw_data_lot_yieldrate.append(raw_data_lot_yieldrate_tmp)
        raw_data_lot_yieldrate_tmp = []
    Config,  same_machine, machine_name =data_process(df)
    number_of_rows, number_of_max_steps, nonzero_foot_tmp = Config_range_calculation (Config)
    Recorded_goodpiece, Transpose_of_ng_piece = Recorded_goodpiece_calculation (Config, current_total_piece, ng_piece, number_of_max_steps, nonzero_foot_tmp) 
    machine_ini_prob = ini_machine_good_production_rate_estimation (Config[final_idx,:], raw_data_lot_yieldrate)
    print("Compute", time.time())
    p, E_of_Zij = EM_process (Config, same_machine, number_of_rows, number_of_max_steps, nonzero_foot_tmp, Recorded_goodpiece, Transpose_of_ng_piece, machine_ini_prob, machine_ini_prob)
    bad_pieces_estimation_value = bad_pieces_estimation (p, E_of_Zij,number_of_max_steps,Transpose_of_ng_piece) 
    print_report (p,bad_pieces_estimation_value,machine_name,ReportPath)
def Config_range_calculation (Config): 
        number_of_rows, number_of_max_steps = Config.shape[0:2]#保留2次
        #根據Config 記錄每一列，1出現的下標
        nonzero_foot_tmp = tuple(np.argwhere(Config[i,:]).ravel() for i in range(0,number_of_rows))
        return number_of_rows, number_of_max_steps, nonzero_foot_tmp
def  Recorded_goodpiece_calculation (Config, cross_lots_with_diff_mac_total_pieces, ng_piece, number_of_max_steps, nonzero_foot_tmp):
        Recorded_goodpiece = np.zeros((number_of_max_steps,)) 
        for i,nonzero_foot in enumerate(nonzero_foot_tmp): 
            Recorded_goodpiece[nonzero_foot] += cross_lots_with_diff_mac_total_pieces[i] - ng_piece[i] 
        Transpose_of_ng_piece = ng_piece.reshape((-1,)) 
        return Recorded_goodpiece, Transpose_of_ng_piece 
def ini_machine_good_production_rate_estimation (X, y): 
        d = X.shape[1]#維度
        p = np.zeros((d,1)) #n個1維數組
        XX= X.T.dot(X)#X轉置矩陣 * X  
        Xy= X.T.dot(y)
        def __object_func(h, X, y, XX, Xy): 
            g   = (XX.dot(h.reshape(-1,1))- Xy)/2 
            val = X.dot(h.reshape(-1,1)) - y
            val*= val
            return val.sum()/2, g
        p, minv, info = scipy.optimize.fmin_l_bfgs_b(__object_func, p, None, (X, y, XX, Xy), False, [(None,0) for _ in range(0,d)]) 
        p = np.exp(p)
        return p

def  EM_process (Config, same_machine, number_of_rows, number_of_max_steps, nonzero_foot_tmp, Recorded_goodpiece, ng_piece, opt_Pmj, p):
    epsilon = 1.e-4
    E_of_Zij = np.zeros(Config.shape)
    Mj_good_expect = np.zeros((number_of_max_steps,))
    Mj_bad_expect = np.zeros((number_of_max_steps,))
    iterration_count = 0
    max_iteration = 100
    for _ in range(0, max_iteration):
        iterration_count = iterration_count + 1
        print('Iterations: ', iterration_count)
        p = np.where(p <= 0, 1e-8, p)
        logp = np.log(p) 
        for idx, nonzero_foot in enumerate(nonzero_foot_tmp):
            _E_of_Zij = np.zeros((nonzero_foot.size,))
            if ng_piece[idx] > 0:
                for i in range(_E_of_Zij.size): 
                    _E_of_Zij[i] = np.exp(logp[nonzero_foot[0:i]].ravel().sum()) * (1 - p[nonzero_foot[i]]) + epsilon
                E_of_Zij[idx, nonzero_foot] = _E_of_Zij / _E_of_Zij.sum()
        # print(E_of_Zij)
        # M-Step Begin
        Non_zero_EZij_expectation_value = E_of_Zij.copy()
        for j in range(0, number_of_max_steps):
            Non_zero_EZij_expectation_value[:, j] *= ng_piece
            jth = j + 1
            # sum of each machine bad piece expectation value within a same lot
        bad_pieces_expect = np.sum(Non_zero_EZij_expectation_value, axis=0)
        # print('')
        good_pieces_expect = np.zeros((number_of_rows, number_of_max_steps))
        for j in range(number_of_max_steps - 2, -1, -1):
            good_pieces_expect[:, j] = good_pieces_expect[:, j + 1] + Non_zero_EZij_expectation_value[:, j + 1]
        # To pick up machine, which element = 1 within Config 
        good_pieces_expect = good_pieces_expect * Config
        # print (good_pieces_expect)
        # To calculate good and bad piece of Machine j
        # To apply PMj formula start 
        for j in range(0, number_of_max_steps):
            sum_of_good_pieces_expect = good_pieces_expect[:, j].sum()
            Mj_good_expect[j] = good_pieces_expect[:, j].sum() + Recorded_goodpiece[j]
            Mj_bad_expect[j] = bad_pieces_expect[j]
        # If Loop Process is selected, the same_machine would be diff than good and bad piece of Machine j
        for mid in same_machine:
            sum_of_Mj_good_exp, sum_of_Mj_bad_exp = 0, 0
            for j in mid:
                sum_of_Mj_good_exp += Mj_good_expect[j]
                sum_of_Mj_bad_exp += Mj_bad_expect[j]
            # To form a new good production rate of machine aspect
            p[mid] = sum_of_Mj_good_exp / (sum_of_Mj_good_exp + sum_of_Mj_bad_exp)
            # To apply PMj formula end 
        toler = 1.e-6
        if np.linalg.norm(opt_Pmj - p) <= toler:
            break
        opt_Pmj[:] = p
    return p, E_of_Zij
def  bad_pieces_estimation (p, E_of_Zij,number_of_max_steps, ng_piece):
        bad_pieces_estimation_value = np.zeros((number_of_max_steps,)) 
        for j in range(0,number_of_max_steps): 
            bad_pieces_estimation_value [j] = (E_of_Zij[:,j].ravel() * ng_piece.ravel()).sum()
        return bad_pieces_estimation_value
def  print_report (p,bad_pieces_estimation_value,machine_name,ReportPath='bad_pieces_report.csv'):
        # To sort the original data
        order = np.argsort(p.ravel()) 
        # print output grid head
        # print('%10s %9s %s'%('YieldRate','BadPiece','Machine'))
        # To print all piese
        with open(ReportPath, 'w') as file_output:
         file_output.write('YieldRate,BadPiece,Machine\n')
         for i in range(0,p.size):
            # print('   %.5f %.3f %s'%(p[order[i]],bad_pieces_estimation_value[order[i]],machine_name[order[i]]))
            file_output.write('%.6f'%(p[order[i]]))
            file_output.write(',')
            file_output.write('%.3f'%(bad_pieces_estimation_value[order[i]]))
            file_output.write(',')
            file_output.write('%s'%(machine_name[order[i]]))
            file_output.write('\n')
        return
def get_onehot_list(total, current, not_nan=True):
    list=[]
    for i in range(total):
        if i ==current:
            if not_nan==True:
                list.append(1)
            else:
                list.append(0)
        else:
            list.append(0)
    return list 
def data_process(df):
    columns = []
    same_machine = []
    machine_columns = []
    Config_list = []
    machine_name = {}
    machine_index = 0
    Process_Machine_count_no_nan = []
    for column in df:
        if column.find("UserID") == -1 and column.find("QTime") == -1:  # 過濾掉
            columns.append(column)
        if column.find("MachineNo") != -1:
            machine_columns.append(column)
            # 統計各個Process出現的機器
    for machine_column in machine_columns:
        temp_dict = {}
        for used_machine in df[machine_column]:
            temp_dict[str(used_machine)] = 1
        no_nan_index = 0
        for key in temp_dict:
            if key != "nan":
                machine_name[machine_index] = machine_column + ":" + key
                machine_index += 1
                no_nan_index += 1
        Process_Machine_count_no_nan.append(no_nan_index)
    sum_step = len(df["Lot"])
    for i in range(sum_step):
        Config_list.append([])
    process_index = 0
    current_process_used_machine_num = 0
    all_machine_count = 0
    for machine_column in machine_columns:
        current_process_used_machine_num = Process_Machine_count_no_nan[process_index]
        all_machine_count += current_process_used_machine_num
        this_process_machine = []  # 這個過程中用到的機器
        for i in range(all_machine_count - current_process_used_machine_num, all_machine_count):
            this_process_machine.append(machine_name[i].split(":")[1])
        temp_index = 0
        for used_machine in df[machine_column]:
            in_this_process_machine_index = 0
            not_nan = True
            if used_machine in this_process_machine:  # 非空
                in_this_process_machine_index = this_process_machine.index(used_machine)
            else:
                not_nan = False
            Config_list[temp_index] = Config_list[temp_index] + get_onehot_list(
                current_process_used_machine_num, in_this_process_machine_index, not_nan)
            temp_index += 1
        process_index += 1
    Config = np.array(Config_list, dtype=np.float)
    for key1 in machine_name:
        sameid = []
        temp_machine = machine_name[key1].split(":")[1]
        for key2 in machine_name:
            if temp_machine in machine_name[key2]:
                sameid.append(key2)
        same_machine.append(np.array(sameid))
    return Config,same_machine,machine_name
if __name__ == "__main__":
    micro_crack_esimator('08_06_2018_08_12_2018_ProcessedData.csv',ReportPath='bad_pieces_report.csv')