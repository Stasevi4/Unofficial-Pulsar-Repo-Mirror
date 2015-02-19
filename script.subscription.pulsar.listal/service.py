# coding: utf-8
import re
import subscription
from time import time
from time import asctime
from time import localtime
from time import strftime
from time import gmtime
from xbmc import log
from xbmc import sleep
from xbmc import abortRequested
from xbmcaddon import Addon


def update_service():
    # this read the settings
    settings = subscription.Settings()
    # define the browser
    browser = subscription.Browser()

    list = Addon().getSetting('list')
    if list != '':
        url_search = "http://www.listal.com/list/%s" % list
        listing = []
        ID = []  # IMDB_ID or thetvdb ID
        settings.log('[%s]%s' % (settings.name_provider_clean, url_search))
        if browser.open(url_search):
            data = browser.content
            data = data.replace('</a></span>', '')
            for line in re.findall("style='font-weight:bold;font-size:110%;'>(.*?)>(.*?)</div>", data, re.S):
                listing.append(line[1].replace('\r', '').replace('\n', '').replace('\t', ''))
            subscription.integration(listing, ID, 'MOVIE', settings.movie_folder, silence=True, name_provider=settings.name_provider)
        else:
            settings.log('[%s]>>>>>>>%s<<<<<<<' % (settings.name_provider_clean, browser.status))
            settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)
    del settings
    del browser


if Addon().getSetting('service') == 'true':
    sleep(int(Addon().getSetting('delay_time')))  # get the delay to allow pulsar starts
    persistent = Addon().getSetting('persistent')
    name_provider = re.sub('.COLOR (.*?)]', '', Addon().getAddonInfo('name').replace('[/COLOR]', ''))
    every = 28800  # seconds
    previous_time = time()
    log("[%s] Update Service starting..." % name_provider)
    update_service()
    while (not abortRequested) and persistent == 'true':
        if time() >= previous_time + every:  # verification
            previous_time = time()
            update_service()
            log('[%s] Update List at %s' % (name_provider, asctime(localtime(previous_time))))
            log('[%s] Next Update in %s' % (name_provider, strftime("%H:%M:%S", gmtime(every))))
            update_service()
        sleep(500)
