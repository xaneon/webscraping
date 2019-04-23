import requests
import getpass
from myinfo import *
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import re
import json
from collections import defaultdict

loginurl = f"{indeed_baseurl}/account/login"

url = (f"{indeed_baseurl}/Jobs?as_and={with_all_words}"+
       f"&as_phr={with_exact_wordgroup}"+
       f"&as_any={with_atleastoneofthesewords}"+
       f"&as_not={without_thesewords}&as_ttl={with_thesewords_intitle}"+
       f"&as_cmp={without_thesecompanies}&st=&as_src={from_theseportals}"+
       f"&radius={radius}&l={location}&fromage={fromage}"+
       f"&limit={results_per_page}&sort={sort_by}&psf=advsrch")

password = getpass.getpass(prompt="Indeed Password: ")

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)

driver.get(loginurl)
driver.find_element_by_id("login-email-input").send_keys(username)
driver.find_element_by_id("login-password-input").send_keys(password)
driver.find_element_by_id("login-submit-button").click()

driver.get(url)
source = driver.page_source
driver.close()

soup = BeautifulSoup(source, "html.parser")
l = re.findall("(jobmap.*)= ({.+})", source) # get joblist with ids
d = defaultdict(dict)
for idx, (mapname, s) in enumerate(l):
    # curr = json.loads(re.sub(r'([a-zA-Z]+):', r' "\1": ', s.replace("\'", "\"")))
    itemlist = re.sub(r"[{}]", r"", s.replace("'", "\"")).split(",")
    for elem in itemlist:
        tmp = elem.split(":")
        key, value = tmp[:2]
        d[idx][key] = value[1:-1] # remove " at the beg and end

for entry in d:
    d[entry]["res"] = soup.find("div", attrs={'id':"p_" + d[0]["jk"]})
    ts = d[entry]["res"].find("div", attrs={"class": "title"}).text.strip()
    company = d[entry]["res"].find("span", attrs={"class": "company"}).text.strip()
    d[entry]["title" + "_scraped"] = ts
    d[entry]["company" + "_scraped"] = company
    # TODO: summary, a href and date


print(d)

# TODO: get joblist, and afertwards find contents by ID
# TODO: write function for indeed and then monster etc
# Write Jobs to Excel table with pandas

with open("response.html", "w") as fid:
     fid.write(source)

