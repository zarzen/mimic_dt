from pssh.clients.native.single import SSHClient
import sys
import subprocess

class ExpCtl:
    
    def __init__(self, hosts):
        self.clients = []
        for h in hosts:
            self.clients.append(SSHClient(h))

    def update(self):
        cmd = "cd ~; ls | grep mimic_dt"
        for c in self.clients:
            _channel, _host, stdout, stderr, stdin = c.run_command(cmd, encoding="utf-8")
            c.wait_finished(_channel)
            output = _channel.read()
            if output[1] == b'':
                print('not exist; start cloning')
                clone_cmd = "cd ~; git clone git@github.com:zarzen/mimic_dt.git"
                self._exe_cmd(c, clone_cmd)
            else:
                print(output[1].decode('utf-8'))
    
    def run(self):
        """"""
        exp_cmd = "cd ~/mimic_dt; ./run.sh"
        subprocess.run(exp_cmd)
    
    def _exe_cmd(self, client, cmd):
        _channel, _host, stdout, stderr, stdin = client.run_command(cmd)
        for line in stdout:
            print(_host, ":", line)
        for line in stderr:
            print(_host, ":", line)
        
    def build(self):
        """"""
        self.update()
        build_cmd = "cd ~/mimic_dt; ./build.sh"
        for c in self.clients:
            self._exe_cmd(c, build_cmd)
    
    def __del__(self):
        kill_proc = "kill -9 $(nvidia-smi | sed -n 's/|\s*[0-9]*\s*\([0-9]*\)\s*.*/\1/p' | sort | uniq | sed '/^$/d')"
        for c in self.clients:
            self._exe_cmd(c, kill_proc)
        
def main():
    hosts = ['localhost', "172.31.29.187"]
    exp = ExpCtl(hosts)
    
    if len(sys.argv) < 2:
        print("specify commands: update/run")
    
    if sys.argv[1] == "update":
        exp.update()
    elif sys.argv[1] == "run":
        exp.run()
    elif sys.argv[1] == "build":
        exp.build()
    else:
        print('wrong command')


if __name__ == "__main__":
    main()