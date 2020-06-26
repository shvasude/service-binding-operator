import pdb
import re
import util
from pyshould import should, should_not

from command import Command


class Openshift():
    def __init__(self):
        self.cmdObj = Command()
        self.nodejs_app = "https://github.com/pmacik/nodejs-rest-http-crud"
        self.opearator_source_yaml_template = '''
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

    def oc_apply(self, yaml):
        return self.cmdObj.run_yaml(yaml)

    def create_operator_source(self, name, registry_namespace):
        operator_source = self.opearator_source_yaml_template.format(
            name=name, registry_namespace=registry_namespace)
        return self.oc_apply(operator_source)

    def get_current_csv(self, package_name, catalog, channel):
        cmd = "oc get packagemanifests -o json | jq -r '.items[] \
            | select(.metadata.name==\"{package_name}\") \
            | select(.status.catalogSource==\"{catalog}\").status.channels[] \
            | select(.name==\"{channel}\").currentCSV'".format(
            package_name=package_name, catalog=catalog, channel=channel)
        return self.cmdObj.run(cmd)

    def create_operator_subscription(self, package_name, operator_source_name, channel):
        operator_subscription = self.opearator_source_yaml_template.format(
            name=package_name, operator_source_name=operator_source_name, channel=channel,
            csv_version=self.get_current_csv(package_name, operator_source_name, channel))
        return self.oc_apply(operator_subscription)

    def wait_for_package_manifest(self, package_manifest):
        print("TODO implememt this for {}".format(package_manifest))
        pass

    def create_new_app(self, app_name, project):
        nodjs_app_arg = "nodejs~" + self.nodeJSApp
        cmd = "oc new-app {} --name {} -n {}".format(
            nodjs_app_arg, app_name, project)
        create_new_app_output = self.cmdObj.run(cmd)
        pdb.set_trace()
        create_new_app_output | should_not.be_equal_to(None)

        build_config = self.get_build_config()
        build_config | should.have(app_name)

        (build_name, build_status) = self.get_build_status()
        build_status | should.be_equal_to("Complete")
        build_name | should.have(build_config)

        exp_build_pod_name = build_name + "-build"
        nodejs_app_pod_status = self.get_nodejs_app_pod_status(
            exp_build_pod_name, project, "Succeeded")
        nodejs_app_pod_status | should.be_equal_to("Succeeded")

        deployment_config = self.get_deployment_config(project)
        deployment_config | should.be_equal_to(build_config)

        return build_config, build_status, deployment_config, nodejs_app_pod_status

    def get_nodejs_app_pod_status(self, exp_build_pod_name, project, wait_for_status):
        return util.get_pod_status(exp_build_pod_name, project, wait_for_status)

    def get_build_config(self):
        cmd = 'oc get bc -o "jsonpath={.items[*].metadata.name}"'
        build_config = self.cmdObj.run(cmd)
        build_config | should_not.be_equal_to(None)
        return

    def get_build_status(self):
        cmd_build_name = 'oc get build -o "jsonpath={.items[*].metadata.name}"'
        build_name = self.cmdObj.run(cmd_build_name)
        build_name | should_not.be_equal_to(None)

        cmd_build_status = 'oc get build {} -o "jsonpath={{.status.phase}}"'.format(
            build_name)
        build_status = self.cmdObj.run_check_for_status(
            cmd_build_status, "Complete", 5, 300)
        build_status | should_not.be_equal_to(None)
        return build_name, build_status

    def get_deployment_config(self, project):
        cmd = 'oc get dc -n {} -o "jsonpath={{.items[*].metadata.name}}"'.format(
            project)
        deployment_config = self.cmdObj.run(cmd)
        deployment_config | should_not.be_equal_to(None)
        return deployment_config

    def delete_deployment_config(self, deployment_config, project, db_name):
        cmd = 'oc delele dc {} -n {}'.format(deployment_config, project)
        delete_output = self.cmdObj.run(cmd)
        pdb.set_trace()
        if re.search(r'.*database.postgresql.baiju.dev/%s\sdeleted' % db_name, delete_output):
            return True
        else:
            return False

        '''
        pods := util.GetPodLst(operatorsNS)
        checkFlag, podName := util.SrchItemFromLst(pods, dcPod)

        require.Equal(t, false, checkFlag, "list contains deployment config pod from the list of pods running in the cluster")
        require.Equal(t, "", podName, "list contains %s deployment config pod from the list of pods running in the cluster", podName)
        t.Logf("-> List does not conta
        '''

    def get_deployment_info(self, app_name, project):
        deployment_cmd = 'oc get deployment -n {} -o "jsonpath={{.items[*].metadata.name}}"'.format(
            project)
        deployment = self.cmdObj.run(deployment_cmd)
        deployment | should_not.be_equal_to(None)

        deployment_status_cmd = 'oc get deployment {} -n {} -o "jsonpath={{.status.conditions[*].status}}"'.format(
            deployment, project)
        deployment_status = self.cmdObj.run_check_for_status(
            deployment_status_cmd, "True", 5, 300)
        deployment_status | should_not.be_equal_to(None)

        env_cmd = 'oc get deploy {} -n {} "jsonpath={{.spec.template.spec.containers[0].env}}"'.format(
            app_name, project)
        env = self.cmdObj.run(env_cmd)
        env | should_not.be_equal_to(None)

        env_from_cmd = 'oc get deploy {} -n {} "jsonpath={{.spec.template.spec.containers[0].envFrom}}"'.format(
            app_name, project)
        env_from = self.cmdObj.run(env_from_cmd)
        env_from | should_not.be_equal_to(None)

        return deployment, deployment_status

    def use_deployment(self, application_name, deployment_config, project):
        self.delete_deployment_config(
            deployment_config, project) | should.be_truthy
        self.oc_apply("deployment.yaml")
        return self.get_deployment_info(application_name, project)
