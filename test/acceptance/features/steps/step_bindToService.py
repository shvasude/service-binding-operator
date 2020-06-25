# @mark.steps
# ----------------------------------------------------------------------------
# STEPS:
# ----------------------------------------------------------------------------
from behave import given, then, when
import pdb
from pyshould import *
from pyshould.expect import *

from servicebindingoperator import Servicebindingoperator
from dboperator import DbOperator
from project import Project

@given('Service Binding Operator is installed')
def given_sbo_is_installed(context):
    context.sbo = Servicebindingoperator()    
    install_sbo_status = context.sbo.install("make install-service-binding-operator-master") 
    install_sbo_status | should.be_truthy
    print("Service binding operator is installed as the result is {}".format(install_sbo_status))

    install_plan_sbo_status = context.sbo.get_install_plan_status_sbo()
    install_plan_sbo_status | should.equal('Complete')
    print("Install plan status is {}".format(install_plan_sbo_status))    

    sbo_pod_status = context.sbo.get_sbo_pod_status()
    sbo_pod_status | should.be_equal_to('Running')
    print("Status of the pod that is running service binding operator is {}".format(sbo_pod_status))

@given('PostgreSQL DB operator is installed')
def given_db_operator_is_installed(context):
    context.dbOpr = DbOperator()
    install_dbOpr_status = context.dbOpr.install_src("make install-backing-db-operator-source")
    install_dbOpr_status | should.be_truthy
    print("Postgres DB operator source is installed as the result is {}".format(install_dbOpr_status))    

    manifest = context.dbOpr.get_package_manifest()
    manifest | should.be_truthy   
    print('Manifest is displays as {}'.format(manifest)) 

    install_dbOpr_sub_status = context.dbOpr.install_sub("make install-backing-db-operator-subscription")
    install_dbOpr_sub_status | should.be_truthy
    print("Postgres DB operator subscription is installed as the result is {}".format(install_dbOpr_sub_status))    

    install_plan_dbOpr_status = context.dbOpr.get_install_plan_status_dbOpr()
    install_plan_dbOpr_status | should.equal('Complete')
    print("Install plan status is {}".format(install_plan_dbOpr_status))    

    dbOpr_pod_status = context.dbOpr.get_dbOpr_pod_status()
    dbOpr_pod_status | should.be_equal_to('Running')
    print("Status of the pod that is running service binding operator is {}".format(dbOpr_pod_status))
            
@given(u'Project "{project_name}" is used')
def given_namespace_is_used(context, project_name):
    context.pjt = Project()
    create_project_status = context.pjt.create("make create-project", project_name)
    create_project_status | should.be_truthy
    print("Project created and set is {} as the result is {}".format(project_name, create_project_status))    

    project_cluster = context.pjt.get_project_from_cluster(project_name)
    project_cluster | should.be_equal_to(project_name)
    print("Project created within the cluster is {}".format(project_cluster))

    project_status = context.pjt.get_project_status(project_cluster)
    project_status | should.be_equal_to('Active')
    print("Status of the project in a cluster is {}".format(project_status))
   
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