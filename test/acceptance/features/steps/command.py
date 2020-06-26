import subprocess
import time
import os


class Command(object):
    path = ""
    env = {}

    def __init__(self, path=None):
        if path is None:
            self.path = os.getcwd()
        else:
            self.path = path

    def setenv(self, key, value):
        self.env[key] = value

    def run(self, cmd):
        output = None
        exit_code = 0
        try:
            output = subprocess.check_output(
                cmd, shell=True, stderr=subprocess.STDOUT, cwd=self.path, env=self.env)
        except subprocess.CalledProcessError as err:
            output = err.output
            exit_code = err.returncode
            print('ERROR MESSGE:', output)
            print('ERROR CODE:', exit_code)
        return output, exit_code

    def run_wait_for_status(self, cmd, status=None, interval=10, timeout=60):
        start = 0
        if status is not None:
            while ((start + interval) <= timeout):
                cmd_output = self.run(cmd)
                if status in cmd_output:
                    return cmd_output
                time.sleep(interval)
                start += interval
        return self.run(cmd)
