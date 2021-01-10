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
        cloud_config= {'secure_connect_bundle': objControl.rutaLocal+'secure-connect-dbtest.zip'}


    auth_provider = PlainTextAuthProvider(objCC.cc_user_test,objCC.cc_pwd_test)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider) 

    return cluster  
              
def insertJSON(json_file):
     
    cluster=getCluster()
    session = cluster.connect()
    session.default_timeout=timeOut
    #Insert Data as JSON
    jsonS=json.dumps(json_file)           
    insertSt="INSERT INTO "+keyspace+".tbcourtdecisioncjf_byfolder JSON '"+jsonS+"';" 
    future = session.execute_async(insertSt)
    future.result()  
    cluster.shutdown()     
                    
                         
    return True

def executeNonQuery(query):

    cluster=getCluster()
    session = cluster.connect()
    session.default_timeout=timeOut         
    future = session.execute_async(query)
    future.result()
                         
    return True

def executeQuery(query):

    cluster=getCluster()
    session = cluster.connect()
    session.default_timeout=timeOut      
    future = session.execute_async(query)
    resultSet=future.result()
    cluster.shutdown()
                                         
    return resultSet


   

   
class CassandraConnection():
    cc_user='quartadmin'
    cc_keyspace='thesis'
    cc_pwd='P@ssw0rd33'
    cc_user_test='test'
    cc_pwd_test='testquart'
        

