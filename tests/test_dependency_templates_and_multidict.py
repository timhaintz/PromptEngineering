"""Offline security boundaries for fsspec and the native multidict backend."""

import gc
import json
import sys
from uuid import uuid4

import pytest


_UNSAFE_TEMPLATE = "{{ ''.__class__.__mro__|length }}"


def _reference(document, **options):
    from fsspec.implementations.reference import ReferenceFileSystem

    return ReferenceFileSystem(
        fo=document, remote_protocol="memory", simple_templates=False,
        skip_instance_cache=True, **options,
    )


@pytest.mark.parametrize("field", ["key", "url", "offset", "length"])
def test_fsspec_generator_templates_reject_object_introspection(field):
    from jinja2.exceptions import SecurityError

    generator = {
        "key": "chunk/{{ i }}", "url": "memory://data",
        "offset": "0", "length": "2", "dimensions": {"i": [0]},
    }
    generator[field] = _UNSAFE_TEMPLATE
    with pytest.raises(SecurityError):
        _reference({"version": 1, "refs": {}, "gen": [generator]})


@pytest.mark.parametrize("representation", ["inline", "json_file"])
def test_fsspec_reference_templates_are_sandboxed(representation, tmp_path):
    from jinja2.exceptions import SecurityError

    document = {
        "version": 1, "templates": {"base": "memory://"},
        "refs": {"data": [_UNSAFE_TEMPLATE]},
    }
    if representation == "json_file":
        filename = tmp_path / "references.json"
        filename.write_text(json.dumps(document))
        document = str(filename)
    with pytest.raises(SecurityError):
        _reference(document)


def test_fsspec_template_helpers_are_sandboxed():
    from jinja2.exceptions import SecurityError

    with pytest.raises(SecurityError):
        _reference({
            "version": 1, "templates": {"hostile": _UNSAFE_TEMPLATE},
            "refs": {"data": ["{{ hostile() }}"]},
        })


def test_fsspec_memory_ranges_and_inline_data_remain_usable():
    import fsspec

    memory = fsspec.filesystem("memory")
    filename = "/offline-" + uuid4().hex
    memory.pipe(filename, b"abcdef")
    try:
        references = _reference({
            "version": 1,
            "refs": {"inline": "abc", "range": ["memory://" + filename, 2, 3]},
        })
        assert references.cat_file("inline") == b"abc"
        assert references.cat_file("range") == b"cde"
    finally:
        memory.rm(filename)


def test_fsspec_explicit_generator_preserves_normal_substitution():
    references = _reference({
        "version": 1, "refs": {},
        "gen": [{
            "key": "chunk/{{ i }}", "url": "memory://data",
            "offset": "{{ i * 2 }}", "length": "2", "dimensions": {"i": [0, 1]},
        }],
    })
    assert references.references == {
        "chunk/0": ["memory://data", 0, 2], "chunk/1": ["memory://data", 2, 2],
    }


@pytest.mark.parametrize("class_name", ["MultiDict", "CIMultiDict"])
@pytest.mark.parametrize("operation", ["reflected_union", "subtraction", "union", "intersection"])
def test_multidict_native_items_operations_release_operand_references(class_name, operation):
    import multidict

    dictionary_class = getattr(multidict, class_name)
    # CPython CI and the supported Mac must exercise the affected C extension.
    assert dictionary_class.__module__ == "multidict._multidict"
    dictionary = dictionary_class({"seed": "value"})
    value = object()
    operand = [(f"key{i}", value) for i in range(50)]
    gc.collect()
    before = sys.getrefcount(value)
    if operation == "reflected_union":
        result = operand | dictionary.items()
        assert len(result) == 51
    elif operation == "subtraction":
        result = dictionary.items() - operand
        assert result == {("seed", "value")}
    elif operation == "union":
        result = dictionary.items() | operand
        assert len(result) == 51
    else:
        result = dictionary.items() & operand
        assert result == set()
    del result
    gc.collect()
    assert sys.getrefcount(value) == before


def test_multidict_preserves_duplicate_headers_and_case_semantics():
    from multidict import CIMultiDict, MultiDict

    headers = CIMultiDict([("X-Trace", "one"), ("x-trace", "two")])
    assert headers.getall("X-TRACE") == ["one", "two"]
    query = MultiDict([("key", "one"), ("key", "two"), ("Key", "three")])
    assert query.getall("key") == ["one", "two"]
    assert query["Key"] == "three"
