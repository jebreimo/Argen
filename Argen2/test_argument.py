import pytest
import argument


def test_find_commas():
    assert argument.find_commas("-a M,N, -b") == [6]
    assert argument.find_commas("-a M,N,-b") == [6]


def test_split_argument_text():
    assert argument.split_arguments("-a N, --abra=N") == [("-a", "N"), ("--abra", "N")]
    assert argument.split_arguments("-a N, --abra N") == [("-a", "N"), ("--abra", "N")]
    assert argument.split_arguments("-a, --abra N") == [("-a", None), ("--abra", "N")]
    assert argument.split_arguments("-a N --abra=N") == [("-a", "N"), ("--abra", "N")]
    assert argument.split_arguments("-a N --abra N") == [("-a", "N"), ("--abra", "N")]
    assert argument.split_arguments("-a --abra N") == [("-a", None), ("--abra", "N")]
    assert argument.split_arguments("-a X,Y,Z --abra=X,Y,Z") == [("-a", "X,Y,Z"), ("--abra", "X,Y,Z")]
    assert argument.split_arguments("/a X,Y,Z,/abra=X,Y,Z") == [("/a", "X,Y,Z"), ("/abra", "X,Y,Z")]
    assert argument.split_arguments("-=, --=N") == [("-=", None), ("--=N", None)]
    assert argument.split_arguments("-=, --foo= B") == [("-=", None), ("--foo=", "B")]


def test_find_metavar_separator():
    assert argument.find_metavar_separator("ABC") is None
    assert argument.find_metavar_separator("nxn") is None
    assert argument.find_metavar_separator("NxN") == "x"
    assert argument.find_metavar_separator("Ax:Bx:Cx") == ":"
    assert argument.find_metavar_separator("AB+") is None
    assert argument.find_metavar_separator("AB+CD") == "+"
    assert argument.find_metavar_separator("AB+CD...") == "+"
    assert argument.find_metavar_separator("AB+CD+...") == "+"
    assert argument.find_metavar_separator("AB+...") == "+"


def test_determine_metavar_type():
    f = lambda s: argument.determine_metavar_type(
                    s.split(),
                    argument.DEFAULT_METAVAR_TYPES)
    assert f("FLOAT") == "double"
    assert f("NUM1 NUM2") == "int"
    assert f("HEX1 HEX2") == "int"
    assert f("NUMBER FILE") == "std::string"


def test_parse_metavar_numbers_and_ellipsis():
    props = argument.parse_metavar("NUM1:NUM2...")
    assert props["separator"] == ":"
    assert props["type"] == "int"
    assert props["separator_count"] == "0..."
    assert props["meta_variable"] == "NUM1:NUM2..."


def test_parse_metavar_three_files():
    props = argument.parse_metavar("FILE1+FILE2+FILE3")
    assert props["separator"] == "+"
    assert props["type"] == "std::string"
    assert props["separator_count"] == "2"
    assert props["meta_variable"] == "FILE1+FILE2+FILE3"


def test_parse_flags():
    props = argument.parse_flags("-r MIN-MAX --range=MIN-MAX")
    assert props["flags"] == "-r --range"
    assert props["meta_variable"] == "MIN-MAX"


def test_get_argument_metavar_and_count():
    f = argument.get_argument_metavar_and_count
    assert f("<file>") == ("file", "1")
    assert f("[file]") == ("file", "0")
    assert f("[file ...]") == ("file", "0...")
    assert f("[file]...") == ("file", "0...")
    assert f("<file> ...") == ("file", "1...")
    assert f("file ...") == ("file", "1...")
    assert f("Xx,Yy,Z...") == ("Xx,Yy,Z...", "1")


def test_make_member_name():
    assert argument.make_member_name("_test") == "_test"
    assert argument.make_member_name("+test") == "test"
    assert argument.make_member_name("test_") == "test_"
    assert argument.make_member_name("test+=") == "test"
    assert argument.make_member_name("123test") == "_123test"
    assert argument.make_member_name("12+t-p_s**2") == "_12_t_p_s_2"
    assert argument.make_member_name("t_$_t") == "t_t"
    assert argument.make_member_name("foo faa") == "foo_faa"


def test_parse_argument_text():
    arg = argument.Argument("-")
    props = argument.parse_argument_text(arg)
    assert props["flags"] == "-"
