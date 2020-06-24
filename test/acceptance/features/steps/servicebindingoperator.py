import pdb, re, util
from command import Command
from pyshould import *

class Servicebindingoperator(object):  
    def __init__(self):
        self.cmdObj = Command()
        self.operatorsNS  = "openshift-operators"
        self.operatorName = "service-binding-operator"

    def install(self, cmd):    
        install_output = self.cmdObj.run(cmd)
        if re.search(r'.*redhat-developer-operators\s(unchanged|created)', install_output) and re.search(r'.*service-binding-operator\s(unchanged|created)', install_output):
    	    return True
    
    def get_install_plan_status_sbo(self):
        return util.get_install_plan_status(self.operatorName, self.operatorsNS)

    def get_sbo_pod_status(self):
        return util.get_pod_status(self.operatorName, self.operatorsNS)