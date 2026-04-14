# ckanext-resource-pagination

A CKAN extension that adds pagination to the resource list on dataset pages.

CKAN renders every resource on a single page by default. For datasets with hundreds or thousands of resources, this crashes the browser and makes pages unusable. This plugin paginates the resource list with configurable page sizes and Bootstrap 5 navigation controls.

## Features

- Paginates the resource list on dataset detail pages (`/dataset/<id>`)
- Configurable number of resources per page (default: 50)
- Only processes visible resources (skips `resource_view_list` calls for off-page resources)
- Bootstrap 5 pagination controls with windowed page numbers
- "Showing X-Y of Z resources" counter
- Works with all dataset types
- No database changes or migrations required

## Requirements

- CKAN 2.11+
- Python 3.8+

## Installation

```bash
pip install ckanext-resource-pagination
```

Add `resource_pagination` to `ckan.plugins` in your `ckan.ini`:

```ini
ckan.plugins = ... resource_pagination
```

Restart CKAN.

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `ckanext.resource_pagination.per_page` | `50` | Number of resources to show per page |

Example:

```ini
ckanext.resource_pagination.per_page = 25
```

## How it works

The plugin registers a Flask blueprint via `IBlueprint` that intercepts the dataset read route (`/dataset/<id>`). The view:

1. Calls `package_show` to fetch the dataset (standard CKAN behavior)
2. Reads the `resource_page` query parameter from the URL
3. Slices the resources list to the configured page size
4. Only calls `resource_view_list` on visible resources
5. Passes pagination metadata to the template

The plugin also overrides `package/read.html` and `package/snippets/resources_list.html` to render the sliced resource list with pagination controls.

## License

AGPL-3.0
