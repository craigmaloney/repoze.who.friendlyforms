# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009, Gustavo Narea <me@gustavonarea.net>.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################

"""Collection of :mod:`repoze.who` friendly forms"""

from urlparse import urlparse, urlunparse
from urllib import urlencode
try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

from paste.httpexceptions import HTTPFound
from paste.request import construct_url, resolve_relative_url, \
                          parse_dict_querystring
from paste.response import replace_header, header_value

from repoze.who.plugins.form import RedirectingFormPlugin

__all__ = ['FriendlyFormPlugin']


class FriendlyFormPlugin(RedirectingFormPlugin):
    """
    Make the :class:`RedirectingFormPlugin 
    <repoze.who.plugins.form.RedirectingFormPlugin>` friendlier.
    
    It makes ``RedirectingFormPlugin`` friendlier in the following aspects:
    
    * Users are not challenged on logout, unless the referrer URL is a
      private one (but that's up to the application).
    * Developers may define post-login and/or post-logout pages.
    * In the login URL, the amount of failed logins is available in the
      environ. It's also increased by one on every login try. This counter 
      will allow developers not using a post-login page to handle logins that
      fail/succeed.
    
    You should keep in mind that if you're using a post-login or a post-logout
    page, that page will receive the referrer URL as a query string variable
    whose name is "came_from".
    
    .. warning::
    
        Do not use this plugin directly: It's likely that it will get included
        into :mod:`repoze.who` under a new name. If this happens, we will
        remove it from the quickstart to use the new one in :mod:`repoze.who`.
        
        So, in the mean time, if you want to use it in your project you 
        should copy it.
    
    """
    
    def __init__(self, *args, **kwargs):
        """
        Setup the friendly ``RedirectingFormPlugin``.
        
        It receives the same arguments as the parent, plus the following
        *keyword* arguments:
        
        * ``login_counter_name``: The name of the login counter variable
          in the query string. Defaults to ``__logins``.
        * ``post_login_url``: The URL/path to the post-login page, if any.
        * ``post_logout_url``: The URL/path to the post-logout page, if any.
        
        """
        
        # Extracting the keyword arguments for this plugin:
        self.login_counter_name = kwargs.pop('login_counter_name', None)
        self.post_login_url = kwargs.pop('post_login_url', None)
        self.post_logout_url = kwargs.pop('post_logout_url', None)
        # If the counter name is something useless, like "" or None:
        if not self.login_counter_name:
            self.login_counter_name = '__logins'
        # Finally we can invoke the parent constructor
        super(FriendlyFormPlugin, self).__init__(*args, **kwargs)
    
    def identify(self, environ):
        """
        Override the parent's identifier to introduce a login counter
        (possibly along with a post-login page) and load the login counter into
        the ``environ``.
        
        """
        
        identity = super(FriendlyFormPlugin, self).identify(environ)
        
        if environ['PATH_INFO'] == self.login_handler_path:
            ## We are on the URL where repoze.who processes authentication. ##
            # Let's append the login counter to the query string of the
            # "came_from" URL. It will be used by the challenge below if
            # authorization is denied for this request.
            destination = environ['repoze.who.application'].location()
            if self.post_login_url:
                # There's a post-login page, so we have to replace the
                # destination with it.
                destination = self._get_full_path(self.post_login_url,
                                                  environ)
                # Let's check if there's a referrer defined.
                query_parts = parse_dict_querystring(environ)
                if 'came_from' in query_parts:
                    # There's a referrer URL defined, so we have to pass it to
                    # the post-login page as a GET variable.
                    destination = self._insert_qs_variable(
                        destination,
                        'came_from',
                        query_parts['came_from'])
            failed_logins = self._get_logins(environ, True)
            new_dest = self._set_logins_in_url(destination, failed_logins)
            environ['repoze.who.application'] = HTTPFound(new_dest)
            
        elif environ['PATH_INFO'] == self.login_form_url or \
             self._get_logins(environ):
            ##  We are on the URL that displays the from OR any other page  ##
            ##   where the login counter is included in the query string.   ##
            # So let's load the counter into the environ and then hide it from
            # the query string (it will cause problems in frameworks like TG2,
            # where this unexpected variable would be passed to the controller)
            environ['repoze.who.logins'] = self._get_logins(environ, True)
            # Hiding the GET variable in the environ:
            qs = parse_dict_querystring(environ)
            if self.login_counter_name in qs:
                del qs[self.login_counter_name]
                environ['QUERY_STRING'] = urlencode(qs, doseq=True)
        
        return identity
    
    def challenge(self, environ, status, app_headers, forget_headers):
        """
        Override the parent's challenge to avoid challenging the user on
        logout, introduce a post-logout page and/or pass the login counter 
        to the login form.
        
        """
        
        challenger = super(FriendlyFormPlugin, self).\
                     challenge(environ, status, app_headers, forget_headers)
        
        headers = [(h, v) for (h, v) in challenger.headers
                   if h.lower() != 'location']
        
        if environ['PATH_INFO'] == self.logout_handler_path:
            # Let's log the user out without challenging.
            came_from = environ.get('came_from')
            SCRIPT_NAME = environ.get('SCRIPT_NAME', '')
            if self.post_logout_url:
                # Redirect to a predefined "post logout" URL.
                destination = self._get_full_path(self.post_logout_url,
                                                  environ)
                if came_from:
                    destination = self._insert_qs_variable(
                                  destination, 'came_from', came_from)
            else:
                # Redirect to the referrer URL.
                destination = came_from or SCRIPT_NAME or '/'
            return HTTPFound(destination, headers=headers)
        
        if 'repoze.who.logins' in environ:
            # Login failed! Let's redirect to the login form and include
            # the login counter in the query string
            environ['repoze.who.logins'] += 1
            #raise Exception(environ['repoze.who.logins'])
            # Re-building the URL:
            old_destination = challenger.location()
            destination = self._set_logins_in_url(old_destination,
                                                  environ['repoze.who.logins'])
            return HTTPFound(destination, headers=headers)
        
        return challenger
    
    def _get_full_path(self, path, environ):
        """
        Return the full path to ``path`` by prepending the SCRIPT_NAME.
        
        If ``path`` is a URL, do nothing.
        
        """
        if path.startswith('/'):
            path = environ.get('SCRIPT_NAME', '') + path
        return path
    
    def _get_logins(self, environ, force_typecast=False):
        """
        Return the login counter from the query string in the ``environ``.
        
        If it's not possible to convert it into an integer and  
        ``force_typecast`` is ``True``, it will be set to zero (int(0)). 
        Otherwise, it will be ``None`` or an string.
        
        """
        variables = parse_dict_querystring(environ)
        failed_logins = variables.get(self.login_counter_name)
        if force_typecast:
            try:
                failed_logins = int(failed_logins)
            except (ValueError, TypeError):
                failed_logins = 0
        return failed_logins
    
    def _set_logins_in_url(self, url, logins):
        """
        Insert the login counter variable with the ``logins`` value into
        ``url`` and return the new URL.
        
        """
        return self._insert_qs_variable(url, self.login_counter_name, logins)
    
    def _insert_qs_variable(self, url, var_name, var_value):
        """
        Insert the variable ``var_name`` with value ``var_value`` in the query
        string of ``url`` and return the new URL.
        
        """
        url_parts = list(urlparse(url))
        query_parts = parse_qs(url_parts[4])
        query_parts[var_name] = var_value
        url_parts[4] = urlencode(query_parts, doseq=True)
        return urlunparse(url_parts)
