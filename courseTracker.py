import re
import urllib2
from bs4 import BeautifulSoup

tuAllCourseUrl = "http://resources.utulsa.edu/schedule/2016FATUSCHED.html"
tuBaseUrl = "http://resources.utulsa.edu/schedule/"
tuCourseUrl = "http://resources.utulsa.edu/schedule/2016FACS.html"

class Course ():
    def __init__ (self, status, course, sect, title, mtgtim, instr ):

            self.sect   = sect
            self.instr  = instr
            self.title  = title
            self.status = status
            self.course = course.split(" ") #[0]: departmentName [1]: courseCode
            self.acLvl = self.course[1][0]

            times = timeRE(mtgtim)
            self.mtgtim =  times

            if(len(times) == 2): # Have to do this wierd stuff for the new mtgtim stuff
                preStartTime = startTime(times)
                if(preStartTime <= 7):
                    preStartTime += 12
                self.startTime = preStartTime

                preEndTime = endTime(times)
                if(preEndTime <= 8):
                    preEndTime += 12
                self.endTime = preEndTime
            else:
                self.startTime = str.upper('TBA')
                self.endTime = str.upper('TBA')

    def getAcademicLvl (self):
        return self.acLvl

    def getSection (self):
        return self.sect

    def getInstructor(self):
        return self.instr

    def getTitle(self):
        return self.title

    def isCourseOpen(self):
        return (self.status.upper() == 'OPEN')

    def getDepartment (self):
        return self.course[0]

    def getCourseNumber (self):
        return self.course[1]

    def getMeetingTime (self):
        return self.mtgtim

    def getCourseInformation (self):
        s = self.status + ", "
        s += self.course[0] + ", "
        s += self.course[1] + ", "
        s += self.sect + ", "
        s += self.title + ", "

        if(len(self.mtgtim) == 2): # Have to do this wierd stuff for the new mtgtim stuff
            s += self.mtgtim[0] + ", "
            s += self.mtgtim[1] + ", "
        else:
            s += self.mtgtim + ", "

        return s

#------------------------------------------------------------------------------
# Functions dealing with the time portion of the course class
#------------------------------------------------------------------------------

#Function that returns a list in format: ['12:00PM', '12:50PM']
def timeRE(fullTime):
    withBuilding = re.split(r'\s*', fullTime) # Reg Ex with the building code and time
    if(len(withBuilding) != 4): # Check for uniformity
        return fullTime
    if(withBuilding[3] == 'TBA -'): # Check for
        return ['TBA']
    else:
        time = re.split('-', withBuilding[3]) # This give us just the time from start to end
        return time

#Function that takes a "normal" mtgtim and converts to a start time
def startTime(meet):
    start = meet[0][0:2]
    return int(start)

#Function that takes a "normal" mtgtim and converts to an end time
def endTime(meet):
    end = meet[1][0:2]
    return int(end)

#------------------------------------------------------------------------------
# Functions dealing with the departments of the courses
#------------------------------------------------------------------------------

def listDeptNames(courselist):
    departments = [] # List of departments
    for course in courselist:
        dept = course.getDepartment()
        i = 0 # Start our i count over again
        for found in departments:
            if(found == dept): # Count how many times a dept has already been found
                i += 1
        if(i == 0): # If this dept hasn't been found yet, add it
            departments.append(dept)
    return departments

#------------------------------------------------------------------------------
# HTML Scraping and course forming
#------------------------------------------------------------------------------

#Function that gives back html from a given URL
def downloadHtml(url):
    response = urllib2.urlopen(url)
    return response.read()

# Function that returns a list of ending URLs
def hrefScrape(html):
    soup = BeautifulSoup(html, 'html.parser')
    tdElem = soup.find_all('td')
    hrefs = []
    for row in tdElem:
        aElems = row.find_all('a') # Cascades through the page (1st entry has all, 2nd has all but first, etc.)
        aElem = str(aElems[0]) # Gets unique anchors, and makes them into a string for the next step
        href = re.findall('"([^"]*)"', aElem) # Get the href out of the anchors tag (will always be inside of quotes)
        hrefs.append(href[0]) # Add the new ending href to the list of hrefs
    return hrefs

# Uses other functions to scrape for all courses
def getAllCourses(baseUrl, hrefs):
    allCourses = []
    for href in hrefs:
        urlString = str(baseUrl + href)
        html = downloadHtml(urlString)
        courses = scrapeHtml(html)
        allCourses.append(courses)
    return allCourses

#Function that returns a list of dictionaries, each dictionary is a specific course section
def scrapeHtml(html):
    soup = BeautifulSoup(html, 'html.parser')
    table_rows = soup.find('table').find_all('tr')
    courses = []
    for row in table_rows[1:]:
        table_data = row.find_all('td')
        course = {
            "Status" : table_data[0].text,
            "Course" : table_data[1].text,
            "Section" : table_data[2].text,
            "Title" : table_data[4].text,
            "Meeting Times" : table_data[5].text,
            "Instructor" : table_data[6].text,
        }
        courses.append(course)
    return courses

# Function that takes in a dictionary for a course and returns a Course object
def createCourseObjects(singleCourse):
    newCourse = Course (singleCourse['Status'],singleCourse['Course'],singleCourse['Section'],singleCourse['Title'],singleCourse['Meeting Times'],singleCourse['Instructor'])
    return newCourse




#-----------------------------------------------------------------------------------
# Magic functions because I don't know how to code
#-----------------------------------------------------------------------------------

# This returns a list of course objects
def preGui():
    html = downloadHtml(tuAllCourseUrl)
    hrefs = hrefScrape(html)
    courses = getAllCourses(tuBaseUrl, hrefs)
    courseObjectList = []
    for dept in courses:
        for course in dept:
            tempCourse = createCourseObjects(course)
            courseObjectList.append(tempCourse)
    return courseObjectList

# This returns a list of strings (one each course) that can be displayed in the GUI
def objListToStrings(courseObjectList):
    courseStrings = []
    for i in courseObjectList:
        courseString = (i.getCourseInformation()).encode('ascii', errors='backslashreplace')
        courseStrings.append(courseString)
        print courseString
    return courseStrings

objectList = preGui()
courseStringList = objListToStrings(objectList)








"""
GUI.PY - a gui for a web scraper for TU catalog information
"""
#import course as course
from Tkinter import *

class filterCatalog (Frame):
    def __init__(self, master):
        Frame.__init__(self)
        self.master.title("Find my class")
        self.master.minsize (width = 800, height = 1000)
        self.grid()
        self.nestedFrame = Frame (self)
        self.nestedFrame.grid (row = 1, column = 0)
        #create the labels for input
        self._showAllLabel   = Label (self.nestedFrame, text = "Show All Courses")
        self._showAllLabel.grid(row = 2, column = 0)
        self._showOpenLabel  = Label (self.nestedFrame, text = "Show Only Open \n Courses")
        self._showOpenLabel.grid(row = 2, column = 1)
        self._deptNameLabel  = Label (self, text = "Select department(s) \n to search for \n (use ctrl to select multiple)")
        self._deptNameLabel.grid(row = 0, column = 6)
        self._gradeLvlLabel  = Label (self, text = "Select the academic  level \n of the  course you \n wish to filter by")
        self._gradeLvlLabel.grid(row = 0, column = 9)
        self._KeywordsLabel  = Label (self.nestedFrame, text = "Enter the title of the course you want")
        self._KeywordsLabel.grid(row = 0, column = 0, columnspan = 2)
        self._endTimeLabel   = Label (self, text = "What is the latest you \n want the class to end?")
        self._endTimeLabel.grid(row = 0, column = 15)
        self._startTimeLabel = Label (self, text = "What is the earliest you \n want the class to start?")
        self._startTimeLabel.grid(row = 0, column = 12)


        #data containers for entry field and radionButton
        self.radioButtonVar = IntVar(value = 0)
        self.searchBoxVar = StringVar('')


        #Two radio buttons for "Show Open" and "Show All" options
        self._showAllButton = Radiobutton (self.nestedFrame, text = "",variable = self.radioButtonVar, value = 1)
        self._showAllButton.grid(row = 3, column = 0)

        self._showOpenButton = Radiobutton (self.nestedFrame, text = "",variable = self.radioButtonVar, value = 2)
        self._showOpenButton.grid(row = 3, column = 1)


        #Entry Fields
        self._KeywordEntry = Entry (self.nestedFrame, textvariable = self.searchBoxVar, width = 40, justify = LEFT)
        self._KeywordEntry.grid(row = 1, column = 0, columnspan = 2)

        self.nestedFrame = Frame (self)
        self.nestedFrame.grid (row = 0, column = 0)

        #Listboxes for Department Name, Academic Level, Start Time, and End Time
        self.dptNameScroll = Scrollbar(self, orient = VERTICAL)
        self.dptNameListBox = Listbox(self,selectmode=SINGLE, height = 10,  exportselection=0, yscrollcommand = self.dptNameScroll.set)
        self.dptNameScroll.config (command = self.dptNameListBox.yview)
        for i in (listDeptNames(objectList)): # Thomas
            self.dptNameListBox.insert (END, str(i))
        self.dptNameListBox.grid(row = 1, column = 6, columnspan = 2)
        self.dptNameListBox.columnconfigure(0, weight = 5)
        self.dptNameListBox.rowconfigure (0, weight = 1)
        self.dptNameScroll.grid (row = 1, column = 7, sticky = N+S)

        self.AcLevelScroll = Scrollbar(self, orient = VERTICAL)
        self.AcLevelListBox = Listbox(self,selectmode=SINGLE, exportselection=0, yscrollcommand = self.AcLevelScroll.set)
        self.AcLevelScroll.config (command = self.AcLevelListBox.yview)
        for i in range (0, 6): # Thomas
            self.AcLevelListBox.insert (END, str(i))
        self.AcLevelListBox.grid(row = 1, column = 9, columnspan = 2)
        self.AcLevelListBox.columnconfigure(0, weight = 5)
        self.AcLevelListBox.rowconfigure (0, weight = 1)
        self.AcLevelScroll.grid (row = 1, column = 10, sticky = N+S)

        self.sTimeScroll = Scrollbar(self, orient = VERTICAL)
        self.sTimeListBox = Listbox(self,selectmode=SINGLE, exportselection=0, yscrollcommand = self.sTimeScroll.set)
        self.sTimeScroll.config (command = self.sTimeListBox.yview)
        for i in range (7, 19): # Thomas
            self.sTimeListBox.insert (END, str(i))
        self.sTimeListBox.grid(row = 1, column = 12, columnspan = 2)
        self.sTimeListBox.columnconfigure(0, weight = 5)
        self.sTimeListBox.rowconfigure (0, weight = 1)
        self.sTimeScroll.grid (row = 1, column = 13, sticky = N+S)

        self.eTimeScroll = Scrollbar(self, orient = VERTICAL)
        self.eTimeListBox = Listbox(self,selectmode=SINGLE, exportselection=0, yscrollcommand = self.eTimeScroll.set)
        self.eTimeScroll.config (command = self.eTimeListBox.yview)
        for i in range (8, 20): # Thomas
            self.eTimeListBox.insert (END, str(i))
        self.eTimeListBox.grid(row = 1, column = 15, columnspan = 2)
        self.eTimeListBox.columnconfigure(0, weight = 5)
        self.eTimeListBox.rowconfigure (0, weight = 1)
        self.eTimeScroll.grid (row = 1, column = 16, sticky = N+S)


        #labels for the courses
        self._courseStatusLabel   = Label (self, text = "Status")
        self._courseStatusLabel.grid(row = 8, column = 0)

        self._courseDeptLvlLabel = Label(self, text = "Course")
        self._courseDeptLvlLabel.grid (row = 8, column = 3)

        self._secLabel = Label (self, text = "Section")
        self._secLabel.grid(row = 8, column = 6)

        self._courseTitleLabel = Label (self, text = "Title")
        self._courseTitleLabel.grid(row = 8, column = 9)

        self._meetingTimesLabel = Label (self, text = "Meeting Times")
        self._meetingTimesLabel.grid(row = 8, column = 12)

        self._instructorNameLabel = Label (self, text = "Instructor")
        self._instructorNameLabel.grid (row = 8, column = 15)

        #submit button
        self.submitButton = Button (self, text = "Apply Filters", command = self.submitFilters)
        self.submitButton.grid (row = 0, column = 19)

        #listbox for courses to display
        self.courseScroll = Scrollbar(self, orient = VERTICAL)
        self.courseListBox = Listbox(self,selectmode=MULTIPLE, height = 40,  exportselection=0, yscrollcommand = self.courseScroll.set)

        self.courseScroll.config (command = self.courseListBox.yview)
        for i in (courseStringList): # Thomas
            self.courseListBox.insert (END, str(i))
        self.courseListBox.grid(row = 9, column = 0, columnspan = 20, rowspan = 1, sticky = N+E+W)
        self.courseListBox.columnconfigure(0, weight = 5)
        self.courseListBox.rowconfigure (20, weight = 10)
        self.courseScroll.grid (row = 9, column = 21, sticky = N+S)

    #listFilters = [status, title, int startTime, int EndTime, list departmentName, list academicLevel]
    def submitFilters (self):
        filterItems = ["", "", "", "", "", ""]

        if(self.radioButtonVar == 1):
            filterItems[0] = False
        elif(self.radioButtonVar == 2):
            filterItems[0] = True
        filterItems[1] = self._KeywordEntry.get()
        filterItems[2] = self.sTimeListBox.get(ACTIVE)
        filterItems[3] = self.eTimeListBox.get(ACTIVE)
        filterItems[4] = self.dptNameListBox.get(ACTIVE)
        filterItems[5] = self.AcLevelListBox.get(ACTIVE)

        for i in objectList:
            if(filterItems[4] != i.getDepartment()):
                objectList.remove(i) # Get rid of what we don't want to see
        courseStringList = objListToStrings(objectList) # Make a new list

        #listOfLines = self.dptNameListBox.curselection() # This only tells us which lines are active
        #listOfDept = []
        #for i in range(len(listOfLines)):
            #listOfDept.append(listOfLines.get()) # This actually gets us our info http://stackoverflow.com/questions/13828531/problems-in-python-getting-multiple-selections-from-tkinter-listbox
        #filterItems[4] = listOfDept
        #listOfLines = self.AcLevelListBox.curselection() # This only tells us which lines are active
        #listOfLvl = []
        #for i in range(len(listOfLines)):
            #listOfLvl.append(listOfLines.get()) # This actually gets us our info
        #filterItems[5] = listOfLvl
        #return filterItems

    def checkForGroupUpdates(self):
        self.after(100, self.checkForGroupUpdates)



def main():
    root = Tk()
    gui = filterCatalog(root)
    gui.pack()

    root.after_idle(gui.checkForGroupUpdates)
    root.mainloop()

main()
