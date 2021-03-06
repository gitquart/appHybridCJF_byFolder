from selenium.webdriver.common.by import By
from InternalControl import cInternalControl
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
from selenium import webdriver
from textwrap import wrap
import cassandraSent as bd
import PyPDF2
import uuid
import base64
import time
import json
import os
import sys


objControl=cInternalControl()

def returnChromeSettings():
    browser=''
    chromedriver_autoinstaller.install()
    if objControl.heroku:
        #Chrome configuration for heroku
        chrome_options= webdriver.ChromeOptions()
        chrome_options.binary_location=os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")

        browser=webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),chrome_options=chrome_options)

    else:
        options = Options()
        profile = {"plugins.plugins_list": [{"enabled": True, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
               "download.default_directory": objControl.download_dir , 
               "download.prompt_for_download": False,
               "download.directory_upgrade": True,
               "download.extensions_to_open": "applications/pdf",
               "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
               }           

        options.add_experimental_option("prefs", profile)
        browser=webdriver.Chrome(options=options)  

    

    return browser 


def appendInfoToFile(path,filename,strcontent):
    txtFile=open(path+filename,'a+')
    txtFile.write(strcontent)
    txtFile.close()

def processRow(browser):

    if objControl.heroku:        
        json_doc=devuelveJSON('/app/'+objControl.hfolder+'/json_documento.json')
    else:
        json_doc=devuelveJSON(objControl.rutaLocal+'/json_documento.json')

    neun=devuelveElemento('//*[@id="lblNEUN"]',browser)
    
    #Section A
    lsPanelVista=ReadSectioAndGetList('//*[@id="pnlVista"]',browser)
    for line in lsPanelVista:
        json_doc['sectionA'].append(line)
        
    #Section B    
    lsOtros=ReadSectioAndGetList('//*[@id="panelOtros"]',browser)
    for line in lsOtros:
        json_doc['sectionB'].append(line)
          
    #Section C
    lsReporte=ReadSectioAndGetList('//*[@id="pnlReporteSentencias"]',browser)
    for line in lsReporte:
        json_doc['sectionC'].append(line) 

    #JSON Acuerdos
    lsAcuerdos=[]  
    tablaAcuerdos=devuelveListaElementos('//*[@id="grvAcuerdos"]/tbody/tr',browser)
    intFilas=len(tablaAcuerdos)
    if intFilas>0:
        for row in range(2,intFilas+1):
            json_acuerdo=devuelveJSON(objControl.rutaLocal+'json_acuerdo.json')
            for col in range(2,6):
                if col==2:
                    valor=devuelveElemento('//*[@id="grvAcuerdos"]/tbody/tr['+str(row)+']/td['+str(col)+']',browser)
                    json_acuerdo['fecha_auto']=str(valor.text).replace("'",' ')
                if col==3:
                    valor=devuelveElemento('//*[@id="grvAcuerdos"]/tbody/tr['+str(row)+']/td['+str(col)+']',browser)
                    json_acuerdo['tipo_cuaderno']=str(valor.text).replace("'",' ')
                if col==4:
                    valor=devuelveElemento('//*[@id="grvAcuerdos"]/tbody/tr['+str(row)+']/td['+str(col)+']',browser)
                    json_acuerdo['fecha_pub']=str(valor.text).replace("'",' ')
                if col==5:
                    valor=devuelveElemento('//*[@id="grvAcuerdos"]/tbody/tr['+str(row)+']/td['+str(col)+']',browser)
                    json_acuerdo['summary']=str(valor.text).replace("'",' ')  
            lsAcuerdos.append(json_acuerdo)   
        jsonReady=json.dumps(lsAcuerdos)                     


    
    #Build the json by row   
    json_doc['id']=str(uuid.uuid4())
    json_doc['neun']=neun.text
    json_doc['jsonAcuerdos']=jsonReady
    query="select id from test.tbcourtdecisioncjf_byfolder where neun='"+str(json_doc['neun'])+"' ALLOW FILTERING "
    resultSet=bd.executeQuery(query)
    if resultSet:
        pass
    else:
        res=bd.insertJSON(json_doc)
        if res:
            return True
        else:
            return False




def ReadSectioAndGetList(xPath,browser):
    pnl=devuelveElemento(xPath,browser)
    ls=str(pnl.text).replace("'",' ').splitlines()

    return ls



                    

"""
readPDF is done to read a PDF no matter the content, can be image or UTF-8 text
"""
def readPDF(file):  
    with open(download_dir+'\\'+file, "rb") as pdf_file:
        bContent = base64.b64encode(pdf_file.read()).decode('utf-8')
    
    return bContent  
    

"""
This is the method to call when fetching the pdf enconded from cassandra which is a list of text
but that text is really bytes.
"""
def decodeFromBase64toNormalTxt(b64content):
    normarlText=base64.b64decode(b64content).decode('utf-8')
    return normarlText


def getPDFfromBase64(bContent):
    #Tutorial : https://base64.guru/developers/python/examples/decode-pdf
    bytes = base64.b64decode(bContent, validate=True)
    # Write the PDF contents to a local file
    f = open(download_dir+'\\result.pdf', 'wb')
    f.write(bytes)
    f.close()
    return "PDF delivered!"

def TextOrImageFromBase64(bContent):
    #If sData got "EOF" is an image, otherwise is TEXT
    sData=str(bContent)
    if "EOF" in sData:
        res=getPDFfromBase64(bContent) 
    else:
        res=decodeFromBase64toNormalTxt(bContent)

    return res 

def devuelveJSON(jsonFile):
    with open(jsonFile) as json_file:
        jsonObj = json.load(json_file)
    
    return jsonObj 

def processPDF(json_sentencia,lsRes):
    lsContent=[]  
    for file in os.listdir(download_dir): 
        strFile=file.split('.')[1]
        if strFile=='PDF' or strFile=='pdf':
            strContent=readPDF(file) 
            print('Start wrapping text...') 
            lsContent=wrap(strContent,1000)  
            json_documento=devuelveJSON('json_documento.json')
            if lsRes[0]:
                json_documento['idDocumento']=json_sentencia['id']
            else:
                json_documento['idDocumento']=lsRes[1]

            json_documento['documento']=json_sentencia['filenumber']
            json_documento['fuente']='cjf'
            totalElements=len(lsContent)
            result=insertPDFChunks(0,0,0,totalElements,lsContent,json_documento,0)
            if result==False:
                print('PDF Ended!')       
           
        
def insertPDFChunks(startPos,contador,secuencia,totalElements,lsContent,json_documento,done):
    if done==0:
        json_documento['lspdfcontent'].clear()
        json_documento['id']=str(uuid.uuid4())
        for i in range(startPos,totalElements):
            if i!=totalElements-1:
                if contador<=20:
                    json_documento['lspdfcontent'].append(lsContent[i])
                    contador=contador+1
                else:
                    currentSeq=secuencia+1
                    json_documento['secuencia']=currentSeq
                    res=bd.insertPDF(json_documento) 
                    if res:
                        print('Chunk of pdf added:',str(i),'from ',str(totalElements),' sequence:',str(currentSeq))  
                    else:
                        print('Chunk of pdf already existed:',str(i),'from ',str(totalElements),' sequence:',str(currentSeq)) 

                    return insertPDFChunks(i,0,currentSeq,totalElements,lsContent,json_documento,0) 
            else:
                json_documento['lspdfcontent'].append(lsContent[i])
                currentSeq=secuencia+1
                json_documento['secuencia']=currentSeq
                res=bd.insertPDF(json_documento) 
                if res:
                    print('Last Chunk of pdf added:',str(i),'from ',str(totalElements),' sequence:',str(currentSeq))
                else:
                    print('Last Chunk of pdf already existed:',str(i),'from ',str(totalElements),' sequence:',str(currentSeq))

                return  insertPDFChunks(i,0,currentSeq,totalElements,lsContent,json_documento,1)
    else:
        return False            

                             


                

def readPyPDF(file):
    #This procedure produces a b'blabla' string, it has UTF-8
    #PDF files are stored as bytes. Therefore to read or write a PDF file you need to use rb or wb.
    lsContent=[]
    if objControl.heroku:
        pdfFileObj = open(objControl.download_dir+'/'+file, 'rb')
    else:   
        pdfFileObj = open(objControl.download_dir+'\\'+file, 'rb') 
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    pags=pdfReader.numPages
    for x in range(0,pags):
        pageObj = pdfReader.getPage(x)
        #UTF-8 is the right encodeing, I tried ascii and didn't work
        #1. bContent is the actual byte from pdf with utf-8, expected b'bla...'
        bcontent=base64.b64encode(pageObj.extractText().encode('utf-8'))
        lsContent.append(str(bcontent.decode('utf-8')))
                         
    pdfFileObj.close()    
    return lsContent  

def devuelveElemento(xPath, browser):
    cEle=0
    while (cEle==0):
        cEle=len(browser.find_elements_by_xpath(xPath))
        if cEle>0:
            ele=browser.find_elements_by_xpath(xPath)[0]

    return ele  

def devuelveListaElementos(xPath, browser):
    cEle=0
    while (cEle==0):
        cEle=len(browser.find_elements_by_xpath(xPath))
        if cEle>0:
            ele=browser.find_elements_by_xpath(xPath)

    return ele      

def checkDirAndCreate(folder):
    print('Checking if download folder exists...')
    folder=returnCorrectDownloadFolder(folder)
    isdir = os.path.isdir(folder)
    if isdir==False:
        print('Creating download folder...')
        os.mkdir(folder) 
    print('Download directory created...')    


def returnCorrectDownloadFolder(folder):
    if objControl.heroku:
        folder='/app/'+objControl.download_dir
    else:
        folder='C:\\'+objControl.download_dir

    return folder    
