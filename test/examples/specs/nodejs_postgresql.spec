# A01 Verify the binding of nodejs application with backing service 

Pre condition:
  * Set example directory "nodejs_postgresql"
  * Get oc status

## Install service binding operator
Tags: e2e, smoke

Steps:
  * install service binding operator from "master" version
  * install backing service operator
  * create project
  * install nodejs app
  * create backing db instance
  * create service binding request
 ____________________
These are teardown steps 
  * delete project
  * uninstall backing service operator
  * uninstall service binding operator