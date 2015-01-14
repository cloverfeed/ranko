"""
Glue between Flask and XStatic.
"""

from flask import send_from_directory
from xstatic.main import XStatic


class FlaskXStatic():
    def __init__(self, app):
        self.serve_files = {}

        @app.route('/xstatic/<xs_package>/<path:filename>')
        def xstatic(xs_package, filename):
            base_dir = self.serve_files[xs_package]
            return send_from_directory(base_dir, filename)

    def add_module(self, module_name):
        pkg = __import__('xstatic.pkg', fromlist=[module_name])
        module = getattr(pkg, module_name)
        xs = XStatic(module,
                     root_url='/xstatic',
                     provider='local',
                     protocol='http',
                     )
        self.serve_files[xs.name] = xs.base_dir

    def path_for(self, module_name):
        return self.serve_files[module_name]
