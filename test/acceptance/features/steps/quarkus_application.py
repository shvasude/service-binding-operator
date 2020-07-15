from command import Command
import re
from openshift import Openshift


class QuarkusApplication(object):

    quarkus_application = "https://github.com/sbose78/using-spring-data-jpa-quarkus"
    openshift = Openshift()

    name = ""
    namespace = ""
    pod_name_pattern = "{name}-[1-9]\d*-build"

    def __init__(self, name, namespace):
        self.cmd = Command()
        self.name = name
        self.namespace = namespace
        self.service_template = '''
---
apiVersion: v1
kind: Service
metadata:
  name: {self.name}
  namespace: {self.namespace}
spec:
  template:
    spec:
      containers:
        - image: docker.io/shvasude/ubi-quarkus:latest
          env:
            - name: RESPONSE
              value: "Hello Serverless!"
'''

    def install(self):
        image_stream_output = self.openshift.create_image_stream(self.name, self.namespace)
        if not re.search(r'.*imagestream.image.openshift.io/%s\s(unchanged|created)' % self.name, image_stream_output):
            print("Failed to create {} image stream".format(self.name))
            return False
        build_config_output = self.openshift.create_build_config(self.name, self.namespace, self.quarkus_application)
        if re.search(r'.*buildconfig.build.openshift.io/%s\screated' % self.name, build_config_output) is None:
            return False
        knative_service_output = self.openshift.create_knative_service(self.name, self.namespace)
        if re.search(r'.*service.serving.knative.dev/%s\screated' % self.name, knative_service_output) is None:
            return False
        return True

    def is_running_as_knative_service(self, wait=False):
        build_flag = False
        if wait:
            pod_name = self.openshift.wait_for_pod(self.get_pod_name_pattern(), self.namespace, timeout=180)
        else:
            pod_name = self.openshift.search_pod_in_namespace(self.get_pod_name_pattern(), self.namespace)

        if pod_name is not None:
            application_pod_status = self.openshift.check_pod_status(pod_name, self.namespace, wait_for_status="Running")
            print("The pod {} is running: {}".format(pod_name, application_pod_status))

            build = self.openshift.search_resource_in_namespace("build", f"{self.name}.*", self.namespace)
            if build is not None:
                print("build is {}".format(build))
                build_flag = True

            if application_pod_status and build_flag:
                return True
            else:
                return False
        else:
            return False

    def get_pod_name_pattern(self):
        return self.pod_name_pattern.format(name=self.name)
