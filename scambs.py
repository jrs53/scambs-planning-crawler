import requests
from lxml import html

def process_page(page):
    ret_val = list()

    tree = html.fromstring(page.content)
    # Iterate over matching applications
    for i in range(2, 12):
        id = tree.xpath('//*[@id="apas_form"]/table/tr[' + str(i) + ']/td[1]/a')
        details = get_details(id[0].text_content().strip())
        ret_val.append(details)
    return ret_val


def get_details(application_ref):
    url = 'http://plan.scambs.gov.uk/swiftlg/apas/run/WPHAPPDETAIL.DisplayUrl?theApnID=' + application_ref
    details = requests.get(url)

    # Get the Application Details pane content
    tree = html.fromstring(details.content)
    fields = tree.xpath('//*[@id="fieldset_data"]/p')
    # Extract interesting fields
    registration_date = fields[1].text_content().strip()
    decision_date = fields[2].text_content().strip()
    application_type = fields[3].text_content().strip()
    extension_of_time = fields[4].text_content().strip()
    parish = fields[5].text_content().strip()
    main_location = fields[6].text_content().strip()
    full_description = fields[7].text_content().strip()
    status = fields[8].text_content().strip()

    # Get the Applicant Details content
    fields = tree.xpath('//*[@id="fieldset_dataTab"]/p/a')
    if (len(fields) == 0):
        case_officer = ''
    else:
        case_officer = fields[len(fields) - 1].text_content().strip()

    return (registration_date, decision_date, application_type, extension_of_time, parish, main_location, full_description,
    status, case_officer)

########################################################################################################################################################
########################################################################################################################################################
########################################################################################################################################################

# Copied from Chrome, tweak criteria as needed
URL = 'http://plan.scambs.gov.uk/swiftlg/apas/run/WPHAPPCRITERIA'
payload = {
    'APNID.MAINBODY.WPACIS.1': '',
    'PARISH.MAINBODY.WPACIS.1': '',
    'JUSTLOCATION.MAINBODY.WPACIS.1': '',
    'JUSTDEVDESC.MAINBODY.WPACIS.1': '',
    'SURNAME.MAINBODY.WPACIS.1': '',
    'REGFROMDATE.MAINBODY.WPACIS.1': '01/04/2016',
    'REGTODATE.MAINBODY.WPACIS.1': '',
    'DECFROMDATE.MAINBODY.WPACIS.1': '',
    'DECTODATE.MAINBODY.WPACIS.1': '',
    'FINALGRANTFROM.MAINBODY.WPACIS.1': '',
    'FINALGRANTTO.MAINBODY.WPACIS.1': '',
    'APELDGDATFROM.MAINBODY.WPACIS.1': '',
    'APELDGDATTO.MAINBODY.WPACIS.1': '',
    'APEDECDATFROM.MAINBODY.WPACIS.1': '',
    'APEDECDATTO.MAINBODY.WPACIS.1': '',
    'SEARCHBUTTON.MAINBODY.WPACIS.1': 'Search!'
}

# Copied from Chrome
headers = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'en-GB,en;q=0.8,en-US;q=0.6',
    'Cache-Control':'max-age=0',
    'Connection':'keep-alive',
    'Content-Length':'509',
    'Content-Type':'application/x-www-form-urlencoded',
    'Cookie':'JSESSIONID=672151530A39D3B54AFFA54B2AED9AA1; _ga=GA1.3.2058533064.1485813037; __utmt=1; __utma=256747092.2058533064.1485813037.1486924782.1487450430.3; __utmb=256747092.7.10.1487450430; __utmc=256747092; __utmz=256747092.1485813222.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided)',
    'Host':'plan.scambs.gov.uk',
    'Origin':'http://plan.scambs.gov.uk',
    'Referer':'http://plan.scambs.gov.uk/swiftlg/apas/run/wphappcriteria.display',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
}

# Get initial page
page = requests.post(URL, data=payload, headers=headers)

# Follow links to get details for initial page
details = process_page(page)
print 'Got first page' # first page done

# Follow linked search result pages
tree = html.fromstring(page.content)
page_links = tree.xpath('//*[@id="apas_form_text"]/p[2]/a')
for page_link in page_links:
    url = page_link.get('href')
    page = requests.get('http://plan.scambs.gov.uk/swiftlg/apas/run/' + url)
    details += process_page(page)

    # Print simple progress counter
    details_so_far = len(details)
    page_number = page_link.text_content().strip()
    print str(details_so_far) + ' [Page ' + str(page_number) + ' of ' + str(len(page_links)) + ']'

    #if int(page_link.text_content().strip()) == 3: break

# Write output to file
import csv
print len(details)
with open('c:\\data\\scambs.txt', "wb") as file:
    writer = csv.writer(file)
    for tup in details:
        writer.writerow(tup)