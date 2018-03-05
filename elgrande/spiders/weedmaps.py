# -*- coding: utf-8 -*-
import scrapy
from scraper.base_spider import TapHunterBaseSpider
from scraper.items_weedmaps import WeedMapsDispensary
from scraper.spiders.weedmaps_base import WeedmapsBaseSpider
import math
import json
import scraper.utils as utils


class WeedmapsSpider(WeedmapsBaseSpider):
    name = 'weedmaps'
    base_url = 'https://api-g.weedmaps.com/wm/v2/listings?&filter[plural_types][]=dispensaries&page_size=100&size=100'
    export_closeio = False

    custom_settings = {
        'ITEM_PIPELINES': {
            'scraper.pipelines.TapHunterImporterPipeline': 400,
        },
        # 10 second delay minimum. Default 5
        'AUTOTHROTTLE_START_DELAY': 10,
        # max delay of 360 seconds per group of requests. Default 60
        'AUTOTHROTTLE_MAX_DELAY': 360,
        # lower the parallel requests ratio to not hammer the server. Default 1.0
        'AUTOTHROTTLE_TARGET_CONCURRENCY': .4,
    }

    # Get a page of data and pass to dispensary_range for paging
    def start_requests(self):
        yield scrapy.Request(url=self.base_url, callback=self.dispensary_range, meta={'dont_cache': False})

    # Calculate how many pages we are going to need to crawl.
    def dispensary_range(self, response):
        dispensaries_raw = json.loads(response.body)
        total_listings = dispensaries_raw['meta']['total_listings']
        pages = int(math.ceil(total_listings / 100))

        crawl_dis_pages = xrange(0, pages)
        for dis_page in crawl_dis_pages:
            crawl_url = self.base_url + '&page={}'.format(dis_page)
            yield scrapy.Request(url=crawl_url, callback=self.dispensary_parse, meta={'dont_cache': False})

    def dispensary_parse(self, response):
        dispensaries_raw = json.loads(response.body)
        for jah in dispensaries_raw['data']['listings']:
            source_url = 'https://api-g.weedmaps.com/wm/web/v1/listings/{}/menu?type=dispensary'.format(jah['slug'])
            yield scrapy.Request(url=source_url, callback=self.dispensary_details_parse, meta={'dont_cache': False})