from mechanize import *         # external library for creating browsing agents
from bs4 import BeautifulSoup   # external library that simplifies data scraping
import sys                      # for system functionalities
import getpass                  # for getting passwords
import re                       # for regex stuff


def runBot(username,studentid,password,year,sem):
    print "Retrieving results..."
    
    br = Browser()
    br.set_handle_robots(False)

    # pretending to be a browser
    br.addheaders = [('User-agent','Firefox')]

    # result page with placeholders for year and semester
    url = "https://apps.knust.edu.gh/students/ResultCheck?ACADYEAR=ACADEMICYEAR&SEM=SEMESTER"

    #fixing in the year and sem
    url = url.replace("ACADEMICYEAR",year.split("-")[1])
    url = url.replace("SEMESTER",sem)
    
    #going to academic section but we will get redirected to login page
    try:
        br.open(url)
    except:
        print "Error connecting to site"

        # mission failed
        return

    # select the login form,the first and only form on the page
    br.select_form(nr=0)

    #fill the login form
    br.form['UserName'] = username
    br.form['Password'] = password
    br.form['studentid'] = studentid

    # submit the form
    res = br.submit()

    # read the html from the response page which happens to be the result page
    data = res.read()

    # strings copied from different pages on the site
    # helps us know which page we have landed on instead of the results page
    noResultsAlert = "Your records are not available for this semester!"
    invalidLoginAlert = "The user name, password or studentid provided is incorrect."

    
    # will occur when there are no results for the given year and we get redirected
    if noResultsAlert in data:
        print "No results found for given year and sem."
        return
        
    # will occur when login is invalid and we get redirected
    if invalidLoginAlert in data:
        print invalidLoginAlert
        return

    # pass the html on to be parsed if we got the right data
    parseHTML(data)

def parseHTML(html):
    # cooking some soup
    bsObj = BeautifulSoup(html,"html.parser")

    # the main results table is the second on the page
    resultsTable = bsObj.findAll("table")[1]

    # the results stats table is the third on the page
    statsTable = bsObj.findAll("table")[2]

    # get rows from the various tables in format that's
    # easy to iterate on
    resultsRows = scrapeTable(resultsTable)
    analysisRows = scrapeTable(statsTable)

    # outputting the main results table
    print "\n\n"
    for row in resultsRows:
        if len(row) > 0:
            print "%50s%5s%5s%5s"%(row[1],row[2],row[3],row[4])
            print "----------------------------------------------------------------------\n"

    print "\n\n"

    # outputting the results analysis table
    print "%40s%15s%15s"%(" ","SEMESTER","CUMULATIVE")
    for row in analysisRows:
        if len(row) > 0:
            print "%40s%15s%15s"%(row[1],row[2],row[3])
            

def scrapeTable(bsTableObj):
    table = bsTableObj
    rows = table.findAll('tr')

    # will finally contain all rows from the table
    rowsData = []

    # a list that temporary stores the columns of current row
    # as we obtain them one by one
    tempList = []

    # for each row object            
    for tr in rows:
        # for each column object
        for td in tr.findAll("td"):
            # add to the temporary list its siblings
            # i.e columns that share the same parent <tr>
            tempList.append(td.findNext(text=True))

        # the original data comes with lots of whitespace
        # so we get rid of them
        tempList = [i.strip() for i in tempList]
        rowsData.append(tempList)
        tempList = []

    return rowsData

                  
def inputClear(studentId,year,sem):
    inputErrors = []

    # is the student id numeric ?
    if studentid.isdigit() == False:
        inputErrors.append('idError')

    pattern = re.compile(r'\b^[0-9]{4}-[0-9]{4}$\b')

    # does the academic year conform to the pattern shown?
    if not pattern.match(year):
        inputErrors.append('yearError')

    # is the sem numeric and either 1 or 2 ?
    if sem.isdigit() == False:
        inputErrors.append('semError')
    else:
        if sem != "1" and sem != "2":
            inputErrors.append('semError')

    # if there are errors, we are not clear to proceed
    if len(inputErrors) > 0:
        return False

    # let's go
    return True

    
def printUsage():
    print """
          Usage:
             techres username studentid academic_year sem

             eg.
               techres user1 20400000 2015-2016 1
         """


# get command line arguments
inputs = sys.argv

if len(inputs) < 5:
    # user supplied no commandline arguments so we are
    # running as an interactive program
    username = raw_input("Please enter your username:")
    studentid = raw_input("Please enter your id:")
    password = getpass.getpass("Please enter your password(won't be shown):")
    year = raw_input("Please enter academic year of examination(eg.2016-2017):")
    sem = raw_input("Please enter semester:")

    runBot(username,studentid,password,year,sem)
    
else:
    username = inputs[1]
    studentid = inputs[2]
    year = inputs[3]
    sem = inputs[4]

    if not inputClear(studentid,year,sem):
        printUsage()
        sys.exit()

    password = getpass.getpass("Enter password(won't be shown):")

    runBot(username,studentid,password,year,sem)

raw_input("\n\nPress Enter to exit")
print "\nThanks for using Techres.Made with Python by Algor :)"
    


    

    

    
