from __future__ import annotations

from typing import Union

from flask import Blueprint, request

import ckan.plugins.toolkit as tk
from ckan import model
from ckan.common import _, current_user, g
from ckan.lib import base
from ckan.logic import NotAuthorized, NotFound, get_action
from ckan.views.dataset import (
    _get_pkg_template,
    _setup_template_variables,
)

DEFAULT_ITEMS_PER_PAGE = 50


def get_blueprint() -> Blueprint:
    blueprint = Blueprint("resource_pagination", __name__, url_prefix="/dataset")
    blueprint.add_url_rule("/<id>", view_func=paginated_read)
    return blueprint


def paginated_read(id: str) -> Union[str, base.Response]:
    """Dataset read view with paginated resources.

    Mirrors ckan.views.dataset.read() but slices pkg_dict['resources']
    and only fetches resource_view_list for the visible page.
    """
    package_type = "dataset"
    context = {
        "user": current_user.name,
        "for_view": True,
        "auth_user_obj": current_user,
    }

    try:
        pkg_dict = get_action("package_show")(context, {"id": id})
        pkg = context["package"]
    except NotFound:
        return base.abort(404, _("Dataset not found or you have no permission to view it"))
    except NotAuthorized:
        if tk.config.get("ckan.auth.reveal_private_datasets"):
            if current_user.is_authenticated:
                return base.abort(403, _("Unauthorized to read package %s") % id)
            else:
                return tk.redirect_to(
                    "user.login",
                    came_from=tk.url_for("{}.read".format(package_type), id=id),
                )
        return base.abort(404, _("Dataset not found or you have no permission to view it"))

    g.pkg_dict = pkg_dict
    g.pkg = pkg

    # Redirect package id to package name
    if id == pkg_dict["id"] and id != pkg_dict["name"]:
        return tk.redirect_to("{}.read".format(package_type), id=pkg_dict["name"])

    # Activity redirect
    if tk.check_ckan_version(min_version="2.9"):
        activity_id = request.args.get("activity_id")
        if activity_id:
            return tk.redirect_to(
                "activity.package_history", id=id, activity_id=activity_id
            )

    # --- Pagination ---
    all_resources = pkg_dict.get("resources", [])
    total = len(all_resources)
    per_page = tk.asint(tk.config.get(
        "ckanext.resource_pagination.per_page", DEFAULT_ITEMS_PER_PAGE
    ))
    pages = max(1, (total + per_page - 1) // per_page)

    cur_page = request.args.get("resource_page", 1, type=int)
    if cur_page < 1:
        cur_page = 1
    if cur_page > pages:
        cur_page = pages

    start = (cur_page - 1) * per_page
    end = min(start + per_page, total)
    page_resources = all_resources[start:end]

    # Only fetch resource_view_list for visible resources
    for resource in page_resources:
        resource_views = get_action("resource_view_list")(
            context, {"id": resource["id"]}
        )
        resource["has_views"] = len(resource_views) > 0

    pkg_dict["resources"] = page_resources

    # Follow status
    try:
        am_following = get_action("am_following_dataset")(
            {"user": current_user.name}, {"id": id}
        )
    except NotAuthorized:
        am_following = False

    package_type = pkg_dict.get("type") or package_type
    _setup_template_variables(context, {"id": id}, package_type=package_type)
    template = _get_pkg_template("read_template", package_type)

    return base.render(
        template,
        {
            "dataset_type": package_type,
            "pkg_dict": pkg_dict,
            "am_following": am_following,
            "resource_pagination": {
                "page": cur_page,
                "per_page": per_page,
                "total": total,
                "pages": pages,
                "start": start + 1,
                "end": end,
            },
        },
    )
