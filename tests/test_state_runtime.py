from father_fua.state_runtime import State, state_hash, transition


def test_state_transition_monotonic():
    s=State(0,"S1","CREATED")
    n=transition(s,"RUNNING")
    assert n.revision==1
    assert state_hash(s)!=state_hash(n)
