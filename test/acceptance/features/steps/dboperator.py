import pdb, re, util
from pyshould import *

from command import Command
from servicebindingoperator import Servicebindingoperator

class DbOperator(Servicebindingoperator):  
    def __init__(self):
        Servicebindingoperator.__init__(self)
        self.cmdObj = Command()
        self.pkgManifest = "db-operators"       
        self.backSvcName = "postgresql-operator" 

    def install_src(self, cmd):       
        install_src_output = self.cmdObj.run(cmd)
        if re.search(r'.*operatorsource.operators.coreos.com/db-operators\s(unchanged|created)', install_src_output):
    	    return True

    def install_sub(self, cmd):
        install_sub_output = self.cmdObj.run(cmd)
        if re.search(r'.*subscription.operators.coreos.com/db-operators\s(unchanged|created)', install_sub_output):
            return True
        
    def get_package_manifest(self):
        cmd = 'oc get packagemanifest %s -o "jsonpath={.metadata.name}"'%self.pkgManifest
        manifest = self.cmdObj.run_check_for_status(cmd, status=self.pkgManifest)      
        manifest | should_not.be_equal_to(None)
        manifest | should.equal(self.pkgManifest)
        return manifest
    
    def get_install_plan_status_dbOpr(self):
        return util.get_install_plan_status(self.pkgManifest, self.operatorsNS)

    def get_db_operator_pod_status(self):
        return util.get_pod_status(self.backSvcName, self.operatorsNS)

    def create_db_instance(self, db_name):
        cmd = 'make create-backing-db-instance'
        create_db_instance_output = self.cmdObj.run(cmd)        
        if re.search(r'.*database.postgresql.baiju.dev/%s\s(created|unchanged)'%db_name, create_db_instance_output):
    	    return True
    
    def get_db_instance_name(self, project):
        cmd = 'oc get db -n %s -o "jsonpath={.items[*].metadata.name}"'%project
        self.db_instance = self.cmdObj.run(cmd)      
        self.db_instance | should_not.be_equal_to(None)
        return self.db_instance
    
    def get_connection_ip(self):
        cmd = 'oc get db %s -o "jsonpath={.status.dbConnectionIP}"'%self.db_instance
        self.connection_ip = self.cmdObj.run(cmd) 
        self.connection_ip | should_not.be_equal_to(None)
        if re.match(r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}',self.connection_ip):
            return True
        else:
            return False

    def get_db_instance_pod_status(self, db_name, project):
        return util.get_pod_status(db_name, project)

    def check_db_instance_status(self, db_name, project):
        db_instance_name = self.get_db_instance_name(project)
        connection_ip = self.get_connection_ip()
        db_instance_pod_status = self.get_db_instance_pod_status(db_name, project)
        if (db_instance_name == db_name) and (connection_ip == True) and (db_instance_pod_status == "Running"):
            return True, db_instance_name, connection_ip, db_instance_pod_status 
        else:
            return False, None, None, None
        