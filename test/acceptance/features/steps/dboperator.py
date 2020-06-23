import pdb, re
from command import Command

class DbOperator(object):  
    def install(self, cmd):        
        cmdObj = Command()
        self.output = cmdObj.run(cmd)
        print(self.output)