FROM python

#WORKDIR /usr/src/app
WORKDIR /app

#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONBUFFERED 1

COPY requirements.txt ./
COPY main.py ./

RUN pip install -r requirements.txt

#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]