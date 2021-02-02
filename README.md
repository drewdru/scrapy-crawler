# Scrapy site crawler

## Build
```bash
pip install -r requirements.txt
```
### install selenium
```bash
sudo apt-get install firefox
curl -s "https://api.github.com/repos/mozilla/geckodriver/releases/latest" \
    | grep browser_download_url \
    | grep linux64 \
    | cut -d '"' -f 4 \
    | xargs wget -O /tmp/geckodriver.tar.gz \
    && rm -rf /opt/geckodriver \
    && tar -C /opt -zxf /tmp/geckodriver.tar.gz \
    && rm /tmp/geckodriver.tar.gz \
    && chmod 755 /opt/geckodriver \
    && ln -fs /opt/geckodriver /usr/bin/geckodriver \
    && touch /usr/bin/geckodriver.log \
    && chmod 777 /usr/bin/geckodriver.log
```

## Run
```bash
scrapy runspider roszdravnadzor_xml.py
scrapy runspider roszdravnadzor.py
python roszdravnadzor_opendata_parser.py
scrapy runspider asna_spider.py
```