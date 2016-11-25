import os, csv, sys

# Script to go through the downloaded connectionlists. Options are 1) create id-scrapedata matrix (i.e. an overview 
# of when which profile was scraped, 2) build cofounderconnectionlists (use earliest connectionlist to build an edgelist 
# in wihch per cofounder you have an list of connections, or 3) compile all unique connections. 


# The directory should have the format of folders with names of dates and inside the connectionslists with a 
# name memberid_connections.csv

directory = '/Connectionlistsdownloads/' # set correct folder
today = input("what is the date? (YYYMMDD): ")
savedirectory = '/Users/Eveleens/Desktop/'

def find_and_copy(body, begin, end, position):
	p1 = body.find(begin, position) + len(begin)
	p2 = body.find(end, p1)
	value = body[p1:p2]
	return value

def menu():
	print('\n1: create id-scrapedate matrix\n2: build cofounderconnectionlist \n3: compile all connections\n4: exit\n')
	choice = str(input('option: '))
	return choice

def main(directory):
	choice = menu()
	if choice == "1":
		idmatrix(directory)
	elif choice == "2":
		cofounderconnections(directory)
	elif choice == "3":
		compiledconnections(directory)
	elif choice == "4":
		sys.exit()
	else:
		print('not an option')
	print('\n')

#build idmatrix
def idmatrix(directory):
	id_date_mat = []
	filecount = 0
	idcount = 0
	for root, dirs, files in os.walk(directory):
		for file in files:
			if file.endswith(".csv"):
				filecount = filecount + 1
				fullname = (os.path.join(root, file))
				print('.',end="",flush=True)
				x = find_and_copy(fullname, 'Connectionlistsdownloads/', '_',0)
				date = x.split('/')[0]
				date = date[6:] + "-" + date[4:6] + "-" + date[0:4]
				id = x.split('/')[1]
				row = [id,date]
				id_date_mat.append(row)
	id_dates = []
	for row in id_date_mat:
		check = False
		for id_dates_row in id_dates:
			if row[0] == id_dates_row[0]:
				check = True
				id_dates_row.append(row[1])
				break
		if check == False:
			idcount = idcount + 1
			id_dates.append(row)
	print('\n-filecount: ',filecount,'\n-idcount: ', idcount)
	fn = today + '_date_id_mat.csv'
	fp = os.path.join(savedirectory, fn)
	with open(fp, 'w', newline='') as dm:
		writer = csv.writer(dm, delimiter=';')
		writer.writerows(id_dates)

#build cofounderconnectionlist with earliest? connectionlists
def cofounderconnections(directory):
	idlist = []
	cofcon = []
	strow = ['memberid', 'connectionname', 'link', 'headline', 'connectionid', 'date']
	cofcon.append(strow)
	filecount = 0
	connectioncount = 0
	for root, dirs, files in os.walk(directory):
		for file in files:
			if file.endswith(".csv"):
				filecount = filecount + 1
				fullname = (os.path.join(root, file))
				print('.',end="",flush=True)
				x = find_and_copy(fullname, 'Connectionlistsdownloads/', '_',0)
				date = x.split('/')[0]
				date = date[6:] + "-" + date[4:6] + "-" + date[0:4]
				id = x.split('/')[1]
				check = False
				for ids in idlist:
					if ids == id:
						check = True
						break
				if check == False:
					idlist.append(id)
					with open(fullname, 'r') as fh:
						reader = csv.reader(fh, delimiter=';')
						for row in reader:
							row.insert(0, id)
							row.append(date)
							cofcon.append(row)
							connectioncount = connectioncount + 1
	print('\n-filecount: ',filecount,'\n-connectioncount: ', connectioncount)
	fn = today + '_cofounderconnections.csv'
	fp = os.path.join(savedirectory, fn)
	with open(fp, 'w', newline='') as dm:
		writer = csv.writer(dm, delimiter=';')
		writer.writerows(cofcon)

#compile all unique connections
def compiledconnections(directory):
	connectionslist = []
	filecount = 0
	connectioncount = 0
	unique_connectioncount = 0
	for root, dirs, files in os.walk(directory):
		for file in files:
			if file.endswith(".csv"):
				filecount = filecount + 1
				fullname = (os.path.join(root, file))
				print('.',end="",flush=True)
				with open(fullname, 'r') as fh:
					filereader = csv.reader(fh, delimiter=';')
					for row in filereader:
						connectioncount = connectioncount + 1
						check = False
						for x in connectionslist:
							if row[3] == x[3]:
								check = True
								break
						if check == False:
							unique_connectioncount = unique_connectioncount + 1
							connectionslist.append(row)
	print('\n-filecount: ',filecount,'\n-connectioncount: ', connectioncount,'\n-unique_connectioncount: ', unique_connectioncount)
	fn = today + '_compiledconnectionlists.csv'
	fp = os.path.join(savedirectory, fn)
	with open(fp, 'w', newline='') as dm:
		writer = csv.writer(dm, delimiter=';')
		writer.writerows(connectionslist)

main(directory)
