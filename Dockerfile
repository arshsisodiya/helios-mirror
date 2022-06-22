FROM arm64

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m mjwebhacks
USER mjwebhacks

CMD ["bash", "start.sh"]
