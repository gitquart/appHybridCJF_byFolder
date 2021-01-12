import os

class cInternalControl:
    timeout=70
    hfolder='appcodefolder' 
    heroku=False
    rutaHeroku='/app/'+hfolder
    rutaLocal=os.getcwd()+'\\'+hfolder+'\\'
    download_dir='Download_cjf_by_folder'
    enablePdf=False
      