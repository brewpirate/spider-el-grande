# -*- coding: utf-8 -*-
import scrapy


class YelpLocation(scrapy.Item):
    name = scrapy.Field()
    address = scrapy.Field()
    phone = scrapy.Field()
    website = scrapy.Field()
    url = scrapy.Field()
    facebook = scrapy.Field()
    twitter = scrapy.Field()
    status = scrapy.Field()

    address_1 = scrapy.Field()
    address_2 = scrapy.Field()
    city = scrapy.Field()
    zip = scrapy.Field()
    state = scrapy.Field()
    country = scrapy.Field()

    categories = scrapy.Field()
    hours_sunday = scrapy.Field()
    hours_monday = scrapy.Field()
    hours_tuesday = scrapy.Field()
    hours_wednesday = scrapy.Field()
    hours_thursday = scrapy.Field()
    hours_friday = scrapy.Field()
    hours_saturday = scrapy.Field()
    hours = scrapy.Field()

    source_url = scrapy.Field()
    notes = scrapy.Field()

    # optional but I got zee data
    reviews_count = scrapy.Field()
    reviews_score = scrapy.Field()
    claim = scrapy.Field()
    price_range = scrapy.Field()
    biz_info = scrapy.Field()
    biz_description = scrapy.Field()
    cross_streets = scrapy.Field()
    neighborhood = scrapy.Field()
    is_closed = scrapy.Field()
    yelp_url = scrapy.Field()
    reviews_count = scrapy.Field()
    reviews_score = scrapy.Field()
    photo_count = scrapy.Field()
    claim = scrapy.Field()
    owner_name = scrapy.Field()
    owner_replies = scrapy.Field()
    owner_replies_text = scrapy.Field()
    open_date = scrapy.Field()

    note_fields = [
        'is_closed',
        'source_url',
        'claim',
        'location_type',
        'reviews_count',
        'reviews_score',
        'price_range',
        'hours',
        'cross_streets',
        'neighborhood',
        'categories',
        'reviews',
        'beers',
        'biz_description',
        'biz_info',
        'owner_name',
        'owner_replies_text'
    ]