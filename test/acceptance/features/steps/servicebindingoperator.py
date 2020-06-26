import re
import util
from command import Command


class Servicebindingoperator(object):
    def __init__(self):
        self.cmdObj = Command()
        self.operatorsNS = "openshift-operators"
        self.operatorName = "service-binding-operator"

    def install_master(self):
        # src_result = create_operator_source("redhat-developer-operators", "redhat-developer")
        cmd = 'make install-service-binding-master'
        install_output = self.cmdObj.run(cmd)
        if re.search(r'.*redhat-developer-operators\s(unchanged|created)', install_output) \
                and re.search(r'.*service-binding-operator\s(unchanged|created)', install_output):
            return True

    def get_install_plan_status_sbo(self):
        return util.get_install_plan_status(self.operatorName, self.operatorsNS)

    def get_sbo_pod_status(self):
        return util.get_pod_status(self.operatorName, self.operatorsNS)
