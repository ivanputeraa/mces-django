import pandas as pd
import time
from estimator import ConstructWeeklyFinishTime
from estimator.models import MachineUsedByLotInformation
from estimator import lot_classifier
class LotInformation:
    def __init__(self):
        self.MaterialNumber = ""
        self.GBOM = ""
        self.Lot = ""
        self.MachineInformationList = [][:]
        self.FinishTime = ""
        self.TypeSettingNumber = ""
    def SetMaterialNumber(self,MaterialNumber):
        self.MaterialNumber = MaterialNumber
    def SetGBOM(self,GBOM):
        self.GBOM = GBOM
    def SetLot(self,Lot):
        self.Lot = Lot
    def SetMachineInformationList(self,MachineInformationList):
        self.MachineInformationList = MachineInformationList
    def SetFinishTime(self,FinishTime):
        self.FinishTime = FinishTime
    def SetTypeSettingNumber(self,TypeSettingNumber):
        self.TypeSettingNumber = TypeSettingNumber
class MachineInformation:
    def __init__(self):
        self.Machine = ""
        self.CheckInTime = ""
        self.CheckOutTime = ""
        self.StationNumber = ""
        self.GoodPieces = 0
        self.BadPieces = 0
        self.FirstStation = 0
        self.CurrentTotalPieces = 0
        self.Period = ""
    def SetMachine(self, Machine):
        self.Machine = Machine
    def SetCheckInTime(self, CheckInTime):
        self.CheckInTime = CheckInTime
    def SetCheckOutTime(self, CheckOutTime):
        self.CheckOutTime = CheckOutTime
    def SetStationNumber(self, StationNumber):
        self.StationNumber = StationNumber
    def SetGoodPieces(self, GoodPieces):
        self.GoodPieces = GoodPieces
    def SetBadPieces(self, BadPieces):
        self.BadPieces = BadPieces
    def SetFirstStation(self, FirstStation):
        self.FirstStation = FirstStation
    def SetCurrentTotalPieces(self, CurrentTotalPieces):
        self.CurrentTotalPieces = CurrentTotalPieces 
    def SetPeriod(self,Period):
        self.Period = Period
#   將生產數據，按Lot分列
#  人工站未使用的機器名由""或"nan"改爲NA
def GetRawDataToLotInformationDict(RawDataFileName):
    DataFlow = pd.read_csv(RawDataFileName, encoding='big5')
    DataFlow.sort_values(by=['GBOM','批號','CHECK IN TIME'],inplace=True)
    MaterialNumberList = DataFlow['料號'].values.copy()
    GBOMList = DataFlow['GBOM'].values.copy()
    LotList = DataFlow['批號'].values.copy()
    MachineList = DataFlow['機器編號'].values.copy()
    CheckInTimeList = DataFlow['CHECK IN TIME'].values.copy()
    CheckOutTimeList = DataFlow['CHECK OUT TIME'].values.copy()
    StationNumberList = DataFlow['站別次序'].values.copy()
    GoodPiecesList = DataFlow['GOODNUM'].values.copy()
    BadPiecesList = DataFlow['BADNUM'].values.copy()
    TypeSettingNumberList = DataFlow['排版數'].values.copy()
    FinishTimeList = DataFlow['入庫日期'].values.copy() 
    RawLotInformationDict = {} 
    for i in range(0,len(GBOMList)):
        MaterialNumber = str(MaterialNumberList[i])
        GBOM = str(GBOMList[i])
        Lot = str(LotList[i])
        Machine = str(MachineList[i])  
        CheckInTime = str(CheckInTimeList[i]) 
        CheckOutTime = str(CheckOutTimeList[i])
        StationNumber = str(StationNumberList[i])
        GoodPieces = 0
        BadPieces = 0
        TypeSettingNumber = str(TypeSettingNumberList[i])
        FinishTime = str(FinishTimeList[i]) 
        if len(Machine) == 3 or len(Machine) == 1:
            Machine = "NA"
        if str(GoodPiecesList[i]).replace(",", "").replace("nan", "") != "":#  3,876,456 ==>>> 3876456 
            GoodPieces = str(GoodPiecesList[i]).replace(",", "").replace("nan", "").split(".")
            GoodPieces = int(GoodPieces[0])
        if str(BadPiecesList[i]).replace(",", "").replace("nan", "") != "":
            BadPieces = str(BadPiecesList[i]).replace(",", "").replace("nan", "").split(".") 
            BadPieces = int(BadPieces[0]) 
        if Lot not in RawLotInformationDict: 
            MachineInformationList = []
            MachineInfo = MachineInformation()
            MachineInfo.SetMachine(Machine)
            MachineInfo.SetCheckInTime(CheckInTime)
            MachineInfo.SetCheckOutTime(CheckOutTime)
            MachineInfo.SetStationNumber(StationNumber)
            MachineInfo.SetGoodPieces(GoodPieces)
            MachineInfo.SetBadPieces(BadPieces)
            MachineInformationList.append(MachineInfo) 
            LotInfo = LotInformation()
            LotInfo.SetMaterialNumber(MaterialNumber)
            LotInfo.SetGBOM(GBOM)
            LotInfo.SetLot(Lot)
            LotInfo.SetMachineInformationList(MachineInformationList[:])
            LotInfo.SetFinishTime(FinishTime)
            LotInfo.SetTypeSettingNumber(TypeSettingNumber)
            RawLotInformationDict[Lot] = LotInfo
        else:
            MachineInfo = MachineInformation()
            MachineInfo.SetMachine(Machine)
            MachineInfo.SetCheckInTime(CheckInTime)
            MachineInfo.SetCheckOutTime(CheckOutTime)
            MachineInfo.SetStationNumber(StationNumber)
            MachineInfo.SetGoodPieces(GoodPieces)
            MachineInfo.SetBadPieces(BadPieces) 
            RawLotInformationDict[Lot].MachineInformationList.append(MachineInfo)
    return RawLotInformationDict
#Case1: 1.去掉進入機器前人工站（回收批破片）
#       2.挑出Lot使用機器編碼記錄錯誤的情況
def ProcessDataByRemoveHumanStationInTheProduceBeforeAndRemoveWrongMachine(RawLotInformationDict={}):
    ProcessedLotInformationDict = {}
    MachineErrorLotInformationDict = {}
    for Lot in RawLotInformationDict:
        Error = 0
        ProcessedMachineInformationList = []
        for MachineInfo in RawLotInformationDict[Lot].MachineInformationList:  
            if len(MachineInfo.Machine)!= 6 and MachineInfo.Machine!="NA":#機器編碼錯誤情況
                Error = 1
                break
            if len(ProcessedMachineInformationList)==0:#首站
                if MachineInfo.Machine == "NA":# 1.首站人工站去掉
                    continue
                else:
                    MachineInfo.FirstStation = 1
                    ProcessedMachineInformationList.append(MachineInfo)
            else:#非首站
                MachineInfo.FirstStation = 0
                ProcessedMachineInformationList.append(MachineInfo)
        if Error == 1:#機器編碼錯誤的Lot
            MachineErrorLotInformationDict[Lot] = RawLotInformationDict[Lot]
        else:#正常的Lot
            LotInfo = LotInformation()
            LotInfo.SetMaterialNumber(RawLotInformationDict[Lot].MaterialNumber)
            LotInfo.SetGBOM(RawLotInformationDict[Lot].GBOM)
            LotInfo.SetLot(RawLotInformationDict[Lot].Lot)
            LotInfo.SetMachineInformationList(ProcessedMachineInformationList[:])
            LotInfo.SetFinishTime(RawLotInformationDict[Lot].FinishTime)
            LotInfo.SetTypeSettingNumber(RawLotInformationDict[Lot].TypeSettingNumber)
            ProcessedLotInformationDict[Lot] = LotInfo 
    return ProcessedLotInformationDict,MachineErrorLotInformationDict
#   更新當前站生產縂片數
#   處理與上一機器站別名相同1.上一站是首站，好片相加，坏片相加 2，上一站不是首站，坏片相加
def ProcessDataByMergeSameMachineOrHumanStationToLastStation(RawLotInformationDict={}):
    ProcessedLotInformationDict = {}
    MaxStep = 0
    for Lot in RawLotInformationDict: 
        for MachineInfo in RawLotInformationDict[Lot].MachineInformationList:
            if Lot not in ProcessedLotInformationDict:
                #首站  更新當前站生產縂片數
                ProcessedMachineInformationList = []
                MachineInfo.CurrentTotalPieces = MachineInfo.GoodPieces + MachineInfo.BadPieces 
                ProcessedMachineInformationList.append(MachineInfo)
                LotInfo = LotInformation()
                LotInfo.SetMaterialNumber(RawLotInformationDict[Lot].MaterialNumber)
                LotInfo.SetGBOM(RawLotInformationDict[Lot].GBOM)
                LotInfo.SetLot(RawLotInformationDict[Lot].Lot)
                LotInfo.SetMachineInformationList(ProcessedMachineInformationList[:])
                LotInfo.SetFinishTime(RawLotInformationDict[Lot].FinishTime)
                LotInfo.SetTypeSettingNumber(RawLotInformationDict[Lot].TypeSettingNumber)
                ProcessedLotInformationDict[Lot] = LotInfo
            else:
                LastMachineInfo = ProcessedLotInformationDict[Lot].MachineInformationList[len(ProcessedLotInformationDict[Lot].MachineInformationList)-1]
                if LastMachineInfo.Machine == MachineInfo.Machine or MachineInfo.Machine =="NA":#當前站與上一站機器名稱相同
                    if LastMachineInfo.FirstStation == 1: #上一站為首站,好片合并、坏片也合并 
                        LastMachineInfo.GoodPieces = LastMachineInfo.GoodPieces + MachineInfo.GoodPieces
                        LastMachineInfo.BadPieces = LastMachineInfo.BadPieces + MachineInfo.BadPieces
                        LastMachineInfo.CurrentTotalPieces = LastMachineInfo.GoodPieces + LastMachineInfo.BadPieces
                        #合并機器完成時間
                        LastMachineInfo.CheckOutTime = MachineInfo.CheckOutTime
                        ProcessedLotInformationDict[Lot].MachineInformationList[
                            len(ProcessedLotInformationDict[Lot].MachineInformationList) - 1] = LastMachineInfo
                    else:#上一站不是首站 只需要合并坏片數
                        LastMachineInfo.BadPieces = LastMachineInfo.BadPieces + MachineInfo.BadPieces
                        # 合并機器完成時間  注意人工站不合并
                        if MachineInfo.Machine !="NA":
                            LastMachineInfo.CheckOutTime = MachineInfo.CheckOutTime
                        ProcessedLotInformationDict[Lot].MachineInformationList[
                            len(ProcessedLotInformationDict[Lot].MachineInformationList) - 1] = LastMachineInfo
                else:
                    MachineInfo.CurrentTotalPieces = LastMachineInfo.CurrentTotalPieces - LastMachineInfo.BadPieces
                    ProcessedLotInformationDict[Lot].MachineInformationList.append(MachineInfo)
        if Lot in ProcessedLotInformationDict:
            CurrentStep = len(ProcessedLotInformationDict[Lot].MachineInformationList)
            if CurrentStep > MaxStep:
                MaxStep = CurrentStep
    return ProcessedLotInformationDict,MaxStep

def ProcessDataByPrecessPerfectMachine(PerfectMachineList, RawLotInformationDict={}): 
    for Lot in RawLotInformationDict: 
        MachineInfoList = RawLotInformationDict[Lot].MachineInformationList[:] 
        #update badpieces 
        for ReveseIndex in range(len(RawLotInformationDict[Lot].MachineInformationList[:])-1,-1,-1):
            CurrentMachinInfo = MachineInfoList[ReveseIndex]
            if CurrentMachinInfo.Machine in PerfectMachineList: 
                CurrentBadPieces = CurrentMachinInfo.BadPieces
                CurrentMachinInfo.BadPieces = 0
                MachineInfoList[ReveseIndex] = CurrentMachinInfo
                if CurrentMachinInfo.FirstStation != 1:
                   LastMachineInfo = MachineInfoList[ReveseIndex-1]
                   LastMachineInfo.BadPieces += CurrentBadPieces
                   MachineInfoList[ReveseIndex - 1] = LastMachineInfo
        #update current pieces
        for Index in range(0,len(RawLotInformationDict[Lot].MachineInformationList[:])):
            CurrentMachinInfo = MachineInfoList[Index]
            if CurrentMachinInfo.FirstStation == 1 :
                CurrentMachinInfo.CurrentTotalPieces = CurrentMachinInfo.GoodPieces + CurrentMachinInfo.BadPieces
                MachineInfoList[Index] = CurrentMachinInfo
            else:
                LastMachineInfo =  MachineInfoList[Index-1]
                CurrentMachinInfo.CurrentTotalPieces = LastMachineInfo.CurrentTotalPieces - LastMachineInfo.BadPieces
                MachineInfoList[Index] = CurrentMachinInfo
        RawLotInformationDict[Lot].SetMachineInformationList(MachineInfoList[:])
    return RawLotInformationDict
def ModifyMachineByWeeklyFinishTime(WeeklyFinishDateDict,RawLotInformationDict={}):
    TheLotOfOutsideTheRange = []
    for Lot in RawLotInformationDict:
        for index in range(0,len(RawLotInformationDict[Lot].MachineInformationList)):
            MachineInfo = RawLotInformationDict[Lot].MachineInformationList[index]
            CheckInTimeList = MachineInfo.CheckInTime.split(" ")
            CheckInTimeDate = CheckInTimeList[0]
            CheckOutTimeList = MachineInfo.CheckOutTime.split(" ")
            CheckOutTimeDate = CheckOutTimeList[0] 
            # search the WeeklyFinishDateDict
            PeriodOfCheckInTimeDate = ""
            PeriodOfCheckOutTimeDate = ""
            IsFindThePeriodOfCheckInTimeDate = 0
            IsFindThePeriodOfCheckOutTimeDate = 0 
            for Period in WeeklyFinishDateDict:
                if CheckInTimeDate in WeeklyFinishDateDict[Period]:
                    PeriodOfCheckInTimeDate = Period
                    IsFindThePeriodOfCheckInTimeDate = 1 
                if CheckOutTimeDate in WeeklyFinishDateDict[Period]:
                    PeriodOfCheckOutTimeDate = Period
                    IsFindThePeriodOfCheckOutTimeDate = 1
                if IsFindThePeriodOfCheckInTimeDate and IsFindThePeriodOfCheckOutTimeDate :
                    break
            # Not Include Current Range
            if IsFindThePeriodOfCheckInTimeDate==0 or IsFindThePeriodOfCheckOutTimeDate==0: 
                TheLotOfOutsideTheRange.append(Lot)
                break
            if PeriodOfCheckInTimeDate == PeriodOfCheckOutTimeDate :
                MachineInfo.SetPeriod(PeriodOfCheckInTimeDate)
            elif str(PeriodOfCheckInTimeDate)=="" or str(PeriodOfCheckInTimeDate)=="nan" or str(PeriodOfCheckOutTimeDate)=="" or str(PeriodOfCheckOutTimeDate)=="nan":
                if len(PeriodOfCheckInTimeDate)>15:
                    MachineInfo.SetPeriod(PeriodOfCheckInTimeDate)
                elif len(PeriodOfCheckOutTimeDate)>15:
                    MachineInfo.SetPeriod(PeriodOfCheckOutTimeDate)
                else:
                    MachineInfo.SetPeriod("Wrong")
            else : 
                #select the bigger Period
                ChechInTimeIndex = WeeklyFinishDateDict[PeriodOfCheckInTimeDate].index(CheckInTimeDate)
                ChechOutTimeIndex = WeeklyFinishDateDict[PeriodOfCheckOutTimeDate].index(CheckOutTimeDate)
                if 7 - ChechInTimeIndex > ChechOutTimeIndex:
                    MachineInfo.SetPeriod(PeriodOfCheckInTimeDate)
                else:
                    MachineInfo.SetPeriod(PeriodOfCheckOutTimeDate)
            RawLotInformationDict[Lot].MachineInformationList[index] = MachineInfo 
    for ErrorLot in TheLotOfOutsideTheRange:
        RawLotInformationDict.pop(ErrorLot)
    return RawLotInformationDict
def RemoveErrorData(RawLotInformationDict = {}):
    ErrorLotList = []
    MaxStep = 0
    for Lot in RawLotInformationDict:
        for MachineInfo in RawLotInformationDict[Lot].MachineInformationList:
            if MachineInfo.CurrentTotalPieces<=0 :
                ErrorLotList.append(Lot)
                break
    for ErrorLot in ErrorLotList:
        RawLotInformationDict.pop(ErrorLot)
    return RawLotInformationDict
# 輸出
def WriteToCSV(RawLotInformationDict = {},MaxStep = 1,Path="pure_stand4_process.csv"):
    ProcessedDataPathByCell = Path.replace("ProcessedData.csv", "ProcessedDataByCell.csv")
    ProcessedDataPathByPanel = Path.replace("ProcessedData.csv", "ProcessedDataByPanel.csv")
    ProcessedDataPathByCellNotSplit = Path.replace("ProcessedData.csv", "ProcessedDataByCellNotSplit.csv")
    ProcessedDataPathByPanelNotSplit = Path.replace("ProcessedData.csv", "ProcessedDataByPanelNotSplit.csv")
    CSVTitle = "Lot"
    for index in range(1,MaxStep+1):
        IndexStr = str(index+1000)
        CSVTitle = CSVTitle+",Process"+ IndexStr[1:4]+"_MachineNo"
    CSVTitle = CSVTitle+",Final,CurrentTotalNum,BadNum,TotalNum\n"
    #Split By Week
    #By Cell
    print("Process By Cell")
    with open(ProcessedDataPathByCell, 'w') as file_output:
        file_output.write(CSVTitle)
        for Lot in RawLotInformationDict:
            TheStepOfCurrentMachine = 1
            TheStepOfTheLot = len(RawLotInformationDict[Lot].MachineInformationList)
            for IndexOfTheMachineUesdByTheLot in range(0,TheStepOfTheLot):
                Conten = Lot
                for j in range(0,MaxStep):
                    if j < TheStepOfCurrentMachine:
                        #By Period 
                        Conten = Conten + ","+RawLotInformationDict[Lot].MachineInformationList[j].Machine+"By"+RawLotInformationDict[Lot].MachineInformationList[j].Period
                        #Before 
                        # Conten = Conten + "," + RawLotInformationDict[Lot].MachineInformationList[j].Machine
                    else:
                        Conten = Conten + ","
                if IndexOfTheMachineUesdByTheLot == TheStepOfTheLot-1:#last step machine
                    Conten = Conten+",-1,"
                else:
                    Conten = Conten + ","+ str(TheStepOfCurrentMachine)+ "," 
                Conten = Conten +str(RawLotInformationDict[Lot].MachineInformationList[IndexOfTheMachineUesdByTheLot].CurrentTotalPieces) + \
                             ","+str(RawLotInformationDict[Lot].MachineInformationList[IndexOfTheMachineUesdByTheLot].BadPieces) +\
                             ","+str(RawLotInformationDict[Lot].MachineInformationList[0].CurrentTotalPieces)+"\n"
                file_output.write(Conten)
                TheStepOfCurrentMachine += 1

        # By Panel
    print("Process By Panel")
    with open(ProcessedDataPathByPanel, 'w') as file_output:
        file_output.write(CSVTitle)
        for Lot in RawLotInformationDict:
            TheStepOfCurrentMachine = 1
            TheStepOfTheLot = len(RawLotInformationDict[Lot].MachineInformationList)
            for IndexOfTheMachineUesdByTheLot in range(0, TheStepOfTheLot):
                Conten = Lot
                for j in range(0, MaxStep):
                    if j < TheStepOfCurrentMachine:
                        # By Period 
                        Conten = Conten + ","+RawLotInformationDict[Lot].MachineInformationList[j].Machine+"By"+RawLotInformationDict[Lot].MachineInformationList[j].Period
                        # Before 
                        # Conten = Conten + "," + RawLotInformationDict[Lot].MachineInformationList[j].Machine
                    else:
                        Conten = Conten + ","
                if IndexOfTheMachineUesdByTheLot == TheStepOfTheLot - 1:  # last step machine
                    Conten = Conten + ",-1,"
                else:
                    Conten = Conten + "," + str(TheStepOfCurrentMachine) + "," 
                Conten = Conten + str(float(RawLotInformationDict[Lot].MachineInformationList[IndexOfTheMachineUesdByTheLot].CurrentTotalPieces)/float(RawLotInformationDict[Lot].TypeSettingNumber)) + \
                         "," + str(float(RawLotInformationDict[Lot].MachineInformationList[IndexOfTheMachineUesdByTheLot].BadPieces)/float(RawLotInformationDict[Lot].TypeSettingNumber)) + \
                         "," + str(float(RawLotInformationDict[Lot].MachineInformationList[0].CurrentTotalPieces)/float(RawLotInformationDict[Lot].TypeSettingNumber)) + "\n"
                file_output.write(Conten)
                TheStepOfCurrentMachine += 1
    #Not Split 
    print("Process By Cell Not Split")
    with open(ProcessedDataPathByCellNotSplit, 'w') as file_output:
        file_output.write(CSVTitle)
        for Lot in RawLotInformationDict:
            TheStepOfCurrentMachine = 1
            TheStepOfTheLot = len(RawLotInformationDict[Lot].MachineInformationList)
            for IndexOfTheMachineUesdByTheLot in range(0, TheStepOfTheLot):
                Conten = Lot
                for j in range(0, MaxStep):
                    if j < TheStepOfCurrentMachine:
                        # By Period 
                        # Conten = Conten + "," + RawLotInformationDict[Lot].MachineInformationList[j].Machine + "By" + \
                        #          RawLotInformationDict[Lot].MachineInformationList[j].Period
                        # Before 
                        Conten = Conten + "," + RawLotInformationDict[Lot].MachineInformationList[j].Machine
                    else:
                        Conten = Conten + ","
                if IndexOfTheMachineUesdByTheLot == TheStepOfTheLot - 1:  # last step machine
                    Conten = Conten + ",-1,"
                else:
                    Conten = Conten + "," + str(TheStepOfCurrentMachine) + ","
                Conten = Conten + str(RawLotInformationDict[Lot].MachineInformationList[
                                          IndexOfTheMachineUesdByTheLot].CurrentTotalPieces) + \
                         "," + str(
                    RawLotInformationDict[Lot].MachineInformationList[IndexOfTheMachineUesdByTheLot].BadPieces) + \
                         "," + str(RawLotInformationDict[Lot].MachineInformationList[0].CurrentTotalPieces) + "\n"
                file_output.write(Conten)
                TheStepOfCurrentMachine += 1
    print("Process By Panel Not Split")
    with open(ProcessedDataPathByPanelNotSplit, 'w') as file_output:
        file_output.write(CSVTitle)
        for Lot in RawLotInformationDict:
            TheStepOfCurrentMachine = 1
            TheStepOfTheLot = len(RawLotInformationDict[Lot].MachineInformationList)
            for IndexOfTheMachineUesdByTheLot in range(0, TheStepOfTheLot):
                Conten = Lot
                for j in range(0, MaxStep):
                    if j < TheStepOfCurrentMachine:
                        # By Period 
                        # Conten = Conten + "," + RawLotInformationDict[Lot].MachineInformationList[j].Machine + "By" + \
                        #          RawLotInformationDict[Lot].MachineInformationList[j].Period
                        # Before 
                        Conten = Conten + "," + RawLotInformationDict[Lot].MachineInformationList[j].Machine
                    else:
                        Conten = Conten + ","
                if IndexOfTheMachineUesdByTheLot == TheStepOfTheLot - 1:  # last step machine
                    Conten = Conten + ",-1,"
                else:
                    Conten = Conten + "," + str(TheStepOfCurrentMachine) + ","
                Conten = Conten + str(float(RawLotInformationDict[Lot].MachineInformationList[
                                                IndexOfTheMachineUesdByTheLot].CurrentTotalPieces) / float(
                    RawLotInformationDict[Lot].TypeSettingNumber)) + \
                         "," + str(float(
                    RawLotInformationDict[Lot].MachineInformationList[IndexOfTheMachineUesdByTheLot].BadPieces) / float(
                    RawLotInformationDict[Lot].TypeSettingNumber)) + \
                         "," + str(
                    float(RawLotInformationDict[Lot].MachineInformationList[0].CurrentTotalPieces) / float(
                        RawLotInformationDict[Lot].TypeSettingNumber)) + "\n"
                file_output.write(Conten)
                TheStepOfCurrentMachine += 1

def SearchTheSameMachineUsedInTheSamePeriod(RawLotInformationDict = {}):
    # Operate HistoryMachineUsage
    #1.delete current data 
    # print("Delete the Data")
    for Lot in RawLotInformationDict:
        # HistoryMachineUsage.objects.filter(Lot__contains=Lot).delete()
        MachineUsedByLotInformation.objects.filter(Lot__contains=Lot).delete()
    #2.select same period
    LotOfSameMachineUsedInSamePeriodDict = {} #differen lot can use the same machine in the same week , so we need to distinct
    # print("Search Machine Used In Different Lot In The Same Period")
    count = 0 
    for Lot in RawLotInformationDict:
        for MachineInfo in RawLotInformationDict[Lot].MachineInformationList:
            SearchResult = MachineUsedByLotInformation.objects.filter(Period=MachineInfo.Period,Machine=MachineInfo.Machine)
            if SearchResult:
                count += 1
                # print("SearchResult", SearchResult[0].Lot ,MachineInfo.Period,MachineInfo.Machine)
                LengthOfSearchResult = len(SearchResult)
                for length in range(0,LengthOfSearchResult):
                    LotOfSameMachineUsedInSamePeriodDict[SearchResult[length].Lot] = 1
    # #3. insert current data SearchResult
    print("Lot ", len(LotOfSameMachineUsedInSamePeriodDict),"Machine",count)
    # print("Insert Current MachineInfo To HistoryMachineUsage & MachineUsedByLotInformation")
    # InsertToHistoryMachineUsage = list()
    InsertToMachineUsedByLotInformationList = list()
    for Lot in RawLotInformationDict:
        for MachineInfo in RawLotInformationDict[Lot].MachineInformationList:
            # MachineUsage = HistoryMachineUsage(Lot=Lot,Machine=MachineInfo.Machine,Period=MachineInfo.Period)
            # InsertToHistoryMachineUsage.append(MachineUsage)
            MachineUsedByLotInfo = MachineUsedByLotInformation(
                MaterialNumber=RawLotInformationDict[Lot].MaterialNumber,
                GBOM=RawLotInformationDict[Lot].GBOM,
                Lot=Lot,
                FinishTime=RawLotInformationDict[Lot].FinishTime,
                TypeSettingNumber=RawLotInformationDict[Lot].TypeSettingNumber,
                Machine=MachineInfo.Machine,
                CheckInTime=MachineInfo.CheckInTime,
                CheckOutTime=MachineInfo.CheckOutTime,
                StationNumber=MachineInfo.StationNumber,
                GoodPieces=MachineInfo.GoodPieces,
                BadPieces=MachineInfo.BadPieces,
                FirstStation=MachineInfo.FirstStation,
                CurrentTotalPieces=MachineInfo.CurrentTotalPieces,
                Period=MachineInfo.Period)
            InsertToMachineUsedByLotInformationList.append(MachineUsedByLotInfo)
    # HistoryMachineUsage.objects.bulk_create(InsertToHistoryMachineUsage,1000)
    MachineUsedByLotInformation.objects.bulk_create(InsertToMachineUsedByLotInformationList,1000)
    # Operate LotUseMachineInformation 
    # print("Select the LotInfo depend on SameMachineUsedInSamePeriod")
    for Lot in LotOfSameMachineUsedInSamePeriodDict:
        SearchResult = MachineUsedByLotInformation.objects.filter(Lot=Lot).order_by('CheckInTime')
        for MachineInfoInSearchResult in SearchResult:
            if Lot not in RawLotInformationDict:
                MachineInformationList = []
                MachineInfo = MachineInformation()
                MachineInfo.SetMachine(MachineInfoInSearchResult.Machine)
                MachineInfo.SetCheckInTime(MachineInfoInSearchResult.CheckInTime)
                MachineInfo.SetCheckOutTime(MachineInfoInSearchResult.CheckOutTime)
                MachineInfo.SetStationNumber(MachineInfoInSearchResult.StationNumber)
                MachineInfo.SetGoodPieces(MachineInfoInSearchResult.GoodPieces)
                MachineInfo.SetBadPieces(MachineInfoInSearchResult.BadPieces)
                MachineInfo.SetFirstStation(MachineInfoInSearchResult.FirstStation)
                MachineInfo.SetCurrentTotalPieces(MachineInfoInSearchResult.CurrentTotalPieces)
                MachineInfo.SetPeriod(MachineInfoInSearchResult.Period)
                MachineInformationList.append(MachineInfo)
                LotInfo = LotInformation()
                LotInfo.SetMaterialNumber(MachineInfoInSearchResult.MaterialNumber)
                LotInfo.SetGBOM(MachineInfoInSearchResult.GBOM)
                LotInfo.SetLot(Lot)
                LotInfo.SetMachineInformationList(MachineInformationList[:])
                LotInfo.SetFinishTime(MachineInfoInSearchResult.FinishTime)
                LotInfo.SetTypeSettingNumber(MachineInfoInSearchResult.TypeSettingNumber)
                RawLotInformationDict[Lot] = LotInfo
            else:
                MachineInfo = MachineInformation()
                MachineInfo.SetMachine(MachineInfoInSearchResult.Machine)
                MachineInfo.SetCheckInTime(MachineInfoInSearchResult.CheckInTime)
                MachineInfo.SetCheckOutTime(MachineInfoInSearchResult.CheckOutTime)
                MachineInfo.SetStationNumber(MachineInfoInSearchResult.StationNumber)
                MachineInfo.SetGoodPieces(MachineInfoInSearchResult.GoodPieces)
                MachineInfo.SetBadPieces(MachineInfoInSearchResult.BadPieces)
                MachineInfo.SetFirstStation(MachineInfoInSearchResult.FirstStation)
                MachineInfo.SetCurrentTotalPieces(MachineInfoInSearchResult.CurrentTotalPieces)
                MachineInfo.SetPeriod(MachineInfoInSearchResult.Period)
                RawLotInformationDict[Lot].MachineInformationList.append(MachineInfo)
    MaxStep = 0
    for Lot in RawLotInformationDict:
        if MaxStep < len(RawLotInformationDict[Lot].MachineInformationList):
            MaxStep = len(RawLotInformationDict[Lot].MachineInformationList)
    return RawLotInformationDict,MaxStep
def ProcessData(RawDataPath="",ProcessedDataPath="",PerfectMachineList = []):
    print("Start ProcessData", time.time())
    RawLotInformationDict = GetRawDataToLotInformationDict(RawDataPath)
    LotInformationDictProcessedByRemoveHumanStationAndRemoveWrongMachine, MachineErrorLotInformationDict = ProcessDataByRemoveHumanStationInTheProduceBeforeAndRemoveWrongMachine(
        RawLotInformationDict)
    InformationDictMergeSameMachineOrHumanStationToLastStation, MaxStep = ProcessDataByMergeSameMachineOrHumanStationToLastStation(
        LotInformationDictProcessedByRemoveHumanStationAndRemoveWrongMachine)
    InformationDictProcessedByPerfectMachine = ProcessDataByPrecessPerfectMachine(PerfectMachineList,
                                                                                  InformationDictMergeSameMachineOrHumanStationToLastStation)
    WeeklyFinishDateDict = ConstructWeeklyFinishTime.GetWeeklyFinishDateDict()
    LotInformationDictProcessedByTimeDimension = ModifyMachineByWeeklyFinishTime(WeeklyFinishDateDict,
                                                                                 InformationDictProcessedByPerfectMachine)
    CorrectInformationDict = RemoveErrorData(LotInformationDictProcessedByTimeDimension)
    
    #Except The Lot
    print("Except The Lot That Dont Flow GBOM", time.time())
    import os
    # GBOMDir = os.getcwd() + "\\analyse\\GBOM"
    GBOMDir = os.getcwd() + "/estimator/GBOM"
    ExceptLotList = lot_classifier.classify_past_weekly_production_data(GBOMDir,RawDataPath)
    print(time.time(),ExceptLotList)
    for ExceptLot in ExceptLotList:
        if ExceptLot in CorrectInformationDict:
            CorrectInformationDict.pop(ExceptLot)
    
    #GetMaxStep
    MaxStep = 0
    for Lot in CorrectInformationDict:
        if MaxStep < len(CorrectInformationDict[Lot].MachineInformationList):
            MaxStep = len(CorrectInformationDict[Lot].MachineInformationList)
    # print("Start Search", time.time())
    # LotInformationDictProcessedBySearchTheSameMachineUsedInTheSamePeriod,MaxStep = SearchTheSameMachineUsedInTheSamePeriod(CorrectInformationDict)
    # print("Start OutPutCSV", time.time())
    WriteToCSV(CorrectInformationDict, MaxStep,ProcessedDataPath)
    print("Finished OutPutCSV", time.time())
if __name__ == "__main__":
    RawLotInformationList = GetRawDataToLotInformationDict('20180806_0812_data.csv')
    LotInformationDictProcessedByRemoveHumanStationAndRemoveWrongMachine, MachineErrorLotInformationDict = ProcessDataByRemoveHumanStationInTheProduceBeforeAndRemoveWrongMachine(RawLotInformationList)
    InformationDictMergeSameMachineOrHumanStationToLastStation,MaxStep = ProcessDataByMergeSameMachineOrHumanStationToLastStation(LotInformationDictProcessedByRemoveHumanStationAndRemoveWrongMachine) 
    # PerfectMachineList = ["SW-031","LS-061","FT-044","FT-086","ME-005","PL-014","GP-007","PL-006","DM-005","EX-002","DR-001","SP-005","ME-004"]
    PerfectMachineList = []
    InformationDictProcessedByPerfectMachine = ProcessDataByPrecessPerfectMachine(PerfectMachineList, InformationDictMergeSameMachineOrHumanStationToLastStation)
    WeeklyFinishDateDict = ConstructWeeklyFinishTime.GetWeeklyFinishDateDict()
    LotInformationDictProcessedByTimeDimension = ModifyMachineByWeeklyFinishTime(WeeklyFinishDateDict,
                                                                                 InformationDictProcessedByPerfectMachine)
    #Need to Recompute the MaxStep
    CorrectInformationDict = RemoveErrorData(LotInformationDictProcessedByTimeDimension)
    WriteToCSV(CorrectInformationDict,MaxStep)
    # # print(MaxStep)
    # for Lot in InformationDictProcessedByPerfectMachine:
    #     for MachineInfo in InformationDictProcessedByPerfectMachine[Lot].MachineInformationList:
    #          print(Lot,MachineInfo.FirstStation,MachineInfo.StationNumber,MachineInfo.Machine,MachineInfo.CurrentTotalPieces,MachineInfo.BadPieces)