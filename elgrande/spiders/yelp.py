# -*- coding: utf-8 -*-
import scrapy
import datetime
import re
import elgrande.settings as settings
from elgrande import utils
from elgrande.base_spider import ElGrandeBaseSpider
from elgrande.items_yelp import YelpLocation
from w3lib.html import remove_tags
from datetime import date


class YelpBaseSpider(ElGrandeBaseSpider):
    name = 'yelp'
    allowed_domains = ['yelp.com']
    start_urls = ['https://www.yelp.com/']
    base_url = 'https://www.yelp.com'
    lead_source = 'Yelp'

    ignore_source = settings.SCRIPT_PATH + 'data/yelp_ignore_categories.list'
    ignore_chain = settings.SCRIPT_PATH + 'data/yelp_ignore_chain.list'
    yelp_busted = settings.SCRIPT_PATH + 'data/yelp_busted.debug'

    handle_httpstatus_list = [301, 302]

    CRAWL_SEARCH_TERMS = []
    is_booze = False
    custom_settings = {
        'ITEM_PIPELINES': {
            'elgrande.pipelines.ElGrandePipeline': 400,
            'elgrande.pipelines.RunLoggerPipeline': 500,
        },
        # 10 second delay minimum. Default 5
        'AUTOTHROTTLE_START_DELAY': 30,
        # max delay of 360 seconds per group of requests. Default 60
        'AUTOTHROTTLE_MAX_DELAY': 260,
        # lower the parallel requests ratio to not hammer the server. Default 1.0
        'AUTOTHROTTLE_TARGET_CONCURRENCY': .6,
    }

    def __init__(self, slug=None, search=None, state=None, zip=None, debug=False, *args, **kwargs):
        super(YelpBaseSpider, self).__init__(*args, **kwargs)
        self.CRAWL_CUSTOM_LOC = slug
        self.CRAWL_SEARCH_TERMS = search
        self.CRAWL_CUSTOM_SEARCH_REGION = state
        self.CRAWL_CUSTOM_SEARCH_ZIP = zip
        self.is_DEBUG = debug
        if search and 'Bar' in search:
            self.is_booze = True

        if self.CRAWL_CUSTOM_SEARCH_REGION:
            self.output_file = '{}/output/{}.{}.{}.csv'.format(settings.SCRIPT_BASE_PATH, self.name,
                                                               self.CRAWL_CUSTOM_SEARCH_REGION,
                                                               datetime.datetime.today().strftime('%Y-%m-%d'))
        self.processed_urls = set()
        self.ignore_list = self.thFileLoader.get_list(self.ignore_source)
        self.ignore_chain_list = self.thFileLoader.get_list(self.ignore_chain)

    def clean_url(self, url):
        """
        Remove search term from URL, you no track Yelp!
        :param url: dirty crawl url with tracking attr
        :return: clean url
        """
        cleaned_search_term = url.split('?osq=')
        if cleaned_search_term[0][1:] == '/':
            cleaned_search = cleaned_search_term[0][1:]
        else:
            cleaned_search = cleaned_search_term[0]
        return cleaned_search

    def start_requests(self):
        # User Specified Location
        if self.CRAWL_CUSTOM_LOC:
            yield scrapy.Request(url='{}biz{}'.format(self.base_url, self.CRAWL_CUSTOM_LOC), callback=self.parse_location, meta={'dont_cache': True})

        # User Specified Zip or Runner
        elif self.CRAWL_CUSTOM_SEARCH_ZIP:
            for category in self.CRAWL_SEARCH_TERMS:
                yield scrapy.Request(
                    url='{}/search?find_desc={}&find_loc={}'.format(self.base_url, category, self.CRAWL_CUSTOM_SEARCH_ZIP),
                    callback=self.parse_listing, meta={'dont_cache': True})
        else:
            zipcode_json = utils.get_usa_zipcodes(state=self.CRAWL_CUSTOM_SEARCH_REGION)
            for state in zipcode_json:
                for zip in zipcode_json[state]:
                    if self.is_DEBUG:
                        print '=============================='
                        print zip
                    for category in self.CRAWL_SEARCH_TERMS:
                        yield scrapy.Request(
                            url='{}/search?find_desc={}&find_loc={}'.format(self.base_url, category, zip['zipcode']),
                            callback=self.parse_listing, meta={'dont_cache': True})

    def parse_listing(self, response):
        # TODO: remove after a full run to purge cache
        # Remove cached versions of listings
        utils.delete_cache(response, self.name)

        if response.status in settings.HTTPCACHE_IGNORE_HTTP_CODES:
            print "############################################"
            print u'Deleting cache for {} HTTP {}'.format(response.url, response.status)
            utils.delete_cache(response, self.name)
            yield scrapy.Request(url=response.url, callback=self.parse_listing, dont_filter=True, meta={'dont_cache': True})
            return

        result_sets = response.xpath('//ul[@class="ylist ylist-bordered search-results"]')

        for result in result_sets:
            # Grab the first list with actual records. F You Yelp.
            if len(result.xpath('.//li[@class="regular-search-result"]').extract()):
                for location in result.xpath('.//li'):
                    # Check for AD listing and skip which by nature will be monitored more closely
                    if location.xpath('.//span[@class="yloca-tip"]/text()').extract_first() == 'Ad':
                        continue
                    biz = location.xpath('.//span/a[@data-analytics-label="biz-name"]/@href').extract()
                    if len(biz):
                        # Check for 'hot and new' icon representing recently added businesses. 'is_new_business' will be
                        # sent to the callback as part of the 'meta' and recorded on the object there. Yelp only
                        # includes 'hot and new' on the search results page.
                        new_business_check = location.xpath('.//li[@class="tag-18x18_flame-dd5114"]')
                        meta = {'dont_cache': False, 'is_new_business': False}
                        if new_business_check:
                            meta['is_new_business'] = True

                        # Check if location has been processed
                        crawl_url = self.base_url + self.clean_url(biz[0])
                        if crawl_url not in self.processed_urls:
                            self.processed_urls.add(crawl_url)
                            yield scrapy.Request(crawl_url, callback=self.parse_location, meta=meta)

        # Extract all the "next" links
        for link in response.css('.next').css('.pagination-links_anchor').xpath('.//@href'):
            url = link.extract()
            yield scrapy.Request(self.base_url + self.clean_url(url), callback=self.parse_listing, meta={'dont_cache': True})

    def parse_location(self, response):
        item = YelpLocation()
        # Check if location is closed
        has_alert = response.css('div.alert-error').xpath('.//p/b/text()').extract()
        if has_alert:
            if utils.clean_item(has_alert) == "Yelpers report this location has closed.":
                item['is_closed'] = True
                item['status'] = 'Out of Business'

        biz_header_block = response.css('.biz-page-header')

        name = biz_header_block.xpath('//h1/text()').extract()
        item['name'] = utils.clean_item(name)

        # If we see Darwin or No Name then you are busted. Nuke the cache and try again without the proxy
        if not item['name'] or response.css('div.maintenance-darwin') or response.status != 200:
            print '=============== BUSTED No Name ======================'
            print 'You done got caught, bad proxy! Nuking cache and trying again, hang tight.'
            print '{}: {}'.format(self.name, response.url)
            # log the site
            self.thFileLoader.add_to_list(self.yelp_busted, response.url)
            # Nuke the cache so when we retry we can get the live site
            utils.delete_cache(response, self.name)

            if self.is_DEBUG:
                print response.xpath('//html').extract()

            # Let's try this again shall we? dont_filter=True bypasses Scrapys dup protection
            yield scrapy.Request(url=response.url, callback=self.parse_location, dont_filter=True)
            return

        # Extract photo count
        photo_parent = response.css('.see-more')
        photo_text = photo_parent.xpath('./text()').extract()
        for blob in photo_text:
            if len(re.findall(r'\d+', blob)):
                item['photo_count'] = re.findall(r'\d+', blob)[0]

        # Retrieve owner info
        owner_blob = response.css('.biz-owner-reply').css('div.media-story').extract()
        if owner_blob:
            item['owner_replies'] = len(owner_blob)
            for text in owner_blob:
                if 'owner_name' not in item:
                    if text.find("Business Owner") != -1:
                        item['owner_name'] = text.split("from ")[1].split(" of")[0]

        # Owner reply text - non-truncated
        item['owner_replies_text'] = ''
        owner_text_short_list = response.css('.biz-owner-reply::text').extract()
        for text in owner_text_short_list:
            text = text.replace("  ", "").replace("\n", "")
            if len(text):
                item['owner_replies_text'] = item['owner_replies_text'] + text + '\n '

        # Owner reply text - truncated
        owner_text_list = response.css('.biz-owner-reply').css('.comment-truncated').extract()
        if len(owner_text_list):
            for text in owner_text_list:
                if text.find(u'\u2026') != -1:
                    text = text.split(u'\u2026')[1]
                text = remove_tags(text).replace("  ", "").replace("\n", "")
                if len(text):
                    item['owner_replies_text'] = item['owner_replies_text'] + text + '\n '

        claimed = biz_header_block.css('.claim-status_teaser::text').extract()
        item['claim'] = True if utils.clean_item(claimed) == 'Claimed' else False

        reviews_score = biz_header_block.css('div.rating-very-large').xpath('@title').extract()
        item['reviews_score'] = utils.clean_item(reviews_score)

        reviews_count = biz_header_block.css('div.biz-rating-very-large').css('span.review-count::text').extract()
        item['reviews_count'] = utils.clean_item(reviews_count)

        biz_info_block = biz_header_block.css('.biz-main-info')

        categories = biz_info_block.css('.category-str-list').xpath('.//a/text()').extract()

        # Exclude Rules
        # ============================

        # If they have an ignored category F* it, skip it!
        for category in categories:
            if category in self.ignore_list:
                raise StopIteration

        # Set some chains as bad fit
        print name[0].strip()

        if name[0].strip() in self.ignore_chain_list:
            if item['status']:
                item['status'] = ', '.join([item['status'], 'Bad Fit'])
            else:
                item['status'] = 'Bad Fit'

        # Has to be at least 1 search term in categories else we bail
        if len(set(categories).intersection(self.CRAWL_SEARCH_TERMS)) == 0:
            raise StopIteration

        print '###### Matched Categories: {}'.format(len(set(categories).intersection(self.CRAWL_SEARCH_TERMS)))

        item['categories'] = utils.clean_item(set(categories), ', ')

        # Remove DJs
        if len(categories) == 2 and 'DJs' in categories and 'Karaoke' in categories:
            if item['status']:
                item['status'] = ', '.join([item['status'], 'Bad Fit'])
            else:
                item['status'] = 'Bad Fit'


        address_string = response.css('.mapbox').css('.street-address').xpath('.//address/text()').extract()
        item['address'] = utils.clean_item(address_string)

        cross_streets = response.xpath('//span[@class="cross-streets"]/text()').extract()
        if len(cross_streets):
            item['cross_streets'] = utils.clean_item(cross_streets)

        neighborhood = response.xpath('//span[@class="neighborhood-str-list"]/text()').extract()
        if neighborhood:
            item['neighborhood'] = utils.clean_item(neighborhood)

        address_1 = response.xpath('//span[@itemprop="streetAddress"]/text()').extract()
        item['address_1'] = utils.clean_item(address_1)

        # address_2
        city = response.xpath('//span[@itemprop="addressLocality"]/text()').extract()
        item['city'] = utils.clean_item(city)

        zip = response.xpath('//span[@itemprop="postalCode"]/text()').extract()
        item['zip'] = utils.clean_item(zip)

        state = response.xpath('//span[@itemprop="addressRegion"]/text()').extract()
        item['state'] = utils.clean_item(state)

        country = response.xpath('//meta[@itemprop="addressCountry"]/@content').extract()
        item['country'] = utils.clean_item(country)

        phone_number = response.xpath('//span[@class="biz-phone"]/text()').extract()
        item['phone'] = utils.clean_item(phone_number)

        website = response.css('.biz-website').xpath('.//a/text()').extract()
        item['website'] = utils.clean_item(website)

        hours_parts = response.css('table.hours-table').css('tr')
        hours_list = []
        for hour in hours_parts:
            day = hour.xpath('.//th[@scope="row"]/text()').extract_first()
            the_day = None

            if day == 'Sun':
                the_day = 'hours_sunday'
            elif day == 'Mon':
                the_day = 'hours_monday'
            elif day == 'Tue':
                the_day = 'hours_tuesday'
            elif day == 'Wed':
                the_day = 'hours_wednesday'
            elif day == 'Thu':
                the_day = 'hours_thursday'
            elif day == 'Fri':
                the_day = 'hours_friday'
            elif day == 'Sat':
                the_day = 'hours_saturday'
            if the_day:
                hours = hour.xpath('.//td/*/text()').extract()
                item[the_day] = utils.clean_item(hours[:2], '-')
                hours_list.append(u'{}: {}'.format(day, item[the_day]))

        if hours_list:
            item['hours'] = utils.clean_item(hours_list, '\\n')

        biz_description = response.css('.js-from-biz-owner').xpath('.//p/text()').extract()
        item['biz_description'] = utils.clean_item(biz_description)

        price_range = response.css('dd.price-description::text').extract()
        item['price_range'] = utils.clean_item(price_range)

        biz_info_dump = response.css('div.short-def-list').xpath('.//dl')
        biz_info_parts = []
        for info in biz_info_dump:
            info_key = utils.clean_item(info.xpath('.//dt[@class="attribute-key"]/text()').extract())
            info_value = utils.clean_item(info.xpath('.//dd/text()').extract())

            # If we are looking for booze and they don't serve booze F* it, skip it!
            if info_key.lower() == 'alcohol' and info_value.lower() == 'no' and self.is_booze:
                raise StopIteration

            biz_info_parts.append(u'{}: {}'.format(info_key, info_value))

        if biz_info_parts:
            item['biz_info'] = utils.clean_item(biz_info_parts, ', ')

        item['source_url'] = response.url
        item['yelp_url'] = response.url
        item['notes'] = utils.build_notes(item)

        item['open_date'] = ''
        if response.meta['is_new_business']:
            # If 'hot and new' icon is present in the Yelp search, records today's date on the object
            item['open_date'] = unicode(date.today())

        item['menu_provider'] = None

        # Test for Menu
        menu_block = response.css('.menu-link-block')
        menu = menu_block.xpath('.//@href').extract()

        # Self Hosted Menu?
        if len(menu) and "biz_redir" in menu[0]:
            item['menu_provider'] = 'External/Self Hosted'
            menu = None

        # Menu? Follow the yellow brick road
        if menu:
            yield scrapy.Request(self.base_url + menu[0], callback=self.parse_menu, meta={'dont_cache': False, 'item': item})
        else:
            print '============= {} ============='.format(item['menu_provider'])
            yield item

    def parse_menu(self, response):
        item = response.meta['item']

        # Find menu provider
        menu_footer = response.css('.menu-footnotes')
        menu_provider = menu_footer.css('.menu-provider-attribution').xpath('.//@alt').extract()

        # Set provider
        if len(menu_provider):
            item['menu_provider'] = menu_provider[0]
        else:
            item['menu_provider'] = 'No provider Attribution'

        print '============= {} ============='.format(item['menu_provider'])
        yield item
