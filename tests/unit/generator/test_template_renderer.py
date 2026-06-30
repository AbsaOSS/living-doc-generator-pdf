import pytest

from generator.template_renderer import TemplateError, TemplateRenderer


@pytest.fixture
def custom_template_dir(tmp_path):
    """Create a minimal self-contained custom template directory."""
    main = tmp_path / "main.html.jinja"
    main.write_text(
        "<html><body><h1>{{ meta.document_title }}</h1>"
        "<p>{{ data.message }}</p></body></html>",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def meta():
    return {
        "document_title": "My Title",
        "generated_at": "2024-01-01T00:00:00Z",
        "source_file": "data.json",
    }


def test_requires_template_path_or_document_type() -> None:
    """Constructor raises when neither template-path nor document-type is given."""
    with pytest.raises(TemplateError, match="Either template-path or document-type"):
        TemplateRenderer()


def test_missing_template_directory_raises() -> None:
    """Constructor raises when the custom template directory does not exist."""
    with pytest.raises(TemplateError, match="not found"):
        TemplateRenderer(template_path="/nonexistent/templates")


def test_unknown_document_type_raises() -> None:
    """Constructor raises when the built-in document type does not exist."""
    with pytest.raises(TemplateError, match="Built-in template set 'nope' not found"):
        TemplateRenderer(document_type="nope")


def test_render_custom_template(custom_template_dir, meta) -> None:
    """render uses data and meta from a custom template directory."""
    renderer = TemplateRenderer(template_path=str(custom_template_dir))
    html = renderer.render({"message": "hello"}, meta)

    assert "<h1>My Title</h1>" in html
    assert "hello" in html


def test_base_dir_points_to_custom_dir(custom_template_dir, meta) -> None:
    """base_dir returns the custom directory for asset resolution."""
    renderer = TemplateRenderer(template_path=str(custom_template_dir))
    assert renderer.base_dir == str(custom_template_dir)


def test_render_builtin_user_stories(meta) -> None:
    """render works with the built-in user-stories document type."""
    renderer = TemplateRenderer(document_type="user-stories")
    data = {"items": [{"id": "US-1", "title": "First", "acceptance_criteria": []}]}
    html = renderer.render(data, meta)

    assert "US-1" in html or "First" in html


def test_partial_override_prefers_custom(tmp_path, meta) -> None:
    """When both are given, a custom main.html.jinja overrides the built-in one."""
    (tmp_path / "main.html.jinja").write_text(
        "<html><body>CUSTOM {{ meta.document_title }}</body></html>",
        encoding="utf-8",
    )
    renderer = TemplateRenderer(template_path=str(tmp_path), document_type="user-stories")
    html = renderer.render({"items": []}, meta)

    assert "CUSTOM My Title" in html


def test_render_missing_main_template_raises(tmp_path, meta) -> None:
    """render raises TemplateError when main.html.jinja is missing."""
    (tmp_path / "other.html.jinja").write_text("nothing", encoding="utf-8")
    renderer = TemplateRenderer(template_path=str(tmp_path))

    with pytest.raises(TemplateError, match="not found"):
        renderer.render({}, meta)


def test_render_syntax_error_raises(tmp_path, meta) -> None:
    """render raises TemplateError on a template syntax error."""
    (tmp_path / "main.html.jinja").write_text("{% for x in %}", encoding="utf-8")
    renderer = TemplateRenderer(template_path=str(tmp_path))

    with pytest.raises(TemplateError, match="Syntax error"):
        renderer.render({}, meta)
