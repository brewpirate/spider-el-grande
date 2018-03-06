    # -*- coding: utf-8 -*-
import os

# Scrapy settings for elgrande project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'elgrande'

SPIDER_MODULES = ['elgrande.spiders']
NEWSPIDER_MODULE = 'elgrande.spiders'

# Paths
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__)) + '/'
SCRIPT_BASE_PATH = os.getcwd()
USA_ZIPCODES_SOURCE = '../zipcode-list/us_zipcodes.json'
CUSTOM_ZIPCODES_SOURCE = '../zipcode-list/us_zipcodes-custom.json'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'elgrande (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'elgrande.middlewares.ElGrandeSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'elgrande.middlewares.ElGrandeDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'elgrande.pipelines.ElGrandePipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [503, 407, 302]
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Compress Response not headers/meta etc
COMPRESSION_ENABLED = True


# scrapy-fake-useragent Settings
# https://github.com/alecxe/scrapy-fake-useragent
# Random User-Agent middleware based on fake-useragent. It picks up User-Agent strings based on usage statistics from a real world database.
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
}

# Proxy Settings
# https://github.com/aivarsk/scrapy-proxies
# Custom Proxy Values
PROXY_USERNAME = 'daniel.zenner@gmail.com'
PROXY_PASSWORD = 'boogereater99'


# 0 = Every requests have different proxy
# 1 = Take only one proxy from the list and assign it to every requests
PROXY_MODE = 0
# CUSTOM_PROXY = 'https://daniel.zenner@gmail.com:drinkcraft4life@us711.nordvpn.com:80'

PROXY_LIST = SCRIPT_PATH + 'proxy.list'

RANDOM_UA_PER_PROXY = True

RETRY_TIMES = 4

# Retry on most error codes since proxies fail for different reasons
RETRY_HTTP_CODES = [500, 504, 400, 403, 404, 408, 407]

DOWNLOADER_MIDDLEWARES.update(
    {
        'elgrande.custom_proxy_list_middleware.BuildProxyList': 1,
        'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
        'scrapy_proxies.RandomProxy': 100,
        'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 501,
    }
)

# https://doc.scrapy.org/en/latest/topics/broad-crawls.html#reduce-download-timeout
DOWNLOAD_TIMEOUT = 15

# https://doc.scrapy.org/en/latest/topics/broad-crawls.html#disable-redirects
# Need for BeerMenus crawlers
REDIRECT_ENABLED = True

# https://doc.scrapy.org/en/latest/topics/broad-crawls.html#increase-twisted-io-thread-pool-maximum-size
REACTOR_THREADPOOL_MAXSIZE = 20