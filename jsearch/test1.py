import requests
import getpass
from myinfo import *
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import re
import json
import os
from collections import defaultdict
from datetime import datetime
import pandas as pd

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

soup = BeautifulSoup(source, "html.parser")
l = re.findall("(jobmap.*)= ({.+})", source) # get joblist with ids
d = defaultdict(dict)
for idx, (mapname, s) in enumerate(l):
    # curr = json.loads(re.sub(r'([a-zA-Z]+):', r' "\1": ', s.replace("\'", "\"")))
    itemlist = re.sub(r"[{}]", r"", s.replace("'", "\"")).split(",")
    for elem in itemlist:
        if ":" in elem:
            tmp = elem.split(":")
            key, value = tmp[:2]
            d[idx][key] = value[1:-1] # remove " at the beg and end

for entry in d:
    d[entry]["res"] = soup.find("div", attrs={'id':"p_" + d[0]["jk"]})
    ts = d[entry]["res"].find("div", attrs={"class": "title"}).text.strip()
    company = d[entry]["res"].find("span", attrs={"class": "company"}).text.strip()
    date = d[entry]["res"].find("span", attrs={"class": "date"}).text.strip()
    if ("Gerade" in date) or ("Heute" in date):
        date = "vor 0 Minuten"
    summary = d[entry]["res"].find("div", attrs={"class": "summary"}).text.strip()
    d[entry]["title" + "_scraped"] = ts
    d[entry]["company" + "_scraped"] = company
    d[entry]["summary" + "_scraped"] = summary
    d[entry]["date" + "_scraped"] = date
    d[entry]["href"] =  indeed_baseurl + os.sep + d[entry]["res"].find("a").attrs["href"]
    driver.get(d[entry]["href"])
    d[entry]["link_content"] = BeautifulSoup(driver.page_source, "html.parser")
    delta_min, delta_hour = 0, 0
    if "Minute" in d[entry]["date_scraped"]:
        delta_min = int(re.sub(r"vor ([0-9]+) Minute[n]*", r"\1",
                               d[entry]["date_scraped"]))
    if "Stunde" in d[entry]["date_scraped"]:
        delta_hour = int(re.sub(r"vor ([0-9]+) Stunde[n]*", r"\1",
                                d[entry]["date_scraped"]))
    curr = datetime.today()
    curr_date = datetime(curr.year, curr.month, curr.day,
                         (curr.hour - delta_hour)%24,
                         (curr.minute - delta_min)%60)
    # d[entry]["date"] = curr_date.strftime('%d.%m.%Y, %H:%M')
    d[entry]["date"] = curr_date

driver.close()

if os.path.isfile(os.path.join("tmp", "data.xlsx")):
    df_old = pd.read_excel(os.path.join("tmp", "data.xlsx"), index_col="jk")
data = defaultdict(list)
for sample, content in d.items():
    for key in content:
        data[key].append(content[key])
data["search_str"] = with_all_words
df = pd.DataFrame(data, columns=data.keys(), index=data["jk"])
# df = df[df.columns.drop("jk")]
if os.path.isfile(os.path.join("tmp", "data.xlsx")):
    # df = pd.merge(df, df_old, left_index=True, right_on="Unnamed: 0")
    # df = pd.merge(df, df_old, left_on="jk", right_on="jk")
    # df = pd.merge(df, df_old, on="jk")
    # df = df.join(df, df_old, on="jk")
    # df = df.append(df_old, ignore_index=True, sort=False)
    df = df.combine_first(df_old)
df.to_excel(os.path.join("tmp", "data.xlsx"), sheet_name="Data")

with open(os.path.join("tmp", "response.html"), "w") as fid:
     fid.write(source)

