import subprocess,builtins,pdb

class Command(object):

    def run(self, cmd):
        try:
            output = subprocess.check_output(cmd,shell=True,stderr=subprocess.STDOUT,cwd=path)
        except subprocess.CalledProcessError as err:
            print('ERROR CODE:', err.returncode)
            print('ERROR MESSAGE:', err.output)
        else:
            return output.decode('utf-8')

    def run_check_for_status(self, cmd, status=None, interval=10, timeout=60):
        pdb.set_trace()
        start = 0
        if status != None:
            while ((start + interval) <= timeout):
                cmd_output = self.run(cmd)
                if status in cmd_output:
                    return cmd_output
                time.sleep(interval)
                start += interval                
        return self.run(cmd)

