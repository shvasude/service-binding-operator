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
        install_output = self.cmdObj.run(cmd)
        if re.search(r'.*operatorsource.operators.coreos.com/db-operators\s(unchanged|created)', install_output):
    	    return True

    def install_sub(self, cmd):
        install_output = self.cmdObj.run(cmd)
        if re.search(r'.*subscription.operators.coreos.com/db-operators\s(unchanged|created)', install_output):
            return True
        
    def get_package_manifest(self):
        cmd = 'oc get packagemanifest %s -o "jsonpath={.metadata.name}"'%self.pkgManifest
        manifest = self.cmdObj.run_check_for_status(cmd, status=self.pkgManifest)      
        manifest | should_not.be_equal_to(None)
        manifest | should.equal(self.pkgManifest)
        return True
    
    def get_install_plan_status_dbOpr(self):
        return util.get_install_plan_status(self.pkgManifest, self.operatorsNS)

    def get_dbOpr_pod_status(self):
        return util.get_pod_status(self.backSvcName, self.operatorsNS)