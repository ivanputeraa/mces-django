import os
import pandas as pd
import numpy as np 
def ShowResult(ProcessedPath,ReportPath): 
    MachineColumns = []
    df = pd.read_csv(ProcessedPath, encoding='big5')
    Lot = df['Lot'].values.copy()
    Final = df['Final'].values.copy()
    TotalNum = df['TotalNum'].values.copy()
    CurrentNum = df['CurrentTotalNum'].values.copy()
    BadNum = df['BadNum'].values.copy()
    RealBad = 0
    for data in BadNum:
        RealBad += data
    for column in df:
        if column.find("MachineNo") != -1:
            MachineColumns.append(column)
    FinalIdx = np.argwhere(Final == -1).ravel()
    RF = pd.read_csv(ReportPath, encoding='big5')
    RFMachine = RF['Machine'].values.copy()
    RFYieldRate = RF['YieldRate'].values.copy()
    MachineYieldRateDict = {}
    for i in range(0, len(RFMachine)):
        Machine = RFMachine[i].split(":")
        MachineYieldRateDict[Machine[1]] = RFYieldRate[i]
    print(MachineYieldRateDict)
    BadPiecesDict = {}
    count = 0
    error = 0
    allsum = 0
    allTotal = 0
    errorRate = 0
    for finalIndex in FinalIdx:
        totalInLot = TotalNum[finalIndex]
        yeildRate = []
        tempLotname = Lot[finalIndex]
        MaxStep = 0
        Badpieces = 0
        for column in MachineColumns:
            tempMachine = str(df[column][finalIndex])
            if (tempMachine != "nan"):
                MaxStep += 1
        for column in MachineColumns:
            tempMachine = str(df[column][finalIndex])
            if (tempMachine != "nan"):
                yeildRate.append(MachineYieldRateDict[tempMachine])
                badpiecesInThisStep = totalInLot
                for yeildIndex in range(0, len(yeildRate)):
                    if (yeildIndex == len(yeildRate) - 1):  # last
                        badpiecesInThisStep = badpiecesInThisStep * float(1 - yeildRate[yeildIndex])
                        Badpieces += badpiecesInThisStep
                    else:  #
                        badpiecesInThisStep = badpiecesInThisStep * float(yeildRate[yeildIndex])
        allTotal += TotalNum[finalIndex]
        print("lotName:", tempLotname, "totalNum:", TotalNum[finalIndex], "EMBadPieces",
              Badpieces, "RealBadPieces", (TotalNum[finalIndex] - (CurrentNum[finalIndex] - BadNum[finalIndex])))
        error += (abs(Badpieces - (TotalNum[finalIndex] - (CurrentNum[finalIndex] - BadNum[finalIndex]))))
        errorRate += (abs(Badpieces - (TotalNum[finalIndex] - (CurrentNum[finalIndex] - BadNum[finalIndex])))) / TotalNum[finalIndex]
        allsum += 1
        # if(abs(badpieces-(totalNum[finalIndex] - goodNum[finalIndex]))>7):
        #     error +=1
        BadPiecesDict[tempLotname] = Badpieces
        count += 1
 
    TotalBad = 0
    for key in BadPiecesDict:
        TotalBad += BadPiecesDict[key] 
    print("allTotalBad", TotalBad, "realTotalBad", RealBad, error / count, RealBad / count, allTotal / count)
    print("ErrorRate", errorRate / count,"LotNumber",count)
    
    
ProcessedPath = os.getcwd()+"\\ProcessedData\\05_21_2018_05_27_2018_ProcessedDataByPanelNotSplit.csv"
ReportPath = os.getcwd()+"\\Report\\05_21_2018_05_27_2018_ReportByCellNotSplit.csv"
ShowResult(ProcessedPath,ReportPath)