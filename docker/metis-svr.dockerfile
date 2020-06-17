FROM codewilling/python27-ci

USER root

COPY requirements.txt /metis/requirements.txt
WORKDIR /metis

RUN pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/
RUN pip install --upgrade numpy -i https://mirrors.aliyun.com/pypi/simple/
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

RUN pip install influxdb -i https://mirrors.aliyun.com/pypi/simple/

ADD . /metis

ENV PYTHONPATH $PYTHONPATH:/metis

ENTRYPOINT ["python","app/controller/manage.py","runserver","0.0.0.0:8080"]