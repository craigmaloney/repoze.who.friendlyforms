*****************************************************
Collection of :mod:`repoze.who` friendly form plugins
*****************************************************

:Author: Gustavo Narea.
:Latest release: |release|

.. module:: repoze.who.plugins.friendlyform
    :synopsis: Developer-friendly repoze.who form plugins
.. moduleauthor:: Gustavo Narea <me@gustavonarea.net>

.. topic:: Overview

    **repoze.who-friendlyform** is a :mod:`repoze.who` plugin which provides
    a collection of developer-friendly form plugins, although for the time
    being such a collection has only one item.


How to install
==============

The minimum requirement is :mod:`repoze.who`, and you can install both with
``easy_install``::
    
    easy_install repoze.who-friendlyform


Available form plugins
======================

.. autoclass:: FriendlyFormPlugin
    :members: __init__


:class:`FriendlyFormPlugin` examples
------------------------------------

When you use this plugin, you would implement a controller action for logins,
like this one::

    # You have to adapt this function to the way things work in your framework:
    
    def login(request):
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            display_message("Wrong credentials", status="error")
        came_from = request.params.get("came_from") or "/"
        return render("login.html", login_counter=login_counter, came_from=came_from)

Where the "login.html" template is defined as:

.. code-block:: html

    <!-- Adapt this code to your templating engine -->
    <form action="/login_handler?came_from={{ came_from }}&amp;__logins={{ login_counter }}"
          method="POST">
      <label>Username: <input type="text" name="login"/></label>
      <label>Password: <input type="password" name="password"/></label>
      <input type="submit" value="Login"/>
    </form>


Post-login action
~~~~~~~~~~~~~~~~~

A controller action for post-logins could look like::

    # You have to adapt this function to the way things work in your framework:
    
    def welcome_back(request):
        identity = request.environ.get("repoze.who.identity")
        came_from = request.params.get('came_from', '') or "/"
        
        if identity:
            # Login succeeded
            userid = identity['repoze.who.userid']
            display_message('Welcome back, %s!' % userid, status="success")
            destination = came_from
        else:
            # Login failed
            login_counter = request.environ['repoze.who.logins'] + 1
            destination = "/login?came_from=%s&__logins=%s" % (came_from, login_counter)
        
        return Redirect(destination)


Post-logout action
~~~~~~~~~~~~~~~~~~

A controller action for post-logouts could look like::

    # You have to adapt this function to the way things work in your framework:
    
    def see_you_later(request):
        display_message("We hope to see you soon!", status="success")
        came_from = request.params.get('came_from', '') or "/"
        return Redirect(came_from)


Support and development
=======================

The prefered place to ask questions is the `Repoze mailing list 
<http://lists.repoze.org/listinfo/repoze-dev>`_ or the `#repoze 
<irc://irc.freenode.net/#repoze>`_ IRC channel. Bugs reports and feature 
requests should be sent to `the issue tracker of the Repoze project 
<http://bugs.repoze.org/>`_.

The development mainline is available at the following Subversion repository::

    http://svn.repoze.org/whoplugins/whofriendlyforms/trunk/


Releases
--------

.. toctree::
    :maxdepth: 2
    
    News
