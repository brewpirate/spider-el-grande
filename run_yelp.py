from twisted.internet import defer
from scrapy.crawler import CrawlerProcess
from elgrande.spiders.yelp import YelpBaseSpider
from elgrande.utils import get_usa_zipcodes, get_custom_zipcodes, ElGrandeFileLoader, merge_output
from scrapy.utils.project import get_project_settings
import random
import datetime
import argparse

# Yelp location Types
custom_yelp_terms = {
    'beer': ['Bar', 'Craft Beer', 'Breweries', 'Distillery'],
    'coffee': ['Coffee & Tea', 'Coffee Roasteries', 'Cafes'],
    'pizza': ['Pizza'],
    'juice': ['Juice Bars & Smoothies'],
}

def crawl_loader(args):
    # Prepare the CrawlerProcess
    process = CrawlerProcess(get_project_settings())
    process.settings.set('PROXY_MODE', 1)
    process.settings.set('COOKIES_ENABLED', False)

    crawl_process(process, args)
    process.start()

    # Done! Merge dem parts
    merge_files()


@defer.inlineCallbacks
def crawl_process(process, args):
    """
    Creates a Runner for each zipcode and set PROXY_MODE to use 1 proxy for the entire zipcode. This is to mimic real
    world usage by a user and not a bot.YelpBaseSpider.custom_settings
    """
    process.settings.set('PROXY_MODE', 1)
    process.settings.set('COOKIES_ENABLED', False)

    search_terms = None

    thFileLoader = ElGrandeFileLoader()
    zipcode_processed_source = 'yelp_zipcode.processed'
    zipcode_processed_list = thFileLoader.get_list(zipcode_processed_source)

    if args.customzip:
        zipcode_json = get_custom_zipcodes()
    else:
        zipcode_json = get_usa_zipcodes()

    state_list = zipcode_json

    if args.state:
        state_list = [args.state]

    if args.type:
        search_terms = custom_yelp_terms[args.type]

    for state in state_list:
        # Randomize the zipcodes for a State so we are not crawling in sequence
        random.shuffle(zipcode_json[state])
        for zip in zipcode_json[state]:
            if zip['zipcode'] not in zipcode_processed_list:
                # Stop crawling at 11:00 PM, cron job will kick off to start a new crawl
                time_cutoff = int(datetime.datetime.today().strftime('%H%M'))

                if time_cutoff < 2300:
                    thFileLoader.add_to_list(zipcode_processed_source, zip['zipcode'])
                    yield process.crawl(YelpBaseSpider, slug=None, search=search_terms, state=None, zip=zip['zipcode'], debug=False)
                    zipcode_processed_list.append(zip['zipcode'])
                else:
                    process.stop()
                    

def merge_files():
    merge_output(YelpBaseSpider)


def main():
    parser = argparse.ArgumentParser(description='Crawl Yelp!')
    parser.add_argument('--merge', action='store_true', required=False, help="merge yelp crawls into a single csv file for import.")
    parser.add_argument('--state', required=False, help="Crawl dis state")
    parser.add_argument('--customzip', required=False, help="Custom Zip List")
    parser.add_argument('--type', required=False, help="Search for specific types of locations  ie beer, coffee")

    args = parser.parse_args()

    if args.merge and not args.state:
        merge_files()
    elif args.type not in custom_yelp_terms.keys():
        print "Not a valid search type"
    else:
        crawl_loader(args)

if __name__ == '__main__':
    main()
