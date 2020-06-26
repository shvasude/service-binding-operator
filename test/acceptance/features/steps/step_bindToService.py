# @mark.steps
# ----------------------------------------------------------------------------
# STEPS:
# ----------------------------------------------------------------------------
from behave import given, then, when
from pyshould import should

from servicebindingoperator import Servicebindingoperator
from dboperator import DbOperator
from project import Project


@given('Service Binding Operator is running')
def given_sbo_is_running(context):
    """
    Checks if the SBO is up and running
    """
    context.sbo = Servicebindingoperator()


@given('PostgreSQL DB operator is installed')
def given_db_operator_is_installed(context):
    context.db_operator = DbOperator()
    install_dbOpr_status = context.db_operator.install_src(
        "make install-backing-db-operator-source")
    install_dbOpr_status | should.be_truthy
    print("Postgres DB operator source is installed as the result is {}".format(
        install_dbOpr_status))

    manifest = context.db_operator.get_package_manifest()
    manifest | should.be_truthy
    print('Manifest is displayed as {}'.format(manifest))

    install_dbOpr_sub_status = context.db_operator.install_sub(
        "make install-backing-db-operator-subscription")
    install_dbOpr_sub_status | should.be_truthy
    print("Postgres DB operator subscription is installed as the result is {}".format(
        install_dbOpr_sub_status))

    install_plan_dbOpr_status = context.db_operator.get_install_plan_status_dbOpr()
    install_plan_dbOpr_status | should.equal('Complete')
    print("Install plan status is {}".format(install_plan_dbOpr_status))

    dbOpr_pod_status = context.db_operator.get_db_operator_pod_status()
    dbOpr_pod_status | should.be_equal_to('Running')
    print("Status of the pod that is running service binding operator is {}".format(
        dbOpr_pod_status))


@given(u'Namespace "{namespace_name}" is used')
def given_namespace_is_used(context, namespace_name):
    context.namespace = namespace_name
    context.pjtObj = Project(namespace_name)
    create_project_status = context.pjtObj.create(namespace_name)
    create_project_status | should.be_truthy
    print("Namespace created and set is {} as the result is {}".format(
        namespace_name, create_project_status))

    context.pjtObj.is_present(namespace_name) | should.be_truthy

    project_status = context.pjtObj.get_project_status(namespace_name)
    project_status | should.be_equal_to('Active')
    print("Namespace of the project in a cluster is {}".format(project_status))


@given(u'Imported Nodejs application "{application_name}" is running')
def given_imported_nodejs_app_is_running(context, application_name):
    (build_config, build_status, deployment_config,
     nodejs_app_pod_status) = context.pjt.create_new_app(application_name, context.namespace)
    print('Nodejs application is deployed successfully and running with deployment config')
    (deployment, deploymentStatus) = context.pjt.use_deployment(
        application_name, deployment_config, context.namespace)
    deploymentStatus | should.be_equal_to('True')
    print("Deployment is successful")


@given(u'DB "{db_name}" is running')
def given_db_instance_is_running(context, db_name):
    (status, db_instance_name, connection_ip,
     db_instance_pod_status) = context.db_operator.check_db_instance_status(db_name, context.namespace)
    if status is True:
        print("db instance name is {}, connection ip is {}, db instance pod status is {}".format(
            db_instance_name, connection_ip, db_instance_pod_status))
    else:
        create_dbInstance_status = context.db_operator.create_db_instance(
            db_name)
        create_dbInstance_status | should.be_truthy
        print("Postgres DB operator source is installed as the result is {}".format(
            create_dbInstance_status))
        given_db_instance_is_running(context, db_name)


@when(u'Service Binding Request is applied to connect the database and the application')
def when_sbr_is_applied(context):
    print("SBO YAML: {}".format(context.text))
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
