# -*- coding: utf-8 -*-
import settings
import datetime
from elgrande.items import ElGrandeItem
from scrapy.exporters import CsvItemExporter


class ElGrandePipeline(object):
    def __init__(self):
        self.processed_urls = set()
        self.payload_file = None

    def open_spider(self, spider):
        self.payload_file = '{}/output/{}.{}.csv'.format(settings.SCRIPT_BASE_PATH, spider.name, datetime.datetime.today().strftime('%Y-%m-%d.%S%f'))

        if spider.output_file:
            self.payload_file = spider.output_file

        file = open(self.payload_file, 'a+')

        # If we are writting to a log check if we need to add headers
        include_headers = False if sum(1 for line in file) else True
        self.exporter = CsvItemExporter(file, include_headers_line=include_headers)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.clean_output(spider)

    def _clean_field(self, value):
        if isinstance(value, (unicode, str, basestring)):
            return unicode(value.strip())

    def process_item(self, item, spider):
        if spider.is_DEBUG:
            print item

        self.exporter.export_item(item)
        return item

        if not spider.export_closeio:
            self.exporter.export_item(item)
            return item

        closeio_item = ElGrandeItem()
        closeio_item['company'] = item.get('name', None)
        closeio_item['url'] = self._clean_field(item.get('url', None))
        closeio_item['phone'] = self._clean_field(item.get('phone', None))
        closeio_item['address'] = item.get('address', None)
        closeio_item['address_1'] = item.get('address1', None)
        closeio_item['city'] = self._clean_field(item.get('city', None))
        closeio_item['state'] = self._clean_field(item.get('state', None))

        # Normalize USA country code for close.io import
        item_country = self._clean_field(item.get('country', None))
        if item_country and item_country.upper() in ['US', 'USA']:
            item_country = 'USA'

        closeio_item['country'] = item_country
        closeio_item['zip'] = self._clean_field(item.get('zip', None))
        closeio_item['source_url'] = self._clean_field(item.get('source_url', None))
        closeio_item['categories'] = self._clean_field(item.get('categories', None))  # TODO: TEMP For debug
        closeio_item['lead_source'] = spider.lead_source
        closeio_item['facebook'] = self._clean_field(item.get('facebook', None))
        closeio_item['twitter'] = self._clean_field(item.get('twitter', None))
        closeio_item['notes'] = self._clean_field(item.get('notes', None))
        closeio_item['status'] = self._clean_field(item.get('status', None))
        closeio_item['reviews_count'] = self._clean_field(item.get('reviews_count', None))
        closeio_item['reviews_score'] = self._clean_field(item.get('reviews_score', None))
        closeio_item['claim'] = self._clean_field(str(item.get('claim', None)))
        closeio_item['photo_count'] = self._clean_field(str(item.get('photo_count', None)))
        closeio_item['owner_name'] = self._clean_field(str(item.get('owner_name', None)))
        closeio_item['owner_replies'] = self._clean_field(str(item.get('owner_replies', None)))
        closeio_item['open_date'] = self._clean_field(item.get('open_date', None))
        closeio_item['email'] = self._clean_field(item.get('email', None))

        self.exporter.export_item(closeio_item)

        return closeio_item

    def clean_output(self, spider):
        """
        Clean up output
        :param spider:
        :return:
        """
        import fileinput
        # Remove duplicate records
        print '*******************************'
        print 'Removing Duplicates Records'
        print '*******************************'
        seen = set()
        for line in fileinput.input(self.payload_file, inplace=1):
            if fileinput.isfirstline():
                line = line.replace('lead_source', '1.4 Lead Source')

            if line not in seen:
                seen.add(line)
                print line,


class RunLoggerPipeline(object):
    count = 0

    def open_spider(self, spider):
        self.file = open(settings.SCRIPT_PATH + 'runner.log', 'ab+')
        self.file.write('\n\n=======================\n{}\n spider started at {}'.format(
            spider.name,
            datetime.datetime.now())
        )

    def close_spider(self, spider):
        self.file.write('\n finised at {}\n {} records written\n=======================\n'.format(
            datetime.datetime.now(),
            self.count
        ))
        self.file.close()

    def process_item(self, item, spider):
        self.count += 1


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


# class ElGrandePipeline(object):
#     def process_item(self, item, spider):
#         return item