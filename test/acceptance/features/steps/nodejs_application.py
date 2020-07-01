from openshift import Openshift
from command import Command
import re


class NodeJSApp(object):

    nodejs_app = "https://github.com/pmacik/nodejs-rest-http-crud"
    openshift = Openshift()

    name = ""
    namespace = ""

    def __init__(self, name, namespace):
        self.cmd = Command()
        self.name = name
        self.namespace = namespace

    def is_running(self):
        pod_name = self.openshift.wait_for_pod(self.name, self.namespace)
        if pod_name is not None:
            application_pod_status = self.openshift.check_pod_status(pod_name, self.namespace)
            print("The pod {} is running: {}".format(self.name, application_pod_status))
            return application_pod_status
        else:
            return False

    def install(self):

        nodejs_app_arg = "nodejs~" + self.nodejs_app
        cmd = "oc new-app {} --name {} -n {}".format(nodejs_app_arg, self.name, self.namespace)
        (create_new_app_output, exit_code) = self.cmd.run(cmd)
        pattern = 'Creating resources\\s...\n\\s?imagestream.image.openshift.io\\s\"{app_name}\"\\screated\n\\s?buildconfig.build.openshift.io\\s\"{app_name}}\"\\screated\n\\s?deploymentconfig.apps.openshift.io\\s\"{app_name}}\"\\screated\n\\s?service\\s\"{app_name}}\"\\screated\n-->\\sSuccess'
        formatted_pattern = pattern.format(self.name)
        print(formatted_pattern)
        if re.search(formatted_pattern % self.name, create_new_app_output):
            return True

        else:
            return False
        build_config = self.get_build_config()
        if build_config is not None:
            print("build config is {}".format(build_config))
        # build_config | should.contains(self.name)

        (flag_for_build, build_name) = self.get_build_name(self.namespace)
        if flag_for_build != 0:
            return None

        deployment_config = self.openshift.get_deployment_config(self.namespace)
        if deployment_config is not None:
            print("deployment config is {}".format(deployment_config))
        # deployment_config | should.be_equal_to(build_config)

        self.is_nodejs_app_running(self.name, self.namespace)

    def get_db_name_from_api(self):
        return ""
