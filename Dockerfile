FROM python:3.6

WORKDIR /usr/src/app

COPY . .

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

CMD python manage.py migrate && daphne -b 0.0.0.0 -p 8000 sp.asgi:application
