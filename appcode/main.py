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
#chromedriver_autoinstaller.install()
#browser=webdriver.Chrome(options=options)

#Since here both versions (heroku and desktop) are THE SAME
url="https://sise.cjf.gob.mx/consultasvp/default.aspx"
response= requests.get(url)
status= response.status_code
if status==200:  
    browser.get(url)
    try:
        WebDriverWait(browser, 5).until (EC.alert_is_present())
        #switch_to.alert for switching to alert and accept
        alert = browser.switch_to.alert
        alert.dismiss()
        browser.refresh()
    except TimeoutException:
        print('No alert found!')
        
    time.sleep(3)  
    #Read the information of query and page
    querySt="select query,page from test.cjf_control where id_control=4  ALLOW FILTERING"
    #1.Topic, 2. Page
    resultSet=bd.executeQuery(querySt)
    lsInfo=[]
        
    if resultSet: 
        for row in resultSet:
            lsInfo.append(str(row[0]))
            print('Cassandra: Star query ->ñ:',str(row[0]))
    folder=str(lsInfo[0])
    txtBuscar= tool.devuelveElemento('//*[@id="txtNumExp"]',browser)
    txtBuscar.send_keys(folder)
    btnBuscar=tool.devuelveElemento('//*[@id="btnBuscar_input"]',browser)
    btnBuscar.click()
    #WAit X secs until query is loaded.
    time.sleep(20)
    print('Start reading the page...')
    #Control the page
    #Page identention
    print('Currently with query:',str(folder))
    for row in range(0,20):
        tool.processRow(browser,strSearch,row)

    #Update the info in file
    infoPage=str(browser.find_element(By.XPATH,'//*[@id="grdSentencias_ctl00"]/tfoot/tr/td/table/tbody/tr/td/div[5]').text)
    data=infoPage.split(' ')
    currentPage=int(data[2])
    print('Page already done:...',str(currentPage))   
    print('------------------------END--------------------------------------------') 
    control_page=int(currentPage)+1
    startPage=control_page
    #Edit  control file
    bd.updatePage(control_page)
    #Change the page with next
    btnnext=browser.find_elements_by_xpath('//*[@id="grdSentencias_ctl00"]/tfoot/tr/td/table/tbody/tr/td/div[3]/input[1]')[0].click()
    btnBuscaTema=browser.find_elements_by_xpath('//*[@id="btnBuscarPorTema_input"]')[0].click()
    time.sleep(5)  
     
          

browser.quit()