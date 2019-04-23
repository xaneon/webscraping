import requests
import getpass
from myinfo import *
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

loginurl = f"{indeed_baseurl}/account/login"

url = (f"{indeed_baseurl}/Jobs?as_and={with_all_words}"+
       f"&as_phr={with_exact_wordgroup}"+
       f"&as_any={with_atleastoneofthesewords}"+
       f"&as_not={without_thesewords}&as_ttl={with_thesewords_intitle}"+
       f"&as_cmp={without_thesecompanies}&st=&as_src={from_theseportals}"+
       f"&radius={radius}&l={location}&fromage={fromage}"+
       f"&limit={results_per_page}&sort={sort_by}&psf=advsrch")

headers = {'User-Agent': 'Mozilla/5.0',  'Content-type': 'application/html'}
# payload = {'username': username, 'pass': getpass.getpass()}
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
print(soup)

with open("response.html", "w") as fid:
     fid.write(source)

