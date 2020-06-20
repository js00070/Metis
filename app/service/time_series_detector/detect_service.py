#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Tencent is pleased to support the open source community by making Metis available.
Copyright (C) 2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the BSD 3-Clause License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
"""

import time
import os
import threading
from app.dao.time_series_detector import anomaly_op
from app.dao.time_series_detector import sample_op
from app.dao.time_series_detector import train_op
from app.dao.db_common import database
from time_series_detector.algorithm import xgboosting
from time_series_detector import detect
from app.common.errorcode import *
from app.common.common import *
from time_series_detector.common.tsd_errorcode import *
MODEL_PATH = os.path.join(os.path.dirname(__file__), './model/')

import influxdb

import logging
import time

logging.basicConfig(filename='log.txt', level=logging.INFO)

class DetectService(object):

    def __init__(self):
        self.sample_op_obj = sample_op.SampleOperation()
        self.anomaly_op_obj = anomaly_op.AbnormalOperation()
        self.detect_obj = detect.Detect()
        self.client = influxdb.InfluxDBClient(database.INFLUX_HOST, database.INFLUX_PORT,
             database.INFLUX_USER, database.INFLUX_PASSWD, database.INFLUX_DB_NAME)

    # 获取一个时间窗口里的单指标数据
    def get_data(self,begin,end,col_name = 'p1',table_name='m01'):
        begin_str = begin.strftime('%Y-%m-%d %H:%M:%S')
        
        end_str = end.strftime('%Y-%m-%d %H:%M:%S')
        # 取名为value_name的指标
        query_res = self.client.query("select {} from {} where time >= {} and time <= {}".format(col_name,table_name,int(time.mktime(begin.timetuple())*1000),int(time.mktime(end.timetuple())*1000)))
        logging.info("select {} from {} where time >= {} and time <= {}".format(col_name,table_name,int(time.mktime(begin.timetuple())*1000),int(time.mktime(end.timetuple())*1000)))
        logging.info(query_res)
        data = [str(x[1]) for x in query_res.raw['series'][0]['values']]
        return ','.join(data)


    # 获取最近180分钟、一天前、一周前的时间数据
    def get_dataABC(self,current_time, col_name = 'p1',table_name='m01'):
        import datetime
        t = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
        day_ago = t - datetime.timedelta(days=1)
        week_ago = t - datetime.timedelta(days=7)
        beginA = t - datetime.timedelta(minutes=180)
        endA = t
        beginB = day_ago - datetime.timedelta(minutes=180)
        endB = day_ago + datetime.timedelta(minutes=180)
        beginC = week_ago - datetime.timedelta(minutes=180)
        endC = week_ago + datetime.timedelta(minutes=180)
        return self.get_data(beginA,endA,col_name,table_name),self.get_data(beginB,endB,col_name,table_name),self.get_data(beginC,endC,col_name,table_name)

    def __generate_model(self, data, task_id):
        """
        Start train a model

        :param data: Training dataset.
        :param task_id: The id of the training task.
        """
        xgb_obj = xgboosting.XGBoosting()
        # pylint: disable=unused-variable
        ret_code, ret_data = xgb_obj.xgb_train(data, task_id)
        current_timestamp = int(time.time())
        train_op_obj = train_op.TrainOperation()
        if ret_code == 0:
            train_status = "complete"
            params = {
                "task_id": task_id,
                "end_time": current_timestamp,
                "status": train_status,
                "model_name": task_id + "_model"
            }
        else:
            train_status = "failed"
            params = {
                "task_id": task_id,
                "end_time": current_timestamp,
                "status": train_status,
                "model_name": ""
            }
        train_op_obj.update_model_info(params)

    def process_train(self, data):
        """
        Start a process to train model
        :param data: Training dataset.
        """
        sample_params = {
            "trainOrTest": data["trainOrTest"],
            "positiveOrNegative": data["positiveOrNegative"],
            "source": data["source"],
            "beginTime": data["beginTime"],
            "endTime": data["endTime"]
        }
        samples = self.sample_op_obj.sample_query_all(sample_params)
        train_op_obj = train_op.TrainOperation()
        samples_list = []
        positive_count = 0
        negative_count = 0
        for index in samples:
            samples_list.append({"flag": index["flag"], "data": map(int, index["data"].split(','))})
            if index["flag"] == 1:
                positive_count = positive_count + 1
            else:
                negative_count = negative_count + 1
        task_id = str(int(round(time.time() * 1000)))
        train_params = {
            "begin_time": int(time.time()),
            "end_time": int(time.time()),
            "task_id": task_id,
            "status": "running",
            "source": data["source"],
            "sample_num": len(samples_list),
            "postive_sample_num": positive_count,
            "negative_sample_num": negative_count
        }
        if positive_count == 0 or negative_count == 0:
            return build_ret_data(LACK_SAMPLE, "")
        train_op_obj.insert_train_info(train_params)
        try:
            t = threading.Thread(target=self.__generate_model, args=(samples_list, task_id, ))
            t.setDaemon(False)
            t.start()
        except Exception:
            train_status = "failed"
            params = {
                "task_id": task_id,
                "end_time": int(time.time()),
                "status": train_status,
                "model_name": ""
            }
            train_op_obj.update_model_info(params)
        return build_ret_data(OP_SUCCESS, "")

    def __list_is_digit(self, data):
        for index in data:
            try:
                float(index)
            except ValueError:
                return False
        return True

    def __check_param(self, data):
        if ("viewName" not in data.keys()) or ("viewId" not in data.keys()) or ("attrId" not in data.keys()) or ("attrName" not in data.keys()) or ("time" not in data.keys()) or ("dataC" not in data.keys()) or ("dataB" not in data.keys()) or ("dataA" not in data.keys()):
            return CHECK_PARAM_FAILED, "missing parameter"
        return OP_SUCCESS, ""

    def value_predict(self, data):
        # ret_code, ret_data = self.__check_param(data)
        # if ret_code != OP_SUCCESS:
        #     return build_ret_data(ret_code, ret_data)

        ret_code, ret_data = 0,{}
        attr = data["attrIds"][0]

        # 改为从influxDB中读取dataA、dataB、dataC
        for attrId in data["attrIds"]:
            data["dataA"], data["dataB"], data["dataC"] = self.get_dataABC(data["time"],attrId,data["viewId"])
            # print([data["dataA"], data["dataB"], data["dataC"]])
            ret_code, ret_data = self.detect_obj.value_predict(data)
            if ret_data["ret"] == 0:
                attr = attrId
                break

       
        if ret_code == TSD_OP_SUCCESS and ret_data["ret"] == 0:
            anomaly_params = {
                "view_id": data["viewId"],
                "view_name": data["viewId"],
                "attr_id": attr,
                "attr_name": attr,
                "time": data["time"],
                "data_c": data["dataC"],
                "data_b": data["dataB"],
                "data_a": data["dataA"]
            }
            self.anomaly_op_obj.insert_anomaly(anomaly_params)
        return build_ret_data(ret_code, ret_data)

    def rate_predict(self, data):
        # ret_code, ret_data = self.__check_param(data)
        # if ret_code != OP_SUCCESS:
        #     return build_ret_data(ret_code, ret_data)
        
        ret_code, ret_data = 0,{}
        attr = data["attrIds"][0]
        # 改为从influxDB中读取dataA、dataB、dataC
        for attrId in data["attrIds"]:
            data["dataA"], data["dataB"], data["dataC"] = self.get_dataABC(data["time"],attrId,data["viewId"])
            ret_code, ret_data = self.detect_obj.rate_predict(data)
            if ret_data["ret"] == 0:
                attr = attrId
                break
        
        if ret_code == TSD_OP_SUCCESS and ret_data["ret"] == 0:
            anomaly_params = {
                "view_id": data["viewId"],
                "view_name": data["viewId"],
                "attr_id": attr,
                "attr_name": attr,
                "time": data["time"],
                "data_c": data["dataC"],
                "data_b": data["dataB"],
                "data_a": data["dataA"]
            }
            self.anomaly_op_obj.insert_anomaly(anomaly_params)
        return build_ret_data(OP_SUCCESS, ret_data)
