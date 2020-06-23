# @mark.steps
# ----------------------------------------------------------------------------
# STEPS:
# ----------------------------------------------------------------------------
from behave import given, then, when
from servicebindingoperator import Servicebindingoperator
from dboperator import DbOperator
import pdb
from pyshould import *
from pyshould.expect import *


@given('Service Binding Operator is installed')
def given_sbo_is_installed(context):
    context.sbo = Servicebindingoperator()
    status = context.sbo.install("make install-service-binding-operator-master")
    status | should.be_truthy
    print("Service binding operator is installed as the result is {}".format(status))

    

@given('PostgreSQL DB operator is installed')
def given_db_operator_is_installed(context):
    context.dbo = DbOperator()
    status = context.dbo.install("make install-backing-db-operator-source")
            
@given(u'namespace "{namespace_name}" is used')
def given_namespace_is_used(context, namespace_name):
    print("namespace name: {}".format(namespace_name))
    raise NotImplementedError(u'STEP: Given namespace "{}" is used'.format(namespace_name))


@given(u'Imported Nodejs application "{application_name}" is running')
def given_imported_nodejs_app_is_running(context, application_name):
    raise NotImplementedError(u'STEP: Given Imported Nodejs application "nodejs-rest-http-crud" is running')


@given(u'DB "{db_name}" is running')
def step_impl(context,db_name):
    raise NotImplementedError(u'STEP: Given DB "{db_name}" is running'.format(db_name))


@when(u'Service Binding Request is applied to connect the database and the application')
def step_impl(context):
    print("SBO YAML: {}".format(context.text))
    raise NotImplementedError(u'STEP: When Service Binding Request is applied to connect the database and the application')


@then(u'application should be re-deployed')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then application should be re-deployed')


@given(u'application should be connected to the DB "{db_name}"')
def step_impl(context, db_name):
    raise NotImplementedError(u'STEP: Given application should be connected to the DB "{}"'.format(db_name))


@given(u'"{json_path}" of Service Binding Request should be changed to "{json_value}"')
def step_impl(context, json_path, json_value):
    raise NotImplementedError(u'STEP: Given "{}" of Service Binding Request should be changed to "{}"'.format(json_path,json_value))