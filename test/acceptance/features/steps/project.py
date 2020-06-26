import re
from pyshould import should_not

from command import Command


class Project():
    def __init__(self, name):
        self.name = name
        self.cmdObj = Command()

    def create(self):
        cmd = "make create-project"
        create_pjt_output = self.cmdObj.run(cmd)
        if re.search(r'.*project.project.openshift.io\s\"%s\"\salready exists' % self.name, create_pjt_output):
            return self.setProject(self.name)
        elif re.search(r'.*Already\son\sproject\s\"%s\"\son\sserver.*' % self.name, create_pjt_output):
            return True
        else:
            print("Returned a different value {}".format(create_pjt_output))
            return False

    def is_present(self):
        cmd = 'oc get project %s"' % (self.name)
        output, exit_code = self.cmdObj.run(cmd)
        return exit_code == 0

    def get_project_status(self):
        cmd = 'oc get project %s -o "jsonpath={.status.phase}"' % (self.name)
        project_status = self.cmdObj.run_check_for_status(cmd, status="Active")
        project_status | should_not.be_equal_to(None)
        return project_status

    def switch_to(self, name):
        cmd = 'oc project %s' % (self.name)
        project_result = self.cmdObj.run(cmd)
        project_result | should_not.be_equal_to(None)
        if re.search(r'Already on project\s\"%s\"\son\sserver.*' % self.name, project_result):
            return True
