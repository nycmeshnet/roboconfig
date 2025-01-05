import re
from .roboconfig import RoboConfig
from .utils import apply_mikrotik_config
from .tplink import tplink_setup


def _get_value_console(prompt, constraint):
    while True:
        user_input = input(f"{prompt}: ")
        if len(user_input) > 0 and re.match(constraint, user_input):
            return user_input


def _select_value_console(prompt, options):
    output = f"{prompt} "
    for i, op in enumerate(options):
        output += f"[{i+1}] {op} "
    output = f"{output[:-1]}: "

    while True:
        user_input = input(output)
        if (
            user_input.isdigit()
            and int(user_input) > 0
            and int(user_input) <= len(options)
        ):
            return options[int(user_input) - 1]


def main():
    local_config_file = "output.rsc"
    c = RoboConfig()

    possible_devices = ["ArcherA6", "Omnitik5AC"]#"LiteBeam5AC", "LiteBeamLR", "SXTsq5AC", "HAPac2"]
    device = _select_value_console("Enter device", possible_devices)

    if device == "ArcherA6":
        tplink_setup()
    else:
        possible_tags = c.get_tag_options()
        tag = _select_value_console("Enter config version", possible_tags)
        c.set_tag(tag)

        number = int(_get_value_console("Enter install/node number", "^[0-9]+$"))

        possible_templates = c.get_template_options(device)
        if len(possible_templates) > 0:
            template = _select_value_console("Enter template", possible_templates)
        else:
            template = possible_templates[0]

        c.generate(device, template, {}, number, local_config_file)

        print("Applying config to device")
        try:
            apply_mikrotik_config(
                "192.168.88.1",
                "admin",
                "",
                local_config_file,
                "flash/roboconfig_generated.rsc",
            )
        except:
            print("Failed to apply configuration")
            return
        print("Rebooting")


if __name__ == "__main__":
    main()
