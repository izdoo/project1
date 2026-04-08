import ast
import os

from odoo import release
from odoo.modules import get_module_path
from .. import __manifest__


def is_enterprise():
    module_name = vars(__manifest__)['__name__'].split('.')[-2]
    mod_path = get_module_path(module_name)
    manifest_file = os.path.join(mod_path, "__manifest__.py")
    with open(manifest_file, mode="r", encoding="utf-8") as f:
        manifest_info = ast.literal_eval(f.read())

    return 'project_enterprise' in manifest_info['depends']


def get_odoo_major_version():
    return f"{release.version_info[0]}.0"

