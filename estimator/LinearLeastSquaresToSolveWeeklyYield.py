import os
import pandas as pd
import numpy as np
from numpy.linalg import lstsq
from estimator.models import Machine_Yield_Rate_History
import time, datetime

class AnalyseFilePathInformation(object):
    def __init__(self,ProductionProcessFilePath,ReportFilePath):
        self.ProductionProcessFilePath = ProductionProcessFilePath
        self.ReportFilePath = ReportFilePath
class Equaltion(object):
    def __init__(self,MachineProcessedPiecesInDifferentPeriodDict = {},BadYieldRate=0):
        self.MachineProcessedPiecesInDifferentPeriodDict = MachineProcessedPiecesInDifferentPeriodDict
        self.BadYieldRate = BadYieldRate
def GetAnalyseFilePathInformationList():
    # ProcessedDataDirPath = os.getcwd() + "\\ProcessedData"
    # ProcessedDataDirPath = os.getcwd() + "\\analyse\\ProcessedData"
    ProcessedDataDirPath = os.getcwd() + "/estimator/ProcessedData"
    AnalyseFilePathInformationByCellList = []
    AnalyseFilePathInformationByPanelList = []
    for Root, Dirs, Files in os.walk(ProcessedDataDirPath, topdown=False):
        for name in Files:
            Path = os.path.join(Root, name)
            if "ProcessedDataByCell.csv" in Path :
                ProductionProcessFilePath = Path
                print(ProductionProcessFilePath)
                ReportFilePath = Path.replace("ProcessedDataByCell.csv", "ReportByCellNotSplit.csv")
                ReportFilePath = ReportFilePath.replace("ProcessedData", "Report")
                AnalyseFilePathInformationByCellList.append(AnalyseFilePathInformation(ProductionProcessFilePath, ReportFilePath))
            elif "ProcessedDataByPanel.csv" in Path :
                ProductionProcessFilePath = Path
                ReportFilePath = Path.replace("ProcessedDataByPanel.csv", "ReportByPanelNotSplit.csv")
                ReportFilePath = ReportFilePath.replace("ProcessedData", "Report")
                AnalyseFilePathInformationByPanelList.append(AnalyseFilePathInformation(ProductionProcessFilePath, ReportFilePath))
    return AnalyseFilePathInformationByCellList,AnalyseFilePathInformationByPanelList
#Get ALl Machine 
def GetAllMachineFromReport(AnalyseFilePathInformationList):
    AllMachineDict = {}
    for AnalyseFilePathInfo in AnalyseFilePathInformationList:
        ReportDataFlow = pd.read_csv(AnalyseFilePathInfo.ReportFilePath, encoding='big5')
        MachineNameList = ReportDataFlow['Machine'].values.copy()
        for MachineName in MachineNameList:
            MachineNameArray = MachineName.split(":")
            AllMachineDict[MachineNameArray[1]] = 1
    return AllMachineDict

def GetMachineProcessedPiecesInDifferentPeriodDict(Machine, AnalyseFilePathInformationList):
    MachineProcessedPiecesInDifferentPeriodDict = {}
    BadPiecesByEMAve = 0
    for AnalyseFilePathInfo in AnalyseFilePathInformationList:
        ReportDataFlow = pd.read_csv(AnalyseFilePathInfo.ReportFilePath, encoding='big5')
        ProductionProcessDataFlow = pd.read_csv(AnalyseFilePathInfo.ProductionProcessFilePath, encoding='big5')
        #Get Last Station Index
        StationList = ProductionProcessDataFlow['Final'].values.copy()
        CurrentTotalNumList = ProductionProcessDataFlow['CurrentTotalNum'].values.copy()
        FinalStationIndexList = np.argwhere(StationList == -1).ravel()
        #Get Csv Column
        MachineColumnList = []
        for column in ProductionProcessDataFlow:
            if column.find("MachineNo") != -1:
                MachineColumnList.append(column)
                #search the pieces of the machine processed in different period (Coefficient) number 1 * badRate1 +  number 2* badRate2 = (number1+2)*badRateave
        CurrentMachineProcessedPiecesInDifferentPeriodDict = {}
        for FinalStationIndex in FinalStationIndexList:
            MachineInDifferentPeriod = ""
            StationNumber = 0
            StationNumberOfMachineInProcessed = 0
            IndexOfMachineInProcessed = 0
            for Column in MachineColumnList:
                MachineName = str(ProductionProcessDataFlow[Column][FinalStationIndex])
                if (MachineName != "nan"):
                    StationNumber += 1
                    if Machine in MachineName:
                        MachineInDifferentPeriod = MachineName
                        StationNumberOfMachineInProcessed = StationNumber
                        IndexOfMachineInProcessed = FinalStationIndex
                else:
                    break
            #Record Machine Processed Pieces 
            if StationNumberOfMachineInProcessed!=0 and IndexOfMachineInProcessed!=0:
                BackIndex = StationNumber - StationNumberOfMachineInProcessed
                if MachineInDifferentPeriod not in CurrentMachineProcessedPiecesInDifferentPeriodDict:
                    CurrentMachineProcessedPiecesInDifferentPeriodDict[MachineInDifferentPeriod] = CurrentTotalNumList[IndexOfMachineInProcessed-BackIndex]
                else:
                    CurrentMachineProcessedPiecesInDifferentPeriodDict[MachineInDifferentPeriod] += CurrentTotalNumList[IndexOfMachineInProcessed-BackIndex]
        # Result : (number1+2)*badRateave
        if len(CurrentMachineProcessedPiecesInDifferentPeriodDict)>0:
            BadYield = 0
            YieldList = ReportDataFlow['YieldRate'].values.copy()
            MachineList = ReportDataFlow['Machine'].values.copy()
            for index in range(0,len(MachineList)):
                if Machine in MachineList[index]:
                    BadYield = 1 - YieldList[index]
                    break
            #BadPieces By EM
            ProcessPieces = 0
            for MachineInDifferentPeriod in CurrentMachineProcessedPiecesInDifferentPeriodDict:
                ProcessPieces += CurrentMachineProcessedPiecesInDifferentPeriodDict[MachineInDifferentPeriod]
            BadPiecesByEM = ProcessPieces * BadYield
            # merege to MachineProcessedPiecesInDifferentPeriodDict
            if len(MachineProcessedPiecesInDifferentPeriodDict)==0:
                MachineProcessedPiecesInDifferentPeriodDict = CurrentMachineProcessedPiecesInDifferentPeriodDict
                BadPiecesByEMAve = BadPiecesByEM
            else:
                for MachineInDifferentPeriod in CurrentMachineProcessedPiecesInDifferentPeriodDict:
                    if MachineInDifferentPeriod not in MachineProcessedPiecesInDifferentPeriodDict:
                        MachineProcessedPiecesInDifferentPeriodDict[MachineInDifferentPeriod] = \
                            CurrentMachineProcessedPiecesInDifferentPeriodDict[MachineInDifferentPeriod]
                    else:
                        MachineProcessedPiecesInDifferentPeriodDict[MachineInDifferentPeriod] += \
                            CurrentMachineProcessedPiecesInDifferentPeriodDict[MachineInDifferentPeriod]
                BadPiecesByEMAve += BadPiecesByEM
    return MachineProcessedPiecesInDifferentPeriodDict,BadPiecesByEMAve
#Solve The Equaltion By LeastSquares
def SolveTheEqualtionByLeastSquare(Machine,MachineProcessedPiecesInDifferentPeriodDict,BadPiecesByEMAve,Type ="Cell"):
    PeriodList = []
    PeicesList = []
    YieldList = []
    for MachineProcessedPiecesPeriod in MachineProcessedPiecesInDifferentPeriodDict:
        MachineAndPeroidAList = MachineProcessedPiecesPeriod.split("By")
        PeriodList.append(MachineAndPeroidAList[1])
        PeicesList.append(MachineProcessedPiecesInDifferentPeriodDict[MachineProcessedPiecesPeriod])
    CoefficientOfEqualtion = np.mat([PeicesList])
    SumOfEqualtion = np.mat([BadPiecesByEMAve]).T
    Result = lstsq(CoefficientOfEqualtion, SumOfEqualtion, rcond=None)
    for BadRate in Result[0]:
        YieldList.append(float(1- BadRate))

    machine_yield_rate_history_instances = []
    for index in range(0, len(PeriodList)):
        # Delete existing data
        Machine_Yield_Rate_History.objects.filter(
            machine=Machine,
            period=PeriodList[index],
            analyze_type=Type
        ).delete()

        period = PeriodList[index].split("_")
        start_period_str = period[0]
        end_period_str = period[1]
        start_period = convert_str_to_date(start_period_str)
        end_period = convert_str_to_date(end_period_str)

        print("Inserting {0} machine_yield_rate_history_instance no. {1}".format(Machine, index))
        instance = Machine_Yield_Rate_History(
            machine=Machine,
            period=PeriodList[index],
            start_period=start_period,
            end_period=end_period,
            yield_rate=YieldList[index],
            processed_pieces=PeicesList[index],
            analyze_type=Type
        )
        machine_yield_rate_history_instances.append(instance)
    Machine_Yield_Rate_History.objects.bulk_create(machine_yield_rate_history_instances)

def ComputeWeeklyYieldWithLeastSquare():
    AnalyseFilePathInformationByCellList, AnalyseFilePathInformationByPanelList = GetAnalyseFilePathInformationList()
    #Cell
    print("Cell", time.time())
    AllMachineDict = GetAllMachineFromReport(AnalyseFilePathInformationByCellList)
    for Machine in AllMachineDict:
        print(Machine)
        MachineProcessedPiecesInDifferentPeriodDict, BadPiecesByEMAve = GetMachineProcessedPiecesInDifferentPeriodDict(
            Machine, AnalyseFilePathInformationByCellList)
        SolveTheEqualtionByLeastSquare(Machine, MachineProcessedPiecesInDifferentPeriodDict, BadPiecesByEMAve,"Cell")
    #Panel
    print("Panel", time.time())
    AllMachineDict = GetAllMachineFromReport(AnalyseFilePathInformationByPanelList)
    for Machine in AllMachineDict:
        print(Machine)
        MachineProcessedPiecesInDifferentPeriodDict, BadPiecesByEMAve = GetMachineProcessedPiecesInDifferentPeriodDict(
            Machine, AnalyseFilePathInformationByPanelList)
        SolveTheEqualtionByLeastSquare(Machine, MachineProcessedPiecesInDifferentPeriodDict, BadPiecesByEMAve,"Panel")

def convert_str_to_date(date_str):
    date_format = '%Y%m%d'
    return datetime.datetime.strptime(date_str, date_format).date()

if __name__ == "__main__":
    AnalyseFilePathInformationByCellList, AnalyseFilePathInformationByPanelList = GetAnalyseFilePathInformationList()
    AllMachineDict = GetAllMachineFromReport(AnalyseFilePathInformationByCellList)
    for Machine in AllMachineDict:
        print(Machine)
        MachineProcessedPiecesInDifferentPeriodDict, BadPiecesByEMAve =GetMachineProcessedPiecesInDifferentPeriodDict(Machine, AnalyseFilePathInformationByCellList)
        SolveTheEqualtionByLeastSquare(Machine,MachineProcessedPiecesInDifferentPeriodDict, BadPiecesByEMAve)
        print(MachineProcessedPiecesInDifferentPeriodDict,BadPiecesByEMAve)
        break