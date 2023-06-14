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


class ImportOdePage(Renderable, rend.Page):
    _templateFileName = 'importode.html'
    name = 'importode'

    def __init__(self, parent, repository_url, ode_id, error=None):
        """
        Initialize
        """
        self.repository_url = repository_url
        self.ode_id = ode_id
        self.error = error
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
        return ctx.tag()["eXe"]
        
    def render_style1(self, ctx, data):
        ctx.tag.clear()
        if self.error:
            return ctx.tag()[('.b{color: red; background-color: lightgray}')]
        else:
            return ctx.tag()['']

    def render_script1(self, ctx, data):
        ctx.tag.clear()
        if self.error:
            return ctx.tag()[('document.getElementById("spinner").hidden = true')]
        else:
            return ctx.tag()['']

    def render_msg1(self, ctx, data):
        ctx.tag.clear()
        if self.error:
            return ctx.tag()[_("Error importing package with id %s from %s") % (self.ode_id, self.repository_url)]
        else:
            return ctx.tag()[_("Importing package with id %s from %s") % (self.ode_id, self.repository_url)]

    def render_msg2(self, ctx, data):
        ctx.tag.clear()
        if self.error:
            return ctx.tag()[self.error]
        else:
            return ctx.tag()[_("This may take a bit...")]
