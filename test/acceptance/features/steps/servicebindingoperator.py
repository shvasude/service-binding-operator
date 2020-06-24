import pdb, re 
from command import Command
from pyshould import *

class Servicebindingoperator(object):  
    def __init__(self):
        self.cmdObj = Command()
        self.operatorsNS  = "openshift-operators"
        self.operatorName = "service-binding-operator"

    def install(self, cmd):    
        install_output = self.cmdObj.run(cmd)
        if re.search(r'.*redhat-developer-operators\s(unchanged|created)', install_output) and re.search(r'.*service-binding-operator\s(unchanged|created)', install_output):
    	    return True
        
    def get_install_plan_name(self):
        cmd = '''oc get subscription %s -n %s -o "jsonpath={.status.installplan.name}"'''%(self.operatorName, self.operatorsNS)        
        return self.cmdObj.run(cmd)
        
    def get_install_plan_status(self):
        install_plan_name = self.get_install_plan_name()    
        print("install plan name is {}".format(install_plan_name))
        cmd = 'oc get ip -n %s %s -o "jsonpath={.status.phase}"'%(self.operatorsNS, install_plan_name)        
        install_plan_status = self.cmdObj.run_check_for_status(cmd, status="Complete")    
        install_plan_status | should_not.be_equal_to(None)             
        return install_plan_status

    def get_pods_lst(self):
        cmd = 'oc get pods -n %s -o "jsonpath={.items[*].metadata.name}"'%(self.operatorsNS)
        return self.cmdObj.run(cmd)

    def get_pod_name_from_lst_of_pods(self):
        pods_lst = self.get_pods_lst()
        print("Pod list are {}".format(pods_lst))
        podName = self.search_item_from_lst(pods_lst, self.operatorName)
        podName | should_not.be_equal_to(None)
        return podName        
        
    @classmethod
    def search_item_from_lst(cls, lst, srchItem):
        lst_arr = lst.split(" ")
        for item in lst_arr:
            if srchItem in item:
                if "-build" in srchItem:
                    print("item matched {}".format(item))
                    return item
                print("item matched {}".format(item))
                return item
        if item is None:
            print("item not matched as the value of item is {}".format(item))
            return

    def get_pod_status(self, podName):
        cmd = 'oc get pod %s -n %s -o "jsonpath={.status.phase}"'%(podName,self.operatorsNS)
        return self.cmdObj.run_check_for_status(cmd, status="Running")      
        
    def get_sbo_pod_status(self):
        pdb.set_trace()
        sbo_pod_name = self.get_pod_name_from_lst_of_pods()        
        sbo_pod_status = self.get_pod_status(sbo_pod_name)
        sbo_pod_status | should_not.be_equal_to(None)
        return sbo_pod_status
