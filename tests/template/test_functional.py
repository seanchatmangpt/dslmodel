from dslmodel.template import render_native


def test_render_native_integer():
    """Test that render_native correctly renders an integer from a template."""
    template_str = "{{ fake_random_int(min=10, max=100) }}"
    result = render_native(template_str)
    assert isinstance(result, int)
    assert 10 <= result <= 100


def test_render_native_list():
    """Test that render_native correctly renders a list from a template."""
    template_list = "['{{ fake_name() }}', '{{ fake_name() }}', '{{ fake_name() }}']"
    result = render_native(template_list)
    assert isinstance(result, list)
    assert len(result) == 3


def test_render_native_dict():
    """Test that render_native correctly renders a dictionary from a template."""
    template_dict = "{'name': '{{ fake_name() }}', 'job': '{{ fake_job() }}'}"
    result = render_native(template_dict)
    assert isinstance(result, dict)
    assert "name" in result and isinstance(result["name"], str)
    assert "job" in result and isinstance(result["job"], str)


def test_render_native_inflection_extension():
    """Test that render_native correctly renders with Inflection extensions."""
    template_str = "{{ 'person' | pluralize }}"
    result = render_native(template_str)
    assert result == "people"  # Plural of "person" is "people"
