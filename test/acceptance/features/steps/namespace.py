import re
from pyshould import should

from command import Command


class Namespace():
    def __init__(self, name):
        self.name = name
        self.cmd = Command()

    def create(self):
        create_ns_output, exit_code = self.cmd.run("oc new-project {}".format(self.name))
        if re.search(r'Now using project \"%s\"\son\sserver' % self.name, create_ns_output):
            return True
        elif re.search(r'.*project.project.openshift.io\s\"%s\"\salready exists' % self.name, create_ns_output):
            return self.switch_to(self.name)
        elif re.search(r'.*Already\son\sproject\s\"%s\"\son\sserver.*' % self.name, create_ns_output):
            return True
        else:
            print("Returned a different value {}".format(create_ns_output))
            return False

    def is_present(self):
        output, exit_code = self.cmd.run('oc get ns {}'.format(self.name))
        return exit_code == 0

    def get_status(self):
        self.is_present() | should.be_truthy
        return self.cmd.run('oc get ns {} -o "jsonpath={{.status.phase}}"'.format(self.name))

    def switch_to(self):
        output, exit_code = self.cmd.run('oc project {}'.format(self.name))
        exit_code | should.be_equal_to(0)
        return output
