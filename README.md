# 读我

- 补充dockerfile以及docker-compose.yml (已完成)
- 集成influxDB以及导入csv的服务至docker-compose中(完成)
- 修改所有相关接口，改成从influxDB中读取数据(已完成)
- 集成多指标检测(初步完成)
- 改进特征工程
- 集成prophet

## 编译
需要先安装nodejs(版本大于等于10)和docker和docker-compose
```bash
# 先进入uweb目录执行
npm install

# 然后回到根目录执行
sh build.sh
```

## 运行
```bash
docker-compose up -d
```

## 使用说明

### 导入csv
打开localhost:8080, 上传new_data.csv文件

### 多指标异常检测

- 异常样例
```bash
curl -X POST localhost/PredictRate -d '{"viewId":"measurementName","attrIds":["p1","p2","p3","p4","p5"], "window":180, "time":"2016-10-18 02:28:00"}'

{"msg": "\u64cd\u4f5c\u6210\u529f", "code": 0, "data": {"p": "0.0014255302", "ret": 0}}
```

- 非异常样例
```bash
curl -X POST localhost/PredictRate -d '{"viewId":"measurementName","attrIds":["p1","p2","p3","p4","p5"], "window":180, "time":"2016-10-16 02:28:00"}'

{"msg": "\u64cd\u4f5c\u6210\u529f", "code": 0, "data": {"p": "1", "ret": 1}}
```

## 接口说明

### 一、HTTP接口

#### 1、量值检测

* API： POST /{ip}:{port}/PredictValue
* 功能说明：根据参考数据检测最近一个数据点是否异常
* 请求参数request：
	
```json
{
    "viewId":"m01",
    "attrIds":["p1"],
    "window":180,
    "time":"2018-10-17 17:28:00"
}
```

* request字段说明：

| 名称  | 类型 |必填| 默认值 | 说明 |
| --- | --- | --- |---- | --- |
| viewId| string| 是|m01|指标集ID, 即influxdb中的measurement名 |
| attrIds| list | 是| p1|指标ID的列表, 即influxdb中对应表的field名的list |
| window|  int| 是| 无|窗口值，目前支持180|
| time|  string| 是| 无|待检测点的时间标识，即dataA的最后一个点，格式："yyyy-MM-dd HH:mm:ss"|


* 详情参数response：
```json
{
    "code":0,
    "msg":"操作成功",
    "data":
    {
        "ret":0,
        "p":"0.05",
    }
}
```

* response 字段说明：

| 名称  | 类型  | 说明 |
|---|---|---|
| code | int | 返回码。0:成功；非0:失败 |
| msg | string | 返回消息 |
| ret | int | 检测结果是否异常。0:异常；1:正常 |
| p | string | 概率值，值越小，判定为异常的置信度越高 |

#### 2、率值检测

* API： POST /{ip}:{port}/PredictRate
* 功能说明：根据参考数据检测最近一个数据点是否异常
* 请求参数request：
	
```json
{
    "viewId":"m01",
    "attrIds":["p1"],
    "window":180,
    "time":"2018-10-17 17:28:00"
}
```

* request字段说明：

| 名称  | 类型 |必填| 默认值 | 说明 |
| --- | --- | --- |---- | --- |
| viewId| string| 是|m01|指标集ID, 即influxdb中的measurement名 |
| attrIds| list| 是| p1|指标ID的列表, 即influxdb中对应表的field名的list |
| window|  int| 是| 无|窗口值，目前支持180|
| time|  string| 是| 无|待检测点的时间标识，即dataA的最后一个点，格式："yyyy-MM-dd HH:mm:ss"|


* 详情参数response：
```json
{
    "code":0,
    "msg":"操作成功",
    "data":
    {
        "ret":0,
        "p":"0.05",
    }
}
```

* response 字段说明：

| 名称  | 类型  | 说明 |
|---|---|---|
| code | int | 返回码。0:成功；非0:失败 |
| msg | string | 返回消息 |
| ret | int | 检测结果是否异常。0:异常；1:正常 |
| p | string | 概率值，值越小，判定为异常的置信度越高 |

## 数据

### 异常样例:

```bash
curl -X POST localhost/PredictRate -d '{"viewId":"measurementName","attrIds":["p1","p2","p3","p4","p5"], "window":180, "time":"2016-10-18 02:28:00"}'

{"msg": "\u64cd\u4f5c\u6210\u529f", "code": 0, "data": {"p": "0.0014255302", "ret": 0}}

```