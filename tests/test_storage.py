import random

from card_identifier.storage import load_random_state, save_random_state


def test_save_random_state_writes_file_and_restores_state(tmp_path):
    random.seed(12345)
    save_random_state(tmp_path)
    expected_first = random.random()
    random.random()  # advance state
    load_random_state(tmp_path)
    restored = random.random()
    assert restored == expected_first
    pickle_path = tmp_path / "random_state.pickle"
    assert pickle_path.exists()
    assert pickle_path.stat().st_size > 0


def test_load_random_state_no_file_leaves_state_unchanged(tmp_path):
    random.seed(54321)
    state_before = random.getstate()
    load_random_state(tmp_path)
    assert random.getstate() == state_before
