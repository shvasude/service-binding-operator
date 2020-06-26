from pyshould import *
from pyshould.expect import *
from command import Command

cmdObj = Command()

def get_install_plan_name(oprName, namespace):
    cmd = 'oc get subscription %s -n %s -o "jsonpath={.status.installplan.name}"' % (
        oprName, namespace)
    return cmdObj.run(cmd)


def get_install_plan_status(oprName, namespace):
    install_plan_name = get_install_plan_name(oprName, namespace)
    print("install plan name is {}".format(install_plan_name))
    cmd = 'oc get ip -n %s %s -o "jsonpath={.status.phase}"' % (
        namespace, install_plan_name)
    install_plan_status = cmdObj.run_check_for_status(cmd, status="Complete")
    install_plan_status | should_not.be_equal_to(None)
    return install_plan_status


def get_pods_lst(namespace):
    cmd = 'oc get pods -n %s -o "jsonpath={.items[*].metadata.name}"' % (
        namespace)
    return cmdObj.run(cmd)


def get_pod_name_from_lst_of_pods(oprName, namespace):
    flag = False
    podName = None
    pods_lst = get_pods_lst(namespace)
    if pods_lst != '':
        print("Pod list are {}".format(pods_lst))
        podName = search_item_from_lst(pods_lst, oprName)
        flag = True    
    return flag, podName


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


def get_pod_status(oprName, namespace, wait_for_status="Running"):
    (flag, sbo_pod_name) = get_pod_name_from_lst_of_pods(oprName, namespace)
    if flag == True:
        cmd = 'oc get pod %s -n %s -o "jsonpath={.status.phase}"' % (
            sbo_pod_name, namespace)
        return cmdObj.run_check_for_status(cmd, wait_for_status)
    else:
        return False

def oc_apply(yaml):
    output = subprocess.check_output(
        "oc apply -f -", shell=True, stderr=subprocess.STDOUT, input=yaml.encode("utf-8"))
    return output.decode("utf-8")


opearator_source_yaml_template = '''
---
apiVersion: operators.coreos.com/v1
kind: OperatorSource
metadata:
  name: {name}
  namespace: openshift-marketplace
spec:
  type: appregistry
  endpoint: https://quay.io/cnr
  registryNamespace: {registry_namespace}
'''


def create_operator_source(name, registry_namespace):
    operator_source = opearator_source_yaml_template.format(
        name=name, registry_namespace=registry_namespace)
    return oc_apply(operator_source)


def get_current_csv(package_name, catalog, channel):
    cmd = "oc get packagemanifests -o json | jq -r '.items[] | select(.metadata.name==\"{package_name}\") | select(.status.catalogSource==\"{catalog}\").status.channels[] | select(.name==\"{channel}\").currentCSV'".format(
        package_name=package_name, catalog=catalog, channel=channel)
    return cmdObj.run(cmd)


operator_subscription_yaml_template = '''
---
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: '{name}'
  namespace: openshift-operators
spec:
  channel: '{channel}' # the quotes are necessary to avoid conversions from strings like '1.0' to be converted to actual decimal numbers
  installPlanApproval: Automatic
  name: '{name}'
  source: '{operator_source_name}'
  sourceNamespace: openshift-marketplace
  startingCSV: '{csv_version}'
'''

def create_operator_subscription(package_name, operator_source_name, channel):
    operator_subscription = opearator_source_yaml_template.format(
        name=package_name, operator_source_name=operator_source_name, channel=channel, csv_version=get_current_csv(package_name, operator_source_name, channel))
    return oc_apply(operator_subscription)

def wait_for_package_manifest(package_manifest):
    pass

