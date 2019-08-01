FROM python
RUN apt-get update && \
  apt-get install sqlite3 -y && \
  apt-get install vim -y
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir numpy && \
    pip install --no-cache-dir Django && \
    pip install --no-cache-dir -r requirements.txt && \
    pip uninstall -y numpy  && \
    pip install numpy
COPY . .
RUN python /usr/src/app/manage.py migrate
ENTRYPOINT [ "python","/usr/src/app/manage.py" ]

