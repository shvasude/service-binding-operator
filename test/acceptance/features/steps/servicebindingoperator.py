import pdb, re
from command import Command

class Servicebindingoperator(object):  
    def __init__(self):
        self.cmdObj = Command()
        self.operatorsNS  = "openshift-operators"
        self.operatorName = "service-binding-operator"

    def install(self, cmd):        
        install_output = self.cmdObj.run(cmd)
        if re.search(r'.*redhat-developer-operators\s(unchanged|created)', install_output) and re.search(r'.*service-binding-operator\s(unchanged|created)', install_output):
    	    return True
    
    @classmethod
    def get_install_plan_name(self):
        sbo_cls_instance = Servicebindingoperator()
        cmd_instance = Command()
        cmd = '''oc get subscription %s -n %s -o "jsonpath={.status.installplan.name}"'''%(sbo_cls_instance.operatorName, sbo_cls_instance.operatorsNS)        
        return cmd_instance.run(cmd)
        
    def get_install_plan_status(self):
        install_plan_name = self.get_install_plan_name()    
        pdb.set_trace()
        cmd = 'oc get ip -n %s %s -o "jsonpath={.status.phase}"'%(self.operatorsNS, install_plan_name)        
        install_plan_status = self.cmdObj.run_check_for_status(cmd, status="Complete")         
        print("install plan status is {}".format(install_plan_status))
        return install_plan_status

    @classmethod
    def get_pods_lst(self):
        cmd = 'oc get pods -n %s -o "jsonpath={.items[*].metadata.name}"'%self.operatorsNS
        return cmd_instance.run(cmd)

    @classmethod
    def get_pod_name_from_lst_of_pods(self):
        sbo_cls_instance = Servicebindingoperator()
        cmd_instance = Command()
        pods_lst = self.get_pods_lst()
        


    def get_sbo_pod_status(self):
        sbo_pod_name = self.get_pod_name_from_lst_of_pods()
