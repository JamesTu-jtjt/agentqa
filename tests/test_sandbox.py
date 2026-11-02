import json
import os

import pytest

from agentqa.sandbox import DockerWorker


def test_image_must_be_pinned():
    with pytest.raises(ValueError):
        DockerWorker("python:latest")


@pytest.mark.parametrize("kwargs", [{"timeout": 0}, {"output_limit": 0}, {"timeout": 100}])
def test_bad_limits_fail_before_launch(kwargs):
    with pytest.raises(ValueError):
        DockerWorker().run("print('x')", **kwargs)


live = pytest.mark.skipif(os.environ.get("AGENTQA_DOCKER_TESTS") != "1",
                          reason="Explicit Docker integration opt-in required")


@live
def test_container_has_no_host_mount_credentials_or_external_network():
    result = DockerWorker().run('''
import json, os, pathlib, socket
facts = {"uid": os.getuid(), "docker_socket": pathlib.Path("/var/run/docker.sock").exists(),
         "host_users": pathlib.Path("/Users").exists(), "secret": os.environ.get("AGENTQA_HOST_SENTINEL")}
try:
    pathlib.Path("/etc/agentqa-probe").write_text("x")
    facts["readonly"] = False
except OSError:
    facts["readonly"] = True
pathlib.Path("/workspace/ok").write_text("local task data")
try:
    socket.create_connection(("1.1.1.1", 443), timeout=0.3)
    facts["network"] = True
except OSError:
    facts["network"] = False
print(json.dumps(facts))
''', timeout=20)
    assert result.status == "completed", result
    assert result.cleanup_confirmed
    assert result.startup_seconds is not None
    assert result.failure_phase is None
    assert json.loads(result.output) == {"uid": 65534, "docker_socket": False,
                                        "host_users": False, "secret": None,
                                        "readonly": True, "network": False}


@live
def test_container_timeout_is_cleaned_up():
    result = DockerWorker().run("import time; time.sleep(30)", timeout=2)
    assert result.status == "timeout", result
    assert result.failure_phase == "execution"
    assert result.cleanup_confirmed


@live
def test_container_output_is_bounded_and_cleaned_up():
    result = DockerWorker().run("print('x' * 100000)", output_limit=1000, timeout=20)
    assert result.status == "output_limit", result
    assert result.failure_phase == "execution"
    assert len(result.output) == 1000
    assert result.cleanup_confirmed
