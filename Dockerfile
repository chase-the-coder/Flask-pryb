FROM python:3.7.2-stretch

WORKDIR /app

ADD . /app

RUN pip install --upgrade pip

RUN pip install uwsgi

RUN pip install -r requirements.txt

RUN apt-get update

RUN apt-get upgrade -y

RUN apt-get install -y build-essential xorg libssl-dev libxrender-dev wget tar

RUN apt-get install -y libssl1.0-dev

RUN wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.3/wkhtmltox-0.12.3_linux-generic-amd64.tar.xz

RUN tar vxf wkhtmltox-0.12.3_linux-generic-amd64.tar.xz

RUN cp wkhtmltox/bin/wk* /usr/local/bin/

# RUN wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.xenial_amd64.deb

# RUN gdebi --n wkhtmltox_0.12.5-1.xenial_amd64.deb

CMD ["uwsgi","app.ini"]
