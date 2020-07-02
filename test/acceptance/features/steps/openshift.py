import re
import time
from pyshould import should
from command import Command

nodejs_app = "https://github.com/pmacik/nodejs-rest-http-crud"


class Openshift(object):
    def __init__(self):
        self.cmd = Command()
        self.operator_source_yaml_template = '''
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
        self.operator_subscription_yaml_template = '''
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

    def get_pods_lst(self, namespace):
        (output, exit_code) = self.cmd.run(f'oc get pods -n {namespace} -o "jsonpath={{.items[*].metadata.name}}"')
        exit_code | should.be_equal_to(0)
        return output

    def search_item_in_lst(self, lst, search_item):
        lst_arr = lst.split(" ")
        for item in lst_arr:
            if search_item in item:
                if "-build" in search_item:
                    print("item matched {}".format(item))
                    return item
                print("item matched {}".format(item))
                return item
        print("Given item not matched from the list of pods")
        return None

    def search_pod_in_namespace(self, pod_name_part, namespace):
        pods_lst = self.get_pods_lst(namespace)
        if len(pods_lst) != 0:
            print("Pod list are {}".format(pods_lst))
            return self.search_item_in_lst(pods_lst, pod_name_part)
        else:
            print('Pods list is empty under namespace - {}'.format(namespace))
            return None

    def wait_for_pod(self, pod_name_part, namespace, interval=5, timeout=60):
        pod = self.search_pod_in_namespace(pod_name_part, namespace)
        start = 0
        if pod is not None:
            return pod
        else:
            while ((start + interval) <= timeout):
                pod = self.search_pod_in_namespace(pod_name_part, namespace)
                if pod is not None:
                    return pod
                time.sleep(interval)
                start += interval
        return None

    def check_pod_status(self, pod_name, namespace, wait_for_status="Running"):
        cmd = f'oc get pod {pod_name} -n {namespace} -o "jsonpath={{.status.phase}}"'
        status_found, output, exit_status = self.cmd.run_wait_for_status(cmd, wait_for_status)
        return status_found

    def oc_apply(self, yaml):
        (output, exit_code) = self.cmd.run("oc apply -f -", yaml)
        return output

    def create_operator_source(self, name, registry_namespace):
        operator_source = self.operator_source_yaml_template.format(name=name, registry_namespace=registry_namespace)
        return self.oc_apply(operator_source)

    def get_current_csv(self, package_name, catalog, channel):
        cmd = f'oc get packagemanifests -o json | jq -r \'.items[] \
            | select(.metadata.name=="{package_name}") \
            | select(.status.catalogSource=="{catalog}").status.channels[] \
            | select(.name=="{channel}").currentCSV\''
        current_csv, exit_code = self.cmd.run(cmd)

        if current_csv is None:
            return current_csv

        current_csv = current_csv.strip("\n")
        if current_csv == "" or exit_code != 0:
            current_csv = None
        return current_csv

    def create_operator_subscription(self, package_name, operator_source_name, channel):
        operator_subscription = self.operator_subscription_yaml_template.format(
            name=package_name, operator_source_name=operator_source_name,
            channel=channel, csv_version=self.get_current_csv(package_name, operator_source_name, channel))
        return self.oc_apply(operator_subscription)

    def wait_for_package_manifest(self, package_name, operator_source_name, operator_channel, interval=5, timeout=60):
        current_csv = self.get_current_csv(package_name, operator_source_name, operator_channel)
        start = 0
        if current_csv is not None:
            return True
        else:
            while ((start + interval) <= timeout):
                current_csv = self.get_current_csv(package_name, operator_source_name, operator_channel)
                if current_csv is not None:
                    return True
                time.sleep(interval)
                start += interval
        return False

    def get_build_config(self, namespace):
        (build_config, exit_code) = self.cmd.run(f'oc get bc -n {namespace} -o "jsonpath={{.items[*].metadata.name}}"')
        exit_code | should.be_equal_to(0)
        return build_config

    def get_build_name(self, namespace):
        (build_name, exit_code) = self.cmd.run(f'oc get build -n {namespace} -o "jsonpath={{.items[*].metadata.name}}"')
        exit_code | should.be_equal_to(0)
        return build_name

    def check_build_status(self, namespace, wait_for_status="Complete"):
        build_name = self.get_build_name(namespace)
        cmd_build_status = f'oc get build {build_name} -o "jsonpath={{.status.phase}}"'
        (status_found, build_status, exit_code) = self.cmd.run_wait_for_status(cmd_build_status, wait_for_status, 5, 300)
        return status_found

    def get_deployment_config(self, namespace):
        (deployment_config, exit_code) = self.cmd.run(f'oc get dc -n {namespace} -o "jsonpath={{.items[*].metadata.name}}"')
        exit_code | should.be_equal_to(0)
        return deployment_config

    def expose_service_route(self, service_name, namespace):
        output, exit_code = self.cmd.run(f'oc expose svc/{service_name} -n {namespace} --name={service_name}')
        return re.search(r'.*%s\sexposed' % service_name, output)

    def get_route_host(self, name, namespace):
        (output, exit_code) = self.cmd.run(f'oc get route {name} -n {namespace} -o "jsonpath={{.status.ingress[0].host}}"')
        exit_code | should.be_equal_to(0)
        return output

    def delete_deployment_config(self, deployment_config, namespace, db_name):
        cmd = 'oc delele dc {} -n {}'.format(deployment_config, namespace)
        delete_output = self.cmd.run(cmd)
        if re.search(r'.*database.postgresql.baiju.dev/%s\sdeleted' % db_name, delete_output):
            return True
        else:
            return False

    def check_for_deployment_status(self, deployment_name, namespace, wait_for_status="True"):
        deployment_status_cmd = f'oc get deployment {deployment_name} -n {namespace} -o "jsonpath={{.status.conditions[*].status}}"'
        deployment_status, exit_code = self.cmd.run_check_for_status(deployment_status_cmd, wait_for_status, 5, 300)
        exit_code | should.be_equal_to(0)
        return deployment_status

    def get_deployment_name(self, namespace):
        deployment, exit_code = self.cmd.run('oc get deployment -n {namespace} -o "jsonpath={{.items[*].metadata.name}}"')
        if exit_code == 0:
            flag = True
        return flag, deployment

    def get_deployment_env_info(self, app_name, namespace):
        env_cmd = 'oc get deploy %s -n %s "jsonpath={{.spec.template.spec.containers[0].env}}"' % (app_name, namespace)
        env, exit_code = self.cmd.run(env_cmd)
        exit_code | should.be_equal_to(0)
        env_from_cmd = 'oc get deploy %s -n %s "jsonpath={{.spec.template.spec.containers[0].envFrom}}"' % (app_name, namespace)
        env_from, exit_code = self.cmd.run(env_from_cmd)
        exit_code | should.be_equal_to(0)
        return env, env_from

    def use_deployment(self, application_name, deployment_config, namespace):
        self.delete_deployment_config(deployment_config, namespace) | should.be_truthy
        self.oc_apply("deployment.yaml")
        return self.get_deployment_info(application_name, namespace)
