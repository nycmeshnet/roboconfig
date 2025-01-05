from paramiko import SSHClient
from scp import SCPClient


def apply_mikrotik_config(ip, username, password, src, dst):
    with SSHClient() as ssh:
        ssh.load_system_host_keys()
        ssh.connect(ip, username=username, password=password, timeout=10)

        with SCPClient(ssh.get_transport()) as scp:
            scp.put(src, dst)

        ssh.exec_command(
            f"/system reset-configuration no-defaults=yes run-after-reset={dst}",
        )
