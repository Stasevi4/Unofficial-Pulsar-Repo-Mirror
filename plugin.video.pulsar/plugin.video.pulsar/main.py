import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'site-packages'))

import json
import urllib2
import xbmcgui
import xbmcplugin
import socket
from pulsar.config import PULSARD_HOST
from pulsar.addon import ADDON_ID
from pulsar.platform import PLATFORM


HANDLE = int(sys.argv[1])


class closing(object):
    def __init__(self, thing):
        self.thing = thing
    def __enter__(self):
        return self.thing
    def __exit__(self, *exc_info):
        self.thing.close()


class NoRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        import urllib
        infourl = urllib.addinfourl(fp, headers, headers["Location"])
        infourl.status = code
        infourl.code = code
        return infourl
    http_error_300 = http_error_302
    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302


def _json(url):
    with closing(urllib2.urlopen(url)) as response:
        if response.code >= 300 and response.code <= 307:
            xbmcplugin.setResolvedUrl(HANDLE, True, xbmcgui.ListItem(path=response.geturl()))
            return
        payload = response.read()
        if payload:
            return json.loads(payload)


def main():
    if ("%(os)s_%(arch)s" % PLATFORM) not in [
        "windows_x86",
        "darwin_x64",
        "linux_x86", "linux_x64", "linux_arm",
    ]:
        from pulsar.util import notify
        notify("Pulsar is compatible only with Windows, Linux and OS X")
        return
    if not os.path.exists(os.path.join(os.path.dirname(__file__), ".firstrun")):
        from pulsar.util import notify
        notify("You must restart XBMC before using Pulsar")
        return
    if PLATFORM["os"] not in ["windows", "linux", "darwin"]:
        from pulsar.util import notify
        notify("Pulsar is compatible only with Windows, Linux and OS X")
        return

    socket.setdefaulttimeout(300)
    urllib2.install_opener(urllib2.build_opener(NoRedirectHandler()))

    url = sys.argv[0].replace("plugin://%s" % ADDON_ID, PULSARD_HOST) + sys.argv[2]
    data = _json(url)
    if not data:
        return

    if data["content_type"]:
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_DATE)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_GENRE)
        xbmcplugin.setContent(HANDLE, data["content_type"])

    listitems = range(len(data["items"]))
    for i, item in enumerate(data["items"]):
        listItem = xbmcgui.ListItem(label=item["label"], iconImage=item["icon"], thumbnailImage=item["thumbnail"])
        if item.get("info"):
            listItem.setInfo("video", item["info"])
        if item.get("stream_info"):
            for type_, values in item["stream_info"].items():
                listItem.addStreamInfo(type_, values)
        if item.get("art"):
            listItem.setArt(item["art"])
        if item.get("context_menu"):
            listItem.addContextMenuItems(item["context_menu"])
        listItem.setProperty("isPlayable", item["is_playable"] and "true" or "false")
        if item.get("properties"):
            for k, v in item["properties"].items():
                listItem.setProperty(k, v)
        listitems[i] = (item["path"], listItem, not item["is_playable"])

    xbmcplugin.addDirectoryItems(HANDLE, listitems, totalItems=len(listitems))
    xbmcplugin.endOfDirectory(HANDLE, succeeded=True, updateListing=False, cacheToDisc=True)

main()
