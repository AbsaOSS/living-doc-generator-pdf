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


def test_render_builtin_technical_project(meta) -> None:
    """render works with the built-in technical-project document type."""
    renderer = TemplateRenderer(document_type="technical-project")
    data = {"items": [{"id": "US-1", "title": "First", "acceptance_criteria": []}]}
    html = renderer.render(data, meta)

    assert "US-1" in html or "First" in html


def test_partial_override_prefers_custom(tmp_path, meta) -> None:
    """When both are given, a custom main.html.jinja overrides the built-in one."""
    (tmp_path / "main.html.jinja").write_text(
        "<html><body>CUSTOM {{ meta.document_title }}</body></html>",
        encoding="utf-8",
    )
    renderer = TemplateRenderer(template_path=str(tmp_path), document_type="technical-project")
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


def _scenario(
    scenario_id: str,
    name: str,
    tags: list[str],
    ac_ids: list[str],
    us_id: str | None = "US-1",
    func_id: str | None = None,
) -> dict:
    """A ui-tests scenario, linked to US-1 by default, with the given tags and criteria."""
    return {
        "id": scenario_id,
        "us_id": us_id,
        "func_id": func_id,
        "ac_ids": ac_ids,
        "scenario_name": name,
        "scenario_type": "Scenario",
        "tags": tags,
        "steps": [],
        "source": {"org": "o", "repo": "r", "file": "features/a.feature", "line": 1},
    }


def _render_catalog_articles(meta, *scenarios: dict) -> dict[str, str]:
    """Render the built-in ui-test-catalog and return each scenario's article HTML by scenario name."""
    html = TemplateRenderer(document_type="ui-test-catalog").render({"items": list(scenarios)}, meta)
    articles = html.split('<article class="scenario">')[1:]
    return {name: next(a for a in articles if name in a) for name in (s["scenario_name"] for s in scenarios)}


@pytest.mark.parametrize(
    "us_id, func_id",
    [("US-1", None), (None, "F-1"), (None, None)],
    ids=["user-story", "functionality", "unlinked"],
)
def test_ui_test_catalog_skipped_scenario_lists_criteria_as_not_counted(meta, us_id, func_id) -> None:
    """A scenario tagged @skip is marked Skipped and lists its criteria as not counted, keeping its tags,
    in every catalog section."""
    articles = _render_catalog_articles(
        meta,
        _scenario("t-1", "Skipped one", ["@smoke", "@skip"], ["US-1-1", "US-1-2"], us_id, func_id),
        _scenario("t-2", "Active one", ["@smoke"], ["US-1-3"], us_id, func_id),
    )

    skipped = articles["Skipped one"]
    assert 'class="scenario-skipped">Skipped</span>' in skipped
    assert "Skipped, not counted:" in skipped
    assert "Covers:" not in skipped
    assert '<span class="ac-ref">US-1-1</span>' in skipped
    assert '<span class="ac-ref">US-1-2</span>' in skipped
    assert '<span class="tag">@skip</span>' in skipped

    active = articles["Active one"]
    assert "Covers:" in active
    assert "scenario-skipped" not in active
    assert "Skipped, not counted:" not in active


@pytest.mark.parametrize("tag", ["@Skip", "@SKIP", "@skip-ci", "skip"])
def test_ui_test_catalog_only_exact_skip_tag_marks_scenario(meta, tag: str) -> None:
    """Only the exact, case-sensitive @skip tag marks a scenario skipped, as the toolkit counts it."""
    article = _render_catalog_articles(meta, _scenario("t-1", "Look-alike", [tag], ["US-1-1"]))["Look-alike"]

    assert "Covers:" in article
    assert "scenario-skipped" not in article


def test_ui_test_catalog_skipped_scenario_without_criteria_shows_only_marker(meta) -> None:
    """A @skip scenario with no criteria gets the Skipped marker and no criteria line."""
    article = _render_catalog_articles(meta, _scenario("t-1", "Bare skip", ["@skip"], []))["Bare skip"]

    assert 'class="scenario-skipped">Skipped</span>' in article
    assert "Skipped, not counted:" not in article
    assert "Covers:" not in article
