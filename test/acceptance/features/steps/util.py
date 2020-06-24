from pyshould import *
from pyshould.expect import *
from command import Command

cmdObj = Command()

def get_install_plan_name(oprName,namespace):
    cmd = 'oc get subscription %s -n %s -o "jsonpath={.status.installplan.name}"'%(oprName, namespace)        
    return cmdObj.run(cmd)
        
def get_install_plan_status(oprName, namespace):
    install_plan_name = get_install_plan_name(oprName,namespace)    
    print("install plan name is {}".format(install_plan_name))
    cmd = 'oc get ip -n %s %s -o "jsonpath={.status.phase}"'%(namespace, install_plan_name)        
    install_plan_status = cmdObj.run_check_for_status(cmd, status="Complete")    
    install_plan_status | should_not.be_equal_to(None)             
    return install_plan_status

def get_pods_lst(namespace):
    cmd = 'oc get pods -n %s -o "jsonpath={.items[*].metadata.name}"'%(namespace)
    return cmdObj.run(cmd)

def get_pod_name_from_lst_of_pods(oprName, namespace):
    pods_lst = get_pods_lst(namespace)
    print("Pod list are {}".format(pods_lst))
    podName = search_item_from_lst(pods_lst, oprName)
    podName | should_not.be_equal_to(None)
    return podName        
    
def search_item_from_lst(lst, srchItem):
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

def get_pod_status(oprName, namespace):
    sbo_pod_name = get_pod_name_from_lst_of_pods(oprName, namespace)        
    cmd = 'oc get pod %s -n %s -o "jsonpath={.status.phase}"'%(sbo_pod_name,namespace)
    return cmdObj.run_check_for_status(cmd, status="Running")  