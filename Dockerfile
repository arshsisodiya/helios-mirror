FROM FROM arshsisodiya/helioskirepo:public

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m itsmearsh
USER itsmearsh

CMD ["bash", "start.sh"]
