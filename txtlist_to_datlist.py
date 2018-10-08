import re
import os
import csv


## converter for ip blocklsists
# reads all files in tmp/, concats them together, and then sorts their contents by format and converts

# CLEAR TMP FILES AND PAST RESULTS
tmpfolder="tmp/"
tmps=["full.txt","full.dat","full_sorted.txt","full_sorted.dat"]
for tmpfile in tmps:
    if os.path.exists(tmpfolder+tmpfile):
        os.remove(tmpfolder+tmpfile)
tmps=["final_sorted.txt","final_sorted.dat"]
for tmpfile in tmps:
    if os.path.exists(tmpfile):
        os.remove(tmpfile)


# SEARCH ALL FILES, CONCATING CONTENTS BASED ON FORMAT TYPE
wfile1 = open(tmpfolder+"full.txt","a")
wfile2 = open(tmpfolder+"full.dat","a")

filelist = os.listdir("lists")
for filename in filelist:
    rfile1 = open("lists/"+filename,"r")
    for line in rfile1:
        rline = line.rstrip("\n\r")
        if re.match("^\w.+\s*\:\s*\d+\.\d+\.\d+\.\d+\s*\-\s*\d+\.\d+\.\d+\.\d+\s*$",rline):
            wfile1.write(rline+"\n")
        elif re.match("^\d{3}\.\d{3}\.\d{3}\.\d{3}\s+\-\s+\d{3}\.\d{3}\.\d{3}\.\d{3}\s+,\s+\d{3}\s+,\s+.*$",rline):
            wfile2.write(rline+"\n")
    rfile1.close()
wfile1.close()
wfile2.close()


# SORT AND UNIQUIFY CONCATED FILES
ftypes = ["dat","txt"]
for ftype in ftypes:
    if os.path.exists(tmpfolder+"full."+ftype):
    	wfile = open(tmpfolder+'full_sorted.'+ftype, 'w')
        rfile = open(tmpfolder+"full."+ftype, "r")
        lines = set(rfile.readlines())
        for line in lines:
    		wfile.write(line+'\n')
    	wfile.close()
        rfile.close()


# CONVERT GENERAL .TXT CONCATED FILE TO .DAT
if os.path.exists(tmpfolder+"full_sorted.txt"):
    wfile = open(tmpfolder+"full_sorted.dat","a")
    rfile = open(tmpfolder+"full_sorted.txt","r")
    for line in rfile:
        rline = line.rstrip("\n\r")
        if re.match("^\w.+\s*\:\s*\d+\.\d+\.\d+\.\d+\s*\-\s*\d+\.\d+\.\d+\.\d+\s*$",rline):

            m0 = re.match("^(\w.+)\s*\:\s*\d+\.\d+\.\d+\.\d+\s*\-\s*\d+\.\d+\.\d+\.\d+\s*$",rline)
            m1 = re.match("^\w.+\s*\:\s*(\d+\.\d+\.\d+\.\d+)\s*\-\s*\d+\.\d+\.\d+\.\d+\s*$",rline)
            m2 = re.match("^\w.+\s*\:\s*\d+\.\d+\.\d+\.\d+\s*\-\s*(\d+\.\d+\.\d+\.\d+)\s*$",rline)
            outtext = ""

            if m0 and m1 and m2:
                name = m0.group(1)
                name = name.replace(",","")

                ip1 = m1.group(1)
                ip2 = m2.group(1)

                a=0
                for ip in [ip1,ip2]:
                    isplit = ip.split(".")
                    c=0
                    for i in isplit:
                        while len(i) < 3:
                            i="0"+i
                        isplit[c]=i
                        c+=1
                    ip = ".".join(isplit)
                    outtext = outtext + ip
                    if a == 0:
                        outtext = outtext + " - "
                    elif a == 1:
                        outtext = outtext + " , 000 , "
                    a+=1
                outtext = outtext + name

                wfile.write(outtext+"\n")
    wfile.close()
    rfile.close()



# FINAL SORT/UNIQUIFY
ftypes = ["dat","txt"]
for ftype in ftypes:
    if os.path.exists(tmpfolder+"full_sorted."+ftype):
    	wfile = open('final_sorted.'+ftype, 'w')
        rfile = open(tmpfolder+"full_sorted."+ftype, "r")
        lines = set(rfile.readlines())
        for line in lines:
    		wfile.write(line+'\n')
    	wfile.close()
        rfile.close()
