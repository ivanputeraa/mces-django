import os
import pandas as pd
import copy


class Gbom:
    def __init__(self, gbom_number, station_numbers, stations, station_classes, making_in_plant_or_outsourcing):
        self._gbom_number = gbom_number
        self._station_list = []
        for i in range(len(station_numbers)):
            self._station_list.append(self.GbomStation(station_numbers[i], stations[i], station_classes[i], making_in_plant_or_outsourcing[i]))
    
    @property
    def gbom_number(self):
        return self._gbom_number
    
    @gbom_number.setter
    def gbom_number(self, value):
        self._gbom_number = value
    
    @property
    def station_list(self):
        return self._station_list
    
    @station_list.setter
    def station_list(self, value):
        self._station_list = value
    
    class GbomStation:
        def __init__(self, station_number, station, station_class, making_in_plant_or_outsourcing):
            self._station_number = station_number
            self._station = station
            self._station_class = station_class
            self._making_in_plant_or_outsourcing = making_in_plant_or_outsourcing
    
        @property
        def station_number(self):
            return self._station_number
        
        @station_number.setter
        def station_number(self, value):
            self._station_number = value
    
        @property
        def station(self):
            return self._station
        
        @station.setter
        def station(self, value):
            self._station = value
    
        @property
        def station_class(self):
            return self._station_class
        
        @station_class.setter
        def station_class(self, value):
            self._station_class = value
    
        @property
        def making_in_plant_or_outsourcing(self):
            return self._making_in_plant_or_outsourcing
        
        @making_in_plant_or_outsourcing.setter
        def making_in_plant_or_outsourcing(self, value):
            self._making_in_plant_or_outsourcing = value


class Lot:
    def __init__(self, lot_number, gbom_number, part_number, station_numbers, stations, machine_numbers):
        self.lot_number = lot_number
        self.gbom_number = gbom_number
        self.part_number = part_number
        self.station_list = []
        for i in range(len(station_numbers)):
            self.station_list.append(self.LotStation(station_numbers[i], stations[i], machine_numbers[i]))

    class LotStation:
        def __init__(self, station_number, station, machine_number):
            self.station_number = station_number
            self.station = station
            self.machine_number = machine_number


def read_gbom_file(gbom_file_name):
    gbom_list = []
    gboms = pd.read_csv(gbom_file_name, encoding='big5hkscs', header=0, engine='python', thousands=',')
    gbom_names = gboms.loc[:, ["GBOM.1"]].drop_duplicates().values.tolist()
    gbom_names = [j for sub in gbom_names for j in sub]

    for name in gbom_names:
        gbom_list.append(
            Gbom(name,  # gbom_number
                 gboms.loc[gboms['GBOM.1'] == name, '次序'].values.tolist(),  # station_numbers
                 gboms.loc[gboms['GBOM.1'] == name, '站別'].values.tolist(),  # stations
                 gboms.loc[gboms['GBOM.1'] == name, '類別'].values.tolist(),  # station_classes
                 gboms.loc[gboms['GBOM.1'] == name, '自製/委外'].values.tolist()))  # making_in_plant_or_outsourcing

    return gbom_list


def read_gbom_all_files(gbom_folder_path):
    all_gbom_list = []
    
    for dirname, dirnames, filenames in os.walk(gbom_folder_path):
        for filename in filenames:
            all_gbom_list += read_gbom_file(os.path.join(gbom_folder_path, filename))
    
    return all_gbom_list


def read_lot_file(lot_file_path):
    lot_list = []
    lots = pd.read_csv(lot_file_path, encoding='big5hkscs', header=0, engine='python', thousands=',')
    lots = lots.sort_values(["批號", "CHECK IN TIME"]).reset_index(drop=True)
    lot_names = lots.loc[:, ["批號"]].drop_duplicates().values.tolist()
    lot_names = [j for sub in lot_names for j in sub]

    for name in lot_names:
        lot_list.append(
            Lot(name,
                lots.loc[lots['批號'] == name, 'GBOM'].drop_duplicates().values.tolist()[0],  # gbom_number
                lots.loc[lots['批號'] == name, '批號'].drop_duplicates().values.tolist()[0],  # part_number
                lots.loc[lots['批號'] == name, '站別次序'].values.tolist(),  # station_numbers
                lots.loc[lots['批號'] == name, '站別'].values.tolist(),  # stations
                lots.loc[lots['批號'] == name, '機器編號'].values.tolist()))  # machine_numbers

    return lot_list


def find_latest_gbom(all_gbom_list, lot):
    return [g for g in reversed(all_gbom_list) if g.gbom_number == lot.gbom_number][0]


def sort_stations(lot):
    lot.station_list = sorted(lot.station_list, key=lambda x: x.station_number, reverse=False)


def fill_spare_virtual_outsourcing_station(lot, gbom):
    lot_copy = copy.deepcopy(lot)
    for station in gbom.station_list:
        if (station.station_class == '備用' or station.station_class == '虛擬' or station.making_in_plant_or_outsourcing == '委外') and (station.station_number not in [station.station_number for station in lot_copy.station_list]):
            lot_copy.station_list.append(lot_copy.LotStation(station.station_number, station.station, 'fill'))
        sort_stations(lot_copy)
    return lot_copy


def classify_past_weekly_production_data(gbom_folder_path, lot_file_path):
    lot_list = read_lot_file(lot_file_path)
    all_gbom_list = read_gbom_all_files(gbom_folder_path)
    analyzable_lot_list = []
    unanalyzable_lot_list = []
    for lot in lot_list:
        try:
            gbom = find_latest_gbom(all_gbom_list, lot)
        except:
            unanalyzable_lot_list.append(lot)
            continue

        lot_station_number_list = [station.station_number for station in lot.station_list]
        gbom_station_number_list = [station.station_number for station in gbom.station_list]
        lot_copy = fill_spare_virtual_outsourcing_station(lot, gbom)
        lot_copy_station_number_list = [station.station_number for station in lot_copy.station_list]

        # 每站都有被使用到，不管順序
        if len(list(set(gbom_station_number_list))) == len(list(set(lot_station_number_list))):
            analyzable_lot_list.append(lot)
            continue
        # 拆批
        elif len(lot.lot_number.split('-')) == 3:
            unanalyzable_lot_list.append(lot)
            continue
        # 先補上缺少的備用、虛擬、委外站，再排序
        elif len(list(set(gbom_station_number_list))) == len(list(set(lot_copy_station_number_list))):
            analyzable_lot_list.append(lot)
            continue
        # 重工LOT
        elif lot.lot_number.split('-')[1][0] == 'D':
            unanalyzable_lot_list.append(lot)
            continue
        # 只有一站正常站
        elif len(lot_station_number_list) == 1 and gbom.station_list[
            lot_station_number_list[0] - 1].station_class == '正常*':
            unanalyzable_lot_list.append(lot)
            continue
        # 只缺一~三站
        elif len(list(set(gbom_station_number_list) - set(lot_copy_station_number_list))) < 5:
            analyzable_lot_list.append(lot)
            continue
        else:
            unanalyzable_lot_list.append(lot)
    
    unanalyzable_lot_number_list = [lot.lot_number for lot in unanalyzable_lot_list]
    
    return unanalyzable_lot_number_list

        
# raw_data_directory = 'recent_raw_data'
# week_folder = '20180716_0722'
# 
# gbom_folder_name = 'gbom'
# lot_file_name = '生產歷程.csv'
# gbom_folder_path = os.path.join(raw_data_directory, gbom_folder_name)
# lot_file_path = os.path.join(raw_data_directory, week_folder, lot_file_name)
# 
# unanalyzable_lot_number_list = classify_past_weekly_production_data(gbom_folder_path, lot_file_path)

