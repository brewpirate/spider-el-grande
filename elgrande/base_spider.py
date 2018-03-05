# -*- coding: utf-8 -*-
import scrapy
from elgrande.utils import ElGrandeFileLoader


class ElGrandeBaseSpider(scrapy.Spider):
    name = None
    allowed_domains = []
    start_urls = []

    output_file = False
    ignore_source = None

    # Close.io Custom Field "1.4 Lead Source"
    lead_source = None
    thFileLoader = ElGrandeFileLoader()

    is_DEBUG = False

    def start_requests(self):
        pass

    def parse(self, response):
        pass