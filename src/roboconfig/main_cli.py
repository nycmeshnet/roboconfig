import click
from .roboconfig import RoboConfig
from .utils import apply_config_to_device


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
@click.option("--output", default="output.rsc", help="Output file")
@click.option("--deploy", help="Deploy config via ssh", is_flag=True)
def main(number, tag, device, template, param, output, deploy):
    c = RoboConfig()
    c.set_tag(tag)
    c.generate(device, template, param, number, output)

    try:
        if deploy:
            apply_config_to_device(device, output)
    except Exception as e:
        print(str(e))
        print("Failed to apply configuration")


if __name__ == "__main__":
    main()
