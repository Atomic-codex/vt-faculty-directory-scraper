import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

#College of Engineering
computerScience = 'https://website.cs.vt.edu/people/faculty.html'

#Pamplin College of business
businessInformationTechnology = 'https://bit.vt.edu/faculty/directory.html'

#College of Science
statisticsDepartment = 'https://www.stat.vt.edu/people/stat-faculty.html'

urls = {
    "Computer Science Department" : computerScience,
    "Business Information Technology Department" : businessInformationTechnology,
    "Statistics Department" : statisticsDepartment
}

response = {}

for department, url in urls.items():
  res = requests.get(url)
  print(department, ": status", res.status_code, 'Success' if res.status_code == 200 else 'Not Found') #Url checker
  response[department] = res

profUrls = {}
csUrls = []
bitUrls = []
statUrls = []
for department, res in response.items():
  soup = BeautifulSoup(res.text, "html.parser")

  #Documentation: https://www.geeksforgeeks.org/python/beautifulsoup-scraping-link-from-html/
  for link in soup.find_all('a',
                            attrs={'href' : re.compile("https://website.cs.vt.edu/people/faculty/")}):
    csUrls.append(link.get('href'))

  #Put links into a set due to there being duplicates
  csUrls = list(set(csUrls))

  for link in soup.find_all('a',
                            attrs={'href' : re.compile("https://bit.vt.edu/faculty/directory/")}):
    bitUrls.append(link.get('href'))
  bitUrls = list(set(bitUrls))

  for link in soup.find_all('a',
                            attrs={'href' : re.compile("https://www.stat.vt.edu/people/stat-faculty/")}):
    statUrls.append(link.get('href'))
  statUrls = list(set(statUrls))


profUrls = {
    "CS Department" : csUrls,
    "BIT Department" : bitUrls,
    "Statistics Department" : statUrls
}

print(profUrls)

for dept, links in profUrls.items():
  for link in links:
    res = requests.get(link)
    if res.status_code != 200:
      print('Invalid Url' + link)
    else:
      soup = BeautifulSoup(res.text, "html.parser")

facultyData = {}

duplicateLinks = set()

for dept, links in profUrls.items():
  for link in links:
    if link in duplicateLinks: #prevents dupes
      continue
    duplicateLinks.add(link)

    departemnt = college = firstName = lastName = professorTitle = officeNum = office = email = phone = None

    soup = BeautifulSoup(requests.get(link).text, "html.parser")

#for professor, res in response.items():
  #soup = BeautifulSoup(res.text, "html.parser")

    department = soup.select_one('.vt-logo-text')
    if(department is not None):
      department = department.get_text(strip=True)

    college = soup.select_one('.vt-parentOrgLink')
    if(college is not None):
      college = college.get_text(strip=True).replace('\xa0\xa0/', '')

    firstName = soup.select_one('.vt-bio-name')
    if(firstName is not None):
      firstName= firstName.get_text(strip=True).split()[0]

    lastName = soup.select_one('.vt-bio-name')
    if(lastName is not None):
      lastName = lastName.get_text(strip=True).split()[-1]

    professorTitle = soup.select_one('.vt-person-title')
    if (professorTitle is not None):
      professorTitle = professorTitle.get_text(strip=True)

    officeNum = soup.select_one('address.vt-bio-address')
    if(officeNum is not None):
      officeNumOnly = officeNum.get_text(separator='|', strip = True).split('|')[0]
      match = re.search(r"(RM|Room)\s*(\d+[A-Z]*)", officeNumOnly, re.IGNORECASE)         #Documentation: https://docs.python.org/3/library/re.html#regular-expression-syntax and regex.pptx
      officeNum = match.group(2) if match else None

    office = soup.select_one('address.vt-bio-address')
    if(office is not None):
      officeLocation = office.get_text(separator='|', strip = True).split('|')[0]
      office = re.sub(r'(?:RM|Room)[\s]*[\d]+[A-Za-z]*', '', officeLocation, flags = re.IGNORECASE).strip(',')

    email = soup.find('a',
                          attrs={'href' : re.compile("mailto:")})
    if(email is not None):
      email = email.get_text(strip=True)

    phone = soup.select_one('.vt-bio-phone-link')
    if(phone is not None):
      phone = phone.get_text(strip=True)

    facultyData[link] = [lastName or 'Not available', firstName or 'Not available', college or 'Not available', department or 'Not Available', professorTitle or 'Not available', email or 'Not Available', office or 'Not available', officeNum or 'Not available', phone or 'Not available'] #rmeoves the none output

print(facultyData)

#Documentation: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html (DataFrames)
df = pd.DataFrame.from_dict(facultyData, orient='index', columns=['lastName', 'firstName', 'college', 'department', 'professorTitle', 'email', 'office', 'officeNum', 'phone'])  #oreint=index makes the urls in rows
df.insert(0,'uniqueID', range(len(df)))         #df.insert: inserts uniqueID column starting at 0
df.to_csv('AdrianPeot_BIT3474_exam1.csv', index = False)
df

