# A04 Verify installing service binding operator

Pre condition:
  * cluster is available when exit code is "0"
  * working directory is set to "nodejs_postgresql" under "examples" directory

Tags: acceptance, smoke

Steps:
  * When "make install-service-binding-operator-master" command is executed
  * Then subscription "service-binding-operator" is created under the "openshift-operators" namespace
  * And install plan owned by "service-binding-operator" subscription is created in the "openshift-operators" namespace
  * And install plan owned by "service-binding-operator" subscription gets to the "Complete" state within 3 minutes
  * And pod with name starting with "service-binding-operator" is created in the "openshift-operators" namespace
  * And pod with name starting with "service-binding-operator" gets to the "Running" state within 3 minutes