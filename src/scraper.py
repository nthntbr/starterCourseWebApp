import os
import re
import string
import requests
from bs4 import BeautifulSoup
import csv


def scrapeCourses(response):
    '''
    with open('test2.csv', 'r') as file:
        textFile = file.read().replace('\\n', '')
        textFile = textFile.replace('\\t', '')
    '''

    #soup = BeautifulSoup(textFile, 'html.parser')
    soup = BeautifulSoup(response.text, 'html.parser')

    departmentName = soup.find('h1', class_ = 'page-title').text
    
    courses = []
    for c in soup.findAll('div', class_ = 'courseblock'):
        course = dict.fromkeys([
            'code',
            'name',
            'credits',
            'description',
            'prerequisite',
            'registration',
            'termsOffered',
            'gradeMode',
            'specialCourseFee',
            'additionalInformation'
        ], None)
        
        ls = list(c.children)
        l = []
        for element in c.findAll('p'):
            l.append(element)
        title = l[0]
        '''
        course_code_pattern = r'[A-Z]+\s+\d+\d+\d'.format(re.escape(string.printable))
        courseCode = re.findall(course_code_pattern, title.text)[0]
        '''
        # Extract course code and title
        course_code_pattern = r'[A-Z]+\s+\d+\d+\d'.format(re.escape(string.printable))
        courseCode_matches = re.findall(course_code_pattern, title.text)

        if courseCode_matches:
            courseCode = courseCode_matches[0]
            nameCredits = title.text.split(courseCode)[1].strip()
        else:
            # Handle the case when no course code is found (e.g., log an error or set courseCode to an empty string)
            courseCode = ""
            nameCredits = title.text.strip()

        #nameCredits = title.text.split(courseCode)[1].strip()
        titleList = []

        if 'Credits:' in title.text:
            titleList = nameCredits.split('Credits: ')
        elif 'CEUs:' in title.text:
            titleList = nameCredits.split('CEUs: ')
        else:
            titleList = nameCredits.split(': ')

        course['code'] = courseCode
        course['name'] = titleList[0]
        course['credits'] = titleList[1]

        description = l[1]

        option = ''
        for element in description.contents:
            if (option == '') and isinstance(element, str):
                continue

            if 'Course Description' in element.text:
                option = 'description'
                course[option] = element.text
                continue

            if 'Prerequisite' in element.text:
                option = 'prerequisite'
                course[option] = element.text
                continue

            if 'Registration Information' in element.text:
                option = 'registrationInformation'
                course[option] = element.text
                continue


            if 'Terms Offered' in element.text:
                option = 'termsOffered'
                course[option] = element.text
                continue

            
            if 'Grade Mode' in element.text:
                option = 'gradeMode'
                course[option] = element.text
                continue

            
            if 'Special Course Fee' in element.text:
                option = 'specialCourseFee'
                course[option] = element.text
                continue

            
            if 'Additional Information' in element.text:
                option = 'additionalInformation'
                course[option] = element.text
                continue

            
            if 'Also Offered As' in element.text:
                option = 'alsoOfferedAs'
                course[option] = element.text
                continue

            
            if 'Restrictions' in element.text:
                option = 'restrictions'
                course[option] = element.text
                continue

            course[option] = course[option] + element.text
            
        courses.append(course)
    return departmentName, courses


#url = 'https://catalog.colostate.edu/general-catalog/courses-az/'
#response = requests.get(url)

def scrapeDepartments(response):
    '''
    with open('test.csv', 'r') as file:
        textFile = file.read().replace('\\n', '')
        textFile = textFile.replace('\\t', '')
    '''
    #soup = BeautifulSoup(textFile, 'html.parser')

    # Clean Up HTML Text
    text = response.text.replace('\\n', '')
    text = text.replace('\\t', '')
    text = text.replace('\n', '')
    text = text.replace('\t', '')

    soup = BeautifulSoup(response.text, 'html.parser')
    head = soup.find('h2', class_ = 'letternav-head')
    departmentURLs = []
    while not(head.next_sibling is None):
        sibling = head.find_next_sibling()
        if sibling is None:
            break
        
        for link in sibling.findAll('a'):   
            l = link.get('href')
            
            if (not(l is None) and ('/general-catalog/' in l)):
                departmentURLs.append(l)

        head = sibling
            


    departments = []
    for departmentURL in departmentURLs:
        url = "https://catalog.colostate.edu" + departmentURL
        departments.append(url)
    
    return departments


departments = [string]
response = requests.get(url = 'https://catalog.colostate.edu/general-catalog/courses-az/')
departments = scrapeDepartments(response)
#scrapeCourses(response)
#departmentName = x[0]
#courseList = x[1]

for departmentURL in departments:
    
    departmentResponse = requests.get(departmentURL)
    departmentCourseData = scrapeCourses(departmentResponse)
    departmentName = departmentCourseData[0].replace(" ", "_")
    courseList = departmentCourseData[1]

    fileName = departmentName + 'Courses.csv'
    fileAddress = os.path.join('/Users/nathanteuber/Desktop/courseSearchApp/csuCourseCatalogDB', fileName)
    with open(fileAddress, 'w', newline='', encoding='utf-8') as csvfile:
        csvWriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvWriter.writerow(['code','name','credits','description',
                            'prerequisite','registration','termsOffered',
                            'gradeMode','additionalInformation'])

        for course in courseList:
            csvWriter.writerow(course.values())

    print("Department Scraping complete! The course data is saved in '{}'.".format(fileName))
