from __future__ import annotations

import ckan.plugins as p
import ckan.plugins.toolkit as tk

DEFAULT_ITEMS_PER_PAGE = 50


class ResourcePaginationPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        tk.add_template_directory(config_, "templates")

    # ITemplateHelpers

    def get_helpers(self):
        return {
            "paginate_resources": _paginate_resources,
            "resource_page_url": _resource_page_url,
        }


def _paginate_resources(resources: list) -> dict:
    """Compute pagination info and return sliced resources with metadata."""
    from flask import request

    total = len(resources)
    per_page = tk.asint(tk.config.get(
        "ckanext.resource_pagination.per_page", DEFAULT_ITEMS_PER_PAGE
    ))
    pages = max(1, (total + per_page - 1) // per_page)

    cur_page = request.args.get("resource_page", 1, type=int)
    cur_page = max(1, min(cur_page, pages))

    start = (cur_page - 1) * per_page
    end = min(start + per_page, total)

    return {
        "resources": resources[start:end],
        "page": cur_page,
        "per_page": per_page,
        "total": total,
        "pages": pages,
        "start": start + 1,
        "end": end,
    }


def _resource_page_url(page: int) -> str:
    """Build a URL for the given resource page, preserving other query params."""
    from flask import request

    args = dict(request.args)
    args["resource_page"] = page
    return request.path + "?" + "&".join(
        f"{k}={v}" for k, v in args.items()
    )
