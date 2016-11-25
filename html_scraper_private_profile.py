
import csv, html.parser, urllib, os, time, codecs
from bs4 import BeautifulSoup as bs


# Script to scrape the linked in profiles html files in folders. This is for the html files of the 
# private profiles. 


directory = "/Profile_full/" #set directory where the html files are
# Functions

def find_and_copy(body, begin, end, position):
	if body.find(begin, position) == -1:
		value = ""
	else:
		p1 = body.find(begin, position) + len(begin)
		p2 = body.find(end, p1)
		value = body[p1:p2]
	return value

def find_and_copy_incl(body, begin, end, position):
	p1 = body.find(begin, position) 
	p2 = body.find(end, p1) + len(end)
	if p1 == -1:
		value = ""
	else:
		value = body[p1:p2]
	return value

def rfind_and_copy(body, begin, end, position):
	p1 = body.rfind(begin, 0, position) + len(begin)
	p2 = body.find(end, p1)
	value = body[p1:p2]
	return value



# Set up matrix

#     memberid
#  1  name
#  2  headline
#  3  locality
#  4  industry
#  5  current
#  6  previous
#  7  number of connections
#  8  languages
#  9  skills


titles = ['memberid','headline','locality','industry','industry_lan','current','previous','connections','skills','languages']

d = list()
d.append(titles)

filecount = 0

start_time = time.time()

for root, dirs, files in os.walk(directory):
	for file in files:
		if file.endswith(".html"):
			filecount = filecount + 1
			pathname = (os.path.join(root, file))
# Extract memberid from filename
			memberid = rfind_and_copy(pathname, "/", ".", len(pathname))
			print('profile number', filecount, ' ', memberid)
# Load html file
			file = codecs.open(pathname, 'r', 'utf-8')
			document= str(bs(file.read(), "lxml"))
#			print(document)


# Parse sections

#			print(document)
			section = find_and_copy_incl(document, '<div class="profile-card vcard">', '<!-- End profile card -->', 0)

#1: memberid
			drow = [memberid]

#2: headline
			value = find_and_copy(section, '<p class="title" dir="ltr">', '</p>', 0)
			value = bs(value,"lxml").text
			drow.append(value)

#3: locality
			value = find_and_copy(section, '<span class="locality">','</span>', 0)
			if "<a href=" in value:
				value = bs(value,"lxml").text
			else:
				value = value
			drow.append(value)

#4: industry
			value = find_and_copy(section, '<dd class="industry">','</dd>', 0)
			value = bs(value,"lxml").text
			drow.append(value)
			value = find_and_copy(document, '<html lang="','"', 0)
			drow.append(value)

#5: current position
			value = find_and_copy(section, '<tr id="overview-summary-current">','</tr>', 0)
			value = find_and_copy(value, '<ol>','</ol>', 0)
			if '>, <' in value:
				value = value.replace(">, <", ">|<")
			value = bs(value,"lxml").text
			drow.append(value)

#6: past position

			value = find_and_copy(section, '<tr id="overview-summary-past">','</tr>', 0)
			value = find_and_copy(value, '<ol>','</ol>', 0)
			if '>, <' in value:
				value = value.replace(">, <", ">|<")
			value = bs(value,"lxml").text
			drow.append(value)

#7: connections

			value = find_and_copy(section, '<div class="member-connections">','</div>', 0)
			value = find_and_copy(value, '<strong>','</strong>', 0)
			value = bs(value,"lxml").text
			drow.append(value)


#8: skills
			section = find_and_copy_incl(document, '<div id="profile-skills">', '</ul></div>', 0)
			li = []
			c = section.count('data-endorsed-item-name="')
			p2 = 0 
			for j in range(0,c):
				p1 = section.find('data-endorsed-item-name="', p2) + len('data-endorsed-item-name="') 
				p2 = section.find('"', p1)
				skill = section[p1:p2]
				skill = bs(skill,"lxml").text
				li.append(skill)
			value = '|'.join(li)
			drow.append(value)

#9: languages
			section = find_and_copy_incl(document, '<div id="languages-view">', '</div></div>', 0)
			c = section.count('<div class="languages-proficiency">')
			p2 = 0
			for j in range(0,c):
#				print('prof')
				p1 = section.find('<div class="languages-proficiency">', p2)
				p2 = section.find('</div>', p1) + len('</div>')
				rem = section[p1:p2]
				section = section.replace(rem, "")
				p2 = p2 - len(rem)
			if '</li><li' in section:
				section = section.replace('</li><li', '</li>|<li')
			value = bs(section,"lxml").text
			drow.append(value)
			d.append(drow)


t = time.time() - start_time
print ('---end---')
print ('time: ',t,' sec')

#print(d)


# Write to file
folder = "htmldata"
file_name = "data_private_profiles"
directory1 = '/Desktop/' + folder
if not os.path.exists(directory1):
	os.makedirs(directory1)
file_path = directory1 + '/' + file_name + '.csv'
with open(file_path, "w+") as file:
	writer = csv.writer(file, delimiter=';')
	writer.writerows(d)
