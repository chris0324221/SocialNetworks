import csv, html.parser, urllib, os, time, codecs
from bs4 import BeautifulSoup as bs


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


# For every file in folders

directory = "/Users/Eveleens/Documents/03_Werk/11_UU/Studie2/Data/Profiles_public_archief/"
filecount = 0

start_time = time.time()

for root, dirs, files in os.walk(directory):
	for file in files:
		if file.endswith(".html"):
			filecount = filecount + 1
print('total filecount: ',filecount, ' Here we go!')


filecount = 0
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


#1: memberid
			drow = [memberid]

			section = find_and_copy_incl(document, 'section class="profile-section" id="topcard">', '</section>', 0)
#			print(section)
#2: headline
			value = find_and_copy(section, '<p class="headline title" data-section="headline">', '</p>', 0)
			value = bs(value,"lxml").text
			drow.append(value)
#3: locality
			value = find_and_copy(section, '<span class="locality">','</span>', 0)
			drow.append(value)
#4: industry
			value = find_and_copy(section, '<dd class="descriptor">','</dd>', 0)
			value = bs(value,"lxml").text
			drow.append(value)
			value = find_and_copy(document, '<html lang="','"', 0)
			drow.append(value)

#5: current position
			if '<tr data-section="currentPositionsDetails">' in section:
				currentpositions = find_and_copy(section, '<tr data-section="currentPositionsDetails">','</tr>', 0)
			elif '<tr data-section="currentPositions">' in section:
				currentpositions = find_and_copy(section, '<tr data-section="currentPositions">','</tr>', 0)
			else:
				currentpositions = ""
#			print('currentpositions: ',currentpositions)
			rem = find_and_copy_incl(currentpositions, "<th>", "</th>", 0)
			currentpositions = currentpositions.replace(rem, "")
			if '>, <' in currentpositions:
				currentpositions = currentpositions.replace(">, <", ">|<")
			value = bs(currentpositions,"lxml").text
#			print(value[0:500])
			drow.append(value)
#6: past position
			if '<tr data-section="pastPositions">' in section:
				pastpositions = find_and_copy(section, '<tr data-section="pastPositions">','</tr>', 0)
			elif '<tr data-section="pastPositionsDetails">' in section:
				pastpositions = find_and_copy(section, '<tr data-section="pastPositionsDetails">','</tr>', 0)
			else:
				pastpositions = ""
			rem = find_and_copy_incl(pastpositions, "<th>", "</th>", 0)
			pastpositions = pastpositions.replace(rem, "")
			if '>, <' in pastpositions:
				pastpositions = pastpositions.replace(">, <", ">|<")
			value = bs(pastpositions,"lxml").text
#			print(value[0:500])
			drow.append(value)
#7: connections
			value = find_and_copy(section, '<div class="member-connections"><strong>','</strong>', 0)
			value = bs(value,"lxml").text
			drow.append(value)

#8: skills
			section = find_and_copy_incl(document, '<section class="profile-section" data-section="skills" id="skills">', '</section>', 0)
#			print(section)
			rem = find_and_copy_incl(section, '<h3','</h3>', 0)
			section = section.replace(rem, "")
			c = section.count('<label')
			p2 = 0
			for j in range(0,c):
#				print('labelskill')
				p1 = section.find('<label', p2) 
				p2 = section.find('</label></li>', p1) + len('</label></li>')
				if p1 == -1:
					rem = ""
				else:
					rem = section[p1:p2]
#				print(rem)
				section = section.replace(rem, "")
			if '</li><li' in section:
				section = section.replace('</li><li', '</li>|<li')
			value = bs(section,"lxml").text
#			print(value)
			drow.append(value)

#9: languages
			section = find_and_copy_incl(document, '<section class="profile-section" data-section="languages" id="languages">', '</section>', 0)
#			print(section)
			rem = find_and_copy_incl(section, '<h3','</h3>', 0)
			section = section.replace(rem, "")
			c = section.count('<label')
			p2 = 0
			for j in range(0,c):
#				print('labellang')
				p1 = section.find('<label', p2) 
				p2 = section.find('</label></li>', p1) + len('</label></li>')
				if p1 == -1:
					rem = ""
				else:
					rem = section[p1:p2]
#				print(rem)
				section = section.replace(rem, "")
			c = section.count('<p class="proficiency">')
			p2 = 0
			for j in range(0,c):
#				print('prof')
				p1 = section.find('<p class="proficiency">', p2) 
				p2 = section.find('</p>', p1) + len('</p>')
				if p1 == -1:
					rem = ""
				else:
					rem = section[p1:p2]
#				print(rem)
				section = section.replace(rem, "")
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
file_name = "data_public_profiles"
directory1 = '/Users/Eveleens/Desktop/' + folder
if not os.path.exists(directory1):
	os.makedirs(directory1)
file_path = directory1 + '/' + file_name + '.csv'
with open(file_path, "w+") as file:
	writer = csv.writer(file, delimiter=';')
	writer.writerows(d)

