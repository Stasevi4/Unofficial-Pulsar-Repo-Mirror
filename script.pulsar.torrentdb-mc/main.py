# coding: utf-8
from pulsar import provider
from urllib import unquote_plus
import re
import common

# this read the settings
settings = common.Settings()
# define the browser
browser = common.Browser()
# create the filters
filters = common.Filtering()


# using function from Steeve to add Provider's name and search torrent
def extract_torrents(data):
    try:
        filters.information()  # print filters settings
        data = common.clean_html(data)
        lname = re.findall('<span class="highlight">(.*?)</a>', data)  # list names
        size = re.findall('class="grey" nowrap><span>(.*?)</span>', data)  # list the size
        cont = 0
        for cm, torrent in enumerate(re.findall('torrent-rating" value="(.*?)"', data)):
            torrent = settings.url + '/torrent/' + torrent
            name = size[cm] + ' - ' + lname[cm].replace('<span class="highlight">', '').replace('<span>', '').replace('</span>', '')
            name += ' - ' + settings.name_provider #find name in the torrent
            name = name.replace('72 0p', '720p').replace('10 80p', '1080p')
            if filters.verify(name,size[cm]):
                    yield {"name": name, "uri":  torrent }  # return le torrent
                    cont+= 1
            else:
                provider.log.warning(filters.reason)
            if cont == settings.max_magnets:  # limit magnets
                break
        provider.log.info('>>>>>>' + str(cont) + ' torrents sent to Pulsar<<<<<<<')
    except:
        provider.log.error('>>>>>>>ERROR parsing data<<<<<<<')
        provider.notify(message='ERROR parsing data', header=None, time=5000, image=settings.icon)


def search(query):
    query += ' ' + settings.extra  # add the extra information
    query = filters.type_filtering(query, '+')  # check type filter and set-up filters.title
    url_search = "%s/?q=%s" % (settings.url, query)  # change in each provider
    provider.log.info(url_search)
    if browser.open(url_search):
        results = extract_torrents(browser.content)
    else:
        provider.log.error('>>>>>>>%s<<<<<<<' % browser.status)
        provider.notify(message=browser.status, header=None, time=5000, image=settings.icon)
        results = []
    return results


def search_movie(info):
    if settings.language == 'en':  # Title in english
        query = info['title'].encode('utf-8')  # convert from unicode
        if len(info['title']) == len(query):  # it is a english title
            query += ' ' + str(info['year'])  # Title + year
        else:
            query = common.IMDB_title(info['imdb_id'])  # Title + year
    else:  # Title en foreign language
        query = common.translator(info['imdb_id'],settings.language)  # Just title
    query += ' #MOVIE&FILTER'  #to use movie filters
    return search(query)


def search_episode(info):
    if info['absolute_number'] == 0:
        query = info['title'].encode('utf-8') + ' s%02de%02d' % (info['season'], info['episode'])  # define query
    else:
        query = info['title'].encode('utf-8') + ' %02d' % info['absolute_number']  # define query anime
    query += ' #TV&FILTER'  #to use TV filters
    return search(query)


# This registers your module for use
provider.register(search, search_movie, search_episode)

del settings
del browser
del filters