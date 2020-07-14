from command import Command
import re
from openshift import Openshift


class QuarkusApplication(object):

    quarkus_application = "https://github.com/sbose78/using-spring-data-jpa-quarkus"
    openshift = Openshift()

    name = ""
    namespace = ""

    def __init__(self, name, namespace):
        self.cmd = Command()
        self.name = name
        self.namespace = namespace
        self.service_template = '''
---
apiVersion: v1
kind: Service
metadata:
  name: {name}
  namespace: {namespace}
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
        image_stream_output = self.openshift.create_image_stream(self.name)
        if not re.search(r'.*imagestream.image.openshift.io/%s\s(unchanged|created)' % self.name, image_stream_output):
            print("Failed to create {} image stream".format(self.name))
            return False
        image_repository = self.openshift.get_docker_image_repository(self.name, namespace=self.namespace)
        self.openshift.create_build_config(self.name, self.quarkus_application, image_repository)

    def is_running_as_knative_service(self):
        return False
