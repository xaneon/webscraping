import requests
import getpass
from myinfo import *
from selenium import webdriver

loginurl = f"{indeed_baseurl}/account/login"

url = (f"{indeed_baseurl}/Jobs?as_and={with_all_words}"+
       f"&as_phr={with_exact_wordgroup}"+
       f"&as_any={with_atleastoneofthesewords}"+
       f"&as_not={without_thesewords}&as_ttl={with_thesewords_intitle}"+
       f"&as_cmp={without_thesecompanies}&st=&as_src={from_theseportals}"+
       f"&radius={radius}&l={location}&fromage={fromage}"+
       f"&limit={results_per_page}&sort={sort_by}&psf=advsrch")

headers = {'User-Agent': 'Mozilla/5.0',  'Content-type': 'application/html'}
payload = {'username': username, 'pass': getpass.getpass()}

driver = webdriver.Firefox()

driver.get(loginurl)
a = driver.find_element_by_id("login-email-input")
print(type(a))

# session = requests.session()
# session.post(loginurl, headers=headers, data=payload)
# r = session.get(url)
# r = requests.get(url, headers=headers)
# print(r.text)

# with open("response.html", "w") as fid:
#     fid.write(r.text)

