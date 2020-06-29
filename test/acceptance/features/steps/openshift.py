import re
import time
from pyshould import should, should_not

from command import Command


class Openshift(object):
    def __init__(self):
        self.cmd = Command()
        self.nodejs_app = "https://github.com/pmacik/nodejs-rest-http-crud"
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
        cmd = 'oc get pods -n %s -o "jsonpath={.items[*].metadata.name}"' % (namespace)
        (output, exit_code) = self.cmd.run(cmd)
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

    def check_pod_status(self, pod_name, namespace, wait_for_status="Running"):
        if pod_name is not None:
            cmd = 'oc get pod %s -n %s -o "jsonpath={.status.phase}"' % (pod_name, namespace)
            status_found, output, exit_status = self.cmd.run_wait_for_status(cmd, wait_for_status)
            return status_found
        else:
            return False

    def oc_apply(self, yaml):
        (output, exit_code) = self.cmd.run("oc apply -f -", yaml)
        print("[{}][{}]".format(exit_code, output))
        return output

    def create_operator_source(self, name, registry_namespace):
        operator_source = self.operator_source_yaml_template.format(name=name, registry_namespace=registry_namespace)
        return self.oc_apply(operator_source)

    def get_current_csv(self, package_name, catalog, channel):
        cmd = "oc get packagemanifests -o json | jq -r '.items[] \
            | select(.metadata.name==\"{package_name}\") \
            | select(.status.catalogSource==\"{catalog}\").status.channels[] \
            | select(.name==\"{channel}\").currentCSV'".format(
            package_name=package_name, catalog=catalog, channel=channel)
        current_csv, exit_code = self.cmd.run(cmd)

        if current_csv is None:
            return current_csv

        current_csv = current_csv.strip("\n")
        if current_csv == "" or exit_code != 0:
            current_csv = None

        print("[{}]".format(current_csv))
        return current_csv

    def create_operator_subscription(self, package_name, operator_source_name, channel):
        operator_subscription = self.operator_subscription_yaml_template.format(
            name=package_name, operator_source_name=operator_source_name,
            channel=channel, csv_version=self.get_current_csv(package_name, operator_source_name, channel))
        return self.oc_apply(operator_subscription)

    def wait_for_package_manifest(self, package_name, operator_source_name, operator_channel, interval=5, timeout=12):
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

    def create_new_app(self, app_name, project):
        nodjs_app_arg = "nodejs~" + self.nodeJSApp
        cmd = "oc new-app {} --name {} -n {}".format(
            nodjs_app_arg, app_name, project)
        create_new_app_output = self.cmd.run(cmd)
        create_new_app_output | should_not.be_equal_to(None)

        build_config = self.get_build_config()
        build_config | should.have(app_name)

        (build_name, build_status) = self.get_build_status()
        build_status | should.be_equal_to("Complete")
        build_name | should.have(build_config)

        exp_build_pod_name = build_name + "-build"
        nodejs_app_pod_status = self.get_nodejs_app_pod_status(exp_build_pod_name, project, "Succeeded")
        nodejs_app_pod_status | should.be_equal_to("Succeeded")

        deployment_config = self.get_deployment_config(project)
        deployment_config | should.be_equal_to(build_config)

        return build_config, build_status, deployment_config, nodejs_app_pod_status

    def get_nodejs_app_pod_status(self, exp_build_pod_name, project, wait_for_status):
        return self.get_pod_status(exp_build_pod_name, project, wait_for_status)

    def get_build_config(self):
        cmd = 'oc get bc -o "jsonpath={.items[*].metadata.name}"'
        build_config = self.cmd.run(cmd)
        build_config | should_not.be_equal_to(None)
        return

    def get_build_status(self):
        cmd_build_name = 'oc get build -o "jsonpath={.items[*].metadata.name}"'
        build_name = self.cmd.run(cmd_build_name)
        build_name | should_not.be_equal_to(None)

        cmd_build_status = 'oc get build {} -o "jsonpath={{.status.phase}}"'.format(
            build_name)
        build_status = self.cmd.run_check_for_status(
            cmd_build_status, "Complete", 5, 300)
        build_status | should_not.be_equal_to(None)
        return build_name, build_status

    def get_deployment_config(self, project):
        cmd = 'oc get dc -n {} -o "jsonpath={{.items[*].metadata.name}}"'.format(
            project)
        deployment_config = self.cmd.run(cmd)
        deployment_config | should_not.be_equal_to(None)
        return deployment_config

    def delete_deployment_config(self, deployment_config, project, db_name):
        cmd = 'oc delele dc {} -n {}'.format(deployment_config, project)
        delete_output = self.cmd.run(cmd)
        if re.search(r'.*database.postgresql.baiju.dev/%s\sdeleted' % db_name, delete_output):
            return True
        else:
            return False

    def get_deployment_info(self, app_name, project):
        deployment_cmd = 'oc get deployment -n {} -o "jsonpath={{.items[*].metadata.name}}"'.format(
            project)
        deployment = self.cmd.run(deployment_cmd)
        deployment | should_not.be_equal_to(None)

        deployment_status_cmd = 'oc get deployment {} -n {} -o "jsonpath={{.status.conditions[*].status}}"'.format(
            deployment, project)
        deployment_status = self.cmd.run_check_for_status(
            deployment_status_cmd, "True", 5, 300)
        deployment_status | should_not.be_equal_to(None)

        env_cmd = 'oc get deploy {} -n {} "jsonpath={{.spec.template.spec.containers[0].env}}"'.format(
            app_name, project)
        env = self.cmd.run(env_cmd)
        env | should_not.be_equal_to(None)

        env_from_cmd = 'oc get deploy {} -n {} "jsonpath={{.spec.template.spec.containers[0].envFrom}}"'.format(
            app_name, project)
        env_from = self.cmd.run(env_from_cmd)
        env_from | should_not.be_equal_to(None)

        return deployment, deployment_status

    def use_deployment(self, application_name, deployment_config, project):
        self.delete_deployment_config(
            deployment_config, project) | should.be_truthy
        self.oc_apply("deployment.yaml")
        return self.get_deployment_info(application_name, project)
