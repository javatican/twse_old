from bs4 import BeautifulSoup
import datetime
import requests
import time

message_list=[]
access_error=False
response_slow=False
ACCESS_LAG_THRESHOLD=10
with open("/tmp/smartweb_status.log", "a") as fd:
    message_list.append('*** Access time: %s' % datetime.datetime.now())
    start_time = time.time()
    try:        
        serviceUrl = 'https://www.smartweb.tw/'
        # print serviceUrl
        httpResponse = requests.get(serviceUrl)
        httpResponse.encoding = "utf-8"
    except requests.RequestException, e:
        result = e.read()
        message_list.append("home page request exception message: %s" % result)  
        access_error=True
    except requests.ConnectionError, e:
        result = e.read()
        message_list.append("home page request connection error message: %s" % result)  
        access_error=True
    except requests.HTTPError, e:
        result = e.read()
        message_list.append("home page request http error message: %s" % result)    
        access_error=True
    end_time= time.time()
#
    soup = BeautifulSoup(httpResponse.text, 'lxml')              
    if soup:
        banner_div = soup.find('div', id='banner')
        if banner_div:
            page_load_time = round(end_time - start_time, 4)
            message_list.append("home page loading ok!")
            message_list.append("home page load time : %s sec" % page_load_time )
            if page_load_time>=ACCESS_LAG_THRESHOLD:
                message_list.append("!!!page loading sluggish!!!")
                response_slow=True
        else:
            message_list.append("home page loading error!")
            access_error=True
    else:
        message_list.append("home page loading error!")
        access_error=True
    #write to log file
    if access_error:
        message_list.insert(0,'WARNING: Smartweb access error!')
    elif response_slow:
        message_list.insert(0,'WARNING: Smartweb slow response!')
    fd.write('\n'.join(message_list))
    fd.write('\n')

if access_error or response_slow:
    # Import smtplib for the actual sending function
    import smtplib
    
    # Import the email modules we'll need
    from email.mime.text import MIMEText
    
    # Create a text/plain message
    msg = MIMEText("\n".join(message_list))
    
    me = "efmp.migulu@gmail.com"
    me_passwd="27328703ef"
    
    smtpserver = smtplib.SMTP("smtp.gmail.com",587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(me, me_passwd)
    you =['ryan@migulu.com','allan@migulu.com', 'james@migulu.com']
    msg['Subject'] = message_list[0]
    msg['From'] = me
    msg['To'] = ','.join(you)
    smtpserver.sendmail(me, you, msg.as_string())
    smtpserver.quit()