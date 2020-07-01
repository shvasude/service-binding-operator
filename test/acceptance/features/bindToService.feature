Feature: Bind an application to a service

    As a user of Service Binding Operator
    I want to bind applications to services it depends on

    Background:
        Given Service Binding Operator is running
        * PostgreSQL DB operator is installed
        * Namespace "service-binding-demo" is used

    Scenario: Bind an imported nodejs app to PostgreSQL database
        Given Imported Nodejs application "nodejs-rest-http-crud" is running
        * DB "db-demo" is running
        When Service Binding Request is applied to connect the database and the application
            """
            apiVersion: apps.openshift.io/v1alpha1
            kind: ServiceBindingRequest
            metadata:
                name: binding-request
            spec:
                applicationSelector:
                    resourceRef: nodejs-rest-http-crud
                    group: apps
                    version: v1
                    resource: deployments
                backingServiceSelector:
                    group: postgresql.baiju.dev
                    version: v1alpha1
                    kind: Database
                    resourceRef: db-demo
            """
        Then application should be re-deployed
        And application should be connected to the DB "db-demo"
        And "<jsonPath>" of Service Binding Request should be changed to "<value>"