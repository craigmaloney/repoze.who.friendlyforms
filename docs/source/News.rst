************************************
**repoze.who-friendlyform** releases
************************************

This document describes the releases of :mod:`repoze.who.plugins.friendlyform`.


.. _1.0b1:

**repoze.who-friendlyform** 1.0b1 (2009-02-17)
==============================================

This is the first release of **repoze.who-friendlyform** as an
independent project. The initial form plugin, 
:class:`repoze.who.plugins.friendlyform.FriendlyFormPlugin`, has been moved
from :class:`repoze.what.plugins.quickstart.FriendlyRedirectingFormPlugin`.

This new version of ``FriendlyRedirectingFormPlugin`` doesn't extends 
:class:`RedirectingFormPlugin <repoze.who.plugins.form.RedirectingFormPlugin>`
anymore. Instead, the relevant bits from the ``RedirectingFormPlugin`` have
been copied over, as recommended by Chris McDonough.

This new version of ``FriendlyRedirectingFormPlugin`` behaves exactly as the
original one.
