from __future__ import annotations

import ckan.plugins as p
import ckan.plugins.toolkit as tk

from . import views


class ResourcePaginationPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)
    p.implements(p.IConfigurer)
    p.implements(p.ITemplateHelpers)

    # IBlueprint

    def get_blueprint(self):
        return views.get_blueprint()

    # IConfigurer

    def update_config(self, config_):
        tk.add_template_directory(config_, "templates")

    # ITemplateHelpers

    def get_helpers(self):
        return {
            "resource_page_url": _resource_page_url,
        }


def _resource_page_url(page: int) -> str:
    """Build a URL for the given resource page, preserving other query params."""
    from flask import request

    args = dict(request.args)
    args["resource_page"] = page
    return request.path + "?" + "&".join(
        f"{k}={v}" for k, v in args.items()
    )
