import pytest

from app.curriculum.directives import DirectiveError, parse


def test_markdown_and_blocks_are_split_in_order():
    blocks = parse(
        '# Title\n\nintro\n\n:::concept title="x"\nbody **bold**\n:::\n\n'
        ':::quiz id="q1":::\nafter\n'
    )
    assert [b.type for b in blocks] == ["markdown", "concept", "quiz", "markdown"]
    assert blocks[1].attrs == {"title": "x"}
    assert blocks[1].body == "body **bold**"
    assert blocks[2].attrs == {"id": "q1"} and blocks[2].body == ""
    assert blocks[1].line == 5


def test_code_body_keeps_indentation():
    (block,) = parse(':::code mode="notebook"\nfor i in range(2):\n    print(i)\n:::')
    assert block.body == "for i in range(2):\n    print(i)"
    assert block.attrs["mode"] == "notebook"


def test_unclosed_directive_raises():
    with pytest.raises(DirectiveError, match="never closed"):
        parse(":::concept\nno end")


def test_stray_closing_fence_raises():
    with pytest.raises(DirectiveError, match="without an opening"):
        parse("text\n:::\n")


def test_nested_directive_raises():
    with pytest.raises(DirectiveError, match="inside"):
        parse(":::concept\n:::tip\nx\n:::\n:::")
