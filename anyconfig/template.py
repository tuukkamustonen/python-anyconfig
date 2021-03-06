#
# Jinja2 (http://jinja.pocoo.org) based template renderer.
#
# Author: Satoru SATOH <ssato redhat.com>
# License: MIT
#
import logging
import os

import anyconfig.compat

LOGGER = logging.getLogger(__name__)
SUPPORTED = False
try:
    import jinja2
    from jinja2.exceptions import TemplateNotFound

    SUPPORTED = True

    def tmpl_env(paths):
        return jinja2.Environment(loader=jinja2.FileSystemLoader(paths))

except ImportError:
    LOGGER.warn("Jinja2 is not available on your system, so "
                "template support will be disabled.")

    class TemplateNotFound(RuntimeError):
        pass

    def tmpl_env(*args):
        return None


def make_template_paths(template_file, paths=None):
    """
    :param template_file: Absolute or relative path to the template file
    :param paths: A list of template search paths

    >>> make_template_paths("/path/to/a/template")
    ['.', '/path/to/a']
    >>> make_template_paths("/path/to/a/template", ["/tmp", "."])
    ['/tmp', '.', '/path/to/a']
    """
    tmpldir = os.path.abspath(os.path.dirname(template_file))
    return [os.curdir, tmpldir] if paths is None else paths + [tmpldir]


def render_s(tmpl_s, ctx=None, paths=[os.curdir]):
    """
    Compile and render given template string `tmpl_s` with context `context`.

    :param tmpl_s: Template string
    :param ctx: Context dict needed to instantiate templates
    :param paths: Template search paths

    >>> s = render_s('a = {{ a }}, b = "{{ b }}"', {'a': 1, 'b': 'bbb'})
    >>> if SUPPORTED:
    ...     assert s == 'a = 1, b = "bbb"'
    """
    env = tmpl_env(paths)

    if env is None:
        return tmpl_s
    else:
        if ctx is None:
            ctx = {}

        return tmpl_env(paths).from_string(tmpl_s).render(**ctx)


def render_impl(template_file, ctx=None, paths=None):
    """
    :param template_file: Absolute or relative path to the template file
    :param ctx: Context dict needed to instantiate templates
    """
    env = tmpl_env(make_template_paths(template_file, paths))

    if env is None:
        return anyconfig.compat.copen(template_file).read()
    else:
        if ctx is None:
            ctx = {}

        return env.get_template(os.path.basename(template_file)).render(**ctx)


def render(filepath, ctx=None, paths=None, ask=False):
    """
    Compile and render template and return the result as a string.

    :param template_file: Absolute or relative path to the template file
    :param ctx: Context dict needed to instantiate templates
    :param paths: Template search paths
    :param ask: Ask user for missing template location if True
    """
    try:
        return render_impl(filepath, ctx, paths)
    except TemplateNotFound as mtmpl:
        if not ask:
            raise RuntimeError("Template Not found: " + str(mtmpl))

        usr_tmpl = anyconfig.compat.raw_input("\n*** Missing template "
                                              "'%s'. Please enter absolute "
                                              "or relative path starting from "
                                              "'.' to the template file: " %
                                              mtmpl)
        usr_tmpl = os.path.normpath(usr_tmpl.strip())
        paths = make_template_paths(usr_tmpl, paths)

        return render_impl(usr_tmpl, ctx, paths)

# vim:sw=4:ts=4:et:
