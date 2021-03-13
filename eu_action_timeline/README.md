# Scrap [Timeline of EU action](https://ec.europa.eu/info/live-work-travel-eu/coronavirus-response/timeline-eu-action_en)

## Run the `eu-timeline` spider

1. install the dependencies from [`eu_action_timeline/requirements.txt`](/eu_action_timeline/requirements.txt):
   ```
   make install-scrapy-dependencies
   ```
2. run the [`splash`](https://github.com/scrapinghub/splash) container for JS rendering:
   ```shell
   make start-splash
   ```

3. go inside the `eu_action_timeline` folder and run the scrapper with:
   ```shell
   scrapy crawl eu-timeline -o output.json
   ```
   > You can use another name for `output.json`