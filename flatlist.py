import os, shutil

currdir = os.getcwd()
print "Starting move"
myfiles = []
for q in os.walk('.'):
    myfiles.append(q)
for q in myfiles:
    ## Ignore the current dir - find a better way
    if len(q[0]) < 2: continue
    for my_file in os.listdir(q[0]):
	print "Moving " + my_file
	source = os.path.join(currdir+q[0]+ os.sep+my_file)
	dest = currdir + os.sep + my_file
	shutil.move(source, dest)
    shutil.rmtree(currdir + q[0])

