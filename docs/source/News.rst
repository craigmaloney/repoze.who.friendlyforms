************************************
**repoze.who-friendlyform** releases
************************************

This document describes the releases of :mod:`repoze.who.plugins.friendlyform`.


.. _1.0.6:

Version 1.0.6 (2010-04-28)
==========================

* Restricted the plugin to identify and challenge to browser requests only. So
  it won't come into play if the client is a Subversion client, for example.


.. _1.0.5:

Version 1.0.5 (2010-04-22)
==========================

* Made the plugin return :class:`str` instead of :class:`unicode` when the request
  is made using ASCII.
* Added sample code to the documentation on how to use
  :class:`~repoze.who.plugins.friendlyform.FriendlyFormPlugin`, as suggested by
  Ian Stevens.


.. _1.0.1:

Version 1.0.1 (2010-01-29)
==========================

Added the ability to set another default character encoding for the credentials
in :class:`~repoze.who.plugins.friendlyform.FriendlyFormPlugin`.

Although ISO-8859-1 (aka "Latin-1") is the official default charset according to
the HTTP 1.1 specification (the one to be used when no encoding is explicitly
mentioned in the request), browsers (e.g., Firefox) don't set it even when
they use other encodings like UTF-8.

So, if you use a charset other than Latin-1, you should let the plugin know.

This has been `reported by Christoph Zwerschke
<http://trac.turbogears.org/ticket/2438#comment:6>`_.


.. _1.0:

Version 1.0 Final (2010-01-28)
==============================

Christoph Zwerschke made the
:class:`~repoze.who.plugins.friendlyform.FriendlyFormPlugin` support non-ASCII
credentials. Thank you Christoph!

It made no sense to do a release candidate because this has been the only bug
over the last year. Hence the "final" release.


.. _1.0b3:

Version 1.0b3 (2009-03-02)
==========================

* Specified the required version of :mod:`repoze.who`, otherwise the buggy
  setuptools won't install it.


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
