from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert 
from selenium import webdriver
import utils as tool
import chromedriver_autoinstaller
import json
import textract
import time
import os
import requests 
import sys
import PyPDF2
import uuid
import cassandraSent as bd
import base64
from InternalControl import cInternalControl

pathToHere=os.getcwd()
print('Current path:',pathToHere)
objControl=cInternalControl()

#Erase every file in download folder at the beginning to avoid mixed files
tool.checkDirAndCreate(objControl.download_dir)
print('Download directory created...')
folder=tool.returnCorrectDownloadFolder(objControl.download_dir)
for file in os.listdir(folder):
    if objControl.heroku:
        os.remove(folder+'/'+file)
    else:
        os.remove(folder+'\\'+file)


print('Download folder empty...')
browser=tool.returnChromeSettings()
querySt="select query from test.cjf_control where id_control=4  ALLOW FILTERING"
#1.Topic, 2. Page
resultSet=bd.executeQuery(querySt)
lsInfo=[] 
if resultSet: 
    for row in resultSet:
        lsInfo.append(str(row[0]))
        print('Cassandra: Star query ->',str(row[0]))
folder=str(lsInfo[0])
chunk=folder.split('/')
num=int(chunk[0])
year=chunk[1]
for x in range(num,2000):
    url=" https://www.dgepj.cjf.gob.mx/siseinternet/Reportes/VerCaptura.aspx?tipoasunto=1&organismo=10&expediente="+str(2000)+"/"+year+"&tipoprocedimiento=0"
    response= requests.get(url)
    status= response.status_code
    if status==200:  
        browser.get(url)        
        #WAit X secs until query is loaded.
        time.sleep(5)
        bAlert=False
        try:
            WebDriverWait(browser, 5).until (EC.alert_is_present())
            alert = browser.switch_to.alert
            alert.dismiss()
            print('No folder found, updating number of sequential NO FOUND cases')
            bAlert=True
        except TimeoutException:
            print('No alert found!') 

        if not bAlert:       
            print('Start reading the page...')
            print('Currently with query:',str(folder))
            tool.processRow(browser)
            print('Restarting sequential NO FOUND counter to Zero')
            query="update test.cjf_control set page=0 where  id_control=4;" 
            bd.executeNonQuery(query)
        else:
            query="select page from test.cjf_control where id_control=4  ALLOW FILTERING"
            resultSet=bd.executeQuery(query)
            if resultSet:
                for row in resultSet:
                    countNoFound=int(str(row[0]))
                    countNoFound+=1
                    query="update test.cjf_control set page="+str(countNoFound)+" where  id_control=4;" 
                    bd.executeNonQuery(query)
                    if countNoFound>=20:
                        print('20 times NOT FOUND for year ',str(year)) 
                        year=int(year)
                        year+=1 
                        query="update test.cjf_control set page=0, query='1/"+str(year)+"' where  id_control=4;" 
                        bd.executeNonQuery(query)
                        print('Ready to restart with new query->1/',str(year))
                        os.sys.exit(0)  

     
          

browser.quit()