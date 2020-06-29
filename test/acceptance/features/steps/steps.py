# @mark.steps
# ----------------------------------------------------------------------------
# STEPS:
# ----------------------------------------------------------------------------
from behave import given, then, when
from pyshould import should

from servicebindingoperator import Servicebindingoperator
from dboperator import DbOperator
from namespace import Namespace


@given('Service Binding Operator is running')
def given_sbo_is_running(context):
    """
    Checks if the SBO is up and running
    """
    sb_operator = Servicebindingoperator()
    sb_operator.is_running() | should.be_truthy.desc("Service Binding Operator is running")
    context.sb_operator = sb_operator
    print("Service binding operator is running!!!")


@given('PostgreSQL DB operator is installed')
def given_db_operator_is_installed(context):
    db_operator = DbOperator()
    if not db_operator.is_running():
        print("DB operator is not installed, installing...")
        db_operator.install_operator_source() | should.be_truthy.desc("DB operator source installed")
        db_operator.install_operator_subscription() | should.be_truthy.desc("DB operator subscription installed")
    db_operator.is_running() | should.be_truthy.desc("DB operator installed")
    context.db_operator = db_operator
    print("PostgresSQL DB operator is running!!!")


@given(u'Namespace "{namespace_name}" is used')
def given_namespace_is_used(context, namespace_name):
    namespace = Namespace(namespace_name)
    if not namespace.is_present():
        namespace.create() | should.be_truthy.desc("Namespace {} is created".format(namespace_name))
    context.namespace = namespace_name


@given(u'Imported Nodejs application "{application_name}" is running')
def given_imported_nodejs_app_is_running(context, application_name):

    # namespace = context.namespace_name
    # openshift = openshift()
    # (build_config, build_status, deployment_config,nodejs_app_pod_status) = openshift.create_new_app(application_name, namespace)
    # print('Nodejs application is deployed successfully and running with deployment config')
    # (deployment, deploymentStatus) = openshift.use_deployment(application_name, deployment_config, namespace)
    # deploymentStatus | should.be_equal_to('True')
    # print("Deployment is successful")

    raise NotImplementedError(u'Imported Nodejs application "{}" is running'.format(application_name))


@given(u'DB "{db_name}" is running')
def given_db_instance_is_running(context, db_name):

    # (status, db_instance_name, connection_ip,
    # db_instance_pod_status) = context.db_operator.check_db_instance_status(db_name, context.namespace.name)
    # if status is True:
    #    print("db instance name is {}, connection ip is {}, db instance pod status is {}".format(
    #        db_instance_name, connection_ip, db_instance_pod_status))
    # else:
    #    create_db_instance_status = context.db_operator.create_db_instance(
    #        db_name)
    #    create_db_instance_status | should.be_truthy
    #    print("Postgres DB operator source is installed as the result is {}".format(
    #        create_db_instance_status))
    #    given_db_instance_is_running(context, db_name)

    raise NotImplementedError(
        u'DB "{}" is running'.format(db_name))


@when(u'Service Binding Request is applied to connect the database and the application')
def when_sbr_is_applied(context):
    # print("SBO YAML: {}".format(context.text))
    raise NotImplementedError(
        u'STEP: When Service Binding Request is applied to connect the database and the application')


@then(u'application should be re-deployed')
def then_application_redeployed(context):
    raise NotImplementedError(u'STEP: Then application should be re-deployed')


@then(u'application should be connected to the DB "{db_name}"')
def then_app_is_connected_to_db(context, db_name):
    raise NotImplementedError(
        u'STEP: Then application should be connected to the DB "{}"'.format(db_name))


@then(u'"{json_path}" of Service Binding Request should be changed to "{json_value}"')
def then_sbo_json_is(context, json_path, json_value):
    raise NotImplementedError(
        u'STEP: Then "{}" of Service Binding Request should be changed to "{}"'.format(json_path, json_value))
