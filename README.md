# ckanext-resource-pagination

Paginate resources on CKAN dataset pages. Prevents browser crashes on datasets with thousands of resources by showing 50 per page with navigation controls.

## Requirements

- CKAN 2.11+
- Python 3.8+

## Installation

```bash
pip install ckanext-resource-pagination
```

Or from source:

```bash
pip install -e git+https://github.com/tanmayagrawal21/ckanext-resource-pagination.git#egg=ckanext-resource-pagination
```

## Configuration

Add `resource_pagination` to `ckan.plugins` in your `ckan.ini`:

```ini
ckan.plugins = ... resource_pagination
```

No other configuration needed.

## How it works

The plugin overrides the dataset read view (`/dataset/<id>`) to:

1. Fetch the dataset via `package_show` (standard CKAN behavior)
2. Slice the resources list to 50 items based on the `resource_page` URL parameter
3. Only call `resource_view_list` on the visible 50 resources (not all of them)
4. Pass pagination metadata to the template for rendering page controls

This means a dataset with 11,000 resources loads as fast as one with 20.

## License

AGPL-3.0
