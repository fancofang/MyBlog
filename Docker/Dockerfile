FROM python:3.7

RUN apt-get update

RUN pip3 install --upgrade pip \
    && pip3 install pipenv \
    && apt-get install -y nginx \
    && apt-get install -y vim \
    && apt-get install -y supervisor

WORKDIR /etc/nginx/sites-enabled
RUN rm *

WORKDIR /usr/src/app
COPY . .
ADD visorblog.conf /etc/supervisor/conf.d/
ADD blog.conf /etc/nginx/sites-enabled/


RUN pipenv install --system --deploy --dev --ignore-pipfile

CMD ["nginx", "-g", "daemon off;"]