from headroom.adaptive_policy import AdaptivePolicy, get_global_policy


def test_defaults_are_task_aware():
    policy = AdaptivePolicy()
    assert policy.get_level("json", "search") == 0.20
    assert policy.get_level("json", "debug") == 0.70
    assert policy.get_level("code", "debug") > policy.get_level("code", "search")


def test_runtime_update_and_snapshot():
    policy = AdaptivePolicy()
    policy.set_level("json", "debug", 0.60)
    assert policy.get_level("json", "debug") == 0.60
    snapshot = policy.snapshot()
    snapshot["json_debug"] = 0.10
    assert policy.get_level("json", "debug") == 0.60


def test_unknown_task_uses_fallback():
    policy = AdaptivePolicy()
    assert policy.get_level("image", "search", fallback=0.35) == 0.35


def test_invalid_ratio_rejected():
    policy = AdaptivePolicy()
    for value in (0, -0.1, 1.1):
        try:
            policy.set_level("json", "search", value)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid ratio was accepted")


def test_global_policy_is_shared():
    assert get_global_policy() is get_global_policy()
