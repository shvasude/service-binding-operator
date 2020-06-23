import subprocess,builtins


class Command(object):
    def __init__(self):
        self.cmd = None
        self.timeout = 5

    def run(self, cmd):
        try:
            self.output = subprocess.check_output(cmd,self.timeout,shell=True,stderr=subprocess.STDOUT,cwd=path)
        except subprocess.CalledProcessError as err:
            print('ERROR CODE:', err.returncode)
            print('ERROR MESSAGE:', err.output)
        else:
            return self.output.decode('utf-8')

    def cmd_timeout(command=None,timeout=60):
        p1 = subprocess.Popen(command, timeout, shell=True,stderr = subprocess.PIPE) 
        try:
            outs, errs = p1.communicate(timeout) 
        except subprocess.TimeoutExpired as e:
            p1.kill()
            outs, errs = p1.communicate()
            print(outs)
            print(errs)