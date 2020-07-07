import re

from command import Command
from openshift import Openshift


class ServerlessOperator():

    openshift = Openshift()
    cmd = Command()

    pod_name_pattern = "{name}.*"

    name = ""
    namespace = ""
    operator_source_name = "redhat-operators"
    operator_registry_channel = "techpreview"

    def __init__(self, name="serverless-operator", namespace="openshift-operators"):
        self.name = name
        self.namespace = namespace

    def is_running(self, name, namespace, wait=False):
        if wait:
            pod_name = self.openshift.wait_for_pod(self.pod_name_pattern.format(name=self.name), self.namespace)
        else:
            pod_name = self.openshift.search_pod_in_namespace(self.pod_name_pattern.format(name=self.name), self.namespace)
        if pod_name is not None:
            operator_pod_status = self.openshift.check_pod_status(pod_name, self.namespace)
            print("The pod {} is running: {}".format(self.name, operator_pod_status))
            return operator_pod_status
        else:
            return False

    def install_operator_subscription(self):
        install_sub_output = self.openshift.create_operator_subscription(self.name, self.operator_source_name, self.operator_registry_channel)
        return re.search(r'.*subscription.operators.coreos.com/%s\s(unchanged|created)' % self.operator_source_name, install_sub_output)
