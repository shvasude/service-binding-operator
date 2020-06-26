import subprocess
import time
import os
import sys


class Command(object):

    def __init__(self, path=None):
        if path is None:
            self.path = os.getcwd()
        else:
            self.path = path

    def run(self, cmd):
        exit_code = 0
        try:
            output = subprocess.check_output(
                cmd, shell=True, stderr=subprocess.STDOUT, cwd=self.path)
        except subprocess.CalledProcessError as err:
            print('ERROR CODE:', err.returncode)
            print('ERROR MESSAGE:', err.output)
            output = err.output

            print('exit code: {}'.format(err.returncode))
            exit_code = err.returncode
            print('stdout: {}'.format(
                err.output.decode(sys.getfilesystemencoding())))
            print('stderr: {}'.format(
                err.stderr.decode(sys.getfilesystemencoding())))

        else:
            return output.decode('utf-8'), exit_code

    def run_check_for_status(self, cmd, status=None, interval=10, timeout=60):
        start = 0
        if status is not None:
            while ((start + interval) <= timeout):
                cmd_output = self.run(cmd)
                if status in cmd_output:
                    return cmd_output
                time.sleep(interval)
                start += interval
        return self.run(cmd)

    def run_yaml(self, yaml):
        output = subprocess.check_output(
            "oc apply -f -", shell=True, stderr=subprocess.STDOUT, input=yaml.encode("utf-8"))
        return output.decode("utf-8")
