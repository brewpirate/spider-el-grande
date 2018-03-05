# -*- coding: utf-8 -*-
import scrapy

class WeedMapsStrain(scrapy.Item):
    name = scrapy.Field()


class WeedMapsDispensary(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    wmid = scrapy.Field()
    name = scrapy.Field()
    slug = scrapy.Field()
    published = scrapy.Field()
    _type = scrapy.Field()
    package_level = scrapy.Field()
    address = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    zip = scrapy.Field()
    country = scrapy.Field()
    region = scrapy.Field()
    region_slug_path = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    license_type = scrapy.Field()
    is_delivery = scrapy.Field()
    is_recreational = scrapy.Field()
    has_testing = scrapy.Field()
    hours_of_operation = scrapy.Field()

    phone_number = scrapy.Field()
    url = scrapy.Field()
    listing_url = scrapy.Field()
    email = scrapy.Field()
    reviews_count = scrapy.Field()
    rating = scrapy.Field()

    last_updated = scrapy.Field()
    verified_seller = scrapy.Field()
    notes = scrapy.Field()

    note_fields = [
        'license_type',
        'latitude',
        'longitude',
        'is_recreational',
        'published',
        'listing_url',
        'region_slug_path',
        'reviews_count',
        'rating',
        'package_level',
        'last_updated',
        'id',
        'wmid',
        'weedmaps_url',
    ]