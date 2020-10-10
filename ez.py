#so basically multithread http load tester
#syntaxbender
import logging
import threading
import time
from io import BytesIO
import pycurl
import re
totalloginresptime=0;
totalsetentryresptime=0;
threadcount=200
repeatcountperthread=20
def curl(url,header,postdata,timeout,sessid="",proxy="",proxyport="",proxyuserpass="",proxytype=""):
	databuffer = BytesIO()
	c1 = pycurl.Curl()
	c1.setopt(c1.URL, url)
	c1.setopt(c1.USERAGENT, "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36")
	if(postdata):
		c1.setopt(c1.POST, 1)
		c1.setopt(c1.POSTFIELDS, postdata)
	if(sessid):
		c1.setopt(c1.COOKIE, "PHPSESSID="+sessid)
	#c1.setopt(c1.PROXY, proxy)
	#c1.setopt(c1.PROXYPORT, int(proxyport))
	#c1.setopt(c1.USE_SSL, True)
	#c1.setopt(c1.SSL_VERIFYPEER, False)
	c1.setopt(c1.HEADER, header)
	#c1.setopt(c1.PROXYUSERPWD, proxyuserpass)
	#c1.setopt(c1.PROXYTYPE, proxytype)
	c1.setopt(c1.IPRESOLVE, c1.IPRESOLVE_V4)
	c1.setopt(c1.WRITEDATA, databuffer)
	c1.setopt(c1.TIMEOUT_MS, timeout)
	c1.setopt(c1.NOSIGNAL, 1)
	try:
		t1 = time.time()
		c1.perform()
		status_code = c1.getinfo(c1.HTTP_CODE)
		c1.close()
		t2 = time.time()
		responsetime = t2-t1
		responsedata = databuffer.getvalue().decode('UTF-8')
		return [True,responsedata,status_code,responsetime]
	except Exception as e:
		return [False,e];
def login(email,password,tnum):
	logindata = curl("http://domain.com/login",True,"email="+email+"&password="+password,3000)
	if not logindata[0]:
		f = open("reports.txt", "a")
		f.write("loginmobile - "+str(logindata[1])+"#######################################################################\n\n\n")
		f.close()
		logging.info("Thread login error:	 %d.", tnum)
		return False
	if logindata[2] != 200 or "true" not in logindata[1]:
		f = open("reports.txt", "a")
		f.write("loginmobile - "+str(logindata[2])+" - "+logindata[1]+"#######################################################################\n\n\n")
		f.close()
		logging.info("Thread login error:	 %d.", tnum)
		return False
	else:
		sessid = re.findall('Set-Cookie: PHPSESSID=(.+?);', logindata[1])
		return sessid[0]
def sentry(param1,param2,param3,lang,token,tnum):
	setentrydata = curl("http://domain.com/endpoint",True,"param1="+param1+"&param2="+param2+"&param3="+param3+"lang="+lang+"&token="+token,3000)
	if not setentrydata[0]:
		f = open("reports.txt", "a")
		f.write("setentrymobile - "+str(setentrydata[1])+"#######################################################################\n\n\n")
		f.close()
		logging.info("Thread setentry error:	 %d.", tnum)
		return False
	if setentrydata[2] != 200 or "true" not in setentrydata[1]:
		f = open("reports.txt", "a")
		f.write("setentrymobile - "+str(setentrydata[2])+" - "+setentrydata[1]+"#######################################################################\n\n\n")
		f.close()
		logging.info("Thread setentry error:	 %d.", tnum)
		return False
	else:
		logging.info("Thread done:	 %d.", tnum)
		return True
def curlprocess(tnum):
	for x in range(repeatcountperthread):
		islogged = login("syntaxbender@syntaxbender.com","123456xd",tnum)
		if islogged:
			sentry('param1','param2','param3','tr',islogged,tnum)
if __name__ == "__main__":
	logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")
	threads = list()
	for index in range(threadcount):
		logging.info("Main    : create and start thread %d.", index)
		x = threading.Thread(target=curlprocess, args=(index,))
		threads.append(x)
		x.start()

	for index, thread in enumerate(threads):
		logging.info("Main    : before joining thread %d.", index)
		thread.join()
		logging.info("Main    : thread %d done", index)