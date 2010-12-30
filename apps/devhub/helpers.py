from collections import defaultdict

import jinja2
from jingo import register
from tower import ugettext as _, ungettext as ngettext

import amo
from amo.urlresolvers import reverse
from amo.helpers import breadcrumbs, page_title
from addons.helpers import new_context
from . import views


@register.inclusion_tag('devhub/addons/listing/items.html')
@jinja2.contextfunction
def dev_addon_listing_items(context, addons, src=None, notes={}):
    return new_context(**locals())


@register.function
@jinja2.contextfunction
def dev_page_title(context, title=None, addon=None):
    """Wrapper for devhub page titles."""
    if addon:
        title = u'%s :: %s' % (title, addon.name)
    else:
        devhub = _('Developer Hub')
        title = '%s :: %s' % (title, devhub) if title else devhub
    return page_title(context, title)


@register.function
@jinja2.contextfunction
def dev_breadcrumbs(context, addon=None, items=None, add_default=False):
    """
    Wrapper function for ``breadcrumbs``. Prepends 'Developer Hub'
    breadcrumbs.

    **items**
        list of [(url, label)] to be inserted after Add-on.
    **addon**
        Adds the Add-on name to the end of the trail.  If items are
        specified then the Add-on will be linked.
    **add_default**
        Prepends trail back to home when True.  Default is False.
    """
    crumbs = [(reverse('devhub.index'), _('Developer Hub'))]
    if not addon and not items:
        # We are at the end of the crumb trail.
        crumbs.append((None, _('My Add-ons')))
    else:
        crumbs.append((reverse('devhub.addons'), _('My Add-ons')))
    if addon:
        if items:
            url = reverse('devhub.addons.edit', args=[addon.slug])
        else:
            # The Addon is the end of the trail.
            url = None
        crumbs.append((url, addon.name))
    if items:
        crumbs.extend(items)
    return breadcrumbs(context, crumbs, add_default)


@register.function
def dev_files_status(files):
    """Group files by their status (and files per status)."""
    status_count = defaultdict(int)

    for file in files:
        status_count[file.status] += 1

    return [(count, unicode(amo.STATUS_CHOICES[status])) for
            (status, count) in status_count.items()]

@register.function
def status_class(addon):
    classes = {
        amo.STATUS_NULL: 'incomplete',
        amo.STATUS_UNREVIEWED: 'unreviewed',
        amo.STATUS_NOMINATED: 'nominated',
        amo.STATUS_PUBLIC: 'fully-approved',
        amo.STATUS_DISABLED: 'admin-disabled',
        amo.STATUS_LITE: 'lite',
        amo.STATUS_LITE_AND_NOMINATED: 'lite-nom',
        amo.STATUS_PURGATORY: 'purgatory',
    }
    if addon.disabled_by_user:
        cls = 'disabled'
    else:
        cls = classes.get(addon.status, 'none')
    return 'status-' + cls


@register.function
def can_edit_addon(request, addon):
    return views.can_edit(request, addon)


@register.function
def summarize_validation(validation):
    """Readable summary of add-on validation results."""
    # L10n: first parameter is the number of errors
    errors = ngettext('{0} error', '{0} errors',
                      validation.errors).format(validation.errors)
    # L10n: first parameter is the number of warnings
    warnings = ngettext('{0} warning', '{0} warnings',
                        validation.warnings).format(validation.warnings)
    return "%s, %s" % (errors, warnings)
