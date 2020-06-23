import pdb, re
from command import Command

class DbOperator(object):  
    def install(self, cmd):        
        cmdObj = Command()
        self.output = cmdObj.run(cmd)
        print(self.output)
        #if re.search(r'.*redhat-developer-operators\s(unchanged|created)', self.output) and re.search(r'.*service-binding-operator\s(unchanged|created)', self.output):
    	#    return True