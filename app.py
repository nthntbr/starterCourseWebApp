
import csv
import os
from flask import session
from flask import Flask, render_template, render_template_string, request

app = Flask(__name__)
app.secret_key = 'your-secret-key'



@app.route("/")
def home():
    departments = populateDepartments()
    departments.sort()
    
    alphabetCatg = {}

    for department in departments:
        firstLetter = department[0]
        d = department[:-11]
        d = d.replace('_', ' ')
        if firstLetter in alphabetCatg:
            alphabetCatg[firstLetter].append(d)
        else:
            alphabetCatg[firstLetter] = [d]
    return render_template('index.html', alphabetCatg=alphabetCatg)

@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('q')
        if 'queryList' not in session:
            session['queryList'] = []
        session['queryList'].append(query)
        session.modified = True

    queryList = session.get('queryList', [])
    results = []
    for query in queryList:
        results.extend(searchHelper(query, results))

    return render_template('search.html', results=results, queryList=queryList)

@app.route("/remove_filter/<filter>")
def remove_filter(filter):
    session['queryList'].remove(filter)
    session.modified = True
    return search()


@app.route("/search1")
def search1(queryList=[], results=[]):
    query = request.args.get('q')
    print('Test: 0' + str(results))
    results = searchHelper(query, results)
    print('test 1: ' + str(queryList))
    if query:
        queryList.append(query)
    print('test 2: ' + str(queryList))

    return render_template('search.html', query=query, results=results, queryList=queryList)

@app.route("/departments/<department>")
def department(department):
    courses = populateCourses(department)
    courseList = []
    for course in courses:
        if course[0] == 'code':
            continue
        c = dataDeciphering(course)
        courseList.append(c)

    return render_template('department.html', courseList=courseList, department=department)


def populateDepartments():
    path = 'csuCourseCatalogDB'
    contents = os.listdir(path)
    return contents

def populateCourses(department):
    path = 'csuCourseCatalogDB/' + department.replace(' ', '_') + 'Courses.csv'
    courseData = []
    with open(path, 'r') as f:
        csvRows = csv.reader(f, delimiter=',', quotechar='"')
        data = list(csvRows)
        
        for row in data:
            course = row
            for i, element in enumerate(course):
                if element == '':
                    course[i] = None
            #courseData.append(course)
             
        
    return data

def dataDeciphering(course):

    c = dict.fromkeys([
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

    c['code'] = course[0]
    c['name'] = course[1]
    c['credits'] = course[2]
    c['description'] = course[3]
    c['prerequisite'] = course[4]
    c['registration'] = course[5]
    c['termsOffered'] = course[6]
    c['gradeMode'] = course[7]
    c['specialCourseFee'] = course[8]
    c['additionalInformation'] = course[9]

    return c


def searchHelper(searchTerm, results):
    if not searchTerm:
        return []
    if results:
        return searchHelper3(searchTerm, results)
    searchResults = []

    path = 'csuCourseCatalogDB'
    contents = os.listdir(path)
    for department in contents:
        path = 'csuCourseCatalogDB/' + department.replace(' ', '_')
        with open(path, 'r') as f:
            csvRows = csv.reader(f, delimiter=',', quotechar='"')
            departmentData = list(csvRows) 
            
            positiveResults = []
            for row in departmentData:
                matchFound = False
                for element in row:
                    if searchTerm.lower() in element.lower():
                        matchFound = True
                        break
                if matchFound:
                    course = row
                    for i, element in enumerate(course):
                        if element == '':
                            course[i] = None
                    positiveResults.append(course)
                
        
        departmentResults = (department, positiveResults)
        searchResults.append(departmentResults)


    results = searchHelper1(searchTerm, searchResults)

    return results

def searchHelper1(searchTerm, searchResults):
    decipheredData = []
    for departmentTuple in searchResults:
        l = departmentTuple[1]
        departmentList = []
        if not l:
            continue
        for course in l:
            c = dataDeciphering(course)
            departmentList.append(c)
        tuple = (departmentTuple[0], departmentList)
        decipheredData.append(tuple)

        
    return decipheredData

#deprecated
def searchHelper2(searchTerm, department, departmentData):
    positiveSearch = []
    for course in departmentData[1:]:
        for element in course:
            if element is not None:
                if searchTerm.lower() in element.lower():
                    positiveSearch.append(course)
    departmentResults = (department, positiveSearch)
    return departmentResults

def searchHelper3(searchTerm, results):
    output = []
    for department in results:
        positiveSearch = []
        for course in department[1]:
            matchFound = False
            for key, value in course.items():
                if value is not None and searchTerm.lower() in value.lower():
                    matchFound = True
                    break
            if matchFound:
                positiveSearch.append(course)

                    

        departmentResults = (department, positiveSearch)
        output.append(departmentResults)
    
    return output

if __name__ == "__main__":
    app.run()

    