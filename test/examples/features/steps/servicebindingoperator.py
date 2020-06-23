import pdb, re
from command import Command

class Servicebindingoperator(object):  
    def __init__(self):
        #self.cmd = None
        self.cmdObj = Command()

    def install(self, cmd):        
        #cmdObj = Command()
        self.output = cmdObj.run(cmd)
        if re.search(r'.*redhat-developer-operators\s(unchanged|created)', self.output) and re.search(r'.*service-binding-operator\s(unchanged|created)', self.output):
    	    return True
    
    def get_install_plan_status(self, cmd):
