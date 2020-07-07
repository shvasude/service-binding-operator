Feature: Bind an application to a service

    As a user of Service Binding Operator
    I want to bind applications to services it depends on

    Background:
        Given Namespace "default" is used
        * Service Binding Operator is running
        * PostgreSQL DB operator is installed

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
        And "{.status.conditions[*].status}" of Service Binding Request should be changed to "True"

    Background:
        Given Openshift Serverless Operator is running
        * Knative serving is running
        * ubi-quarkus-native-s2i builder image is present

    Scenario: Bind an imported quarkus app which is deployed as knative service to PostgreSQL database
        Given DB "db-demo" is running
        * Imported Quarkus application "knative-app" is running
        When Service Binding Request is applied to connect the database and the application
            """
            apiVersion: apps.openshift.io/v1alpha1
            kind: ServiceBindingRequest
            metadata:
                name: binding-request
                namespace: service-binding-demo
            spec:
                applicationSelector:
                    group: serving.knative.dev
                    version: v1beta1
                    resource: services
                    resourceRef: knative-app
                backingServiceSelector:
                    group: postgresql.baiju.dev
                    version: v1alpha1
                    kind: Database
                    resourceRef: db-demo
                customEnvVar:
                    - name: JDBC_URL
                    value: 'jdbc:postgresql://{{ .status.dbConnectionIP }}:{{ .status.dbConnectionPort }}/{{ .status.dbName }}'
                    - name: DB_USER
                    value: '{{ index .status.dbConfigMap "db.username" }}'
                    - name: DB_PASSWORD
                    value: '{{ index .status.dbConfigMap "db.password" }}'
            """
        Then application should be re-deployed
        And application should be connected to the DB "db-demo"
        And "{.status.conditions[*].status}" of Service Binding Request should be changed to "True"