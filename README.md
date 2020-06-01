# 读我

- 补充dockerfile以及docker-compose.yml (已完成)
- 集成influxDB以及导入csv的服务至docker-compose中
- 修改所有相关接口，改成从influxDB中读取数据
- 集成多指标检测
- 改进特征工程

## 编译
需要先安装docker和docker-compose
```bash
sh build.sh
```

## 运行
```bash
docker-compose up -d
```
