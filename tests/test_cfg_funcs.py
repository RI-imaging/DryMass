import numpy as np

from drymass import cfg_funcs


def test_fbool():
    assert isinstance(cfg_funcs.fbool("true"), bool)
    assert isinstance(cfg_funcs.fbool("True"), bool)
    assert isinstance(cfg_funcs.fbool("false"), bool)
    assert isinstance(cfg_funcs.fbool("False"), bool)
    assert isinstance(cfg_funcs.fbool("1"), bool)
    assert isinstance(cfg_funcs.fbool("1."), bool)
    assert isinstance(cfg_funcs.fbool("0"), bool)
    assert isinstance(cfg_funcs.fbool("0."), bool)
    assert isinstance(cfg_funcs.fbool(1.0), bool)
    assert isinstance(cfg_funcs.fbool(1), bool)
    assert isinstance(cfg_funcs.fbool(0.0), bool)
    assert isinstance(cfg_funcs.fbool(0), bool)
    assert cfg_funcs.fbool("true")
    assert cfg_funcs.fbool("True")
    assert cfg_funcs.fbool("1")
    assert cfg_funcs.fbool("1.")
    assert cfg_funcs.fbool(1.)
    assert cfg_funcs.fbool(1)
    assert not cfg_funcs.fbool("false")
    assert not cfg_funcs.fbool("False")
    assert not cfg_funcs.fbool("0.")
    assert not cfg_funcs.fbool("0")
    assert not cfg_funcs.fbool(0)
    assert not cfg_funcs.fbool(0.)

    try:
        cfg_funcs.fbool("")
    except ValueError:
        pass
    else:
        assert False, "emtpy string"


def test_fintlist():
    assert cfg_funcs.fintlist("1, 2, 3") == [1, 2, 3]
    assert cfg_funcs.fintlist("1.1, 2.1, 3.1") == [1, 2, 3]
    assert cfg_funcs.fintlist([1, 2, 3]) == [1, 2, 3]
    assert cfg_funcs.fintlist([1.1, 2.1, 3.1]) == [1, 2, 3]


def test_float01():
    assert cfg_funcs.float01(.03) == .03

    try:
        cfg_funcs.float01(1.03)
    except ValueError:
        pass
    else:
        assert False

    try:
        cfg_funcs.float01(-1.03)
    except ValueError:
        pass
    else:
        assert False


def test_float_or_str():
    assert np.isnan(cfg_funcs.float_or_str("nan"))
    assert isinstance(cfg_funcs.float_or_str("1.1"), float)
    assert isinstance(cfg_funcs.float_or_str(1), float)
    assert isinstance(cfg_funcs.float_or_str(False), float)
    assert cfg_funcs.float_or_str("1.1") == 1.1
    assert cfg_funcs.float_or_str("1.1b") == "1.1b"
    assert cfg_funcs.float_or_str("1.1e-5") == 1.1e-5


def test_float_tuple_or_one():
    assert cfg_funcs.floattuple_or_one("1") == 1
    assert cfg_funcs.floattuple_or_one("+1") == 1
    assert cfg_funcs.floattuple_or_one("-1") == -1
    assert cfg_funcs.floattuple_or_one(1) == 1
    assert cfg_funcs.floattuple_or_one(-1) == -1
    assert cfg_funcs.floattuple_or_one(1.0) == 1
    assert cfg_funcs.floattuple_or_one(-1.0) == -1
    assert np.allclose(cfg_funcs.floattuple_or_one([1, 2]), [1, 2])
    assert np.allclose(cfg_funcs.floattuple_or_one(["1", "2"]), [1, 2])
    assert np.allclose(cfg_funcs.floattuple_or_one("1.0, 2"), [1, 2])
    assert np.allclose(cfg_funcs.floattuple_or_one((1, 2)), [1, 2])
    assert np.allclose(cfg_funcs.floattuple_or_one([1.2, 2.9]), [1.2, 2.9])
    assert np.allclose(cfg_funcs.floattuple_or_one(np.array([1, 2])), [1, 2])

    try:
        cfg_funcs.floattuple_or_one("1,2,3,4")
    except ValueError:
        pass
    else:
        assert False

    try:
        cfg_funcs.floattuple_or_one("nan")
    except ValueError:
        pass
    else:
        assert False

    try:
        cfg_funcs.floattuple_or_one(2)
    except ValueError:
        pass
    else:
        assert False


def test_int_or_str():
    assert isinstance(cfg_funcs.int_or_str("1.1"), int)
    assert isinstance(cfg_funcs.int_or_str(1), int)
    assert isinstance(cfg_funcs.int_or_str(False), int)
    assert cfg_funcs.int_or_str("1.1") == 1
    assert cfg_funcs.int_or_str("1.1b") == "1.1b"
    assert cfg_funcs.int_or_str("2") == 2


def test_lcstr():
    assert cfg_funcs.lcstr("ASD") == "asd"


def test_tupletupleint():
    assert cfg_funcs.tupletupleint("") == ()
    assert cfg_funcs.tupletupleint("[(1, 2), (3, 4)]") == ((1, 2), (3, 4))
    assert cfg_funcs.tupletupleint("1, 2, 3, 4") == ((1, 2), (3, 4))
    assert cfg_funcs.tupletupleint("1.1, 2.1, 3.1, 4.1") == ((1, 2), (3, 4))
    assert cfg_funcs.tupletupleint(()) == ()
    assert cfg_funcs.tupletupleint([]) == ()
    assert cfg_funcs.tupletupleint([(1, 2), (3, 4)]) == ((1, 2), (3, 4))
    assert cfg_funcs.tupletupleint([(1.1, 2.0), (3.0, 4)]) == ((1, 2), (3, 4))


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
