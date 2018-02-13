from cloudbot import hook
from cloudbot.event import EventType

import asyncio
import re
import requests

from bs4 import BeautifulSoup as BS

@asyncio.coroutine
@hook.event([EventType.message, EventType.action], singlethread=True)
def get_speccy_url(conn, message, chan, content, nick):
    re_content = re.search(r"https?:\/\/speccy.piriform.com\/results\/[A-z0-9]+", content)
    if re_content:
        return parse_speccy(message, nick, str(re_content.group(0)))

def parse_speccy(message, nick, url):

    response = requests.get(url)
    if not response:
        return None

    soup = BS(response.content, "lxml-xml")

    try:
        osspec = soup.body.find("div", text='Operating System').next_sibling.next_sibling.text
    except AttributeError:
        return "Invalid Speccy URL"

    try:
        ramspec = soup.body.find("div", text='RAM').next_sibling.next_sibling.text
    except AttributeError:
        ramspec = None

    try:
        cpuspec = soup.body.find("div", text='CPU').next_sibling.next_sibling.text
    except AttributeError:
        cpuspec = None

    try:
        gpufind = soup.body.find("div", text='Graphics').next_sibling.next_sibling.text
        for gpuspec in re.finditer(r".*(amd|radeon|intel|integrated|nvidia|geforce|gtx).*\n.*", gpufind, re.I):
            print(gpuspec.group(0)) # <--------- this is proof it works, but I can't make the bot output it right
    except AttributeError:
        gpuspec = None

    try:
        picospec = soup.body.find("div", text=re.compile('.*pico', re.I)).text
    except AttributeError:
        picospec = None

    try:
        kmsspec = soup.body.find("div", text=re.compile('.*kms', re.I)).text
    except AttributeError:
        kmsspec = None

    try:
        boosterspec = soup.body.find("div", text=re.compile('.*booster', re.I)).text
    except AttributeError:
        boosterspec = None

    try:
        xtuspec = soup.body.find("div", text=re.compile('.*xtu', re.I)).text
    except AttributeError:
        xtuspec = None

    try:
        reviverspec = soup.body.find("div", text=re.compile('.*reviver', re.I)).text
    except AttributeError:
        reviverspec = None

    def smartcheck():
        drivespec = soup.body.find_all("div", text="05")
        number_of_drives = len(drivespec)

        values = []
        for i in range(0, number_of_drives):
            z = drivespec[i].next_sibling.next_sibling.stripped_strings
            saucy = list(z)
            rv_index = saucy.index("Raw Value:")
            raw_value = saucy[rv_index+1]
            if raw_value != "0000000000":
                values.append(str(i+1))
        return values

    try:
        z = smartcheck()
        if len(z) != 0:
            smartspec = " Disk:"
            for item in z:
                smartspec += item + " "
        else:
            smartspec = None
    except Exception:
        smartspec = None

    badware_list = [picospec, kmsspec, boosterspec, xtuspec, reviverspec]
    badware = ', '.join(filter(None, badware_list))
    if not badware:
        badware = None

    specin = "\x02OS:\x02 {} ● \x02RAM:\x02 {} ● \x02CPU:\x02 {} ● \x02GPU:\x02 {} ● \x02Badware:\x02 {} ● \x02Failing Drive(s):\x02 {}".format(osspec, ramspec, cpuspec, gpuspec, badware, smartspec)

    specout = re.sub("\s{2,}|\r\n|\n", " ", specin)

    return specout
