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

"""Test suite for the collection of :mod:`repoze.who` friendly forms."""

from unittest import TestCase
from urllib import quote as original_quoter

from paste.httpexceptions import HTTPFound

from repoze.who.plugins.friendlyform import FriendlyFormPlugin

# Let's prevent the original quote() from leaving slashes:
quote = lambda txt: original_quoter(txt, '')


class TestFriendlyFormPlugin(TestCase):
    
    def test_constructor(self):
        p = self._make_one()
        self.assertEqual(p.login_counter_name, '__logins')
        self.assertEqual(p.post_login_url, None)
        self.assertEqual(p.post_logout_url, None)
    
    def test_login_without_postlogin_page(self):
        """
        The page to be redirected to after login must include the login 
        counter.
        
        """
        # --- Configuring the plugin:
        p = self._make_one()
        # --- Configuring the mock environ:
        came_from = '/some_path'
        environ = self._make_environ('/login_handler',
                                     'came_from=%s' % quote(came_from))
        # --- Testing it:
        p.identify(environ)
        app = environ['repoze.who.application']
        new_redirect = came_from + '?__logins=0'
        self.assertEqual(app.location(), new_redirect)
    
    def test_post_login_page_as_url(self):
        """Post-logout pages can also be defined as URLs, not only paths"""
        # --- Configuring the plugin:
        login_url = 'http://example.org/welcome'
        p = self._make_one(post_login_url=login_url)
        # --- Configuring the mock environ:
        environ = self._make_environ('/login_handler')
        # --- Testing it:
        p.identify(environ)
        app = environ['repoze.who.application']
        self.assertEqual(app.location(), login_url + '?__logins=0')
    
    def test_post_login_page_with_SCRIPT_NAME(self):
        """
        While redirecting to the post-login page, the SCRIPT_NAME must be
        taken into account.
        
        """
        # --- Configuring the plugin:
        p = self._make_one(post_login_url='/welcome_back')
        # --- Configuring the mock environ:
        environ = self._make_environ('/login_handler', SCRIPT_NAME='/my-app')
        # --- Testing it:
        p.identify(environ)
        app = environ['repoze.who.application']
        self.assertEqual(app.location(), '/my-app/welcome_back?__logins=0')
    
    def test_post_login_page_with_SCRIPT_NAME_and_came_from(self):
        """
        While redirecting to the post-login page with the came_from variable, 
        the SCRIPT_NAME must be taken into account.
        
        """
        # --- Configuring the plugin:
        p = self._make_one(post_login_url='/welcome_back')
        # --- Configuring the mock environ:
        came_from = '/something'
        environ = self._make_environ('/login_handler',
                                     'came_from=%s' % quote(came_from),
                                     SCRIPT_NAME='/my-app')
        # --- Testing it:
        p.identify(environ)
        app = environ['repoze.who.application']
        redirect = '/my-app/welcome_back?__logins=0&came_from=%s'
        self.assertEqual(app.location(), redirect % quote(came_from))
    
    def test_post_login_page_without_login_counter(self):
        """
        If there's no login counter defined, the post-login page should receive
        the counter at zero.
        
        """
        # --- Configuring the plugin:
        p = self._make_one(post_login_url='/welcome_back')
        # --- Configuring the mock environ:
        environ = self._make_environ('/login_handler')
        # --- Testing it:
        p.identify(environ)
        app = environ['repoze.who.application']
        self.assertEqual(app.location(), '/welcome_back?__logins=0')
    
    def test_post_login_page_with_login_counter(self):
        """
        If the login counter is defined, the post-login page should receive it
        as is.
        
        """
        # --- Configuring the plugin:
        p = self._make_one(post_login_url='/welcome_back')
        # --- Configuring the mock environ:
        environ = self._make_environ('/login_handler', '__logins=2',
                                     redirect='/some_path')
        # --- Testing it:
        p.identify(environ)
        app = environ['repoze.who.application']
        self.assertEqual(app.location(), '/welcome_back?__logins=2')
    
    def test_post_login_page_with_invalid_login_counter(self):
        """
        If the login counter is defined with an invalid value, the post-login 
        page should receive the counter at zero.
        
        """
        # --- Configuring the plugin:
        p = self._make_one(post_login_url='/welcome_back')
        # --- Configuring the mock environ:
        environ = self._make_environ('/login_handler', '__logins=non_integer',
                                     redirect='/some_path')
        # --- Testing it:
        p.identify(environ)
        app = environ['repoze.who.application']
        self.assertEqual(app.location(), '/welcome_back?__logins=0')
    
    def test_post_login_page_with_referrer(self):
        """
        If the referrer is defined, it should be passed along with the login
        counter to the post-login page.
        
        """
        # --- Configuring the plugin:
        p = self._make_one(post_login_url='/welcome_back')
        # --- Configuring the mock environ:
        orig_redirect = '/some_path'
        came_from = quote('http://example.org')
        environ = self._make_environ(
            '/login_handler',
            '__logins=3&came_from=%s' % came_from,
            redirect=orig_redirect,
            )
        # --- Testing it:
        p.identify(environ)
        app = environ['repoze.who.application']
        new_url = '/welcome_back?__logins=3&came_from=%s' % came_from
        self.assertEqual(app.location(), new_url)
    
    def test_login_page_with_login_counter(self):
        """
        In the page where the login form is displayed, the login counter
        must be defined in the WSGI environment variable 'repoze.who.logins'.
        
        """
        # --- Configuring the plugin:
        p = self._make_one()
        # --- Configuring the mock environ:
        environ = self._make_environ('/login', '__logins=2')
        # --- Testing it:
        p.identify(environ)
        self.assertEqual(environ['repoze.who.logins'], 2)
        self.assertEqual(environ['QUERY_STRING'], '')
    
    def test_login_page_without_login_counter(self):
        """
        In the page where the login form is displayed, the login counter
        must be defined in the WSGI environment variable 'repoze.who.logins' 
        and if it's not defined in the query string, set it to zero in the
        environ.
        
        """
        # --- Configuring the plugin:
        p = self._make_one()
        # --- Configuring the mock environ:
        environ = self._make_environ('/login')
        # --- Testing it:
        p.identify(environ)
        self.assertEqual(environ['repoze.who.logins'], 0)
        self.assertEqual(environ['QUERY_STRING'], '')
    
    def test_login_page_with_camefrom(self):
        """
        In the page where the login form is displayed, the login counter
        must be defined in the WSGI environment variable 'repoze.who.logins' 
        and hidden in the query string available in the environ.
        
        """
        # --- Configuring the plugin:
        p = self._make_one()
        # --- Configuring the mock environ:
        came_from = 'http://example.com'
        environ = self._make_environ('/login',
                                     'came_from=%s' % quote(came_from))
        # --- Testing it:
        p.identify(environ)
        self.assertEqual(environ['repoze.who.logins'], 0)
        self.assertEqual(environ['QUERY_STRING'], 
                         'came_from=%s' % quote(came_from))
    
    def test_logout_without_post_logout_page(self):
        """
        Users must be redirected to '/' on logout if there's no referrer page
        and no post-logout page defined.
        
        """
        # --- Configuring the plugin:
        p = self._make_one()
        # --- Configuring the mock environ:
        environ = self._make_environ('/logout_handler')
        # --- Testing it:
        app = p.challenge(environ, '401 Unauthorized', [('app', '1')],
                          [('forget', '1')])
        self.assertEqual(app.location(), '/')
    
    def test_logout_with_SCRIPT_NAME_and_without_post_logout_page(self):
        """
        Users must be redirected to SCRIPT_NAME on logout if there's no 
        referrer page and no post-logout page defined.
        
        """
        # --- Configuring the plugin:
        p = self._make_one()
        # --- Configuring the mock environ:
        environ = self._make_environ('/logout_handler', SCRIPT_NAME='/my-app')
        # --- Testing it:
        app = p.challenge(environ, '401 Unauthorized', [('app', '1')],
                          [('forget', '1')])
        self.assertEqual(app.location(), '/my-app')
    
    def test_logout_with_camefrom_and_without_post_logout_page(self):
        """
        Users must be redirected to the referrer page on logout if there's no
        post-logout page defined.
        
        """
        # --- Configuring the plugin:
        p = self._make_one()
        # --- Configuring the mock environ:
        environ = self._make_environ('/logout_handler')
        environ['came_from'] = '/somewhere'
        # --- Testing it:
        app = p.challenge(environ, '401 Unauthorized', [('app', '1')],
                          [('forget', '1')])
        self.assertEqual(app.location(), '/somewhere')
    
    def test_logout_with_post_logout_page(self):
        """Users must be redirected to the post-logout page, if defined"""
        # --- Configuring the plugin:
        p = self._make_one(post_logout_url='/see_you_later')
        # --- Configuring the mock environ:
        environ = self._make_environ('/logout_handler')
        # --- Testing it:
        app = p.challenge(environ, '401 Unauthorized', [('app', '1')],
                          [('forget', '1')])
        self.assertEqual(app.location(), '/see_you_later')
    
    def test_logout_with_post_logout_page_as_url(self):
        """Post-logout pages can also be defined as URLs, not only paths"""
        # --- Configuring the plugin:
        logout_url = 'http://example.org/see_you_later'
        p = self._make_one(post_logout_url=logout_url)
        # --- Configuring the mock environ:
        environ = self._make_environ('/logout_handler')
        # --- Testing it:
        app = p.challenge(environ, '401 Unauthorized', [('app', '1')],
                          [('forget', '1')])
        self.assertEqual(app.location(), logout_url)
    
    def test_logout_with_post_logout_page_and_SCRIPT_NAME(self):
        """
        Users must be redirected to the post-logout page, if defined, taking
        the SCRIPT_NAME into account.
        
        """
        # --- Configuring the plugin:
        p = self._make_one(post_logout_url='/see_you_later')
        # --- Configuring the mock environ:
        environ = self._make_environ('/logout_handler', SCRIPT_NAME='/my-app')
        # --- Testing it:
        app = p.challenge(environ, '401 Unauthorized', [('app', '1')],
                          [('forget', '1')])
        self.assertEqual(app.location(), '/my-app/see_you_later')
    
    def test_logout_with_post_logout_page_and_came_from(self):
        """
        Users must be redirected to the post-logout page, if defined, and also
        pass the came_from variable.
        
        """
        # --- Configuring the plugin:
        p = self._make_one(post_logout_url='/see_you_later')
        # --- Configuring the mock environ:
        came_from = '/the-path'
        environ = self._make_environ('/logout_handler')
        environ['came_from'] = came_from
        # --- Testing it:
        app = p.challenge(environ, '401 Unauthorized', [('app', '1')],
                          [('forget', '1')])
        redirect = '/see_you_later?came_from=%s'
        self.assertEqual(app.location(), redirect % quote(came_from))
    
    def test_failed_login(self):
        """
        Users must be redirected to the login form if the tried to log in with
        the wrong credentials.
        
        """
        # --- Configuring the plugin:
        p = self._make_one()
        # --- Configuring the mock environ:
        environ = self._make_environ('/somewhere')
        environ['repoze.who.logins'] = 1
        # --- Testing it:
        app = p.challenge(environ, '401 Unauthorized', [('app', '1')],
                          [('forget', '1')])
        came_from = 'http://example.org/somewhere'
        redirect = '/login?__logins=2&came_from=%s' % quote(came_from)
        self.assertEqual(app.location(), redirect)
    
    def test_not_logout_and_not_failed_logins(self):
        """
        Do not modify the challenger unless it's handling a logout or a
        failed login.
        
        """
        # --- Configuring the plugin:
        p = self._make_one()
        # --- Configuring the mock environ:
        environ = self._make_environ('/somewhere')
        # --- Testing it:
        app = p.challenge(environ, '401 Unauthorized', [('app', '1')],
                          [('forget', '1')])
        came_from = 'http://example.org/somewhere'
        redirect = '/login?came_from=%s' % quote(came_from)
        self.assertEqual(app.location(), redirect)
    
    def _make_one(self, login_counter_name=None, post_login_url=None,
                  post_logout_url=None):
        p = FriendlyFormPlugin('/login', '/login_handler', '/logout_handler',
                               'whatever',
                               login_counter_name=login_counter_name,
                               post_login_url=post_login_url,
                               post_logout_url=post_logout_url)
        return p
    
    def _make_redirection(self, url):
        app = HTTPFound(url)
        return app
    
    def _make_environ(self, path_info, qs='', SCRIPT_NAME='', redirect=None):
        environ = {
            'PATH_INFO': path_info,
            'SCRIPT_NAME': SCRIPT_NAME,
            'QUERY_STRING': qs,
            'SERVER_NAME': 'example.org',
            'SERVER_PORT': '80',
            'wsgi.input': '',
            'wsgi.url_scheme': 'http',
            }
        if redirect:
            environ['repoze.who.application'] = self._make_redirection(redirect)
        return environ
