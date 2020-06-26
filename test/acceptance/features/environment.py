"""
before_step(context, step), after_step(context, step)
    These run before and after every step.
    The step passed in is an instance of Step.
before_scenario(context, scenario), after_scenario(context, scenario)
    These run before and after each scenario is run.
    The scenario passed in is an instance of Scenario.
before_feature(context, feature), after_feature(context, feature)
    These run before and after each feature file is exercised.
    The feature passed in is an instance of Feature.
before_all(context), after_all(context)
    These run before and after the whole shooting match.
"""

import os
import builtins
import subprocess
from pyshould import should


def before_scenario(_context, scenario):
    if scenario.name == "Bind an imported nodejs app to PostgreSQL database":
        # Setting the directory
        home_path = os.getcwd()
        # Printing CWD after setting it to nodejs_postgresql folder
        builtins.path = os.path.join(home_path, 'examples/nodejs_postgresql')


def before_all(_context):
    os.system('export KUBECONFIG=$HOME/.kube/config')


def before_step(_context, _step):
    print("Getting OC status on each step")
    code, output = subprocess.getstatusoutput('oc status')
    print("[CODE] {}".format(code))
    print("[CMD] {}".format(output))
    code | should.be_an_integer.and_equal(0)
    print("***Connected to cluster***")
