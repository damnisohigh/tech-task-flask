import os
import tempfile

import pandas as pd

from parser import read_file, validate_and_map, parse_file


def _write_tmp(content, suffix=".csv"):
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.write(fd, content)
    os.close(fd)
    return path


def test_read_file_valid_csv(app):
    with app.app_context():
        path = _write_tmp(b"Advertiser,Brand,Start,End,Format,Platform,Impr\nA,B,01.01.2023,31.01.2023,Banner,Web,100\n")
        df, err = read_file(path)
        os.unlink(path)
        assert err is None
        assert len(df) == 1
        assert "advertiser" in df.columns


def test_read_file_unsupported_format(app):
    with app.app_context():
        path = _write_tmp(b"some text", suffix=".txt")
        df, err = read_file(path)
        os.unlink(path)
        assert df is None
        assert "Unsupported" in err


def test_read_file_corrupted(app):
    with app.app_context():
        path = _write_tmp(b"\x00\x01\x02\x03", suffix=".xlsx")
        df, err = read_file(path)
        os.unlink(path)
        assert df is None
        assert "Failed to read" in err


def test_validate_matching_columns(app):
    with app.app_context():
        df = pd.DataFrame({
            "advertiser": ["A"],
            "brand": ["B"],
            "start": ["01.01.2023"],
            "end": ["31.01.2023"],
            "format": ["Banner"],
            "platform": ["Web"],
            "impr": [100],
        })
        result, err = validate_and_map(df)
        assert err is None
        assert len(result) == 1


def test_validate_missing_columns(app):
    with app.app_context():
        df = pd.DataFrame({"advertiser": ["A"], "brand": ["B"]})
        result, err = validate_and_map(df)
        assert result is None
        assert "Missing required columns" in err


def test_validate_extra_columns_ok(app):
    with app.app_context():
        df = pd.DataFrame({
            "advertiser": ["A"],
            "brand": ["B"],
            "start": ["01.01.2023"],
            "end": ["31.01.2023"],
            "format": ["Banner"],
            "platform": ["Web"],
            "impr": [100],
            "extra_col": ["ignored"],
        })
        result, err = validate_and_map(df)
        assert err is None
        assert "extra_col" not in result.columns


def test_validate_empty_file(app):
    with app.app_context():
        df = pd.DataFrame(columns=["advertiser", "brand", "start", "end", "format", "platform", "impr"])
        result, err = validate_and_map(df)
        assert result is None
        assert "no data rows" in err.lower()


def test_parse_file_success(app):
    with app.app_context():
        path = _write_tmp(b"Advertiser,Brand,Start,End,Format,Platform,Impr\nA,B,01.01.2023,31.01.2023,Banner,Web,100\n")
        df, err = parse_file(path)
        os.unlink(path)
        assert err is None
        assert len(df) == 1


def test_parse_file_failure(app):
    with app.app_context():
        path = _write_tmp(b"wrong,columns\n1,2\n")
        df, err = parse_file(path)
        os.unlink(path)
        assert df is None
        assert err is not None
