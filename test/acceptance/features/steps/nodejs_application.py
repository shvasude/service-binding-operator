from openshift import Openshift
from command import Command
import re


class NodeJSApp(object):

    nodejs_app = "https://github.com/pmacik/nodejs-rest-http-crud"
    api_end_point = 'http://{route}/api/status/dbNameCM'
    openshift = Openshift()

    name = ""
    namespace = ""

    def __init__(self, name, namespace):
        self.cmd = Command()
        self.name = name
        self.namespace = namespace

    def is_running(self, wait=False):
        build_status_flag = False
        deployment_config_flag = False

        if wait:
            pod_name = self.openshift.wait_for_pod(self.name, self.namespace)
        else:
            pod_name = self.openshift.search_pod_in_namespace(self.name, self.namespace)

        if pod_name is not None:
            pod_name = pod_name + "-build"
            application_pod_status = self.openshift.check_pod_status(pod_name, self.namespace, wait_for_status="Succeeded")
            print("The pod {} is running: {}".format(self.name, application_pod_status))

            if self.openshift.check_build_status(self.namespace):
                build_status_flag = True

            deployment_config = self.openshift.get_deployment_config(self.namespace)
            if deployment_config is not None:
                print("deployment config is {}".format(deployment_config))
                deployment_config_flag = True

            if application_pod_status and build_status_flag and deployment_config_flag:
                return True
            else:
                return False
        else:
            return False

    def install(self):
        nodejs_app_arg = "nodejs~" + self.nodejs_app
        cmd = f"oc new-app {nodejs_app_arg} --name {self.name} -n {self.namespace}"
        (create_new_app_output, exit_code) = self.cmd.run(cmd)
        if exit_code != 0:
            return False
        for pattern in [f'imagestream.image.openshift.io\\s\"{self.name}\"\\screated',
                        f'deploymentconfig.apps.openshift.io\\s\"{self.name}\"\\screated',
                        f'service\\s\"{self.name}\"\\screated']:
            if not re.search(pattern, create_new_app_output):
                return False
        if not self.openshift.expose_service_route(self.name, self.namespace):
            print("Unable to expose the service with build config")
            return False
        return True

    def get_db_name_from_api(self, namespace):
        route_url = self.openshift.get_route_host(self.name, self.namespace)
        print(route_url)
        # return util.get_data_from_api(route_url)
        return None
