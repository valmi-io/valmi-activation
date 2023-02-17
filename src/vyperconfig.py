from vyper import v


def setup_vyper() -> None:
    v.set_config_type("yaml")
    v.set_config_name("config")
    v.add_config_path(".")
    v.read_in_config()
    v.automatic_env()
