import requests
import getpass
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import re
import json
import os
from collections import defaultdict
from datetime import datetime
import pandas as pd
from IPython.core.debugger import set_trace

def get(indeed_baseurl, username, password, with_all_words="", with_exact_wordgroup="",
        with_atleastoneofthesewords="", without_thesewords="",
        with_thesewords_intitle="", without_thesecompanies="",
        from_theseportals="", radius=50, location="", fromage=15,
        results_per_page=50, sort_by="date", sheet_name="Data",
        excel_fname="data.xlsx", html_fname="response.html"):
    loginurl = f"{indeed_baseurl}/account/login"
    url = (f"{indeed_baseurl}/Jobs?as_and={with_all_words}"+
           f"&as_phr={with_exact_wordgroup}"+
           f"&as_any={with_atleastoneofthesewords}"+
           f"&as_not={without_thesewords}&as_ttl={with_thesewords_intitle}"+
           f"&as_cmp={without_thesecompanies}&st=&as_src={from_theseportals}"+
           f"&radius={radius}&l={location}&fromage={fromage}"+
           f"&limit={results_per_page}&sort={sort_by}&psf=advsrch")
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
        d[entry]["date"] = curr_date
    driver.close()
    data = defaultdict(list)
    for sample, content in d.items():
        for key in content:
            data[key].append(content[key])
    data["search_str"] = with_all_words
    data["location_str"] = location
    data["radius_str [km]"] = radius
    df_old = pd.DataFrame()
    # set_trace()
    if os.path.isfile(os.path.join("tmp", excel_fname)):
        df_old = pd.read_excel(os.path.join("tmp", excel_fname))
        df_old = df_old[list(data.keys())]
        # df_old = df_old.reset_index().dropna().set_index("jk")
        df_old.set_index("jk", inplace=True)
    df = pd.DataFrame(data, columns=data.keys())
    #df = df[list(data.keys())]
    df.set_index("jk", inplace=True)
    # df = df.reset_index().dropna().set_index("jk")
    if os.path.isfile(os.path.join("tmp", excel_fname)):
        df = df.combine_first(df_old)
        # df = df.set_index("jk", inplace=True, verify_integrity=False)
    # df = df[list(data.keys())]
    # df.set_index("jk", inplace=True)
    df = df.reset_index().dropna().set_index("jk")
    df.to_excel(os.path.join("tmp", excel_fname), sheet_name=sheet_name)
    with open(os.path.join("tmp", html_fname), "w") as fid:
         fid.write(source)

if __name__ == "__main__":
    from myinfo import *
    password = getpass.getpass(prompt="Indeed Password: ")
    get(indeed_baseurl, username, password, with_all_words, with_exact_wordgroup,
        with_atleastoneofthesewords, without_thesewords,
        with_thesewords_intitle, without_thesecompanies,
        from_theseportals, radius, location, fromage,
        results_per_page, sort_by)
