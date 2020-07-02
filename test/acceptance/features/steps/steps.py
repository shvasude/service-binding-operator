# @mark.steps
# ----------------------------------------------------------------------------
# STEPS:
# ----------------------------------------------------------------------------
from behave import given, then, when
from pyshould import should

from servicebindingoperator import Servicebindingoperator
from dboperator import DbOperator
from postgres_db import PostgresDB
from namespace import Namespace
from nodejs_application import NodeJSApp
from service_binding_request import ServiceBindingRequest


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
        db_operator.is_running(wait=True) | should.be_truthy.desc("DB operator installed")
    context.db_operator = db_operator
    print("PostgresSQL DB operator is running!!!")


@given(u'Namespace "{namespace_name}" is used')
def given_namespace_is_used(context, namespace_name):
    namespace = Namespace(namespace_name)
    if not namespace.is_present():
        print("Namespace is not present, creating namespace: {}...".format(namespace_name))
        namespace.create() | should.be_truthy.desc("Namespace {} is created".format(namespace_name))
    print("Namespace {} is created!!!".format(namespace_name))
    context.namespace = namespace


@given(u'Imported Nodejs application "{application_name}" is running')
def given_imported_nodejs_app_is_running(context, application_name):
    namespace = context.namespace
    application = NodeJSApp(application_name, namespace.name)
    if not application.is_running():
        application.install() | should.be_truthy.desc("Application is installed")
        application.is_running(wait=True) | should.be_truthy.desc("Application is running")
    print("Nodejs application is running!!!")
    application.get_db_name_from_api() | should.be_equal_to("N/A")


@given(u'DB "{db_name}" is running')
def given_db_instance_is_running(context, db_name):
    namespace = context.namespace

    db = PostgresDB("db-demo", namespace.name)
    if not db.is_running():
        db.create() | should.be_truthy.desc("Postgres DB created")
        db.is_running(wait=True) | should.be_truthy.desc("Postgres DB is running")
    context.postgres_db = db


@when(u'Service Binding Request is applied to connect the database and the application')
def when_sbr_is_applied(context):
    sbr_yaml = context.text
    print("SBO YAML: {}".format(sbr_yaml))
    sbr = ServiceBindingRequest()
    sbr.create(sbr_yaml) | should.be_truthy.desc("Service Binding Request Created")


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
