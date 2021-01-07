import json
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement
from InternalControl import cInternalControl
import os

keyspace='test'
timeOut=100
objControl=cInternalControl()

def getCluster():
    #Connect to Cassandra
    objCC=CassandraConnection()
    cloud_config=''
    if objControl.heroku:
        cloud_config= {'secure_connect_bundle': objControl.rutaHeroku+'/secure-connect-dbtest.zip'}
    else:
        cloud_config= {'secure_connect_bundle': 'appHybridCJF_byFolder\\appcode\\secure-connect-dbtest.zip'}


    auth_provider = PlainTextAuthProvider(objCC.cc_user_test,objCC.cc_pwd_test)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider) 

    return cluster  
              
def cassandraBDProcess(json_sentencia):
     
    sent_added=False
    cluster=getCluster()
    session = cluster.connect()
    session.default_timeout=timeOut
    row=''
    fileNumber=json_sentencia['filenumber']
    #Check wheter or not the record exists, check by numberFile and date
    #Date in cassandra 2020-09-10T00:00:00.000+0000
    querySt="select id from "+keyspace+".tbcourtdecisioncjf where filenumber='"+str(fileNumber)+"'  ALLOW FILTERING"            
    future = session.execute_async(querySt)
    row=future.result()
    lsRes=[]
        
    if row: 
        sent_added=False
        valid=''
        for val in row:
            valid=str(val[0])
        lsRes.append(sent_added) 
        lsRes.append(valid)   
        cluster.shutdown()
    else:        
        #Insert Data as JSON
        jsonS=json.dumps(json_sentencia)           
        insertSt="INSERT INTO "+keyspace+".tbcourtdecisioncjf JSON '"+jsonS+"';" 
        future = session.execute_async(insertSt)
        future.result()  
        sent_added=True
        lsRes.append(sent_added)
        cluster.shutdown()     
                    
                         
    return lsRes

def updatePage(page):

    cluster=getCluster()
    session = cluster.connect()
    session.default_timeout=timeOut
    page=str(page)
    querySt="update "+keyspace+".cjf_control set page="+page+" where  id_control=1;"          
    future = session.execute_async(querySt)
    future.result()
                         
    return True

def executeQuery(query):

    cluster=getCluster()
    session = cluster.connect()
    session.default_timeout=timeOut
    #select page from  thesis.cjf_control where id_control=1 and query='Primer circuito'       
    future = session.execute_async(query)
    resultSet=future.result()
    cluster.shutdown()
                                         
    return resultSet


def insertPDF(json_doc):
     
    record_added=False
    cluster=getCluster()
    session = cluster.connect()
    session.default_timeout=timeOut
    iddocumento=str(json_doc['idDocumento'])
    documento=str(json_doc['documento'])
    fuente=str(json_doc['fuente'])
    secuencia=str(json_doc['secuencia'])
    querySt="select id from "+keyspace+".tbDocumento_cjf where iddocumento="+iddocumento+" and documento='"+documento+"' and fuente='"+fuente+"' AND secuencia="+secuencia+"  ALLOW FILTERING"          
    future = session.execute_async(querySt)
    row=future.result()

    if row:
        cluster.shutdown()
    else:    
        jsonS=json.dumps(json_doc)           
        insertSt="INSERT INTO "+keyspace+".tbDocumento_cjf JSON '"+jsonS+"';" 
        future = session.execute_async(insertSt)
        future.result()  
        record_added=True
        cluster.shutdown()     
                    
                         
    return record_added     

   
class CassandraConnection():
    cc_user='quartadmin'
    cc_keyspace='thesis'
    cc_pwd='P@ssw0rd33'
    cc_user_test='test'
    cc_pwd_test='testquart'
        

