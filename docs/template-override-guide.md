# Template Override Guide

This guide explains how to customize the PDF output of the Living Doc Generator
PDF action using Jinja2 templates.

## Concepts

- **Entry point.** Rendering always starts from `main.html.jinja`. Every other
  template file is a partial that `main.html.jinja` includes.
- **Template context.** Templates receive exactly two variables:
  - `data` — the raw parsed JSON source, unchanged.
  - `meta` — injected metadata with three fields:
    - `document_title` — the resolved cover title.
    - `generated_at` — ISO 8601 UTC timestamp (e.g. `2024-01-01T12:00:00Z`).
    - `source_file` — the basename of the source file.
- **Assets.** Relative URLs in templates (CSS, images, fonts) resolve against the
  primary template directory (`base_url`). For a custom directory, that is your
  directory; for a built-in set, it is the set's folder.

## The three override levels

### 1. Built-in only

Use a shipped template set; provide no custom templates.

```yaml
with:
  source-path: doc-source.json
  document-type: user-stories
```

### 2. Custom only (full override)

Provide a self-contained directory. It **must** contain `main.html.jinja`, plus
any partials it includes and the CSS it references.

```yaml
with:
  source-path: doc-source.json
  template-path: templates/my-pack
```

### 3. Partial override

Provide both a custom directory and a built-in type. Your files take precedence;
any partial you do not provide falls back to the built-in set.

```yaml
with:
  source-path: doc-source.json
  document-type: user-stories
  template-path: templates/my-overrides   # e.g. only cover.html.jinja
```

## Copying a built-in set

The simplest way to build a full custom pack is to copy a built-in set and edit
it. The built-in sets live under `generator/templates/<document-type>/`:

```bash
cp -r generator/templates/user-stories templates/my-pack
# edit templates/my-pack/*.jinja and styles.css
```

Then point the action at it with `template-path: templates/my-pack`.

## Available Jinja filters

| Filter | Signature | Purpose |
|--------|-----------|---------|
| `markdown` | `markdown(text)` | Convert Markdown to HTML. Pair with `\| safe`. |
| `format_datetime` | `format_datetime(value, fmt='%Y-%m-%d %H:%M')` | Format an ISO 8601 timestamp. |
| `default_if_none` | `default_if_none(value, fallback='')` | Replace `None` with a fallback. |
| `natural_sort` | `natural_sort(items, attribute=None)` | Natural ordering so `US-2` precedes `US-10`. |

### Examples

```jinja
{# Cover #}
<h1>{{ meta.document_title }}</h1>
<p>Generated {{ meta.generated_at | format_datetime('%B %d, %Y') }}</p>
<p>Source: {{ meta.source_file }}</p>

{# Body, ID-ordered #}
{% for item in data.get('items', []) | natural_sort(attribute='id') %}
  <section id="{{ item.id.split('/') | last }}">
    <h2>{{ item.id }} — {{ item.title }}</h2>
    <div>{{ item.description | default_if_none('') | markdown | safe }}</div>
  </section>
{% endfor %}
```

## Best practices

- Order chapters by ID using `natural_sort` so numbering is human-friendly.
- Give each chapter a stable anchor `id` and place a Table of Contents after the
  cover that links to those anchors.
- Insert page breaks between chapters via CSS (e.g. `page-break-before: always`).
- Keep styling in `styles.css`; avoid inline `style="..."` attributes.
- Use `| safe` only on trusted, filter-produced HTML (e.g. the `markdown` output).

## Troubleshooting

**`Template error: Template 'main.html.jinja' not found`**
Your custom directory is missing the entry point. Add `main.html.jinja`, or also
set `document-type` so the built-in entry point is used.

**A partial include fails (e.g. `cover.html.jinja` not found)**
When using a custom-only pack, every `{% include %}` target must exist in your
directory. Either add the missing partial or switch to a partial override by also
setting `document-type`.

**`Template error: Syntax error in '<file>' at line N`**
A Jinja tag is malformed (unclosed `{% %}` or `{{ }}`). Fix the indicated line.

**Assets (CSS/images) do not appear in the PDF**
Use relative paths and place the asset inside your template directory so it
resolves against `base_url`.

**Markdown shows raw `**` or `#` characters**
Pipe the value through `| markdown | safe`. Without `markdown`, the text is
emitted verbatim; without `safe`, the generated HTML is escaped.
