********************************************
**repoze.who.plugins.friendlyform** releases
********************************************

This document describes the releases of :mod:`repoze.who.plugins.friendlyform`.


.. _1.0b3:

Version 1.0b3 (2009-03-02)
==========================
* Renamed this project from ``repoze.who-friendlyform`` to
  :mod:`repoze.who.plugins.friendlyform` due to ugly problems with setuptools.

.. _1.0b2:

Version 1.0b2 (2009-02-20)
==========================

* Forced the login counter name in the query string to be ``'__logins'`` even 
  when ``login_counter_name`` is passed as ``None`` to
  :meth:`repoze.who.plugins.friendlyform.FriendlyFormPlugin.__init__`. The
  previous behavior was causing some weird problems on TG2 applications.


.. _1.0b1:

Version 1.0b1 (2009-02-17)
==========================

This is the first release of **repoze.who.plugins.friendlyform** as an
independent project. The initial form plugin, 
:class:`repoze.who.plugins.friendlyform.FriendlyFormPlugin`, has been moved
from :class:`repoze.what.plugins.quickstart.FriendlyRedirectingFormPlugin`.

This new version of ``FriendlyRedirectingFormPlugin`` doesn't extends 
:class:`RedirectingFormPlugin <repoze.who.plugins.form.RedirectingFormPlugin>`
anymore. Instead, the relevant bits from the ``RedirectingFormPlugin`` have
been copied over, as recommended by Chris McDonough.

This new version of ``FriendlyRedirectingFormPlugin`` behaves exactly as the
original one.
