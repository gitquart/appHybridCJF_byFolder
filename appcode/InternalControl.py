import os

class cInternalControl:
    idControl=9
    timeout=70
    hfolder='appcode' 
    heroku=False
    rutaHeroku='/app/'+hfolder
    rutaLocal=os.getcwd()+'\\'+hfolder+'\\'
    download_dir=''/app/Download''
      