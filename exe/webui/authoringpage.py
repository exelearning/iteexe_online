# ===========================================================================
# eXe
# Copyright 2004-2006, University of Auckland
# Copyright 2006-2007 eXe Project, New Zealand Tertiary Education Commission
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# ===========================================================================
"""
AuthoringPage is responsible for creating the XHTML for the authoring
area of the eXe web user interface.
"""
import os
import logging
import time
import exceptions
import sys
from twisted.web.resource    import Resource
from exe.webui               import common
from cgi                     import escape
import exe.webui.builtinblocks
from exe.webui.blockfactory  import g_blockFactory
from exe.engine.error        import Error
from exe.webui.renderable    import RenderableResource
from exe.engine.path         import Path
from exe                     import globals as G
import re

log = logging.getLogger(__name__)


# ===========================================================================
class AuthoringPage(RenderableResource):
    """
    AuthoringPage is responsible for creating the XHTML for the authoring
    area of the eXe web user interface.
    """
    name = u'authoring'

    def __init__(self, parent):
        RenderableResource.__init__(self, parent)
        self.blocks  = []

    def getChild(self, name, request):
        """
        Try and find the child for the name given
        """
        if name == "":
            return self
        else:
            return Resource.getChild(self, name, request)

    def _process(self, request):
        """
        Delegates processing of args to blocks
        """
        # Still need to call parent (mainpage.py) process
        # because the idevice pane needs to know that new idevices have been
        # added/edited..
        self.parent.process(request)
        for block in self.blocks:
            block.process(request)
        # now that each block and corresponding elements have been processed,
        # it's finally safe to remove any images/etc which made it into
        # tinyMCE's previews directory, as they have now had their
        # corresponding resources created:
        webDir     = Path(G.application.tempWebDir)
        previewDir  = webDir.joinpath('previews')

        previewsFiles = []
        if previewDir.exists():
            previewsFiles = previewDir.listdir()

        # To prevent deletion of images when there are multiple users
        if self.blocks:
            for resource in self.blocks[0].idevice.userResources:
                if resource.userName and resource.storageName:

                    resource_name = resource.storageName
                    resource_path = Path(resource.userName)
                    if resource_path.exists() and resource_path in previewsFiles:
                        try:
                            resource_path.remove()
                        except:
                            pass

                    fs_file_name = G.application.config.userResourcesDir.replace('/','_') + '_' + resource_name
                    fs_file_path = Path(previewDir / fs_file_name)
                    fs_file_info_name = fs_file_name + '.exe_info'
                    fs_file_info_path = Path(previewDir / fs_file_info_name)
                    if fs_file_path.exists():
                        try:
                            fs_file_path.remove()
                        except:
                            pass
                    if fs_file_info_path.exists():
                        try:
                            fs_file_info_path.remove()
                        except:
                            pass

                    allyourbase_file = Path(previewDir / 'allyourbase' / resource_name)
                    if allyourbase_file.exists():
                        try:
                            allyourbase_file.remove()
                        except:
                            pass
        #
        topNode = self.package.currentNode
        if "action" in request.args:
            if request.args["action"][0] == u"changeNode":
                topNode = self.package.findNode(request.args["object"][0])
            elif "currentNode" in request.args:
                topNode = self.package.findNode(request.args["currentNode"][0])
        elif "currentNode" in request.args:
            topNode = self.package.findNode(request.args["currentNode"][0])

        log.debug(u"After authoringPage process" + repr(request.args))
        return topNode

    def render_GET(self, request=None):
        """
        Returns an XHTML string for viewing this page
        if 'request' is not passed, will generate psedo/debug html
        """
        log.debug(u"render_GET "+repr(request))

        topNode = self.package.root
        if request is not None:
            # Process args
            for key, value in request.args.items():
                request.args[key] = [unicode(value[0], 'utf8')]
            topNode = self._process(request)

        #Update other authoring pages that observes the current package
        activeClient = None
        if "action" in request.args:
            if request.args['clientHandleId'][0] == "":
                raise(Exception("Not clientHandleId defined"))
            for client in self.parent.clientHandleFactory.clientHandles.values():
                if request.args['clientHandleId'][0] != client.handleId:
                    if client.handleId in self.parent.authoringPages:
                        destNode = None
                        if request.args["action"][0] == "move":
                            destNode = request.args["move" + request.args["object"][0]][0]
                        client.call('eXe.app.getController("MainTab").updateAuthoring', request.args["action"][0], \
                            request.args["object"][0], request.args["isChanged"][0], request.args["currentNode"][0], destNode)
                else:
                    activeClient = client

            if request.args["action"][0] == "done":
                if activeClient:
                    return "<body onload='location.replace(\"" + request.path + "?clientHandleId=" + activeClient.handleId + "\")'/>"
                else:
                    log.error("No active client")

        self.blocks = []
        self.__addBlocks(topNode)
        html  = self.__renderHeader()
        extraCSS = ''
        if self.package.get_loadMathEngine():
            extraCSS = ' exe-auto-math'
        html += u'<body onload="onLoadHandler();" class="exe-authoring-page'+extraCSS+' js" id="exe-authoring-page-'+unicode(topNode.id)+'">\n'
        html += u"<form method=\"post\" "

        if request is None:
            html += u'action="NO_ACTION"'
        else:
            html += u"action=\""+request.path+"#currentBlock\""
        html += u" id=\"contentForm\">"
        html += u'<div id="main">\n'
        html += common.hiddenField(u"action")
        html += common.hiddenField(u"object")
        html += common.hiddenField(u"isChanged", u"0")
        html += common.hiddenField(u"currentNode", unicode(topNode.id))
        html += common.hiddenField(u'clientHandleId', request.args['clientHandleId'][0])
        html += u'<!-- start authoring page -->\n'
        html += u'<div id="nodeDecoration">\n'
        html += u'<div id="headerContent">\n'
        html += u'<h1 id="nodeTitle">'
        html += escape(topNode.titleLong)
        html += u'</h1>\n'
        html += u'</div>\n'
        html += u'</div>\n'
        counter = 0
        msg = ''
        for block in self.blocks:
            # If we don't have a client, try to get it from request
            if activeClient is None:
                for client in self.parent.clientHandleFactory.clientHandles.values():
                    if request.args['clientHandleId'][0] == client.handleId:
                        activeClient = client

            if not activeClient is None:
                for resources in block.idevice.userResources:
                    if resources.warningMsg != u'':
                        counter +=1
                        msg += (_('Warning: %s') % resources.warningMsg)
                        # Remove warning message
                        resources.warningMsg = ''
            if counter > 0:
                activeClient.alert(msg)
            html += block.render(self.package.style)

        html += u'</div>'
        style = G.application.config.styleStore.getStyle(self.package.style)

        html += common.renderLicense(self.package.license,"authoring")
        html += common.renderFooter(self.package.footer)

        if style.hasValidConfig():
            html += style.get_edition_extra_body()
        html += '<script type="text/javascript">$exeAuthoring.ready()</script>\n'
        html += common.footer()

        html = html.encode('utf8')
        return html

    render_POST = render_GET

    def __renderHeader(self):
        #TinyMCE lang (user preference)
        myPreferencesPage = self.webServer.preferences

        """Generates the header for AuthoringPage"""
        html  = common.docType()
        #################################################################################
        #################################################################################

        html += u'<html xmlns="http://www.w3.org/1999/xhtml" lang="'+myPreferencesPage.getSelectedLanguage()+'">\n'
        html += u'<head>\n'
        html += u"<link rel=\"stylesheet\" type=\"text/css\" href=\"/css/exe.css\" />"

        # Use the Style's base.css file if it exists
        style = G.application.config.styleStore.getStyle(self.package.style)
        if style.isValid():
            themePath = style.get_web_path()
        else:
            themePath = Path("/style/base")
        themeBaseCSS = themePath.joinpath("base.css")
        if themeBaseCSS.exists():
            html += u"<link rel=\"stylesheet\" type=\"text/css\" href=\"%s/base.css\" />" % themePath
        else:
            html += u"<link rel=\"stylesheet\" type=\"text/css\" href=\"/style/base.css\" />"

        html += u"<link rel=\"stylesheet\" type=\"text/css\" href=\"/css/exe_wikipedia.css\" />"
        html += u"<link rel=\"stylesheet\" type=\"text/css\" href=\"/scripts/exe_effects/exe_effects.css\" />"
        html += u"<link rel=\"stylesheet\" type=\"text/css\" href=\"/scripts/exe_highlighter/exe_highlighter.css\" />"
        html += u"<link rel=\"stylesheet\" type=\"text/css\" href=\"/scripts/exe_games/exe_games.css\" />"
        html += u"<link rel=\"stylesheet\" type=\"text/css\" href=\"/scripts/tinymce_4/js/tinymce/plugins/abcmusic/export/exe_abcmusic.css\" />" #93 (to do)
        html += u"<link rel=\"stylesheet\" type=\"text/css\" href=\"%s/content.css\" />" % themePath
        if G.application.config.assumeMediaPlugins:
            html += u"<script type=\"text/javascript\">var exe_assume_media_plugins = true;</script>\n"
        #JR: anado una variable con el estilo
        estilo = u'%s/content.css' % themePath
        html += common.getJavaScriptStrings()
        # The games require additional strings
        html += common.getGamesJavaScriptStrings()
        html += u"<script type=\"text/javascript\">"
        html += u"var exe_style = '%s';top.exe_style = exe_style;" % estilo
        # editorpane.py uses exe_style_dirname to auto-select the current style (just a provisional solution)
        html += u"var exe_style_dirname = '%s'; top.exe_style_dirname = exe_style_dirname;" % self.package.style
        html += u"var exe_package_name='"+self.package.name+"';"
        html += 'var exe_export_format="'+common.getExportDocType()+'".toLowerCase();'
        html += 'var exe_editor_mode="'+myPreferencesPage.getEditorMode()+'";'
        html += 'var exe_editor_version="'+myPreferencesPage.getEditorVersion()+'";'
        html += '</script>\n'
        html += u'<script type="text/javascript" src="../jsui/native.history.js"></script>\n'
        htmlLang = G.application.config.locale
        if self.package.dublinCore.language!="":
            htmlLang = self.package.dublinCore.language
        for subDir in G.application.config.localeDir.dirs():
            if (subDir/'LC_MESSAGES'/'exe.mo').exists():
                if  str(subDir.basename())==htmlLang and htmlLang!=myPreferencesPage.getSelectedLanguage():
                    html += u'<script type="text/javascript" src="../jsui/i18n/'+htmlLang+'.js"></script>\n'
                    html += u'<script type="text/javascript">var exe_elp_lang="'+htmlLang+'";</script>\n'
        html += u'<script type="text/javascript" src="/scripts/authoring.js"></script>\n'
        html += u'<script type="text/javascript" src="/scripts/exe_jquery.js"></script>\n'
        html += u'<script type="text/javascript" src="/scripts/exe_lightbox/exe_lightbox.js"></script>\n'
        html += u'<script type="text/javascript" src="/scripts/exe_effects/exe_effects.js"></script>\n'
        html += u'<script type="text/javascript" src="/scripts/exe_highlighter/exe_highlighter.js"></script>\n'
        html += u'<script type="text/javascript" src="/scripts/exe_games/exe_games.js"></script>\n'
        html += u'<script type="text/javascript" src="/scripts/fix_webm_duration/fix_webm_duration.js"></script>\n'
        html += u'<script type="text/javascript" src="/scripts/tinymce_4/js/tinymce/plugins/abcmusic/export/exe_abcmusic.js"></script>\n' #93 (to do)
        html += u'<script type="text/javascript" src="/scripts/common.js"></script>\n'
        html += '<script type="text/javascript">document.write(unescape("%3Cscript src=\'" + eXeLearning_settings.wysiwyg_path + "\' type=\'text/javascript\'%3E%3C/script%3E"));</script>';
        html += '<script type="text/javascript">document.write(unescape("%3Cscript src=\'" + eXeLearning_settings.wysiwyg_settings_path + "\' type=\'text/javascript\'%3E%3C/script%3E"));</script>';
        html += common.printJavaScriptIdevicesScripts('edition',self)
        html += u'<title>"+_("eXe : elearning XHTML editor")+"</title>\n'
        html += u'<meta http-equiv="content-type" content="text/html; '
        html += u' charset=UTF-8" />\n'

        if style.hasValidConfig():
            html += style.get_edition_extra_head()
        html += common.getExtraHeadContent(self.package)
        html += u'</head>\n'
        return html


    def __addBlocks(self, node):
        """
        Add All the blocks for the currently selected node
        """
        for idevice in node.idevices:
            block = g_blockFactory.createBlock(self, idevice)
            if not block:
                log.critical(u"Unable to render iDevice.")
                raise Error(u"Unable to render iDevice.")
            self.blocks.append(block)

# ===========================================================================
