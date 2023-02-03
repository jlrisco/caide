FROM python:3.8.7

WORKDIR /forecaster

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./src/deployer.py"]
