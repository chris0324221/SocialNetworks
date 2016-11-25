import requests, getpass, csv, random, time, sys, os.path
from unidecode import unidecode
from bs4 import BeautifulSoup

def call():
	sess = login()
	mainloop(sess)

def login(): 
	linkedin_username = '........@..........' #enter LinkedIn e-mail
	linkedin_password = '.................' #enter LinkedIn password
	sess = requests.session()
	loginpage = sess.get('https://www.linkedin.com/uas/login')
	loginpagetext = BeautifulSoup(loginpage.text, "lxml")
	loginfields = loginpagetext.find('form', {'name': 'login'}).findAll('input', {'type': ['hidden', 'submit']})
	postfields = {field.get('name'): field.get('value') for field in loginfields}
	postfields['session_key'] = linkedin_username
	postfields['session_password'] = linkedin_password
	postresp = sess.post('https://www.linkedin.com/uas/login-submit', data=postfields)
	return sess

def mainloop(sess):	
	start_time = time.time()
	filecounter = 0
	foundercounter = 0 
	ids = 0
	filecounter = filecounter + 1
	input_file = '/Desktop/memberids.txt' #this is a simple textfile that lists the memberships id's of the people you're interested in
	folder = input('Date (YYYYMMDD): ')  #folder to save the output in (e.g. the date)
	with open(input_file, 'r') as li:
		lines = li.readlines()
		for row in lines:
			ids = ids + 1
		for row in lines:
			foundercounter = foundercounter + 1
			print(foundercounter," of ",ids,end="",flush=True)
			row = row.strip()
			memberid = row
            #Scrape connections of this member
			scrape_conn(sess, memberid, folder)
            #Scrape the profile while you're at it
			scrape_prof(sess, memberid, folder)
			wait_time = random.uniform(10, 20)		
			time.sleep(wait_time)
	t = time.time() - start_time
	print ('---end---')
	print ('time: ',t,' sec')
	print ('number of files: ',filecounter)
	print ('number of founders: ',foundercounter)
	
def scrape_conn(sess, memberid, folder):
#	print('scrape_con')
	a = 'https://www.linkedin.com/profile/profile-v2-connections?id='
	id = memberid
	b = '&offset='
	offset = 0
	c = '&count=10&distance=1&type=INITIAL'
	lengthcheck = 100
	addressbook = []
	addressbookrow = []
	pos_body = 0
	pagecount = 0

	beginendarray=[['_full_name":"','",'],['"pview":"','",'],['"headline":"','",'],['"memberID":','}']]

	while lengthcheck > 45:
#		print('in while')
		pagecount = pagecount + 1
		pos_body = 0
		targetlink = a + str(id) + b + str(offset) + c
		targetlink = str(targetlink)
		targetpage = sess.get(targetlink)
		bodyhand = targetpage.text
		lengthcheck = len(bodyhand)
		for member in range(bodyhand.count('memberID')):
#			print('in for member in range')
			addressbookrow = []
			print('.',end="",flush=True)
			for i in range(len(beginendarray)):
				pos_begin = bodyhand.find(beginendarray[i][0], pos_body) + len(beginendarray[i][0])
				pos_end = bodyhand.find(beginendarray[i][1], pos_begin)
				value = bodyhand[pos_begin:pos_end]
				value = value.rstrip('\r\n')
				value = unidecode(value)
				pos_body = pos_end
				addressbookrow.append(value)
			addressbook.append(addressbookrow)
		offset = offset + 10
		wait_time = random.uniform(1, 5)		
		time.sleep(wait_time)

	print('')
	#Save result
	file_name = str(memberid)    
	directory1 = '/Desktop/Connectionlists/' + folder
	if not os.path.exists(directory1):
		os.makedirs(directory1)    
	file_path = directory1 + '/' + file_name + '_connections.csv'
	with open(file_path, "w+") as file:
		writer = csv.writer(file, delimiter=';')
		writer.writerows(addressbook)

def scrape_prof(sess, memberid, folder):
#	print('in scrape_prof')
	profile_url = 'https://www.linkedin.com/profile/view?id='+ memberid	
	profile_page = sess.get(profile_url)
	html = profile_page.text
	file_name = str(memberid)
	directory2 = '/Desktop/Profile_full/' + folder	
	if not os.path.exists(directory2):
		os.makedirs(directory2)    
	file_path = directory2 + '/' + file_name + '.html'
	with open(file_path, "w+") as file:
		file.write(html)

call()

