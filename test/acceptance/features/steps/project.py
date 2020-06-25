import pdb, re, util
from pyshould import *

from command import Command

class Project():  
    def __init__(self):
        self.cmdObj = Command()
        
    def create(self, cmd, project):       
        create_pjt_output = self.cmdObj.run(cmd)
        if re.search(r'.*project.project.openshift.io\s\"%s\"\salready exists'%project, create_pjt_output):
            return self.setProject(project)
        elif re.search(r'.*Already\son\sproject\s\"%s\"\son\sserver.*'%project, create_pjt_output):
            return True
        else:
            print("Returned a different value {}".format(create_pjt_output))
            return False

    def get_project_from_cluster(self, project):
        cmd = 'oc get project %s -o "jsonpath={.metadata.name}"'%(project)
        project = self.cmdObj.run(cmd)      
        project | should_not.be_equal_to(None)
        return project

    def get_project_status(self, project):
        cmd = 'oc get project %s -o "jsonpath={.status.phase}"'%(project)
        project_status = self.cmdObj.run_check_for_status(cmd, status="Active")    
        project_status | should_not.be_equal_to(None)             
        return project_status

    def setProject(self, project):
        cmd = 'oc project %s'%(project)
        project_result = self.cmdObj.run(cmd)      
        project_result | should_not.be_equal_to(None)
        if re.search(r'Already on project\s\"%s\"\son\sserver.*'%project, project_result):
            return True

