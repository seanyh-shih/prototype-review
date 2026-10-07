"""欄位規格：範例檔都要通過；缺欄位、格式不對、混用格式要被擋下。"""
import copy
import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

from conftest import REPO, before_after_block, standard_block

TB = REPO / "core" / "blocks" / "topbanner"
SCHEMA = json.loads((TB / "block.schema.json").read_text(encoding="utf-8"))
V = Draft202012Validator(SCHEMA)


def errors(content):
    return list(V.iter_errors(content))


def test_schema_itself_is_valid():
    Draft202012Validator.check_schema(SCHEMA)


@pytest.mark.parametrize("name", ["example.yaml", "example.standard-video.yaml", "example.slider.yaml"])
def test_examples_validate(name):
    content = yaml.safe_load((TB / name).read_text(encoding="utf-8"))
    assert errors(content) == []


def test_before_after_ok():
    assert errors(before_after_block()) == []


def test_standard_ok():
    assert errors(standard_block()) == []


def test_missing_heading():
    b = before_after_block()
    del b["heading"]
    assert errors(b)


def test_unknown_variant():
    b = before_after_block()
    b["variant"] = "carousel"
    assert errors(b)


def test_standard_requires_poster_with_video():
    b = standard_block()
    del b["media"]["dt"]["poster"]
    assert errors(b)


def test_standard_requires_all_three_devices():
    b = standard_block()
    del b["media"]["mb"]
    assert errors(b)


def test_before_after_requires_both_images():
    b = before_after_block()
    del b["images"]["after"]["pd"]
    assert errors(b)


def test_cannot_mix_variants():
    b = before_after_block()
    b["media"] = standard_block()["media"]
    assert errors(b)


def test_max_two_ctas():
    b = before_after_block()
    b["ctas"] = b["ctas"] + [{"label": "Third", "href": "#"}]
    assert errors(b)


def test_slider_needs_two_slides_min():
    c = yaml.safe_load((TB / "example.slider.yaml").read_text(encoding="utf-8"))
    c = copy.deepcopy(c)
    c["slides"] = c["slides"][:1]
    assert errors(c)


def test_slider_has_no_upper_limit():
    c = yaml.safe_load((TB / "example.slider.yaml").read_text(encoding="utf-8"))
    c["slides"] = [copy.deepcopy(c["slides"][0]) for _ in range(8)]
    assert errors(c) == []
