import subprocess,builtins,pdb,time

class Command(object):

    def run(self, cmd):
        try:
            output = subprocess.check_output(cmd,shell=True,stderr=subprocess.STDOUT,cwd=path)
        except subprocess.CalledProcessError as err:
            print('ERROR CODE:', err.returncode)
            print('ERROR MESSAGE:', err.output)

            print('exit code: {}'.format(err.returncode))
            print('stdout: {}'.format(err.output.decode(sys.getfilesystemencoding())))
            print('stderr: {}'.format(err.stderr.decode(sys.getfilesystemencoding())))

        else:
            return output.decode('utf-8')

    def run_check_for_status(self, cmd, status=None, interval=10, timeout=60):
        start = 0
        if status != None:
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