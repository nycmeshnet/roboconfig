from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient


def apply_mikrotik_config(ip, username, password, src, dst):
    with SSHClient() as ssh:
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=10)

        with SCPClient(ssh.get_transport()) as scp:
            scp.put(src, dst)

        ssh.exec_command(
            f"/system reset-configuration no-defaults=yes run-after-reset={dst}",
        )


def apply_lbe_config(ip, username, password, src, dst):
    with SSHClient() as ssh:
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=10)

        ssh.exec_command(f"rm -f {dst}")
        with open(src, "r") as fd:
            for l in fd.readlines():
                ssh.exec_command(f"echo '{l}' >> {dst}")

        stdin, stdout, stderr = ssh.exec_command(
            f"cfgmtd -w -f {dst} && sleep 10 && reboot"
        )
        print(stdout.read())
        print(stderr.read())
