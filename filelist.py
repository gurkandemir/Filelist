## Gurkan Demir 2015400177 ##
## Burak Ikan Yildiz 2015400069 ##

import os, argparse, hashlib, subprocess, re, datetime,pwd,sys, filecmp
from collections import deque


#######################################
############## Methods ################
#######################################

# Parses arguments from command line. Returns parsed argument list. #
def parseArg():
	parser= argparse.ArgumentParser(description='Project 2')
	parser.add_argument('-before', dest="before", action='store')
	parser.add_argument('-after', dest="after", action='store')
	parser.add_argument('-match', dest="match", action='store')
	parser.add_argument('-bigger', dest="bigger", action='store')
	parser.add_argument('-smaller', dest="smaller", action='store')
	parser.add_argument('-delete', dest="delete", action='store_true',default=False)
	parser.add_argument('-zip', dest="zip", action='store')
	parser.add_argument('-duplcont', dest="duplcont", action='store_true',default=False)
	parser.add_argument('-duplname', dest="duplname", action='store_true',default=False)
	parser.add_argument('-stats', dest="stats", action='store_true',default=False)
	parser.add_argument('-nofilelist', dest="nofilelist", action='store_true',default=False)
	parser.add_argument('directories', action='store',nargs='*')
	return parser.parse_args()

# Extract directories from arguments. Returns the list of directories; default is current directory. #
def handleDir():
	dirlist=[]
	global arguments
	if arguments.directories:
		for path in arguments.directories:
			if path[0]=="/":
				dirlist.append(path)
 			#Add current directory path to relative path			
			else:
				dirlist.append(os.path.abspath(path))
	# If no path is given, add current directory path
	if not dirlist:
		dirlist=[os.getcwd()]
	return dirlist

#Traverse directories and finds files which has properties that we want. Returns filelist, and statistics of program.
def dirTraverse():
	filelist=[]
	namelist=[]
	totalFileVisited=0
	totalFileListed=0
	totalSizeVisited=0
	totalSizeListed=0
	temp=1
	while dirlist:
		path=dirlist.popleft()
		curlist=os.listdir(path)
		for name in curlist:
			newpath=path+"/"+name
			if os.path.isdir(newpath):
				if not(name=="ZIP"):
					dirlist.append(newpath)
			else:
				counter=0
				if(arguments.before):
					counter=counter+1
					if(before(newpath)):
						counter=counter-1
				if(arguments.after):
					counter=counter+1
					if(after(newpath)):
						counter=counter-1
				if(arguments.bigger):
					counter=counter+1
					if(bigger(newpath)):
						counter=counter-1
				if(arguments.smaller):
					counter=counter+1
					if(smaller(newpath)):
						counter=counter-1
				if(arguments.match):
					counter=counter+1
					if(match(name)):
						counter=counter-1
				
				totalFileVisited=totalFileVisited+1
				totalSizeVisited=totalSizeVisited+fSize(newpath)
				if(counter==0):
					if(arguments.zip):
						if name in namelist:
							tempname,tempext=getName(name)
							newname=tempname+"\("+str(temp)+"\)"+tempext
							temp=temp+1
							os.system("mv "+escape(newpath)+" "+escape(path)+"/"+newname)
							os.system("cp "+escape(path)+"/"+newname+" "+escape(curPath)+"/ZIP")
							os.system("mv "+escape(path)+"/"+newname+" "+escape(path)+"/"+name)
						else:
							os.system("cp "+escape(newpath)+" "+escape(curPath)+"/ZIP")
					filelist.append(newpath)
					namelist.append(name)
					totalFileListed=totalFileListed+1
					totalSizeListed=totalSizeListed+fSize(newpath)
	
	return filelist,namelist,totalFileVisited,totalFileListed,totalSizeVisited,totalSizeListed

#Returns the file name and extension of given path.
def getName(name):
	filename,fileext = os.path.splitext(name)
	return filename,fileext

#Returns given files' size.
def fSize(filepath):
	filesize=os.path.getsize(filepath)
	return filesize	

#Checks whether the given file is last modified before the given time.
def before(filepath):
	modtime=os.path.getmtime(filepath)
	time=datetime.datetime.fromtimestamp(modtime).strftime('%Y%m%dT%H%M%S')
	if len(arguments.before)>8:	
		return arguments.before>time
	else:
		time=datetime.datetime.fromtimestamp(modtime).strftime('%Y%m%d')
		return arguments.before>time

#Checks whether the given file is last modified after the given time.
def after(filepath):
	modtime=os.path.getmtime(filepath)
	time=datetime.datetime.fromtimestamp(modtime).strftime('%Y%m%dT%H%M%S')
	if len(arguments.after)>8:	
		return arguments.after<time
	else:
		time=datetime.datetime.fromtimestamp(modtime).strftime('%Y%m%d')
		return arguments.after<time

#Checks whether the given file's size is bigger than the given number.
def bigger(filepath):
	filesize=os.path.getsize(filepath)
	bigArg=arguments.bigger
	bigArg=str(bigArg)
	newInt=arguments.bigger
	if bigArg[-1]=='K':
		newInt=int(bigArg[:-1])*1024
	elif bigArg[-1]=='M':
		newInt=int(bigArg[:-1])*1024*1024
	elif bigArg[-1]=='G':
		newInt=int(bigArg[:-1])*1024*1024*1024				
	return int(newInt)<int(filesize)

#Checks whether the given file's size is smaller than the given number.
def smaller(filepath):
	filesize=os.path.getsize(filepath)
	smallArg=arguments.smaller
	smallArg=str(smallArg)
	newInt=arguments.smaller
	if smallArg[-1]=='K':
		newInt=int(smallArg[:-1])*1024
	elif smallArg[-1]=='M':
		newInt=int(smallArg[:-1])*1024*1024
	elif smallArg[-1]=='G':
		newInt=int(smallArg[:-1])*1024*1024*1024		
	return int(newInt)>int(filesize)

#Deletes the given file.
def delete(filepath):
	os.system("rm "+escape(filepath))

#Replaces space and quotes for path, returns safe path
def escape(filepath):
	filepath = filepath.replace(" ", "\\ ")
    	filepath = filepath.replace("\"", "\\\"")
	return filepath

#Zips the given files.
def zipper():
	os.chdir(escape(curPath)+"/ZIP")
	os.system("zip ../"+arguments.zip+" ./*")
	os.chdir(escape(curPath))

#Checks whether the given file's name matches with given regex.
def match(filepath):
	return bool(re.match(arguments.match,filepath))

#Sorts the files according to their names.
def sortedList(filelist,namelist):
	for i in range (len(namelist)):
		for j in range(0,len(namelist)-i-1):
			if(namelist[j]>namelist[j+1]):
				namelist[j],namelist[j+1]=namelist[j+1],namelist[j]
				filelist[j],filelist[j+1]=filelist[j+1],filelist[j]
	return filelist,namelist
	
#######################################
########### Main Method ###############
#######################################

arguments = parseArg()
curPath=os.getcwd()

if(arguments.zip):
	os.system("mkdir ZIP")

dirlist = deque(handleDir())
filetemp,nametemp,totalFileVisited,totalFileListed,totalSizeVisited,totalSizeListed = dirTraverse()

filelist,namelist= sortedList(filetemp,nametemp)
check=True
uniqueSize=0
uniqueNum=0

#If zip argument is given, zips the files.
if(arguments.zip):
	zipper()

#If duplname argument is given, prints the files by comparing them with their names.
if arguments.duplname:
	check=False
	test=[False]*len(namelist)
	for i in range (0,len(namelist)):
		if(not test[i]):
			test[i]=True
			if(not arguments.nofilelist):
				print("-----")
				print(filelist[i])
			for j in range(i+1,len(namelist)):
				if(not test[j]):
					if(namelist[i]==namelist[j]):
						test[j]=True
						if(not arguments.nofilelist):
							print(filelist[j])
						uniqueSize=uniqueSize - fSize(filelist[j])
						uniqueNum=uniqueNum-1
	
	if(not arguments.nofilelist):
		print("-----")
		
#If duplcont argument is given, prints the files by comparing them with their contents.
if (check and arguments.duplcont):
	cont=[False]*len(namelist)
	for i in range (0,len(namelist)):
		if(not cont[i]):
			cont[i]=True
			if(not arguments.nofilelist):
				print("-----")
				print(filelist[i])
			for j in range(i+1,len(namelist)):
				if(not cont[j]):
					if(filecmp.cmp(filelist[i],filelist[j],shallow=False)):
						cont[j]=True
						if(not arguments.nofilelist):
							print(filelist[j])
						uniqueSize=uniqueSize - fSize(filelist[j])
						uniqueNum=uniqueNum-1
	if(not arguments.nofilelist):
		print("-----")

#If delete argument is given, deletes the given files.
if arguments.delete:
	for paths in filelist:
		delete(paths)

#Prints the files' paths.
if not arguments.nofilelist and not(arguments.duplcont or arguments.duplname):
	for paths in filelist:
		print(paths)

#If stats argument is given, prints the statistics of program.
if arguments.stats:
	print("Total Number of File Visited: " + str(totalFileVisited))
	print("Total Size of File Visited in bytes: " + str(totalSizeVisited))
	print("Total Number of File Listed: " + str(totalFileListed))
	print("Total Size of Size Listed in bytes: " + str(totalSizeListed))

	totalSizeListed=totalSizeListed+uniqueSize
	totalFileListed=totalFileListed+uniqueNum

	if(arguments.duplcont or arguments.duplname):
		print("Total Number of Unique Files Listed: " + str(totalFileListed))
		print("Total Size of Unique File Listed in bytes: " + str(totalSizeListed))

if(arguments.zip):
	os.system("rm -r ZIP")

