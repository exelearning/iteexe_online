#!/usr/bin/python
# -*- coding: utf-8 -*-
# ===========================================================================
# eXe
# Copyright 2012, Pedro Peña Pérez, Open Phoenix IT
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# ===========================================================================


import logging
from exe.webui.renderable import Renderable
from exe.webui.saml import prepare_nevow_request, init_saml_auth
from nevow import rend, inevow, url, tags

log = logging.getLogger(__name__)


class LoginPage(Renderable, rend.Page):
    _templateFileName = 'login.html'
    name = 'login'

    def __init__(self, parent, configDir):
        """
        Initialize
        """
        self.configDir = configDir
        parent.putChild(self.name, self)
        Renderable.__init__(self, parent)
        rend.Page.__init__(self)

    def renderHTTP(self, ctx):
        request = inevow.IRequest(ctx)
        session = request.getSession()
        return rend.Page.renderHTTP(self, ctx)

    @staticmethod
    def render_title(ctx, data):
        ctx.tag.clear()
        return ctx.tag()[_("eXe")]

    @staticmethod
    def render_msg1(ctx, data):
        ctx.tag.clear()
        return ctx.tag()[_("No user session")]

    def render_msg2(self, ctx, data):
        if self.webServer.application.server:
            ctx.tag.clear()
            return ctx.tag()[[_("Login with Google")]]
        return ctx.tag()
