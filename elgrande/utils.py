# -*- coding: utf-8 -*-
import settings
import json

class ElGrandeFileLoader():

    def get_list(self, file):
        try:
            my_list = open(file, 'rb')
        except IOError:
            return []
        list = my_list.readlines()
        my_list.close()

        # remove linebreaks
        for i, s in enumerate(list):
            list[i] = s.strip()
        return list

    def add_to_list(self, file, value):
        ignore_list = open(file, 'a+')
        ignore_list.write(value + '\n')
        ignore_list.close()
        return True

    def load_data(self, spider, list=None):
        if not list:
            list = spider.crawler_source
        return self.get_list(list)

    def load_ignore_list(self, spider, list=None):
        if not list:
            list = spider.crawler_source
        return self.get_list(list)


def get_usa_zipcodes(state=None):
    with open(settings.USA_ZIPCODES_SOURCE) as data_file:
        data = json.load(data_file)
    if state and data[state]:
        return {state: data[state]}
    else:
        return data


def get_custom_zipcodes():
    with open(settings.CUSTOM_ZIPCODES_SOURCE) as data_file:
        data = json.load(data_file)
    return data

def build_notes(item):
    """
    Creates a custom note field based on optional fields scraped from the spider.
    Args:
        item: Spider Item

    Returns: Unicode version of notes
    """
    custom_notes = {}
    custom_note = u''
    # TODO: Spider Note_list
    if item.get('note_fields'):
        note_fields = item.get('note_fields')
    else:
        note_fields = [
            'is_closed',
            'facebook',
            'twitter',
            'hours',
            'source_url',
            'location_type',
            'categories',
            'reviews',
            'claim',
            'beers',
            'reviews_count',
            'reviews_score',
            'price_range',
            'biz_description',
            'biz_info',
            'cross_streets',
            'neighborhood',
            'owner_name',
            'owner_replies_text',
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

    for field in note_fields:
        if item.get(field):
            custom_notes[field] = item[field]

    for note_k, note_v in custom_notes.iteritems():
        if isinstance(note_v, (list, tuple)) and not isinstance(note_v, basestring):
            note_v = ', '.join(note_v)

        # Remove linebreaks for export to csv
        if isinstance(note_v, (basestring)):
            note_v = note_v.replace('\n', '\\n').replace('\r', '\\r')
        custom_note = custom_note + u'{}: {} \\n'.format(note_k, note_v)

    return custom_note


def clean_item(item, separator=None):
    if not separator:
        separator = ' '
    if len(item):
        return unicode(separator.join([i.replace(u'\xb7', u'').strip() for i in item])).strip()
    else:
        return None


def delete_cache(response, spider):
    """
    Deletes Cache for a url so next time its crawled it can be checked. Useful for Robot Captcha
    :param response: scraper Response
    :param spider: name of the spider
    """
    from scrapy.utils import request
    import shutil
    import os

    basepath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fingerprint = request.request_fingerprint(response.request)
    path = '{}/.scrapy/httpcache/{}/{}/{}/'.format(basepath, spider, fingerprint[:2], fingerprint)
    try:
        shutil.rmtree(path)
        print '========= Deleted: {} ========='.format(fingerprint)
    except:
        None


def merge_output(spider):
    """
    Merges multiple output files for a crawler into a single csv file to be imported
    :param spider:
    :return:
    """
    import os
    import zipfile
    import fileinput
    import glob
    import datetime

    print '*******************************'
    print 'Merge Output Files'
    print '*******************************'

    search_file_part = '{}/output/{}'.format(settings.SCRIPT_BASE_PATH, spider.name)
    output_files = glob.glob(search_file_part + '*.csv')
    date_today = datetime.datetime.today().strftime('%Y-%m-%d.%S%f')
    new_output_data = set()
    new_header = []

    if output_files:
        spider_archive = zipfile.ZipFile('{}/output/archive_{}_{}.gz'.format(settings.SCRIPT_BASE_PATH, spider.name, date_today), "w")

        # Process all output parts and remove duplicates
        for line in fileinput.input(output_files):
            if fileinput.isfirstline() and not len(new_header):
                line = line\
                    .replace('lead_source', '1.4 Lead Source')\
                    .replace('yelp_url', 'Yelp Url')\
                    .replace('claim', '4.0 Yelp Claimed')\
                    .replace('reviews_score', '4.0 Yelp Review Score')\
                    .replace('photo_count', '4.0 Num Yelp Photos')\
                    .replace('reviews_count', '4.0 Num Yelp Reviews')\
                    .replace('owner_name', '4.0 Yelp Owner Name')\
                    .replace('owner_replies', '4.0 Yelp Owner Replies')\
                    .replace('open_date', '4.0 Open Date')

                new_header.append(line)
            else:
                if line not in new_output_data:
                    new_output_data.add(line)

        for logfile in output_files:
            spider_archive.write(logfile)
            os.remove(logfile)

        # Create new output file for import
        with open('{}/output/merged_{}_{}.csv'.format(settings.SCRIPT_BASE_PATH, spider.name, date_today), 'w+') as new_output:
            if len(new_header):
                new_output.write(new_header[0])
            new_output.writelines(new_output_data)
            new_output.close()
