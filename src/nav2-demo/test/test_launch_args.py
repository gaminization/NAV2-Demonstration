import re

LAUNCH = __import__("os").path.join(
    __import__("os").path.dirname(__file__), "..", "launch", "nav2-demo.launch.py"
)


def test_every_argument_used_is_declared():
    s = open(LAUNCH).read()
    used = set(re.findall(r"arg\('(\w+)'\)", s))
    declared = set(re.findall(r"declare\('(\w+)'", s))
    assert used <= declared, used - declared


def test_key_arguments_exist():
    s = open(LAUNCH).read()
    for name in (
        "world",
        "mode",
        "model",
        "nav_profile",
        "dynamic_obstacles",
        "record",
        "gpu",
        "security",
        "security_mode",
        "shutdown_on_done",
    ):
        assert f"declare('{name}'" in s, name
