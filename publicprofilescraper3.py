import requests, csv, random, time, cgi, html.parser, urllib
from bs4 import BeautifulSoup as bs
from unidecode import unidecode
from fuzzywuzzy import process, fuzz


connectionfile = '/Users/Eveleens/Desktop/compiledconnectionlists_recent.csv'
sess = requests.session()
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36'}
no_prof = 10000
wt1 = 0
wt2 = 0
h = html.parser.HTMLParser()

# Build workmatrix of xxxx new members to find
def build_workmatrix (connectionfile):
	memberlist = []
	with open('/Users/Eveleens/Desktop/done_data.csv', 'r') as dd:
		reader = csv.reader(dd,delimiter=',')
		for row in reader:
			memberlist.append(row[3])
	count = 0 
	with open('/Users/Eveleens/Desktop/mandy_connections.csv', 'r') as mc:
		reader = csv.reader(mc)
		for row in reader:
			if len(row) == 0:
				continue
			else:
				memberlist.append(row)
	counter = 0
	workmatrix = []
	with open(connectionfile, 'r') as f:
		reader = csv.reader(f, delimiter=';')
		for row in reader:
			if row[3] not in memberlist:
				workmatrix.append(row)
				counter = counter + 1
				if counter == no_prof:
					break
	return workmatrix

# Searches: Find (find last) and copy functions:
def find_and_copy(body, begin, end, position):
	p1 = body.find(begin, position) + len(begin)
	p2 = body.find(end, p1)
	value = body[p1:p2]
	return value
def rfind_and_copy(body, begin, end, position):
	p1 = body.rfind(begin, 0, position) + len(begin)
	p2 = body.find(end, p1)
	value = body[p1:p2]
	return value

# Search strategy name in http
def search_link(sess, headers, name, headline, pub_url):
	print('search_link')
	first = name.split(' ', 1)[0]
	last = name.split(' ', 1)[1]
	search_url = 'https://www.linkedin.com/pub/dir/?first=' + first + '&last=' + last + '&search=Search'
	url = search_url
	pub_url = direction(sess, headers, url, name, headline, pub_url)
	return pub_url

# Search strategy public directory
def search_dir(sess, headers, name, headline, pub_url):
	print('search_dir')
	name_cgi = cgi.escape(name)
	first_letter = name_cgi[0:1]
	search_url = "https://www.linkedin.com/directory/people-" + first_letter.lower() + "/"
	for j in range(0,3):
#		time.sleep(0.5)
		targetpage = sess.get(search_url, headers = headers)
		text = targetpage.text
		soup = bs(text, 'lxml')
		name_ranges = soup.findAll('li', {'class':'content'})
#		print(name_ranges)
		hyph_c = 0 #check if the names are already there (in cases of u, q, x)
		for nr in name_ranges:
			nr = str(nr)
			hyph_c = hyph_c + nr.count(" - ")
		if hyph_c < 2 * len(name_ranges):
			break
		count = 0
		while (count < len(name_ranges)):
			body = str(name_ranges[count].a)
			value = find_and_copy(body, '>', '<',0)
			p = body.find(" - " + first_letter) + len(" - ")
			name_ch = name + ' - '
			if name_ch in value:
				search_url = find_and_copy(body, 'href="', '"',0)
				break
			elif name <= body[p:]:
				search_url = find_and_copy(body, 'href="', '"',0)
				break
			count = count + 1
#		body = str(name_ranges[count].a)
#		search_url = find_and_copy(body, 'href="', '"',0)
		print(search_url)
	targetpage = sess.get(search_url, headers = headers)
	text = targetpage.text
	text_h = h.unescape(text)
	pos_name = text_h.find('title="' + name)
	if pos_name == -1:
		pub_url = ""
	else:
		url_end = rfind_and_copy(text, 'href="', '"', pos_name)
		url = "https://www.linkedin.com/" + url_end
		pub_url = direction(sess, headers, url, name, headline, pub_url)
	print('pub_url',pub_url)
	return pub_url

# Komend vanaf search strategies; directions to the right next function
def direction(sess, headers, url, name, headline, pub_url):
	print('directions')
	print('url: ',url)
	print('pub_url: ',pub_url)
	count = 0
	while count < 10:
#		print('while')
		try:
#			print('try')
			count = count + 1
			targetpage = sess.get(url, headers = headers)
		except:
			print('ENCODING ERROR')
			time.sleep(10)
			continue
		break
	text = targetpage.text
	if 'content="public_profile' in text:
		pub_url = public_profile(text, headline, name, pub_url)
	elif 'content="public_directory"' in text:
		pub_url = public_directory_page(sess, headers, name, headline, text, pub_url)
	else:
		pub_url = ""
	return pub_url

# Als ik op een public profile kom, check of het de goeie is en geef de url terug
def public_profile(text, headline, name, pub_url):
	print('public_profile')
	text_cgi = cgi.escape(text)
	headline_cgi = cgi.escape(headline)
	name_cgi = cgi.escape(name)
	soup = bs(text, 'lxml')
	headline_check = find_and_copy(text, 'data-section="headline">', '</p>', 0)
	#original
	if headline_cgi in text and name_cgi in text:
		pub_url = find_and_copy(text, '"canonical" href="', '"', 0)
		pub_url = urllib.parse.unquote(pub_url)
		if "https://oo.linkedin.com" in pub_url:
			pub_url = pub_url.replace("oo", "www", 1)
			print('replace oo')
		if "https://FR.linkedin.com" in pub_url:
			pub_url = pub_url.replace("FR", "www", 1)
			print('replace FR')
		if "https://cb.linkedin.com" in pub_url:
			pub_url = pub_url.replace("cb", "www", 1)
			print('replace cs')
		if "https://cs.linkedin.com" in pub_url:
			pub_url = pub_url.replace("cs", "www", 1)
			print('replace cs')
		if "https://NL.linkedin.com" in pub_url:
			pub_url = pub_url.replace("NL", "www", 1)
			print('replace NL')
		if "https://US.linkedin.com" in pub_url:
			pub_url = pub_url.replace("US", "www", 1)
			print('replace US')
		print('pub_url: ',pub_url)
	#extra fuzzywuzzy
	elif fuzz.ratio(headline, headline_check) >= 95 and len(headline) > 10:
		print('using fuzzy')
		pub_url = find_and_copy(text, '"canonical" href="', '"', 0)
		pub_url = urllib.parse.unquote(pub_url)
		if "https://oo.linkedin.com" in pub_url:
			print('replace oo')
			pub_url = pub_url.replace("oo", "www", 1)
		if "https://FR.linkedin.com" in pub_url:
			pub_url = pub_url.replace("FR", "www", 1)
			print('replace FR')
		if "https://cb.linkedin.com" in pub_url:
			pub_url = pub_url.replace("cb", "www", 1)
			print('replace cb')
		if "https://cs.linkedin.com" in pub_url:
			pub_url = pub_url.replace("cs", "www", 1)
			print('replace cs')
		if "https://NL.linkedin.com" in pub_url:
			pub_url = pub_url.replace("NL", "www", 1)
			print('replace NL')
		if "https://US.linkedin.com" in pub_url:
			pub_url = pub_url.replace("US", "www", 1)
			print('replace US')
	else:
		comment = 'Wrong public profile'
	return pub_url

# Als ik in een top-x public directory kom, vind de juiste en ga naar public profile
def public_directory_page(sess, headers, name, headline, text, pub_url):
	print('public_directory_pages')
	headline_cgi = cgi.escape(headline)
	soup = bs(text, 'lxml')
	profile_cards = soup.findAll('div', {'class':'profile-card'})
	if headline_cgi in text:
		count = 0
		while (count < len(profile_cards)):
			paragraph = str(profile_cards[count])
			headline_paragr = paragraph[20:len(paragraph)-4]
			if headline_cgi in headline_paragr:
				pub_url = profile_cards[count].a['href']
				profilepagecheck = sess.get(pub_url, headers = headers)
				text = profilepagecheck.text
				pub_url = public_profile(text, headline, name, pub_url)
				break
			count = count + 1
	elif len(headline_cgi) > 10:
		print('using fuzzy')
		count = 0
		while (count < len(profile_cards)):
			paragraph = str(profile_cards[count])
			headline_paragr = paragraph[20:len(paragraph)-4]
			if fuzz.ratio(headline_cgi, headline_paragr) >= 95:
				pub_url = profile_cards[count].a['href']
				profilepagecheck = sess.get(pub_url, headers = headers)
				text = profilepagecheck.text
				pub_url = public_profile(text, headline, name, pub_url)
				break
			count = count + 1
	else:
		comment = 'Target not found in public directory top x page'
	return pub_url 

# Scrape it
def scraper(sess, pub_url, headers, memberid):
	print(pub_url)
	print('scrape it')
#	time.sleep(0.5)
	profile = sess.get(pub_url, headers = headers)
	html = profile.text	
	file_path = '/Users/Eveleens/Desktop/Profiles_public/' + str(memberid) + '.html'
	with open(file_path, "w+") as file:
		file.write(html)

# Main sessie
def main(sess, headers, workmatrix, wt1, wt2):
	counter = 0
	scraped = 0
	for row in workmatrix:
		done_data = []
		counter = counter + 1
		pub_url = ""
		memberid = row[3]
		name = row[0]
		headline = row[2]
		print('searching for: ',memberid,', ',name,', ',headline)
		pub_url = search_link(sess, headers, name, headline, pub_url)
		if pub_url[:4] == "http":
			row.append(pub_url)
			scraper(sess, pub_url, headers, memberid)
			scraped = scraped + 1
		else:
			first_letter = name[0:1]
			if first_letter.isalpha() == False:
				pub_url = "Cannot find public url"
			else:
				pub_url = search_dir(sess, headers, name, headline, pub_url)
				if pub_url[:4] == "http":
					row.append(pub_url)
					scraper(sess, pub_url, headers, memberid)
					scraped = scraped + 1
				else: 
					pub_url = "Cannot find public url"
					row.append(pub_url)
		done_data.append(row)
		print('searched: ',counter, 'scraped: ',scraped)
		wait_time = random.uniform(wt1, wt2)
		time.sleep(wait_time)
		with open('/Users/Eveleens/Desktop/done_data.csv', 'a') as dd:
			writer = csv.writer(dd, delimiter=',')
			writer.writerows(done_data)

t1 = time.time()
workmatrix = build_workmatrix(connectionfile)
main(sess, headers, workmatrix, wt1, wt2)
t2 = time.time()
print(no_prof,'profiles, time: ', (t2-t1)/60,'min')


#Als er maar één iemand met die naam is, maar zonder headline (of verkeerde headline), dan alsnog een hit?