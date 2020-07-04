# @mark.steps
# ----------------------------------------------------------------------------
# STEPS:
# ----------------------------------------------------------------------------
from behave import given, then, when
from pyshould import should, should_not

from servicebindingoperator import Servicebindingoperator
from dboperator import DbOperator
from openshift import Openshift
from postgres_db import PostgresDB
from namespace import Namespace
from nodejs_application import NodeJSApp
from service_binding_request import ServiceBindingRequest


@given(u'Namespace "{namespace_name}" is used')
def given_namespace_is_used(context, namespace_name):
    namespace = Namespace(namespace_name)
    if not namespace.is_present():
        print("Namespace is not present, creating namespace: {}...".format(namespace_name))
        namespace.create() | should.be_truthy.desc("Namespace {} is created".format(namespace_name))
    print("Namespace {} is created!!!".format(namespace_name))
    context.namespace = namespace


@given('Service Binding Operator is running')
def given_sbo_is_running(context):
    """
    Checks if the SBO is up and running
    """
    sb_operator = Servicebindingoperator(namespace=context.namespace.name)
    sb_operator.is_running() | should.be_truthy.desc("Service Binding Operator is running")
    print("Service binding operator is running!!!")


@given('PostgreSQL DB operator is installed')
def given_db_operator_is_installed(context):
    db_operator = DbOperator()
    if not db_operator.is_running():
        print("DB operator is not installed, installing...")
        db_operator.install_operator_source() | should.be_truthy.desc("DB operator source installed")
        db_operator.install_operator_subscription() | should.be_truthy.desc("DB operator subscription installed")
        db_operator.is_running(wait=True) | should.be_truthy.desc("DB operator installed")
    print("PostgresSQL DB operator is running!!!")


@given(u'Imported Nodejs application "{application_name}" is running')
def given_imported_nodejs_app_is_running(context, application_name):
    namespace = context.namespace
    application = NodeJSApp(application_name, namespace.name)
    if not application.is_running():
        print("application is not running, trying to import it")
        application.install() | should.be_truthy.desc("Application is installed")
        application.is_running(wait=True) | should.be_truthy.desc("Application is running")
    print("Nodejs application is running!!!")
    application.get_db_name_from_api() | should_not.be_none
    context.nodejs_app = application


@given(u'DB "{db_name}" is running')
def given_db_instance_is_running(context, db_name):
    namespace = context.namespace

    db = PostgresDB(db_name, namespace.name)
    if not db.is_running():
        db.create() | should.be_truthy.desc("Postgres DB created")
        db.is_running(wait=True) | should.be_truthy.desc("Postgres DB is running")
    print(f"DB {db_name} is running!!!")


@when(u'Service Binding Request is applied to connect the database and the application')
def when_sbr_is_applied(context):
    sbr_yaml = context.text
    sbr = ServiceBindingRequest()
    application = context.nodejs_app
    context.nodejs_app_original_generation = application.get_observed_generation()
    context.nodejs_app_original_pod_name = application.get_running_pod_name()
    sbr.create(sbr_yaml) | should.be_truthy.desc("Service Binding Request Created")


@then(u'application should be re-deployed')
def then_application_redeployed(context):
    application = context.nodejs_app
    application.get_redeployed_pod_name(context.nodejs_app_original_pod_name) | should_not.be_none.desc(
        "There is a running pod of the application different from the original one before redeployment.")


@then(u'application should be connected to the DB "{db_name}"')
def then_app_is_connected_to_db(context, db_name):
    application = context.nodejs_app
    app_db_name = application.get_db_name_from_api()
    app_db_name | should.be_equal_to(db_name)


@then(u'"{json_path}" of Service Binding Request should be changed to "{json_value}"')
def then_sbo_json_is(context, json_path, json_value):
    openshift = Openshift()
    openshift.get_resource_info_by_jsonpath("sbr", "binding-request", context.namespace.name, json_path) | should.be_equal_to(json_value)
