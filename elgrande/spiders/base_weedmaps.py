# -*- coding: utf-8 -*-
import scrapy
from elgrande.base_spider import ElGrandeBaseSpider
from elgrande.items_weedmaps import WeedMapsDispensary
import json
import scraper.utils as utils
import elgrande.settings as settings


class WeedmapsBaseSpider(ElGrandeBaseSpider):
    allowed_domains = ['weedmaps.com']
    base_url = 'https://www.weedmaps.com'
    handle_httpstatus_list = [404]
    export_closeio = False
    output_file = False

    ignore_source = settings.SCRIPT_PATH + 'data/weedmaps_ignore.list'

    def dispensary_parse(self, response):
        dispensaries_raw = json.loads(response.body)
        for jah in dispensaries_raw['data']['listings']:
            source_url = 'https://api-g.weedmaps.com/wm/web/v1/listings/{}/menu?type=dispensary'.format(jah['slug'])
            yield scrapy.Request(url=source_url, callback=self.dispensary_details_parse, meta={'dont_cache': False})

    def dispensary_details_parse(self, response):
        # Hey we found data! Get Some!!
        if response.status == 200:
            dispensary_raw = json.loads(response.body)
            dispensary_listing = dispensary_raw['listing']

            item = WeedMapsDispensary()

            if dispensary_listing['_type'] == 'dispensary':
                item['id'] = dispensary_listing['id']
                item['wmid'] = dispensary_listing['wmid']
                item['name'] = dispensary_listing['name']
                item['slug'] = dispensary_listing['slug']
                item['published'] = dispensary_listing['published']
                item['_type'] = dispensary_listing['_type']
                item['package_level'] = dispensary_listing['package_level']
                item['address'] = dispensary_listing['address']
                item['city'] = dispensary_listing['city']
                item['state'] = dispensary_listing['state']
                item['zip'] = dispensary_listing['zip_code']
                item['region'] = dispensary_listing['region']
                item['region_slug_path'] = dispensary_listing['region_slug_path']
                item['latitude'] = dispensary_listing['latitude']
                item['longitude'] = dispensary_listing['longitude']
                item['license_type'] = dispensary_listing['license_type']
                item['is_delivery'] = dispensary_listing['is_delivery']
                item['is_recreational'] = dispensary_listing['is_recreational']
                item['has_testing'] = dispensary_listing['has_testing']
                if dispensary_listing.get('hours_of_operation'):
                    item['hours_of_operation'] = str(dispensary_listing['hours_of_operation'])
                item['phone_number'] = dispensary_listing['phone_number']
                item['url'] = dispensary_listing['listing_url']
                item['listing_url'] = dispensary_listing['listing_url']
                item['email'] = dispensary_listing['email']
                item['reviews_count'] = dispensary_listing['reviews_count']
                item['rating'] = dispensary_listing['ranking']


                if dispensary_raw.get('menu_updated'):
                    item['last_updated'] = dispensary_raw['menu_updated']

                item['verified_seller'] = dispensary_listing['verified_seller']

                if self.export_closeio:
                    item['notes'] = utils.build_notes(item)

                yield item

        # 404 Add to ignore list since we do not have a valid location
        elif response.status in [404]:
            self.thFileLoader.add_to_list(self.ignore_source, response.meta['weedmaps_id'])

        # All other errors delete the cache so we can attemt again for the future.
        else:
            utils.delete_cache(response, self.name)