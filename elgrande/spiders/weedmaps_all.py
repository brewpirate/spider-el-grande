# -*- coding: utf-8 -*-
import scrapy
from elgrande.spiders.base_weedmaps import WeedmapsBaseSpider
import random


class WeedmapsAllSpider(WeedmapsBaseSpider):
    name = 'weedmaps-all'
    export_closeio = False

    custom_settings = {
        'ITEM_PIPELINES': {
            'elgrande.pipelines.ElGrandeImporterPipeline': 400,
        },
        # It's there or it isn't so no need to retry with Weedmaps
        'RETRY_TIMES': 1,
    }

    # HARDCODED START AND STOP LOCATION IDS, USE ATTRIBUTES TO OVERRIDE
    CRAWL_START = 1
    CRAWL_END = 60000

    def __init__(self, start=None, end=None, debug=False, *args, **kwargs):
        super(WeedmapsAllSpider, self).__init__(*args, **kwargs)
        self.CRAWL_START = int(start or self.CRAWL_START)
        self.CRAWL_END = int(end or self.CRAWL_END)

    def start_requests(self):
        ignore_list = self.thFileLoader.get_list(self.ignore_source)

        crawl_range = range(self.CRAWL_START, self.CRAWL_END)

        while len(crawl_range) > 0:
            location_id = random.choice(list(crawl_range))
            if location_id not in ignore_list:
                crawl_url = 'https://api-g.weedmaps.com/wm/web/v1/listings/{}/menu?type=dispensary'.format(location_id)
                meta = {
                    'dont_cache': False,
                    'weedmaps_id': unicode(location_id),
                    'weed_url': crawl_url
                }
                yield scrapy.Request(url=crawl_url, callback=self.dispensary_details_parse, meta=meta)
            crawl_range.remove(location_id)
