from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient


def apply_config_to_device(device, local_config_file):
    if device == "Omnitik5AC" or device == "HAPac2":
        apply_mikrotik_config(
            "192.168.88.1",
            "admin",
            "",
            local_config_file,
            "flash/roboconfig_generated.rsc",
        )
    elif device == "LiteBeam5AC" or device == "LiteBeamLR":
        apply_lbe_config(
            "192.168.1.20",
            "ubnt",
            "ubnt",
            local_config_file,
            "/var/etc/persistent/roboconfig_generated.rsc",
        )


def apply_mikrotik_config(ip, username, password, src, dst):
    with SSHClient() as ssh:
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=10)

        with SCPClient(ssh.get_transport()) as scp:
            scp.put(src, dst)

        stdin, stdout, stderr = ssh.exec_command(
            f"/system reset-configuration no-defaults=yes run-after-reset={dst}",
        )
        print(stdout.read())
        print(stderr.read())


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
