from openshift import Openshift
from should import should


class NodeJSApp(object):

    openshift = Openshift()

    name = ""
    namespace = ""

    def __init__(self, name, namespace):
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

        nodjs_app_arg = "nodejs~" + self.nodejs_app
        cmd = "oc new-app {} --name {} -n {}".format(nodjs_app_arg, self.name, self.namespace)

        (create_new_app_output, exit_code) = self.cmd.run(cmd)
        exit_code | should.be_equal_to(0)

        build_config = self.get_build_config()
        build_config | should.contains(self.name)

        (flag_for_build, build_name) = self.get_build_name(self.namespace)
        if flag_for_build != 0:
            return None

        deployment_config = self.get_deployment_config(self.namespace)
        deployment_config | should.be_equal_to(build_config)

        self.is_nodejs_app_running(self.name, self.namespace)

    def get_db_name_from_api(self):
        return ""
