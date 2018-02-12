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
        # message("({}) Analyzing Speccy URL...".format(nick))
        return parse_speccy(message, nick, str(re_content.group(0)))

def parse_speccy(message, nick, url):

    response = requests.get(url)
    if not response:
        #return "Error retrieving speccy URL"
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
        gpuspec = soup.body.find("div", text='Graphics').next_sibling.next_sibling.stripped_strings
        graphics_list = []
        for item in gpuspec:
            graphics_list.append(item)
        length = len(graphics_list)
        gpuspec = graphics_list[length-2] + " " + graphics_list[length-1]
    except Exception:
        gpuspec = None

    try:
        picospec = soup.body.find("div", text=re.compile('.*pico', re.IGNORECASE)).text
    except AttributeError:
        picospec = None

    try:
        kmsspec = soup.body.find("div", text=re.compile('.*kms', re.IGNORECASE)).text
    except AttributeError:
        kmsspec = None

    try:
        boosterspec = soup.body.find("div", text=re.compile('.*booster', re.IGNORECASE)).text
    except AttributeError:
        boosterspec = None

    try:
        xtuspec = soup.body.find("div", text=re.compile('.*xtu', re.IGNORECASE)).text
    except AttributeError:
        xtuspec = None

    try:
        reviverspec = soup.body.find("div", text=re.compile('.*reviver', re.IGNORECASE)).text
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
            smartstr = ""
            for item in z:
                smartstr += " #" + item + " "
            smartspec = "Failing " + smartstr 
        else:
            smartspec = "Good"
    except Exception:
        smartspec = None

    piracy_list = [picospec, kmsspec]
    piracy = ', '.join(filter(None, piracy_list))
    if not piracy:
        piracy = None

    badware_list = [boosterspec, xtuspec, reviverspec]
    badware = ', '.join(filter(None, badware_list))
    if not badware:
        badware = None

    specin = "\x02OS:\x02 {} ● \x02RAM:\x02 {} ● \x02CPU:\x02 {} ● \x02GPU:\x02 {} ● \x02Piracy:\x02 {} ● \x02Badware:\x02 {} ● \x02Drive(s):\x02 {}".format(osspec, ramspec, cpuspec, gpuspec, piracy, badware, smartspec)

    specout = re.sub("\s{2,}|\r\n|\n", " ", specin)

    if piracy:
        message("({}) WARNING: Piracy sofware found ({}). Please be advised we do not support users running software that violates the Terms of Service.".format(nick, piracy))

    return specout
