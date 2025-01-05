import click
from .roboconfig import RoboConfig


@click.command()
@click.option(
    "--number", type=int, prompt="Install/Node number", help="Install/Node number."
)
@click.option("--tag", default=None, help="Config version")
@click.option(
    "--device",
    prompt="Device",
    type=click.Choice(
        ["HAPac2", "LiteBeam5AC", "LiteBeamLR", "Omnitik5AC", "SXTsq5AC"],
        case_sensitive=False,
    ),
)
@click.option("--template", default=None, help="Template file")
@click.option(
    "--param", default=[], help="Template parameters in format key:value", multiple=True
)
@click.option("--output", default=None, help="Output file")
@click.option("--ip", default="192.168.88.1", help="IP to scp the config to")
@click.option("--ssh", help="Deploy config via ssh", is_flag=True)
def main(number, tag, device, template, param, output, ip, ssh):
    c = RoboConfig()
    c.set_tag(tag)
    c.generate(device, template, param, number, output)


if __name__ == "__main__":
    main()
