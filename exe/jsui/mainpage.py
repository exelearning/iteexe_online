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

"""
This is the main Javascript page.
"""

import copy
import os
import json
import sys
import logging
import traceback
import shutil
import tempfile
import uuid
import base64
import certifi
from sys                         import platform
from exe.engine.version          import release, revision
from twisted.internet            import threads, reactor, defer
from exe.webui.livepage          import RenderableLivePage,\
    otherSessionPackageClients, allSessionClients, allSessionPackageClients
from nevow                       import loaders, inevow, tags
from nevow.livepage              import handler, IClientHandle, js
from exe.jsui.idevicepane        import IdevicePane
from exe.jsui.outlinepane        import OutlinePane
from exe.jsui.recentmenu         import RecentMenu
from exe.jsui.stylemenu          import StyleMenu
from exe.jsui.propertiespage     import PropertiesPage
from exe.jsui.templatemenu       import TemplateMenu
from exe.webui.authoringpage     import AuthoringPage
from exe.webui.stylemanagerpage  import StyleManagerPage
from exe.webui.renderable        import File, Download
from exe.export.websiteexport    import WebsiteExport
from exe.export.textexport       import TextExport
from exe.export.singlepageexport import SinglePageExport
from exe.export.scormexport      import ScormExport
from exe.export.imsexport        import IMSExport
from exe.export.xliffexport      import XliffExport
from exe.importers.xliffimport   import XliffImport
from exe.importers.scanresources import Resources
from exe.engine.path             import Path, toUnicode, TempDirPath
from exe.engine.package          import Package
from exe.engine.template         import Template
from exe.engine.integration      import Integration
from exe                         import globals as G
from tempfile                    import mkdtemp, mkstemp
from exe.engine.mimetex          import compile
from urllib                      import unquote, urlretrieve, urlencode, urlopen
from exe.engine.locationbuttons  import LocationButtons
from exe.export.epub3export      import Epub3Export
from exe.export.xmlexport        import XMLExport
#from requests_oauthlib           import OAuth2Session
#from exe.webui.oauthpage         import ProcomunOauth
from suds.client                 import Client
from exe.export.pages            import forbiddenPageNames
from exe.engine.configparser     import ConfigParser
from exe.engine.resource         import Resource

from exe.engine.lom import lomsubs
from exe.engine.lom.lomclassification import Classification
import zipfile
log = logging.getLogger(__name__)
#PROCOMUN_WSDL = ProcomunOauth.BASE_URL + '/oauth_services?wsdl'

import ssl
#ssl._create_default_https_context = ssl._create_unverified_context

class MainPage(RenderableLivePage):
    """
    This is the main Javascript page.  Responsible for handling URLs.
    """

    _templateFileName = 'mainpage.html'
    name = 'to_be_defined'

    def __init__(self, parent, package, session, config,jwt_token=False):
        """
        Initialize a new Javascript page
        'package' is the package that we look after
        """

        self.jwt_token=jwt_token
        self.name = package.name
        self.session = session
        RenderableLivePage.__init__(self, parent, package, config)
        self.putChild("resources", File(package.resourceDir))
        self.tempDir = TempDirPath()
        self.putChild("temp", Download(self.tempDir, 'application/octet-stream', ('*')))

        mainjs = Path(self.config.jsDir).joinpath('templates', 'mainpage.html')
        self.docFactory = loaders.htmlfile(mainjs)

        # Create all the children on the left
        self.outlinePane = OutlinePane(self)
        self.idevicePane = IdevicePane(self)
        self.styleMenu = StyleMenu(self)
        self.recentMenu = RecentMenu(self)
        self.templateMenu = TemplateMenu(self)

        # And in the main section
        self.propertiesPage = PropertiesPage(self)
        self.authoringPage = None
        self.previewPage = None
        self.printPage = None
        self.authoringPages = {}
        self.classificationSources = {}

        G.application.resourceDir = Path(package.resourceDir)

        self.location_buttons = LocationButtons()

        # Save package temporarily
        self.tempPackage = None

        # Integration
        self.integration = Integration()

    def renderHTTP(self, ctx):
        """
        Called when rendering the MainPage.
        """
        # If we are realoading a template, try to translate it in
        # case its language has changed
        if self.package.isTemplate and not self.package.isChanged:
            # We have to reload the template in case it has been already translated before
            template = Package.load(self.config.templatesDir / self.package.get_templateFile() + '.elt', isTemplate=True)
            template.set_lang(self.package.lang)

            # Copy level names and iDevices
            self.package._levelNames = copy.copy(template._levelNames)
            self.package.idevices = copy.copy(template.idevices)

            # TODO: This should be done properly
            self.package.description = copy.copy(template.description)
            self.package.title = copy.copy(template.title)
            self.package.footer = copy.copy(template.footer)
            self.package.objectives = copy.copy(template.objectives)
            self.package.preknowledge = copy.copy(template.preknowledge)
            self.package.author = copy.copy(template.author)

            # Copy the nodes and update the root and current ones
            # Be carefull not to use copy.copy when assigning root and currentNode as this will create entirely new nodes
            self.package._nodeIdDict = copy.copy(template._nodeIdDict)
            rootkey = [k for k,v in self.package._nodeIdDict.items() if not v.parent][0]
            self.package.root = self.package._nodeIdDict[rootkey]
            self.package.currentNode = self.package._nodeIdDict[rootkey]

            # Delete the template as we don't need it in memory anymore
            del template

            # We have to go through all nodes to add the correct reference
            # to the current package
            for node in self.package._nodeIdDict.itervalues():
                node._package = self.package

            self.package.translatePackage()

            self.package.isChanged = False

        # Call parent's renderHTTP method
        return super(MainPage, self).renderHTTP(ctx)

    def child_authoring(self, ctx):
        """
        Returns the authoring page that corresponds to
        the url http://127.0.0.1:port/package_name/authoring
        """
        request = inevow.IRequest(ctx)
        if 'clientHandleId' in request.args:
            clientid = request.args['clientHandleId'][0]
            if clientid not in self.authoringPages:
                self.authoringPages[clientid] = AuthoringPage(self)
                self.children.pop('authoring')

            return self.authoringPages[clientid]
        else:
            try:
                self.idevicePane.client.sendScript(u'top.window.location.reload()')
            except:
                raise Exception('No clientHandleId in request')

    def child_preview(self, ctx):
        if not self.package.previewDir:
            G.application.config = self.config
            style = self.config.styleStore.getStyle(self.package.style)
            stylesDir = style.get_style_dir()
            self.package.previewDir = TempDirPath()
            self.exportWebSite(None, self.package.previewDir, stylesDir)
            self.previewPage = File(self.package.previewDir / self.package.name)
        return self.previewPage

    def child_print(self, ctx):
        if not self.package.printDir:
            G.application.config = self.config
            style = self.config.styleStore.getStyle(self.package.style)
            stylesDir = style.get_style_dir()
            self.package.printDir = TempDirPath()
            self.exportSinglePage(None, self.package.printDir, self.config.webDir, stylesDir, True)
            self.printPage = File(self.package.printDir / self.package.name)
        return self.printPage

    def child_taxon(self, ctx):
        """
        Doc
        """
        request = inevow.IRequest(ctx)
        data = []
        if 'source' in request.args:
            if 'identifier' in request.args:
                source = request.args['source'][0]
                if source:
                    if source not in self.classificationSources:

                        self.classificationSources[source] = Classification()
                        try:
                            self.classificationSources[source].setSource(source, self.config.configDir)
                        except:
                            pass
                    identifier = request.args['identifier'][0]
                    if identifier == 'false':
                        identifier = False
                    if source.startswith("etb-lre_mec-ccaa"):
                        stype = 2
                    else:
                        stype = 1
                    try:
                        data = self.classificationSources[source].getDataByIdentifier(identifier, stype=stype)
                    except:
                        pass

        return json.dumps({'success': True, 'data': data})

    def child_temp_file(self, ctx, randomFile=False):
        request = inevow.IRequest(ctx)
        filetype = request.args.get('filetype', [''])[0]
        if randomFile:
            filename = uuid.uuid4()
        else:
            if request.args.get('filename') and request.args.get('filename')[0]:
                filename = request.args.get('filename')[0]
            else:
                filename =  self.package.name
        path = self.tempDir / filename + filetype[1:]
        return json.dumps({'success': True, 'path': path, 'name': path.basename()})

    def goingLive(self, ctx, client):
        """Called each time the page is served/refreshed"""
        # inevow.IRequest(ctx).setHeader('content-type', 'application/vnd.mozilla.xul+xml')
        # Set up named server side funcs that js can call
        def setUpHandler(func, name, *args, **kwargs):
            """
            Convience function link funcs to hander ids
            and store them
            """
            kwargs['identifier'] = name
            hndlr = handler(func, *args, **kwargs)
            hndlr(ctx, client)     # Stores it

        setUpHandler(self.handleSaveEXeUIversion, 'saveEXeUIversion')
        setUpHandler(self.handleIsExeUIAdvanced, 'eXeUIVersionCheck')

        setUpHandler(self.handleGetSizeProject, 'eXeUIGetSizeProject')
        setUpHandler(self.handleGetMaxSizeProject, 'eXeUIGetMaxSizeProject')
        setUpHandler(self.handleIsPackageDirty, 'isPackageDirty')
        setUpHandler(self.handleIsPackageTemplate, 'isPackageTemplate')
        setUpHandler(self.handlePackageFileName, 'getPackageFileName')
        setUpHandler(self.handleSavePackage, 'savePackage')
        setUpHandler(self.handleLoadPackage, 'loadPackage')
        setUpHandler(self.recentMenu.handleLoadRecent, 'loadRecent')
        # Task 1080, jrf
        # setUpHandler(self.handleLoadTutorial, 'loadTutorial')
        setUpHandler(self.recentMenu.handleClearRecent, 'clearRecent')
        setUpHandler(self.handleImport, 'importPackage')
        setUpHandler(self.handleCancelImport, 'cancelImportPackage')
        setUpHandler(self.handleExport, 'exportPackage')
        setUpHandler(self.handleExportProcomun, 'exportProcomun')
        setUpHandler(self.handleXliffExport, 'exportXliffPackage')
        setUpHandler(self.handleQuit, 'quit')
        setUpHandler(self.handleLogout, 'logout')
        setUpHandler(self.handleBrowseURL, 'browseURL')
        setUpHandler(self.handleMergeXliffPackage, 'mergeXliffPackage')
        setUpHandler(self.handleInsertPackage, 'insertPackage')
        setUpHandler(self.handleExtractPackage, 'extractPackage')
        setUpHandler(self.handleExtractSCORM, 'extractSCORM')        
        setUpHandler(self.outlinePane.handleSetTreeSelection, 'setTreeSelection')
        setUpHandler(self.handleRemoveTempDir, 'removeTempDir')
        setUpHandler(self.handleTinyMCEimageChoice, 'previewTinyMCEimage')
        setUpHandler(self.handleTinyMCEimageDragDrop, 'previewTinyMCEimageDragDrop')
        setUpHandler(self.handleTinyMCEmath, 'generateTinyMCEmath')
        setUpHandler(self.handleTinyMCEmathML, 'generateTinyMCEmathML')
        setUpHandler(self.handleTestPrintMsg, 'testPrintMessage')
        setUpHandler(self.handleReload, 'reload')
        setUpHandler(self.handleSourcesDownload, 'sourcesDownload')
        setUpHandler(self.handleUploadFileToResources, 'uploadFileToResources')
        # PRINT handler
        setUpHandler(self.handleClearAndMakeTempPrintDir, 'makeTempPrintDir')

        # For the new ExtJS 4.0 interface
        setUpHandler(self.outlinePane.handleAddChild, 'AddChild')
        setUpHandler(self.outlinePane.handleDelNode, 'DelNode')
        setUpHandler(self.outlinePane.handleRenNode, 'RenNode')
        setUpHandler(self.outlinePane.handlePromote, 'PromoteNode')
        setUpHandler(self.outlinePane.handleDemote, 'DemoteNode')
        setUpHandler(self.outlinePane.handleUp, 'UpNode')
        setUpHandler(self.outlinePane.handleDown, 'DownNode')
        setUpHandler(self.handleCreateDir, 'CreateDir')
        setUpHandler(self.handleOverwriteLocalStyle, 'overwriteLocalStyle')

        setUpHandler(self.handleSaveTemplate, 'saveTemplate')
        setUpHandler(self.handleLoadTemplate, 'loadTemplate')

        setUpHandler(self.handleMetadataWarning, 'showMetadataWarning')
        setUpHandler(self.hideMetadataWarningForever, 'hideMetadataWarningForever')
        setUpHandler(self.handlePackagePropertiesValidation, 'validatePackageProperties')

        self.idevicePane.client = client
        self.styleMenu.client = client
        self.templateMenu.client = client
        self.webServer.stylemanager.client = client
        self.webServer.templatemanager.client = client

        if not self.webServer.monitoring:
            self.webServer.monitoring = True
            self.webServer.monitor()

    def render_config(self, ctx, data):
        request = inevow.IRequest(ctx)
        session = request.getSession()
        config = {
            'lastDir': G.application.config.lastDir,
            'locationButtons': self.location_buttons.buttons,
            'lang': G.application.config.locale.split('_')[0],
            'showPreferences': G.application.config.showPreferencesOnStart == '1' and not G.application.preferencesShowed,
            'showNewVersionWarning': G.application.config.showNewVersionWarningOnStart == '1' and not G.application.newVersionWarningShowed,
            'release' : release,
            'loadErrors': G.application.loadErrors,
            'showIdevicesGrouped': G.application.config.showIdevicesGrouped == '1',
            'authoringIFrameSrc': '%s/authoring?clientHandleId=%s' % (self.package.name, IClientHandle(ctx).handleId),
            'pathSep': os.path.sep,
            'server': G.application.server,
            'user_root': '/',
			'autosaveTime': float(G.application.config.autosaveTime),
            'publishLabel': self.integration.repo_name,
            'publishHomeURL': self.integration.repo_home_url,
            'maxSizeImportElp': int(G.application.config.configParser.get('system', 'maxSizeImportElp')),
            'maxSizePublish': int(G.application.config.configParser.get('system', 'maxSizePublish')),
            'maxUploadSizeTinyEditorMCE': int(G.application.config.configParser.get('system', 'maxUploadSizeTinyEditorMCE'))
        }
        if session.user:
            config['user'] = session.user.name
            config['user_picture'] = session.user.picture
            config['user_root'] = session.user.root
            config['user_style'] = "style_user_{}".format(config['user'])
            if hasattr(session, 'samlNameId') and session.samlNameId:
                config['saml'] = 1
            else:
                config['saml'] = 0
            # add user styles (/style_user) to webserver path
            self.webServer.root.putChild("style_user_{}".format(config['user']), File(session.user.stylesPath))

        # When working with chinese, we need to add the full language string
        # TODO: We should test if we really need to split the locale
        if G.application.config.locale.split('_')[0] == 'zh':
            config['lang'] = G.application.config.locale

        G.application.preferencesShowed = True
        G.application.newVersionWarningShowed = True
        G.application.loadErrors = []
        return tags.script(type="text/javascript")["var config = %s" % json.dumps(config)]

    def render_jsuilang(self, ctx, data):
        return ctx.tag(src="../jsui/i18n/" + unicode(G.application.config.locale) + ".js")

    def render_extjslang(self, ctx, data):
        return ctx.tag(src="../jsui/extjs/locale/ext-lang-" + unicode(G.application.config.locale) + ".js")

    def render_htmllang(self, ctx, data):
        lang = G.application.config.locale.replace('_', '-').split('@')[0]
        attribs = {'lang': unicode(lang), 'xml:lang': unicode(lang), 'xmlns': 'http://www.w3.org/1999/xhtml'}
        return ctx.tag(**attribs)

    def render_version(self, ctx, data):
        return [tags.p()["eXeLearning %s" % release]]

    def handleTestPrintMsg(self, client, message):
        """
        Prints a test message, and yup, that's all!
        """
        print "Test Message: ", message, " [eol, eh!]"

    def handleIsPackageDirty(self, client, ifClean, ifDirty):
        """
        Called by js to know if the package is dirty or not.
        ifClean is JavaScript to be eval'ed on the client if the package has
        been changed
        ifDirty is JavaScript to be eval'ed on the client if the package has not
        been changed
        """
        if self.package.isChanged:
            client.sendScript(ifDirty)
        else:
            client.sendScript(ifClean)

    def handleIsPackageTemplate(self, client, ifTemplate, ifNotTemplate):
        """
        Called by js to know if the package is a template or not.
        It also checks if the package has already been modified.
        """
        if self.package.isTemplate and not self.package.isChanged:
            client.sendScript(ifTemplate)
        else:
            client.sendScript(ifNotTemplate)

    def handlePackageFileName(self, client, onDone, onDoneParam,export_type_name):
        """
        Calls the javascript func named by 'onDone' passing as the
        only parameter the filename of our package. If the package
        has never been saved or loaded, it passes an empty string
        'onDoneParam' will be passed to onDone as a param after the
        filename
        """
        client.call(onDone, unicode(self.package.filename), onDoneParam,export_type_name)

    def b4save(self, client, inputFilename, ext, msg):
        """
        Call this before saving a file to get the right filename.
        Returns a new filename or 'None' when attempt to override
        'inputFilename' is the filename given by the user
        'ext' is the extension that the filename should have
        'msg' will be shown if the filename already exists
        """
        if not inputFilename.lower().endswith(ext):
            if ext == '.elp' and inputFilename.lower().endswith('.zip'):
                inputFilename = Path(inputFilename[:-4]+ext)
            else:
                inputFilename += ext
            # If after adding the extension there is a file
            # with the same name, fail and show an error
            """
            if Path(inputFilename).exists():
                explanation = _(u'"%s" already exists.\nPlease try again with a different filename') % inputFilename
                msg = u'%s\n%s' % (msg, explanation)
                client.alert(msg)
                raise Exception(msg)
            """
            if Path(inputFilename).exists():
                os.remove(inputFilename)

        # When saving a template, we don't check for the filename
        # before this state, so we have to check for duplicates
        # here
        if ext.lower() == '.elt' and Path(inputFilename).exists():
            explanation = _(u'"%s" already exists.\nPlease try again with a different filename') % inputFilename
            msg = u'%s\n%s' % (msg, explanation)
            client.alert(msg)
            raise Exception(msg)

        return inputFilename

    def handleSavePackage(self, client, filename=None, onDone=None,export_type_name=None):
        """
        Save the current package
        'filename' is the filename to save the package to
        'onDone' will be evaled after saving instead or redirecting
        to the new location (in cases of package name changes).
        (This is used where the user goes file|open when their
        package is changed and needs saving)
        """
        try:
            filename = Path(filename, 'utf-8')
        except:
            filename = None

        # If the script is not passing a filename to us,
        # Then use the last filename that the package was loaded from/saved to
        if not filename:
            filename = self.package.filename
            assert filename, 'Somehow save was called without a filename on a package that has no default filename.'

        saveDir = filename.dirname()
        if saveDir and not saveDir.isdir():
            client.alert(_(u'Cannot access directory named ') + unicode(saveDir) + _(u'. Please use ASCII names.'))
            return
        oldName = self.package.name

        extension = filename.splitext()[1]
        if extension == '.elt':
            return self.handleSaveTemplate(client, filename.basename(), onDone, edit=True)
        # Add the extension if its not already there and give message if not saved
        filename = self.b4save(client, filename, '.elp', _(u'SAVE FAILED!'))

        name = str(filename.basename().splitext()[0])
        if name.upper() in forbiddenPageNames:
            client.alert(_('SAVE FAILED!\n"%s" is not a valid name for a package') % str(name))
            return

        try:
            self.package.save(filename)  # This can change the package name
        except Exception, e:
            client.alert(_('SAVE FAILED!\n%s') % str(e))
            raise

        # Take into account that some names are not allowed, so we have to take care of that before reloading
        if G.application.webServer is not None and self.package.name in G.application.webServer.invalidPackageName:
            self.package._name = self.package._name + '_1'


        if not export_type_name:
            basename = Path(filename).basename()
            save_msx = _(u'Package %s saved. Do not forget to download the package on your system') % basename
            # Tell the user and continue
            if onDone:
                client.filePickerAlert(save_msx, onDone)
            elif self.package.name != oldName:
                # Redirect the client if the package name has changed
                self.session.packageStore.addPackage(self.package)
                self.webServer.root.bindNewPackage(self.package, self.session)
                log.info('Package saved, redirecting client to /%s' % self.package.name)
                client.filePickerAlert(save_msx, 'eXe.app.gotoUrl("/%s")' % self.package.name.encode('utf8'))
            else:
                #client.filePickerAlert(_(u'Package saved to: %s') % filename, filter_func=otherSessionPackageClients)
				# A nice notification instead of an alert
                client.sendScript(u'eXe.app.notifications.savedPackage("%s")' % save_msx)

    def handleSaveTemplate(self, client, templatename=None, onDone=None, edit=False):
        '''Save template'''
        if not templatename.endswith(".elt"):
            filename = Path(self.config.templatesDir/templatename +'.elt', 'utf-8')
        else:
            filename = Path(self.config.templatesDir/templatename, 'utf-8')
            templatename = str(filename.basename().splitext()[0])

        if edit == False:
            filename = self.b4save(client, filename, '.elt', _(u'SAVE FAILED!'))

        name = str(filename.basename().splitext()[0])
        if name.upper() in forbiddenPageNames:
            client.alert(_('SAVE FAILED!\n"%s" is not a valid name for a template') % str(templatename))
            return

        try:
            configxmlData = '<?xml version="1.0"?>\n'
            configxmlData += '<template>\n'
            configxmlData += '<name>'+templatename+'</name>\n'
            configxmlData += '</template>'

            # Make the root node the current one
            self.package.currentNode = self.package.root

            # Save the template
            self.package.save(filename, isTemplate=True, configxml=configxmlData)
        except Exception, e:
            client.alert(_('SAVE FAILED!\n%s') % str(e))
            raise

        template = Template(filename)
        self.config.templateStore.addTemplate(template)

        client.alert(_(u'Template saved: %s') % templatename, onDone)

    def checkMaxSizeKey(self, filename, client, configkey):
        result = True
        _tmpmaxsize = int(G.application.config.configParser.get('system', configkey))
        if os.path.getsize(filename) > _tmpmaxsize:
            result = False
            unit = "bytes"
            if _tmpmaxsize >= 1048576:  # (1 Mb)
                unit = "MB"
            msg = unicode(str(self.convert_unit(_tmpmaxsize, unit)) + " " + unit)
            client.alert(_(u'The size cannot exceed %s') % msg)
        return result

    def handleLoadPackage(self, client, filename, filter_func=None):
        """Load the package named 'filename'"""
        if not self.checkMaxSizeKey(filename,client,'maxSizeImportElp'):
            return

        if self.integration.enabled_jwt == "0":
            package = self._loadPackage(client, filename, newLoad=True)
            self.session.packageStore.addPackage(package)
            self.webServer.root.bindNewPackage(package, self.session)
            if package.load_message:
                client.alert(package.load_message,
                            onDone=(u'eXe.app.gotoUrl("/%s")' % package.name).encode('utf8'),
                            filter_func=filter_func)
            else:
                client.sendScript((u'eXe.app.gotoUrl("/%s")' % package.name).encode('utf8'), filter_func=filter_func)

        else:
            if not self.package.isChanged and self.package.isTemplate:
                self.package.isChanged = True
            
            package = self._loadPackage(client, filename, newLoad=True, preventUpdateRecent=False)
            tmpfile = Path(tempfile.mktemp())
            package.save(tmpfile, preventUpdateRecent=False)
            loadedPackage = self._loadPackage(client, tmpfile, newLoad=False, destinationPackage=self.package, preventUpdateRecent=False)
            loadedPackage.ode_id=self.package.ode_id
            self.package=loadedPackage
            self.session.packageStore.addPackage(loadedPackage)
            self.webServer.root.bindNewPackage(loadedPackage, self.session)
            url=self.package.name+"?jwt_token="+str(self.jwt_token)+"&ode_id="+str( loadedPackage.ode_id)+"&user_id="+str(self.session.user.name)  
            client.sendScript((u'eXe.app.gotoUrl("/%s")' % \
                            url).encode('utf8'))


    def handleLoadTemplate(self, client, filename):
        """Load the template named 'filename'"""
        # By transforming it into a Path, we ensure that it is using the correct directory separator
        template = self._loadPackage(client, Path(filename), newLoad=True, isTemplate=True)
        self.webServer.root.bindNewPackage(template, self.session)
        client.sendScript((u'eXe.app.gotoUrl("/%s")' % template.name).encode('utf8'))

    def handleMetadataWarning(self, client, export_type):
        """
        Checks if the package metadata has been changed and shows
        a warning to the user.
        """
        if self.config.metadataWarning == "1" and self.package.has_custom_metadata():
            client.call(u'eXe.app.getController("Toolbar").showMetadataWarning', export_type, '')
        else:
            client.call(u'eXe.app.getController("Toolbar").processExportEventValidationStep', export_type, '')

    def hideMetadataWarningForever(self, client):
        """
        Updates the user configuration to hide the metadata warning when exporting
        for the current user.
        """
        self.config.metadataWarning = "0"

    def handlePackagePropertiesValidation(self, client, export_type):
        invalid_properties = self.package.valid_properties(export_type)
        if len(invalid_properties) == 0:
            client.call(u'eXe.app.getController("Toolbar").exportPackage', export_type, '')
        else:
            invalid_properties_str = u''
            for prop in invalid_properties:
                invalid_properties_str += prop.get('name') + '|' + prop.get('reason')

                if 'allowed_values' in prop:
                    invalid_properties_str += '|' + prop.get('allowed_values')

                invalid_properties_str +=  ','
            invalid_properties_str = invalid_properties_str[:-1]

            # Get file system encoding
            encoding = sys.getfilesystemencoding()
            if encoding is None:
                encoding = 'utf-8'

            # Turns package filename passed it to unicode when call javascript function
            client.call(u'eXe.app.getController("Toolbar").packagePropertiesCompletion', export_type, unicode(str(self.package.filename), encoding), invalid_properties_str)

    # No longer used - Task 1080, jrf
    # def handleLoadTutorial(self, client):
    #    """
    #    Loads the tutorial file, from the Help menu
    #    """
    #    filename = self.config.webDir.joinpath("docs")\
    #            .joinpath("eXe-tutorial.elp")
    #    self.handleLoadPackage(client, filename)

    def progressDownload(self, numblocks, blocksize, filesize, client):
        try:
            percent = min((numblocks * blocksize * 100) / filesize, 100)
            if percent < 0:
                percent = 0
        except:
            percent = 100
        client.sendScript('Ext.MessageBox.updateProgress(%f, "%d%%", "%s")' % (float(percent) / 100, percent, _("Downloading...")))
        log.info('%3d' % (percent))

    def isConnected(self, hostname):
        try:
            if platform=='darwin' and hasattr(sys, 'frozen'):
                verify = 'cacert.pem'
                urlretrieve(hostname, context=ssl.create_default_context(cafile='cacert.pem'))
            elif platform=='darwin':
                verify = 'cacert.pem'
                urlretrieve(hostname, context=ssl.create_default_context(cafile='cacert.pem'))
                #urlretrieve(hostname, context=ssl.create_default_context(cafile=certifi.where()))
                #urlretrieve(hostname)
            else:
                urlretrieve(hostname)
            log.debug('eXe can reach host %s without problems'%(hostname))
            return True
        except Exception, e:
            log.error('Error checking host %s is %s'%(hostname, e.strerror))
        return False

    def handleSourcesDownload(self, client):
        """
        Download taxon sources from url and deploy in $HOME/.exe/classification_sources
        """
        url = 'https://github.com/exelearning/classification_sources/raw/master/classification_sources.zip'
        client.sendScript('Ext.MessageBox.progress("%s", "%s")' %(_("Sources Download"), _("Connecting to classification sources repository...")))
        d = threads.deferToThread(urlretrieve, url, None, lambda n, b, f: self.progressDownload(n, b, f, client))

        def successDownload(result):
            filename = result[0]
            if not zipfile.is_zipfile(filename):
                client.sendScript('Ext.MessageBox.alert("%s", "%s" )' % (_("Sources Download"), _("There has been an error while trying to download classification sources. Please try again later.")))
                return None

            zipFile = zipfile.ZipFile(filename, "r")
            try:
                zipFile.extractall(G.application.config.configDir)
                client.sendScript('Ext.MessageBox.hide()')
            finally:
                Path(filename).remove()

        if (platform=='darwin'  and hasattr(sys, 'frozen')):
            cafile = "cacert.pem"
            try:
                d = threads.deferToThread(urlretrieve, url, "/tmp/classification_sources.zip", lambda n, b, f: self.progressDownload(n, b, f, client), context=ssl.create_default_context(cafile='cacert.pem')) #, context=ssl._create_unverified_context())
                d.addCallback(successDownload)
            except Exception, e:
                log.error('Error downloading url %s is %s'%(url, e.strerror))
        elif (platform=='darwin'):
            d = threads.deferToThread(urlretrieve, url, "/tmp/classification_sources.zip",
                                      lambda n, b, f: self.progressDownload(n, b, f, client),
                                      context=ssl.create_default_context(
                                          cafile='cacert.pem'))  # , context=ssl._create_unverified_context())
            #d = threads.deferToThread(urlretrieve, url, "/tmp/classification_sources.zip", lambda n, b, f: self.progressDownload(n, b, f, client), context=ssl.create_default_context(cafile=certifi.where()))
            d.addCallback(successDownload)
        else:
            d = threads.deferToThread(urlretrieve, url, None, lambda n, b, f: self.progressDownload(n, b, f, client))
            d.addCallback(successDownload)
    
    def handleOverwriteLocalStyle(self, client, style_dir, downloaded_file):
        """
        Delete locally installed style and import new version from URL
        """
        stylemanager = StyleManagerPage(self)
        stylemanager.client = client
        stylemanager.overwriteLocalStyle(style_dir, downloaded_file)

    def handleReload(self, client):
        self.location_buttons.updateText()
        client.sendScript('eXe.app.gotoUrl()')

    def handleRemoveTempDir(self, client, tempdir, rm_top_dir):
        """
        Removes a temporary directory and any contents therein
        (from the bottom up), and yup, that's all!

        #
        # swiped from an example on:
        #     http://docs.python.org/lib/os-file-dir.html
        ################################################################
        # Delete everything reachable from the directory named in 'top',
        # assuming there are no symbolic links.
        # CAUTION:  This is dangerous!  For example, if top == '/', it
        # could delete all your disk files.
        """
        top = tempdir
        for root, dirs, files in os.walk(top, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        ##################################################################
        # and finally, go ahead and remove the top-level tempdir itself:
        if int(rm_top_dir) != 0:
            os.rmdir(tempdir)

    #### NECESSARY TO PRINT
    def ClearParentTempPrintDirs(self, client, log_dir_warnings):
        """
        Determine the parent temporary printing directory, and clear them
        if safe to do so (i.e., if not the config dir itself, for example)
        Makes (if necessary), and clears out (if applicable) the parent
        temporary directory.
        The calling handleClearAndMakeTempPrintDir() shall then make a
        specific print-job subdirectory.
        """
        #
        # Create the parent temp print dir as hardcoded under the webdir, as:
        #           http://temp_print_dirs
        # (eventually may want to allow this information to be configured by
        #  the user, stored in globals, etc.)
        web_dirname = G.application.tempWebDir
        under_dirname = os.path.join(web_dirname, "temp_print_dirs")
        clear_tempdir = 0
        dir_warnings = ""

        # but first need to ensure that under_dirname itself is available;
        # if not, create it:
        if cmp(under_dirname, "") != 0:
            if os.path.exists(under_dirname):
                if os.path.isdir(under_dirname):
                    # Yes, this directory already exists.
                    # pre-clean it, keeping the clutter down:
                    clear_tempdir = 1
                else:
                    dir_warnings = "WARNING: The desired Temporary Print " \
                            + "Directory, \"" + under_dirname \
                            + "\", already exists, but as a file!\n"
                    if log_dir_warnings:
                        log.warn("ClearParentTempPrintDirs(): The desired " \
                                + "Temporary Print Directory, \"%s\", " \
                                + "already exists, but as a file!", \
                                under_dirname)
                    under_dirname = web_dirname
                    # but, we can't just put the tempdirs directly underneath
                    # the webDir, since no server object exists for it.
                    # So, as a quick and dirty solution, go ahead and put
                    # them in the images folder:
                    under_dirname = os.path.join(under_dirname, "images")

                    dir_warnings += "    RECOMMENDATION: please " \
                            + "remove/rename this file to allow eXe easier "\
                            + "management of its temporary print files.\n"
                    dir_warnings += "     eXe will create the temporary " \
                           + "printing directory directly under \"" \
                           + under_dirname + "\" instead, but this might "\
                           + "leave some files around after eXe terminates..."
                    if log_dir_warnings:
                        log.warn("    RECOMMENDATION: please remove/rename "\
                            + "this file to allow eXe easier management of "\
                            + "its temporary print files.")
                        log.warn("     eXe will create the temporary " \
                            + "printing directory directly under \"%s\" " \
                            + "instead, but this might leave some files " \
                            + "around after eXe terminates...", \
                            under_dirname)
                    # and note that we do NOT want to clear_tempdir
                    # on the config dir itself!!!!!
            else:
                os.makedirs(under_dirname)
                # and while we could clear_tempdir on it, there's no need to.
        if clear_tempdir:
            # before making this particular print job's temporary print
            # directory underneath the now-existing temp_print_dirs,
            # go ahead and clear out temp_print_dirs such that we have
            # AT MOST one old temporary set of print job files still existing
            # once eXe terminates:
            rm_topdir = "0"
            # note: rm_topdir is passed in as a STRING since
            # handleRemoveTempDir expects as such from nevow's
            # clientToServerEvent() call:
            self.handleRemoveTempDir(client, under_dirname, rm_topdir)

        return under_dirname, dir_warnings

    def handleClearAndMakeTempPrintDir(self, client, suffix, prefix, \
                                        callback):
        """
        Makes a temporary printing directory, and yup, that's pretty much it!
        """

        # First get the name of the parent temp directory, after making it
        # (if necessary) and clearing (if applicable):
        log_dir_warnings = 1
        (under_dirname, dir_warnings) = self.ClearParentTempPrintDirs( \
                                             client, log_dir_warnings)

        # Next, go ahead and create this particular print job's temporary
        # directory under the parent temp directory:
        temp_dir = mkdtemp(suffix, prefix, under_dirname)

        # Finally, pass the created temp_dir back to the expecting callback:
        client.call(callback, temp_dir, dir_warnings)
    #### Edit by Manuel Mayo Lado

    def handleTinyMCEimageChoice(self, client, tinyMCEwin, tinyMCEwin_name, \
                             tinyMCEfield, local_filename, preview_filename):
        """
        Once an image is selected in the file browser that is spawned by the
        TinyMCE image dialog, copy this file (which is local to the user's
        machine) into the server space, under a preview directory
        (after checking if this exists, and creating it if necessary).
        Note that this IS a "cheat", in violation of the client-server
        separation, but can be done since we know that the eXe server is
        actually sitting on the client host.
        """
        server_filename = ""
        errors = 0

        log.debug('handleTinyMCEimageChoice: image local = ' + local_filename
                + ', base=' + os.path.basename(local_filename))

        webDir = Path(G.application.tempWebDir)
        previewDir = webDir.joinpath('previews')

        if not previewDir.exists():
            log.debug("image previews directory does not yet exist; " \
                    + "creating as %s " % previewDir)
            previewDir.makedirs()
        elif not previewDir.isdir():
            client.alert( \
                _(u'Preview directory %s is a file, cannot replace it') \
                % previewDir)
            log.error("Couldn't preview tinyMCE-chosen image: " +
                      "Preview dir %s is a file, cannot replace it" \
                      % previewDir)
            errors += 1

        if errors == 0:
            log.debug('handleTinyMCEimageChoice: originally, local_filename='
                    + local_filename)
            local_filename = unicode(local_filename, 'utf-8')
            log.debug('handleTinyMCEimageChoice: in unicode, local_filename='
                    + local_filename)

            localImagePath = Path(local_filename)
            log.debug('handleTinyMCEimageChoice: after Path, localImagePath= '
                    + localImagePath)
            if not localImagePath.exists() or not localImagePath.isfile():
                client.alert( \
                     _(u'Local file %s is not found, cannot preview it') \
                     % localImagePath)
                log.error("Couldn't find tinyMCE-chosen image: %s" \
                        % localImagePath)
                errors += 1

        try:
            # joinpath needs its join arguments to already be in Unicode:
            #preview_filename = toUnicode(preview_filename);
            # but that's okay, cuz preview_filename is now URI safe, right?
            log.debug('URIencoded preview filename=' + preview_filename)

            server_filename = previewDir.joinpath(preview_filename)
            log.debug("handleTinyMCEimageChoice copying image from \'"\
                    + local_filename + "\' to \'" \
                    + server_filename.abspath() + "\'.")
            if self.checkMaxSizeKey(local_filename,client,'maxUploadSizeTinyEditorMCE'):
                shutil.copyfile(local_filename, \
                        server_filename.abspath())
            else:
                return
            # new optional description file to provide the
            # actual base filename, such that once it is later processed
            # copied into the resources directory, it can be done with
            # only the basename.   Otherwise the resource filenames
            # are too long for some users, preventing them from making
            # backup CDs of the content, for example.
            #
            # Remember that the full path of the
            # file is only used here as an easy way to keep the names
            # unique WITHOUT requiring a roundtrip call from the Javascript
            # to this server, and back again, a process which does not
            # seem to work with tinyMCE in the mix.  BUT, once tinyMCE's
            # part is done, and this image processed, it can be returned
            # to just its basename, since the resource parts have their
            # own unique-ification mechanisms already in place.

            descrip_file_path = Path(server_filename + ".exe_info")
            log.debug("handleTinyMCEimageChoice creating preview " \
                    + "description file \'" \
                    + descrip_file_path.abspath() + "\'.")
            descrip_file = open(descrip_file_path, 'wb')

            # safety measures against TinyMCE, otherwise it will
            # later take ampersands and entity-escape them into '&amp;',
            # and filenames with hash signs will not be found, etc.:
            unspaced_filename = local_filename.replace(' ', '_')
            unhashed_filename = unspaced_filename.replace('#', '_num_')
            unamped_local_filename = unhashed_filename.replace('&', '_and_')
            log.debug("and setting new file basename as: "
                    + unamped_local_filename)
            my_basename = os.path.basename(unamped_local_filename)

            descrip_file.write((u"basename=" + my_basename).encode('utf-8'))
            descrip_file.flush()
            descrip_file.close()

            client.sendScript('eXe.app.fireEvent("previewTinyMCEImageDone")')

        except Exception, e:
            client.alert(_('SAVE FAILED!\n%s') % str(e))
            log.error("handleTinyMCEimageChoice unable to copy local image "
                    + "file to server prevew, error = " + str(e))
            raise

    def handleUploadFileToResources(self, client, local_file, preview_filename):

        server_filename = ""
        errors = 0

        webDir = Path(G.application.tempWebDir)
        previewDir = webDir.joinpath('previews')

        if not previewDir.exists():
            log.debug("files previews directory does not yet exist; " \
                    + "creating as %s " % previewDir)
            previewDir.makedirs()
        elif not previewDir.isdir():
            client.alert(\
                _(u'Preview directory %s is a file, cannot replace it') \
                % previewDir)
            log.error("Couldn't preview file: " +
                      "Preview dir %s is a file, cannot replace it" \
                      % previewDir)
            errors += 1
        # else:
            # This will remove the directory content, but we might want to record more than one file before saving
            # shutil.rmtree(previewDir)
            # previewDir.makedirs()

        if errors == 0:
            log.debug('originally, local_file='
                    + local_file)
            log.debug('in unicode, local_file='
                    + local_file)

            localFilePath = Path(local_file)
            log.debug('after Path, localImagePath= '
                    + localFilePath)

        try:
            log.debug('URIencoded preview filename=' + preview_filename)

            server_filename = previewDir.joinpath(preview_filename)

            server_file = open(server_filename, 'wb')

            local_file = local_file.split(";base64,",1)
            local_file = local_file[1]
            server_file.write(base64.b64decode(local_file))
            server_file.flush()
            server_file.close()

            sf = str(server_filename)

            # convert webm to mp3
            # webm_version = AudioSegment.from_file(sf,"webm")
            # webm_version.export(server_filename.replace(".webm",".mp3"), format="mp3")

            client.sendScript('eXe.app.fireEvent("uploadFileToResourcesDone")')

        except Exception, e:
            client.alert(_('SAVE FAILED!\n%s') % str(e))
            log.error("Unable to save file "
                    + "file to server prevew, error = " + str(e))
            raise

    def handleTinyMCEimageDragDrop(self, client, tinyMCEwin, tinyMCEwin_name, \
                              local_filename, preview_filename):
        server_filename = ""
        errors = 0

        log.debug('handleTinyMCEimageChoice: image local = ' + local_filename
                + ', base=' + os.path.basename(local_filename))

        webDir = Path(G.application.tempWebDir)
        previewDir = webDir.joinpath('previews')

        if not previewDir.exists():
            log.debug("image previews directory does not yet exist; " \
                    + "creating as %s " % previewDir)
            previewDir.makedirs()
        elif not previewDir.isdir():
            client.alert(\
                _(u'Preview directory %s is a file, cannot replace it') \
                % previewDir)
            log.error("Couldn't preview tinyMCE-chosen image: " +
                      "Preview dir %s is a file, cannot replace it" \
                      % previewDir)
            errors += 1

        if errors == 0:
            log.debug('handleTinyMCEimageChoice: originally, local_filename='
                    + local_filename)
            log.debug('handleTinyMCEimageChoice: in unicode, local_filename='
                    + local_filename)

            localImagePath = Path(local_filename)
            log.debug('handleTinyMCEimageChoice: after Path, localImagePath= '
                    + localImagePath)

        try:
            log.debug('URIencoded preview filename=' + preview_filename)

            server_filename = previewDir.joinpath(preview_filename)

            descrip_file_path = Path(server_filename + ".exe_info")
            log.debug("handleTinyMCEimageDragDrop creating preview " \
                    + "description file \'" \
                    + descrip_file_path.abspath() + "\'.")
            descrip_file = open(server_filename, 'wb')

            local_filename = local_filename.replace('data:image/jpeg;base64,', '')
            descrip_file.write(base64.b64decode(local_filename))
            descrip_file.flush()
            descrip_file.close()

            client.sendScript('eXe.app.fireEvent("previewTinyMCEDragDropImageDone","'+preview_filename+'")')

        except Exception, e:
            client.alert(_('SAVE FAILED!\n%s') % str(e))
            log.error("handleTinyMCEimageDragDrop unable to copy local image "
                    + "file to server prevew, error = " + str(e))
            raise

    def handleTinyMCEmath(self, client, tinyMCEwin, tinyMCEwin_name, \
                             tinyMCEfield, latex_source, math_fontsize, \
                             preview_image_filename, preview_math_srcfile):
        """
        Based off of handleTinyMCEimageChoice(),
        handleTinyMCEmath() is similar in that it places a .gif math image
        (and a corresponding .tex LaTeX source file) into the previews dir.
        Rather than copying the image from a user-selected directory, though,
        this routine actually generates the math image using mimetex.
        """
        server_filename = ""
        errors = 0

        webDir = Path(G.application.tempWebDir)
        previewDir = webDir.joinpath('previews')

        if not previewDir.exists():
            log.debug("image previews directory does not yet exist; " \
                    + "creating as %s " % previewDir)
            previewDir.makedirs()
        elif not previewDir.isdir():
            client.alert( \
                _(u'Preview directory %s is a file, cannot replace it') \
                % previewDir)
            log.error("Couldn't preview tinyMCE-chosen image: " +
                      "Preview dir %s is a file, cannot replace it" \
                      % previewDir)
            errors += 1

        #if errors == 0:
        #    localImagePath = Path(local_filename)
        #    if not localImagePath.exists() or not localImagePath.isfile():
        #        client.alert( \
        #             _(u'Image file %s is not found, cannot preview it') \
        #             % localImagePath)
        #        log.error("Couldn't find tinyMCE-chosen image: %s" \
        #                % localImagePath)
        #        callback_errors = "Image file %s not found, cannot preview" \
        #                % localImagePath
        #        errors += 1

        # the mimetex usage code was swiped from the Math iDevice:
        if latex_source != "":

            # first write the latex_source out into the preview_math_srcfile,
            # such that it can then be passed into the compile command:
            math_filename = previewDir.joinpath(preview_math_srcfile)
            math_filename_str = math_filename.abspath().encode('utf-8')
            log.info("handleTinyMCEmath: using LaTeX source: " + latex_source)
            log.debug("writing LaTeX source into \'" \
                    + math_filename_str + "\'.")
            math_file = open(math_filename, 'wb')
            # do we need to append a \n here?:
            math_file.write(latex_source)
            math_file.flush()
            math_file.close()

            try:
                use_latex_sourcefile = math_filename_str
                tempFileName = compile(use_latex_sourcefile, math_fontsize, \
                        latex_is_file=True)
            except Exception, e:
                client.alert(_('Could not create the image') + " (LaTeX)","$exeAuthoring.errorHandler('handleTinyMCEmath')")
                log.error("handleTinyMCEmath unable to compile LaTeX using "
                        + "mimetex, error = " + str(e))
                raise

            # copy the file into previews
            server_filename = previewDir.joinpath(preview_image_filename)
            log.debug("handleTinyMCEmath copying math image from \'"\
                    + tempFileName + "\' to \'" \
                    + server_filename.abspath().encode('utf-8') + "\'.")
            shutil.copyfile(tempFileName, \
                    server_filename.abspath().encode('utf-8'))

            # Delete the temp file made by compile
            Path(tempFileName).remove()
        return

    def handleTinyMCEmathML(self, client, tinyMCEwin, tinyMCEwin_name, \
                             tinyMCEfield, mathml_source, math_fontsize, \
                             preview_image_filename, preview_math_srcfile):
        """
        See self.handleTinyMCEmath
        To do: This should generate an image from MathML code, not from LaTeX code.
        """

        # Provisional (just an alert message)
        client.alert(_('Could not create the image') + " (MathML)","$exeAuthoring.errorHandler('handleTinyMCEmathML')")
        return

        server_filename = ""
        errors = 0

        webDir = Path(G.application.tempWebDir)
        previewDir = webDir.joinpath('previews')

        if not previewDir.exists():
            log.debug("image previews directory does not yet exist; " \
                    + "creating as %s " % previewDir)
            previewDir.makedirs()
        elif not previewDir.isdir():
            client.alert( \
                _(u'Preview directory %s is a file, cannot replace it') \
                % previewDir)
            log.error("Couldn't preview tinyMCE-chosen image: " +
                      "Preview dir %s is a file, cannot replace it" \
                      % previewDir)
            errors += 1

        # the mimetex usage code was swiped from the Math iDevice:
        if mathml_source != "":

            # first write the mathml_source out into the preview_math_srcfile,
            # such that it can then be passed into the compile command:
            math_filename = previewDir.joinpath(preview_math_srcfile)
            math_filename_str = math_filename.abspath().encode('utf-8')
            log.info("handleTinyMCEmath: using LaTeX source: " + mathml_source)
            log.debug("writing LaTeX source into \'" \
                    + math_filename_str + "\'.")
            math_file = open(math_filename, 'wb')
            # do we need to append a \n here?:
            math_file.write(mathml_source)
            math_file.flush()
            math_file.close()

            try:
                use_mathml_sourcefile = math_filename_str
                tempFileName = compile(use_mathml_sourcefile, math_fontsize, \
                        latex_is_file=True)
            except Exception, e:
                client.alert(_('Could not create the image') + " (MathML)","$exeAuthoring.errorHandler('handleTinyMCEmathML')")
                log.error("handleTinyMCEmathML unable to compile MathML using "
                        + "mimetex, error = " + str(e))
                raise

            # copy the file into previews
            server_filename = previewDir.joinpath(preview_image_filename)
            log.debug("handleTinyMCEmath copying math image from \'"\
                    + tempFileName + "\' to \'" \
                    + server_filename.abspath().encode('utf-8') + "\'.")
            shutil.copyfile(tempFileName, \
                    server_filename.abspath().encode('utf-8'))

            # Delete the temp file made by compile
            Path(tempFileName).remove()
        return

    def getResources(self, dirname, html, client):
        Resources.cancel = False
        self.importresources = Resources(dirname, self.package.findNode(client.currentNodeId), client)
#        import cProfile
#        import lsprofcalltree
#        p = cProfile.Profile()
#        p.runctx( "resources.insertNode()",globals(),locals())
#        k = lsprofcalltree.KCacheGrind(p)
#        data = open('exeprof.kgrind', 'w+')
#        k.output(data)
#        data.close()
        self.importresources.insertNode([html.partition(dirname + os.sep)[2]])

    def handleImport(self, client, importType, path, html=None):
        if importType == 'html':
            if (not html):
                client.call('eXe.app.getController("Toolbar").importHtml2', path)
            else:
                d = threads.deferToThread(self.getResources, path, html, client)
                d.addCallback(self.handleImportCallback, client)
                d.addErrback(self.handleImportErrback, client)
                client.call('eXe.app.getController("Toolbar").initImportProgressWindow', _(u'Importing HTML...'))
        if importType.startswith('lom'):
            try:
                setattr(self.package, importType, lomsubs.parse(path))
                client.call('eXe.app.getController("MainTab").lomImportSuccess', importType)
            except Exception, e:
                client.alert(_('LOM Metadata import FAILED!\n%s') % str(e))

    def handleImportErrback(self, failure, client):
        client.alert(_(u'Error importing HTML:\n') + unicode(failure.getBriefTraceback()), \
                     (u'eXe.app.gotoUrl("/%s")' % self.package.name).encode('utf8'))

    def handleImportCallback(self, resources, client):
        client.call('eXe.app.getController("Toolbar").closeImportProgressWindow')
        client.sendScript((u'eXe.app.gotoUrl("/%s")' % \
                      self.package.name).encode('utf8'))

    def handleCancelImport(self, client):
        log.info('Cancel import')
        Resources.cancelImport()

    def handleExportProcomun(self, client):
        # If the user hasn't done the OAuth authentication yet, start this process
        if hasattr(client.session,"oauthToken") and client.session.oauthToken:
            if not client.session.oauthToken.get('procomun'):
                verify = True
                if hasattr(sys, 'frozen'):
                    verify = 'cacert.pem'
                oauth2Session = OAuth2Session(ProcomunOauth.CLIENT_ID, redirect_uri=ProcomunOauth.REDIRECT_URI)
                oauth2Session.verify = verify

        def exportScorm():
            """
            Exports the package we are about to upload to Educational Resource Platform to SCORM 1.2.
            :returns: Full path to the exported ZIP.
            """
            # Update progress for the user
            client.call('Ext.MessageBox.updateProgress', 0.3, '30%', _(u'Exporting package as SCORM 1.2...'))

            style = G.application.config.styleStore.getStyle(self.package.style)
            stylesDir = style.get_style_dir()

            fd, filename = mkstemp('.zip')
            os.close(fd)

            scorm = ScormExport(self.config, stylesDir, filename, 'scorm1.2')
            scorm.export(self.package)

            return filename

        def publish(filename):
            """
            Upload the exported package to elp Repository.
            """
            # check file size
            uploading_package_message = _(u'Checking size...')
            
            # Update progress for the user
            client.call('Ext.MessageBox.updateProgress', 0.6, '25%', uploading_package_message)
            
            # Check the size of file, can't be greater than maxSizePublish 
            if not self.checkMaxSizeKey(filename,client,'maxSizePublish'):
                return
            
            # Update progress for the user
            client.call('Ext.MessageBox.updateProgress', 0.6, '50%', uploading_package_message)
            uploading_package_message = _(u'Uploading package to %s...')  % self.integration.repo_name

            # Update progress for the user
            client.call('Ext.MessageBox.updateProgress', 0.6, '50%', uploading_package_message)

            # Update integration
            self.integration = Integration()

            client.call('Ext.MessageBox.updateProgress', 0.6, '60%', uploading_package_message)

            package_name = self.package.name
            package_file = base64.b64encode(open(filename, 'rb').read())

            client.call('Ext.MessageBox.updateProgress', 0.7, '70%', uploading_package_message)

            # Try to upload the ODE to Educational Resource Platform
            publish_document_message = _(u'No response status')
            try:

                # Add the zip (SCORM) extension to the filename
                if package_name[-4:] == '.zip':
                    scorm_filename = package_name
                else:
                    scorm_filename = package_name+'.zip'

                # Check if the package has a ode_ide from repository
                if hasattr(self.package,"ode_id") and self.package.ode_id:
                    response = self.integration.set_ode(
                        scorm_filename,
                        package_file,
                        ode_id=self.package.ode_id,
                        ode_user=self.session.user.name,
                        jwt_token=self.jwt_token
                    )
                else:
                    response = self.integration.set_ode(
                        scorm_filename,
                        package_file,
                        ode_user=self.session.user.name,
                        jwt_token=self.jwt_token
                    )

                client.call('Ext.MessageBox.updateProgress', 1, '100%', uploading_package_message)

                if response and response[0]:
                    dict_response = response[1]
                elif response and not response[0]:
                    client.alert(u'Error in response: %s' % str(response[1]),
                                    title=uploading_package_message)
                    return
                else:
                    client.alert(u'No response',
                                    title=uploading_package_message)
                    return

                if dict_response['status'] == '0':
                    publish_document_message = _(u'Sending document to %s') % self.integration.repo_name

                    if dict_response['ode_id']:
                        self.package.ode_id = dict_response['ode_id']

                    if self.package.title:
                        elp_title = self.package.title
                    else:
                        elp_title = self.package.name

                    if self.integration.publish_redirect_enabled == '1':
                        client.call('Ext.MessageBox.hide')
                        if self.integration.publish_redirect_blank == '1':
                            client.call('window.open', dict_response['ode_uri'], '_blank')
                        else:
                            client.call('window.location.replace', dict_response['ode_uri'])
                            # TODO: CERRAR SESIÓN
                            #self.handleLogout(client)
                    else:
                        client.alert(
                            js(
                                '\''
                                + _(u'Package exported to <a href="%s" target="_blank" title="Click to download ' \
                                    u'the exported package">%s</a>.') % (dict_response['ode_uri'], elp_title)
                                + u'<br />'
                                + u'<br />'
                                + _(u'<small>You can view and manage the uploaded package using '  \
                                    u'<a href="%s" target="_blank" title="Educational Resource Platform Home">%s</a>\\\'s web page.' \
                                        u'</small>').replace('>',' style="font-size:1em">') \
                                        % (self.integration.repo_home_url, self.integration.repo_name)
                                + '\''
                            ),
                            title=publish_document_message)
                else:
                    client.alert(
                        js(
                            '\''
                            + _('An error has ocurred while trying to publish a package to %s. <br />'
                            +  'The error message is: %s') % (self.integration.repo_name, dict_response['description'])
                            + '\''
                        ),
                        title=publish_document_message)

            except Exception as e:
                # If there is an exception, log it and show a generic error message to the user
                log.error('An error has ocurred while trying to publish a package to %s. The error message is: %s' % (self.integration.repo_name, str(e)))
                client.call('Ext.MessageBox.hide')
                error_args = e.args
                if error_args and len(error_args[0]) == 2:
                    client.alert(u'Error {}:{} '.format(*error_args[0]),
                                title=publish_document_message)
                else:
                    client.alert(u'Error {}'.format(e), title=publish_document_message)
                return

        d = threads.deferToThread(exportScorm)
        d.addCallback(lambda filename: threads.deferToThread(publish, filename))


    def handleExport(self, client, exportType, filename, styleNameSelec=None):
        """
        Called by js.
        Exports the current package to one of the above formats
        'exportType' can be one of 'singlePage' 'webSite' 'zipFile'
                     'textFile' or 'scorm'
        'filename' is a file for scorm pages, and a directory for websites
        """
        webDir = Path(self.config.webDir)
        style = self.config.styleStore.getStyle(self.package.style)
        stylesDir = style.get_style_dir()

        G.application.config = self.config

        filename = Path(filename, 'utf-8')
        exportDir = Path(filename).dirname()
        if exportDir and not exportDir.exists():
            client.alert(_(u'Cannot access directory named ') +
                         unicode(exportDir) +
                         _(u'. Please use ASCII names.'))
            return

        name = str(filename.basename().splitext()[0])
        if name.upper() in forbiddenPageNames:
            client.alert(_('SAVE FAILED!\n"%s" is not a valid name for the file') % str(name))
            return

        """
        adding the print feature in using the same export functionality:
        """
        if exportType == 'singlePage' or exportType == 'printSinglePage':
            if exportType == 'printSinglePage':
                printit = 1
            else:
                printit = 0
                filename = self.b4save(client, filename, '.zip', _(u'EXPORT FAILED!'))
            exported_dir = self.exportSinglePage(client, filename, webDir, stylesDir, printit)
            if exported_dir is None:
                client.alert(_(u'Cannot access directory named ')+'""')

        elif exportType == 'webSite':
            self.exportWebSite(client, filename, stylesDir)
        elif exportType == 'csvReport':
            self.exportReport(client, filename, stylesDir)
        elif exportType == 'zipFile':
            filename = self.b4save(client, filename, '.zip', _(u'EXPORT FAILED!'))
            self.exportWebZip(client, filename, stylesDir)
        elif exportType == 'zipStyle':
            filename = self.b4save(client, filename, '.zip', _(u'EXPORT FAILED!'))
            self.exportStyleZip(client, filename, styleNameSelec)
        elif exportType == 'textFile':
            self.exportText(client, filename)
        elif exportType == 'scorm1.2':
            filename = self.b4save(client, filename, '.zip', _(u'EXPORT FAILED!'))
            self.exportScorm(client, filename, stylesDir, "scorm1.2")
        elif exportType == "scorm2004":
            filename = self.b4save(client, filename, '.zip', _(u'EXPORT FAILED!'))
            self.exportScorm(client, filename, stylesDir, "scorm2004")
        elif exportType == "agrega":
            filename = self.b4save(client, filename, '.zip', _(u'EXPORT FAILED!'))
            self.exportScorm(client, filename, stylesDir, "agrega")
        elif exportType == 'epub3':
            filename = self.b4save(client, filename, '.epub', _(u'EXPORT FAILED!'))
            self.exportEpub3(client, filename, stylesDir)
        elif exportType == "commoncartridge":
            filename = self.b4save(client, filename, '.zip', _(u'EXPORT FAILED!'))
            self.exportScorm(client, filename, stylesDir, "commoncartridge")
        elif exportType == 'mxml':
            self.exportXML(client, filename, stylesDir)
        else:
            filename = self.b4save(client, filename, '.zip', _(u'EXPORT FAILED!'))
            self.exportIMS(client, filename, stylesDir)

    def handleQuit(self, client):
        """
        Close client session and stops the server if necessary
        """
        client.close("window.location = \"quit\";")
        # self.authoringPages.pop(client.handleId)
        # self.webServer.root.mainpages[self.session.uid].pop(self.package.name)

        if not self.webServer.application.server:
            if len(self.clientHandleFactory.clientHandles) <= 1:
                self.webServer.monitoring = False
                G.application.config.configParser.set('user', 'lastDir', G.application.config.lastDir)
                try:
                    shutil.rmtree(G.application.tempWebDir, True)
                    shutil.rmtree(G.application.resourceDir, True)
                except:
                    log.debug('Don\'t delete temp directorys. ')
                reactor.callLater(2, reactor.stop)
            else:
                log.debug("Not quiting. %d clients alive." % len(self.clientHandleFactory.clientHandles))

    def handleLogout(self, client):
        try:
            for file in self.session.user.root.listdir():
                if file.isfile():
                    file.remove()
        except:
            log.debug("Error deleting user's files")
        try:
            if hasattr(self.session, 'samlNameId') and self.session.samlNameId:
                #saml logout
                self.authoringPages.pop(client.handleId)
                self.webServer.root.mainpages[self.session.uid].pop(self.package.name)
                del self.webServer.root.mainpages[self.session.uid]
                del G.application.userStore.loaded[self.session.user.name]
                self.handleQuit(client)
            else:
                #htpasswd logout
                #self.authoringPages.pop(client.handleId)
                self.webServer.root.mainpages[self.session.uid].pop(self.package.name)
                del self.webServer.root.mainpages[self.session.uid]
                del G.application.userStore.loaded[self.session.user.name]
                self.session.expire()
        except:
            log.debug("Logout error")


    def handleSaveEXeUIversion(self,client,status):
        initial=G.application.config.configParser.get('user', 'eXeUIversion')
        if initial == '2':
            client.call(u'eXe.app.getController("Toolbar").exeUIalert')
        G.application.config.configParser.set('user', 'eXeUIversion', status)
        client.call(u'eXe.app.getController("Toolbar").eXeUIversionSetStatus', status)

    def handleIsExeUIAdvanced(self,client):
        status=G.application.config.configParser.get('user', 'eXeUIversion')
        client.call(u'eXe.app.getController("Toolbar").exeUIsetInitialStatus', status)

    def convert_unit(self, size_in_bytes, unit):
        if unit == "KB":
            return size_in_bytes/1024
        elif unit == "MB":
            return size_in_bytes/(1024*1024)
        elif unit == "GB":
            return size_in_bytes/(1024*1024*1024)
        else:
            return size_in_bytes

    def handleGetSizeProject(self,client):
        size = 0
        unit = "KB" 
        tmpfile = Path(tempfile.mktemp())
        filename = Path(tmpfile, 'utf-8')
        style = self.config.styleStore.getStyle(self.package.style)
        stylesDir = style.get_style_dir()
        objwebsiteExport = WebsiteExport(self.config, stylesDir, filename,"",True)
        objwebsiteExport.export(self.package)
        size = objwebsiteExport.totalSize
        if size >= 1048576: # (1 Mb)
            unit = "MB"            
        size = unicode(str(self.convert_unit(size, unit)) + " " + unit + " de ")
        client.call(u'eXe.app.getController("Toolbar").eXeUISetSizeProject', size)

    def handleGetMaxSizeProject(self,client):
        tmpmaxsize = int(G.application.config.configParser.get('system', 'maxSizePublish'))
        maxsize = unicode(str(self.convert_unit(tmpmaxsize, "MB")) + " MB.")
        client.call(u'eXe.app.getController("Toolbar").eXeUISetMaxSizeProject', maxsize)

    def handleBrowseURL(self, client, url):
        """
        visit the specified URL using the system browser
        if the URL contains %s, substitute the local webDir
        """
        url = url.replace('%s', self.config.webDir)
        log.debug(u'browseURL: ' + url)
        if hasattr(os, 'startfile'):
            os.startfile(url)
        else:
            G.application.config.browser.open(url, new=True)

    def handleMergeXliffPackage(self, client, filename, from_source):
        """
        Parse the XLIFF file and import the contents based on
        translation-unit id-s
        """

        encoding = sys.getfilesystemencoding()
        if encoding is None:
            encoding = 'utf-8'

        from_source = True if from_source == "true" else False
        try:
            importer = XliffImport(self.package, unquote(filename).encode(encoding))
            importer.parseAndImport(from_source)
            client.alert(_(u'Correct XLIFF import'), (u'eXe.app.gotoUrl("/%s")' % \
                           self.package.name).encode('utf8'))
        except Exception, e:
            client.alert(_(u'Error importing XLIFF: %s') % e, (u'eXe.app.gotoUrl("/%s")' % \
                           self.package.name).encode('utf8'))

    def handleInsertPackage(self, client, filename):
        """
        Load the package and insert in current node
        """
        if not self.checkMaxSizeKey(filename,client,'maxSizeImportElp'):
            return
        # For templates, we need to set isChanged to True to prevent the
        # translation mechanism to execute
        if not self.package.isChanged and self.package.isTemplate:
            self.package.isChanged = True

        package = self._loadPackage(client, filename, newLoad=True, preventUpdateRecent=True)
        tmpfile = Path(tempfile.mktemp())
        package.save(tmpfile, preventUpdateRecent=True)
        loadedPackage = self._loadPackage(client, tmpfile, newLoad=False, destinationPackage=self.package, preventUpdateRecent=True)
        newNode = loadedPackage.root.copyToPackage(self.package,
                                                   self.package.currentNode)
        # trigger a rename of all of the internal nodes and links,
        # and to add any such anchors into the dest package via isMerge:
        newNode.RenamedNodePath(isMerge=True)
        try:
            tmpfile.remove()
        except:
            pass
        client.sendScript((u'eXe.app.gotoUrl("/%s")' % \
                          self.package.name).encode('utf8'))

    def handleExtractPackage(self, client, filename, existOk, allPackage=False):
        """
        Create a new package consisting of the current node and export
        'existOk' means the user has been informed of existance and ok'd it
        """

        filename = Path(filename, 'utf-8')
        saveDir = filename.dirname()
        if saveDir and not saveDir.exists():
            client.alert(_(u'Cannot access directory named ') + unicode(saveDir) + _(u'. Please use ASCII names.'))
            return

        # Add the extension if its not already there
        if not filename.lower().endswith('.elp'):
            filename += '.elp'

        if Path(filename).exists() and existOk != 'true':
            os.remove(filename)

        try:
            if int(allPackage):
                self.package.save(filename)
            else:
                # Create a new package for the extracted nodes
                newPackage = self.package.extractNode()

                # trigger a rename of all of the internal nodes and links,
                # and to remove any old anchors from the dest package,
                # and remove any zombie links via isExtract:
                newNode = newPackage.root
                if newNode:
                    newNode.RenamedNodePath(isExtract=True)

                # Save the new packages
                newPackage.save(filename)
        except Exception, e:
            client.alert(_('EXTRACT FAILED!\n%s') % str(e))
            raise
        client.filePickerAlert(_(u'Package extracted to: %s') % filename)

    def handleExtractSCORM(self, client, filename, existOk):
        """
        Create a new package consisting of the current node and export to SCORM
        'existOk' means the user has been informed of existance and ok'd it
        """
        style = G.application.config.styleStore.getStyle(self.package.style)
        stylesDir = style.get_style_dir()

        filename = Path(filename, 'utf-8')
        saveDir = filename.dirname()
        if saveDir and not saveDir.exists():
            client.alert(_(u'Cannot access directory named ') + unicode(saveDir) + _(u'. Please use ASCII names.'))
            return

        # Add the extension if its not already there
        if not filename.lower().endswith('.zip'):
            filename += '.zip'

        if Path(filename).exists() and existOk != 'true':
            os.remove(filename)
        try:
            # Create a new package for the extracted nodes
            newPackage = self.package.extractNode()

            # trigger a rename of all of the internal nodes and links,
            # and to remove any old anchors from the dest package,
            # and remove any zombie links via isExtract:
            newNode = newPackage.root
            if newNode:
                newNode.RenamedNodePath(isExtract=True)

            scorm = ScormExport(self.config, stylesDir, filename, 'scorm1.2')
            scorm.export(newPackage)

        except Exception, e:
            client.alert(_('EXTRACT FAILED!\n%s') % str(e))
            raise
        client.alert(_(u'Package extracted to: %s') % filename)

    def handleCreateDir(self, client, currentDir, newDir):
        try:
            d = Path(currentDir, 'utf-8') / newDir
            d.makedirs()
            client.sendScript(u"""eXe.app.getStore('filepicker.DirectoryTree').load({
                callback: function() {
                    eXe.app.fireEvent( "dirchange", %s );
                }
            })""" % json.dumps(d))
        except OSError:
            client.alert(_(u"Directory exists"))
        except:
            log.exception("")

    # Public Methods

    """
    Exports to Ustad Mobile XML
    """
    def exportXML(self, client, filename, stylesDir):
        try:
            xmlExport = XMLExport(self.config, stylesDir, filename)
            xmlExport.export(self.package)
        except Exception, e:
            client.alert(_('EXPORT FAILED!\n%s') % str(e))
            raise

    def exportSinglePage(self, client, filename, webDir, stylesDir, \
                         printFlag):
        """
        Export 'client' to a single web page,
        'webDir' is just read from config.webDir
        'stylesDir' is where to copy the style sheet information from
        'printFlag' indicates whether or not this is for print
                    (and whatever else that might mean)
        """
        try:
            imagesDir = webDir.joinpath('images')
            scriptsDir = webDir.joinpath('scripts')
            cssDir = webDir.joinpath('css')
            templatesDir = webDir.joinpath('templates')
            # filename is a directory where we will export the website to
            # We assume that the user knows what they are doing
            # and don't check if the directory is already full or not
            # and we just overwrite what's already there
            filename = Path(filename)
            # Append the package name to the folder path if necessary
            if printFlag:
                if filename.basename() != self.package.name:
                    filename /= self.package.name
                if not filename.exists():
                    filename.makedirs()
                elif not filename.isdir():
                    if client:
                        client.alert(_(u'Filename %s is a file, cannot replace it') %
                                filename)
                    log.error("Couldn't export web page: " +
                            "Filename %s is a file, cannot replace it" % filename)
                    return
                else:
                    if client:
                        client.alert(_(u'Folder name %s already exists. '
                                    'Please choose another one or delete existing one then try again.') % filename)
                    return
            # Now do the export
            singlePageExport = SinglePageExport(stylesDir, filename, \
                                         imagesDir, scriptsDir, cssDir, templatesDir)
            if printFlag:
                singlePageExport.export(self.package, printFlag)
            else:
                singlePageExport.exportZip(self.package)

            has_uncut_resources = False
            if G.application.config.cutFileName == "1":
                has_uncut_resources = singlePageExport.hasUncutResources()
        except Exception, e:
            if client:
                client.alert(_('SAVE FAILED!\n%s') % str(e))
            raise

        # Show the newly exported web site in a new window
        if not printFlag:
            if client:
                if not has_uncut_resources:
                    client.filePickerAlert(_(u'Exported to %s') % filename)
                else:
                    client.filePickerAlert(_(u'Exported to %s.\nThere were some resources that couldn\'t be renamed to be compatible with ISO9660.') % filename)

        # and return a string of the actual directory name,
        # in case the package name was added, etc.:
        return filename.abspath().encode('utf-8')
        # WARNING: the above only returns the RELATIVE pathname

    def exportWebSite(self, client, filename, stylesDir):
        """
        Export 'client' to a web site,
        'webDir' is just read from config.webDir
        'stylesDir' is where to copy the style sheet information from
        """

        try:
            # filename is a directory where we will export the website to
            # We assume that the user knows what they are doing
            # and don't check if the directory is already full or not
            # and we just overwrite what's already there
            filename = Path(filename)
            # Append the package name to the folder path if necessary
            if filename.basename() != self.package.name:
                filename /= self.package.name
            if not filename.exists():
                filename.makedirs()
            elif not filename.isdir():
                if client:
                    client.alert(_(u'Filename %s is a file, cannot replace it') %
                             filename)
                log.error("Couldn't export web page: " +
                          "Filename %s is a file, cannot replace it" % filename)
                return
            else:
                if client:
                    client.alert(_(u'Folder name %s already exists. '
                                'Please choose another one or delete existing one then try again.') % filename)
                return
            # Now do the export
            websiteExport = WebsiteExport(self.config, stylesDir, filename)
            websiteExport.export(self.package)

            has_uncut_resources = False
            if G.application.config.cutFileName == "1":
                has_uncut_resources = websiteExport.hasUncutResources()
        except Exception, e:
            if client:
                client.alert(_('EXPORT FAILED!\n%s') % str(e))
            raise
        if client:
            if not has_uncut_resources:
                client.alert(_(u'Exported to %s') % filename)
            else:
                client.alert(_(u'Exported to %s.\nThere were some resources that couldn\'t be renamed to be compatible with ISO9660.') % filename)
            # Show the newly exported web site in a new window
            self._startFile(filename)

    def exportWebZip(self, client, filename, stylesDir):
        try:
            log.debug(u"exportWebsite, filename=%s" % filename)
            filename = Path(filename)
            # Do the export
            filename = self.b4save(client, filename, '.zip', _(u'EXPORT FAILED!'))
            websiteExport = WebsiteExport(self.config, stylesDir, filename)
            websiteExport.exportZip(self.package)

            has_uncut_resources = False
            if G.application.config.cutFileName == "1":
                has_uncut_resources = websiteExport.hasUncutResources()
        except Exception, e:
            client.alert(_('EXPORT FAILED!\n%s') % str(e))
            raise

        if not has_uncut_resources:
            client.filePickerAlert(_(u'Exported to %s') % filename)
        else:
            client.filePickerAlert(_(u'Exported to %s.\nThere were some resources that couldn\'t be renamed to be compatible with ISO9660.') % filename)

    def exportStyleZip(self, client, filename, styleName):
        style = self.config.styleStore.getStyle(styleName)
        stylesDir = style.get_style_dir()
        if not filename.lower().endswith('.zip'):
            filename += '.zip'
        log.debug("Export style %s" % stylesDir)
        try:
            zippedFile = zipfile.ZipFile(filename, "w")
            for contFile in stylesDir.files():
                zippedFile.write(
                        unicode(contFile.normpath()),
                        contFile.basename(),
                        zipfile.ZIP_DEFLATED)
            zippedFile.close()
        except Exception, e:
            client.alert(_('EXPORT FAILED!\n%s') % str(e))
            raise
        client.filePickerAlert(_(u'Exported to %s') % filename)

    def exportText(self, client, filename):
        try:
            filename = Path(filename)
            log.debug(u"exportWebsite, filename=%s" % filename)
            # Append an extension if required
            if not filename.lower().endswith('.txt'):
                filename += '.txt'
                if Path(filename).exists():
                    msg = _(u'"%s" already exists.\nPlease try again with a different filename') % filename
                    client.alert(_(u'EXPORT FAILED!\n%s') % msg)
                    return
            # Do the export
            textExport = TextExport(filename)
            textExport.export(self.package)
        except Exception, e:
            client.alert(_('EXPORT FAILED!\n%s') % str(e))
            raise
        client.filePickerAlert(_(u'Exported to %s') % filename)

    def handleXliffExport(self, client, filename, source, target, copy, cdata):
        """
        Exports this package to a XLIFF file
        """
        copy = True if copy == "true" else False
        cdata = True if cdata == "true" else False
        try:
            filename = Path(filename, 'utf-8')
            log.debug(u"exportXliff, filename=%s" % filename)
            if not filename.lower().endswith('.xlf'):
                filename += '.xlf'

            name = str(filename.basename().splitext()[0])
            if name.upper() in forbiddenPageNames:
                client.filePickerAlert(_(u'SAVE FAILED!\n"%s" is not a valid name for the file') % str(name))
                return

            xliffExport = XliffExport(self.config, filename, source, target, copy, cdata)
            xliffExport.export(self.package)
        except Exception, e:
            client.alert(_('EXPORT FAILED!\n%s') % str(e))
            raise
        client.filePickerAlert(_(u'Exported to %s') % filename)

    def exportScorm(self, client, filename, stylesDir, scormType):
        """
        Exports this package to a scorm package file
        """
        try:
            filename = Path(filename)
            log.debug(u"exportScorm, filename=%s" % filename)
            # Append an extension if required
            if not filename.lower().endswith('.zip'):
                filename += '.zip'
                if Path(filename).exists():
                    msg = _(u'"%s" already exists.\nPlease try again with a different filename') % filename
                    client.alert(_(u'EXPORT FAILED!\n%s') % msg)
                    return
            # Do the export
            scormExport = ScormExport(self.config, stylesDir, filename, scormType)
            modifiedMetaData = scormExport.export(self.package)

            has_uncut_resources = False
            if G.application.config.cutFileName == "1":
                has_uncut_resources = scormExport.hasUncutResources()
        except Exception, e:
            client.alert(_('EXPORT FAILED!\n%s') % str(e))
            raise
        if modifiedMetaData != False and modifiedMetaData['modifiedMetaData']:
            client.filePickerAlert(_(u'The following fields have been cut to meet the SCORM 1.2 standard: %s') % ', '.join(modifiedMetaData['fieldsModified']))
        else:
            if not has_uncut_resources:
                client.filePickerAlert(_(u'Exported to %s') % filename)
            else:
                client.filePickerAlert(_(u'Exported to %s.\nThere were some resources that couldn\'t be renamed to be compatible with ISO9660.') % filename)

    def exportEpub3(self, client, filename, stylesDir):
        try:
            log.debug(u"exportEpub3, filename=%s" % filename)
            filename = Path(filename)
            # Do the export
            filename = self.b4save(client, filename, '.epub', _(u'EXPORT FAILED!'))
            epub3Export = Epub3Export(self.config, stylesDir, filename)
            epub3Export.export(self.package)
            # epub3Export.exportZip(self.package)
        except Exception, e:
            client.alert(_('EXPORT FAILED!\n%s' % str(e)))
            raise
        client.filePickerAlert(_(u'Exported to %s') % filename)

    def exportReport(self, client, filename, stylesDir):
        """
        Generates this package report to a file
        """
        try:
            log.debug(u"exportReport")
            # Append an extension if required
            if not filename.lower().endswith('.csv'):
                filename += '.csv'
                if Path(filename).exists():
                    msg = _(u'"%s" already exists.\nPlease try again with a different filename') % filename
                    client.alert(_(u'EXPORT FAILED!\n%s' % msg))
                    return
            # Do the export
            websiteExport = WebsiteExport(self.config, stylesDir, filename, report=True)
            websiteExport.export(self.package)
        except Exception, e:
            client.alert(_('EXPORT FAILED!\n%s' % str(e)))
            raise
        client.filePickerAlert(_(u'Exported to %s' % filename))

    def exportIMS(self, client, filename, stylesDir):
        """
        Exports this package to a ims package file
        """
        try:
            log.debug(u"exportIMS")
            # Append an extension if required
            if not filename.lower().endswith('.zip'):
                filename += '.zip'
                if Path(filename).exists():
                    msg = _(u'"%s" already exists.\nPlease try again with a different filename') % filename
                    client.alert(_(u'EXPORT FAILED!\n%s') % msg)
                    return
            # Do the export
            imsExport = IMSExport(self.config, stylesDir, filename)
            imsExport.export(self.package)

            has_uncut_resources = False
            if G.application.config.cutFileName == "1":
                has_uncut_resources = imsExport.hasUncutResources()
        except Exception, e:
            client.alert(_('EXPORT FAILED!\n%s') % str(e))
            raise

        if not has_uncut_resources:
            client.filePickerAlert(_(u'Exported to %s') % filename)
        else:
            client.filePickerAlert(_(u'Exported to %s.\nThere were some resources that couldn\'t be renamed to be compatible with ISO9660.') % filename)

    # Utility methods
    def _startFile(self, filename):
        """
        Launches an exported web site or page
        """
        if not G.application.server:
            if hasattr(os, 'startfile'):
                try:
                    os.startfile(filename)
                except UnicodeEncodeError:
                    os.startfile(filename.encode(Path.fileSystemEncoding))
            else:
                if (filename / 'index.html').exists():
                    filename /= 'index.html'
                else:
                    filename /= 'index.htm'
                G.application.config.browser.open('file://' + filename)

    def _loadPackage(self, client, filename, newLoad=True,
                     destinationPackage=None, isTemplate=False, preventUpdateRecent=False):
        """Load the package named 'filename'"""
        try:
            encoding = sys.getfilesystemencoding()
            if encoding is None:
                encoding = 'utf-8'
            filename2 = toUnicode(filename, encoding)
            log.debug("filename and path" + filename2)
            # see if the file exists AND is readable by the user
            try:
                open(filename2, 'rb').close()
            except IOError:
                filename2 = toUnicode(filename, 'utf-8')
                try:
                    open(filename2, 'rb').close()
                except IOError:
                    client.alert(_(u'File %s does not exist or is not readable.') % filename2)
                    return None
            if isTemplate == False:
                package = Package.load(filename2, newLoad, destinationPackage, preventUpdateRecent=preventUpdateRecent)
            else:
                package = self.session.packageStore.createPackageFromTemplate(filename)
            if package is None:
                raise Exception(_("Couldn't load file, please email file to bugs@exelearning.org"))
        except Exception, exc:
            if True or log.getEffectiveLevel() == logging.DEBUG:
                client.alert(_(u'Sorry, wrong file format:\n%s') % unicode(exc))
            else:
                client.alert(_(u'Sorry, wrong file format'))
            log.error(u'Error loading package "%s": %s' % (filename2, unicode(exc)))
            log.error(u'Traceback:\n%s' % traceback.format_exc())
            f = Path(filename2)
            if f.exists():
                try:
                    f.remove()
                except:
                    pass
            raise
        return package
