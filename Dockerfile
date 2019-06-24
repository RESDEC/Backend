FROM python:2.7.10
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir numpy && \
    pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py migrate
ENTRYPOINT ["bash"]


