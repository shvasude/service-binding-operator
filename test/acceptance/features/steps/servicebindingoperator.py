from openshift import Openshift


class Servicebindingoperator():
    openshift = Openshift()
    operator_name = ""
    operator_namespace = ""

    def __init__(self,  name="service-binding-operator", namespace="openshift-operators"):
        self.operator_namespace = namespace
        self.operator_name = name

    def is_running(self):
        pod_name = self.openshift.search_pod_in_namespace(self.operator_name, self.operator_namespace)
        if pod_name is not None:
            operator_pod_status = self.openshift.check_pod_status(pod_name, self.operator_namespace)
            print("The pod {} is running: {}".format(self.operator_name, operator_pod_status))
            return operator_pod_status
        else:
            return False
