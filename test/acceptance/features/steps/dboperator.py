import re
from pyshould import should, should_not

from command import Command
from openshift import Openshift


class DbOperator():

    openshift = Openshift()
    cmd = Command()

    operator_name = ""
    operator_namespace = ""
    operator_source_name = "db-operators"
    operator_registry_namespace = "pmacik"
    operator_registry_channel = "stable"
    package_name = "db-operators"

    def __init__(self, name="postgresql-operator", namespace="openshift-operators"):
        self.operator_name = name
        self.operator_namespace = namespace

    def is_running(self, wait_for_pod=False):
        if wait_for_pod:
            pod_name = self.openshift.wait_for_pod(self.operator_name, self.operator_namespace)
        else:
            pod_name = self.openshift.search_pod_in_namespace(self.operator_name, self.operator_namespace)
        if pod_name is not None:
            operator_pod_status = self.openshift.check_pod_status(pod_name, self.operator_namespace)
            print("The pod {} is running: {}".format(self.operator_name, operator_pod_status))
            return operator_pod_status
        else:
            return False

    def install_operator_source(self):
        install_src_output = self.openshift.create_operator_source(self.operator_source_name, self.operator_registry_namespace)
        if not re.search(r'.*operatorsource.operators.coreos.com/%s\s(unchanged|created)' % self.operator_source_name, install_src_output):
            print("Failed to create {} operator source".format(self.operator_source_name))
            return False
        return self.openshift.wait_for_package_manifest(self.package_name, self.operator_source_name, self.operator_registry_channel)

    def install_operator_subscription(self):
        install_sub_output = self.openshift.create_operator_subscription(self.package_name, self.operator_source_name, self.operator_registry_channel)
        return re.search(r'.*subscription.operators.coreos.com/%s\s(unchanged|created)' % self.operator_source_name, install_sub_output)

    def get_package_manifest(self):
        cmd = 'oc get packagemanifest %s -o "jsonpath={.metadata.name}"' % self.pkgManifest
        manifest = self.cmd.run_check_for_status(
            cmd, status=self.pkgManifest)
        manifest | should_not.be_equal_to(None)
        manifest | should.equal(self.pkgManifest)
        return manifest

    def create_db_instance(self, db_name):
        cmd = 'make create-backing-db-instance'
        create_db_instance_output = self.cmd.run(cmd)
        if re.search(r'.*database.postgresql.baiju.dev/%s\s(created|unchanged)' % db_name, create_db_instance_output):
            return True

    def get_db_instance_name(self, project):
        cmd = 'oc get db -n %s -o "jsonpath={.items[*].metadata.name}"' % project
        self.db_instance = self.cmd.run(cmd)
        self.db_instance | should_not.be_equal_to(None)
        return self.db_instance

    def get_connection_ip(self):
        cmd = 'oc get db %s -o "jsonpath={.status.dbConnectionIP}"' % self.db_instance
        self.connection_ip = self.cmd.run(cmd)
        self.connection_ip | should_not.be_equal_to(None)
        if re.match(r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}', self.connection_ip):
            return True
        else:
            return False

    def get_db_instance_pod_status(self, db_name, project):
        return self.get_pod_status(db_name, project)

    def check_db_instance_status(self, db_name, project):
        db_instance_name = self.get_db_instance_name(project)
        connection_ip = self.get_connection_ip()
        db_instance_pod_status = self.get_db_instance_pod_status(
            db_name, project)
        if (db_instance_name == db_name) and (connection_ip is True) and (db_instance_pod_status == "Running"):
            return True, db_instance_name, connection_ip, db_instance_pod_status
        else:
            return False, None, None, None
