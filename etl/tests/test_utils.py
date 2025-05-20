from etl.transformer.utils import strip_flag

def test_strip_flag_basic():
    assert strip_flag("24G") == "24"
    assert strip_flag("-99.9*") == "-99.9"
    assert strip_flag("abc") == ""
