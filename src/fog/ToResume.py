import pymongo as pymdb
from datetime import datetime, timezone, timedelta
import h5py
import csv
import numpy as np
from sqlalchemy import between, true
import tables as tb
import pandas as pd
import warnings
from os import path
import sys

class ToResumeInMongoDB:
    '''
    Class that preparate the data.
    '''

    def __init__(self, host="localhost", port="27017", database="solar_irradiation_fogserver", work_path=""):
        self.wok_path = work_path
        self.structure_data = ["ap1","ap3","ap4","ap5","ap6","ap7","dh1","dh2","dh3","dh4","dh5","dh6","dh7","dh8","dh9","dh10","dh11"]
        self.hierarchy_groups = ["datacenter","farm","datetime","day","time"]
        self.conn_db = self.connection(host, port, database)

    def connection(self, host, port, database):
        myclient = pymdb.MongoClient("mongodb://"+host+":"+port+"/")
        return myclient[database]

    def createIndex(self, index, collection, index_name):
        self.conn_db[collection].create_index(index, name=index_name)

    def resume(self, from_date, to_date, collection_from, collection_to):        
        result = self.conn_db[collection_from].aggregate([
                    {
                        "$match": {
                                    "datetime": {"$gte":from_date, "$lte":to_date} 
                                }
                    },
                    {
                        "$group": { 
                                    "_id":{"datacenter":"$datacenter", "farm": "$farm", "sensor": "$sensor", "datetime":from_date},
                                    "avg": {"$avg": "$radiation"},
                                    "stdev": {"$stdDevPop": "$radiation"},
                                    "rows": {"$sum": 1}                  
                                }
                    },
                    {
                        "$merge": collection_to
                    }
                ])
    
    def transpose(self, from_date, to_date, collection_from):        
        result = self.conn_db[collection_from].aggregate([
                    {
                        "$match": {
                                    "_id.datetime": {"$gte":from_date, "$lte":to_date} 
                                }
                    },
                    {
                        "$group": {"_id":{"datetime":"$_id.datetime", "datacenter":"$_id.datacenter", "farm": "$_id.farm"}, 
                                "items":{"$addToSet":{"sensor": "$_id.sensor", "irradiation":"$avg"}}
                                }
                    }, 
                    {
                        "$project":
                        {"tmp":{"$arrayToObject": {"$zip":{"inputs":["$items.sensor", "$items.irradiation"]}}}}
                    }, 
                    {   
                        "$addFields":
                        {
                            "tmp.datetime":"$_id.datetime",
                            "tmp.datacenter":"$_id.datacenter",
                            "tmp.farm":"$_id.farm"
                        }
                    }, 
                    {
                        "$replaceRoot":{"newRoot":"$tmp"}
                    },
                    { 
                        "$sort": { "datetime": 1 }                         
                    }
                ])
        return result
    
    def resetValues(self, dictionary, value):
        x = {}
        for k in dictionary:
            x[k] = value
        return x
    
    def getGroup(self, h5, route):
        try:
            return h5.get_node(route)
        except tb.NoSuchNodeError:
            parent, nodename = route.rsplit('/',1)
            if parent == '':
                parent = '/'
            return h5.create_group(parent, nodename, createparents=True)

    def putData(self, h5, parent, node, data):
        try:
            node = h5.get_node(parent, node)
            node.append(data)
        except tb.NoSuchNodeError:
            h5.create_earray(where=parent, name=node, obj=data)

    def putAttrsMedStd(self, h5, filename, group):
        sc_mean_map = {}
        sc_std_map = {}
        is_mean = true
        with open(filename, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                if is_mean:
                    for k,v in row.items():
                        if v != "mean":
                            sc_mean_map[k] = v
                    is_mean = not is_mean
                else:
                    for k,v in row.items():
                        if v != "stdev":
                            sc_std_map[k] = v                            
            node = h5.get_node(group)
            node._v_attrs["sc_mean_map"] = sc_mean_map
            node._v_attrs["sc_std_map"] = sc_std_map
                
    def putAttrsLatLon(self, h5, filename, group):
        sc_lat_map = {}
        sc_lon_map = {}
        columns = ["time_since_epoch"]
        with open(filename, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter='\t')
            for row in csv_reader:
                columns.append(row["Station"])
                sc_lat_map[ row["Station"] ] = row["Latitude"]
                sc_lon_map[ row["Station"] ] = row["Longitude"]
            node = h5.get_node(group)
            node._v_attrs["sc_lat_map"] = sc_lat_map
            node._v_attrs["sc_lon_map"] = sc_lon_map
            node._v_attrs["columns"] = columns

    def toH5(self, data_to, file_name, field_names=None): 
        dir = path.dirname(path.abspath(__file__))
        file_name = path.join(dir,file_name)
        with tb.open_file(file_name, mode='w') as f, warnings.catch_warnings():
            warnings.simplefilter('ignore', tb.NaturalNameWarning)
            for r in data_to:
                row = self.resetValues(self.structure_data,0)
                groups = self.resetValues(self.hierarchy_groups,"")
                for k,v in r.items():
                    if k in self.hierarchy_groups: 
                        if k == "datetime":
                            groups[k] = v.timestamp()
                            groups["day"] = v.strftime("%Y-%m-%d")
                            groups["time"] = v.strftime("%H:%M:%S")
                        else: 
                            groups[k] = v
                    elif k in self.structure_data : 
                        row[k] = v
                groups_route =  "/" + groups["datacenter"]+ "/" + groups["farm"]
                rgroup = self.getGroup(f, groups_route)
                data= [ ( [groups["datetime"]]+list(row.values()) ) ]
                self.putData(f, rgroup, groups["day"], data)
            # Put attributes
            file_name = path.join(dir,"stations.txt")
            self.putAttrsLatLon(f,file_name,"/DataCenter/FogServer01")
            file_name = path.join(dir,"mean_sd_stations.csv")
            self.putAttrsMedStd(f,file_name,"/DataCenter/FogServer01")
        f.close()

    def toCSV(self, data_to, file_name, field_names=None):
        with open(file_name, 'w') as csvfile:            
            writer = csv.DictWriter(csvfile, delimiter=";")
            writer.writeheader()
            writer.writerows(data_to)

    def run(self, interval, from_date_str, to_date_str):
        collection_from = "sensors"
        collection_to = "sensors_resume"
        ########## Create index for sensors #########
        self.createIndex([("datetime",pymdb.ASCENDING)],collection_from, "idx_datetime")
        ########## Drop database of resume #########
        self.conn_db[collection_to].drop()
        print("End drop")
        from_date = datetime.strptime(from_date_str, '%Y-%m-%dT%H:%M:%S%z')
        to_date = datetime.strptime(to_date_str, '%Y-%m-%dT%H:%M:%S%z')
        ########## Generate resume ############
        prev = from_date 
        while prev <= to_date:
            next = prev + timedelta(seconds=interval)
            ti = prev.replace(hour=7, minute=30, second=0)
            te = prev.replace(hour=17, minute=29, second=59)
            if prev >= ti and prev <= te:
                self.resume(prev, next-timedelta(seconds=1), collection_from, collection_to)
            prev = next
        print("End resume...")
        ########## Transpose the resume ############
        data = list(self.transpose(from_date, to_date, collection_to))
        print("End transpose...")
        ########## Generate h5 ############
        h5_file_name = 'example.h5'
        #csv_file_name = 'example.csv'
        #self.toCSV(data, csv_file_name)
        self.toH5( data, h5_file_name )  
        print("End h5..")

if __name__ == "__main__":
    # Define menu options and call function that runs the menu
    interval = 60
    from_date_str = "2010-03-20T07:30:00+00:00"
    to_date_str = "2010-03-25T17:29:59+00:00"
    if len(sys.argv) > 3:
        largs = sys.argv
        interval = int(largs[1])
        from_date_str = largs[2]
        to_date_str = largs[3]
    p = ToResumeInMongoDB()
    p.run(interval, from_date_str, to_date_str)