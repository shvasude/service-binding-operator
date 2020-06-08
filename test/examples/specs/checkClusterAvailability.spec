# A03 checking the availability of the cluster

Pre condition:
    * KUBECONFIG variable is set properly

## Checking the availability of cluster using oc status command
Tags: acceptance, smoke

## golden-path
Steps: 
    * "oc status" command is executed
    * cluster is available when exit code is "0"

## Checking the non availability of cluster using oc status command
Tags: acceptance, smoke

Pre condition:
    * KUBECONFIG variable is not set properly

##negative-path
Steps: 
    * "oc status" command is executed
    * cluster is not available when exit code is not "0"