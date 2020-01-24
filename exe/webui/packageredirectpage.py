# ===========================================================================
# eXe
# Copyright 2004-2006, University of Auckland
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
PackageRedirectPage is the first screen the user loads.  It doesn't show
anything it just redirects the user to a new package.
"""

import logging
import os
import base64
from exe                        import globals as G

from exe.engine.integration     import Integration
from exe.engine.package         import Package
from exe.engine.packagestore    import PackageStore
from exe.webui.renderable       import RenderableResource
from exe.webui.importode        import ImportOdePage
from exe.jsui.mainpage          import MainPage
from twisted.web                import error, http

log = logging.getLogger(__name__)


class PackageRedirectPage(RenderableResource):
    """
    PackageRedirectPage is the first screen the user loads.  It doesn't show
    anything it just redirects the user to a new package or loads an existing 
    package.
    """
    
    name = '/'

    def __init__(self, webServer, packagePath=None):
        """
        Initialize
        """
        RenderableResource.__init__(self, None, None, webServer)
        self.webServer = webServer
        self.packagePath = packagePath
        self.package_name = ''
        # See if all out main pages are not showing
        # This is a twisted timer
        self.stopping = None
        self.integration = None
        self.mainpages = {}

    def getChild(self, name, request):
        """
        Get the child page for the name given.
        This is called if our ancestors can't find our child.
        This is probably because the url is in unicode
        """
        session = request.getSession()

        # No session
        if self.webServer.application.server and not session.user and not request.getUser():
            if 'login' in request.args and request.args['login'][0] == 'saml':
                return self.webServer.saml
            else:
                return self.webServer.login

        # Import ode from repository (<Edit package> repository option)
        # Importing... page
        if (name == '' or name == 'edit_ode') and 'ode_id' in request.args:
            edit_ode_id = request.args['ode_id'][0]
            self.integration = Integration()
            if self.integration.repo_home_url:
                repository = self.integration.repo_home_url
            else:
                repository = 'Unknown Repository'
            self.webServer.importode = ImportOdePage(self.webServer.root, repository, edit_ode_id)
            request.refresh('import?ode_id={}'.format(edit_ode_id))
            return self.webServer.importode

        # Importing and redirection
        if name == 'import' and 'ode_id' in request.args:
            edit_ode_id = request.args['ode_id'][0]
            if edit_ode_id:
                import_ode_response = self.importOde(session, edit_ode_id)
                if import_ode_response and import_ode_response[0]:
                    imported_package = import_ode_response[1]
                    request.redirect(imported_package.encode('utf8'))
                    return 'loading package'
                else:
                    # Error message
                    if import_ode_response and not import_ode_response[0]:
                        errormsx =  import_ode_response[1]
                    else:
                        errormsx = "Unknown"
                    # Repository URL
                    if self.integration:
                        repository = self.integration.repo_home_url
                    else:
                        repository = "Unknown"

                    return "<h4>Error importing package with id ( {} ) from repository ( {} ).</h4><p>{}</p>".format(
                                edit_ode_id, repository, errormsx)

        # New package
        if name == '' or name == 'new_ode':
            return self

        # Existing package
        else:
            name = unicode(name, 'utf8')
            result = self.children.get(name)
            if result is not None:
                return result
            else:
                if self.packagePath:
                    session.packageStore.addPackage(self.package)
                    self.bindNewPackage(self.package, session)
                    self.packagePath = None
                if session.uid in self.mainpages.keys():
                    if name in self.mainpages[session.uid].keys():
                        return self.mainpages[session.uid][name]
                # This will just raise an error
                log.error("child %s not found. uri: %s" % (name, request.uri))
                log.error("Session uid: %s, Mainpages: %s" % (session.uid, self.mainpages))
                return error.NoResource("No such child resource %(resource)s. Try again clicking %(link)s" % {
                                        "resource": name.encode('utf-8'),
                                        "link": "<a href='%s' target='_top'>%s</a>" % ('/', 'eXe')})

    def bindNewPackage(self, package, session):
        """
        Binds 'package' to the appropriate url
        and creates a MainPage instance for it
        and a directory for the resource files
        """
        log.debug("Mainpages: %s" % self.mainpages)
        session_mainpages = self.mainpages.get(session.uid)
        if session_mainpages:
            session_mainpages[package.name] = MainPage(None, package, session, self.webServer)
        else:
            self.mainpages[session.uid] = {package.name: MainPage(None, package, session, self.webServer)}
        log.debug("Mainpages: %s" % self.mainpages)

    def importOde(self, session, ode_id):
        """
        Import Package from Repository
        """
        response = self.integration.get_ode(ode_id)

        # Manage Response
        if response and response[0]:
            dict_response = response[1]
        elif response and not response[0]:
            return (False, 'Error in response: {}'.format(response[1]))
        else:
            return (False, 'No response')

        # Import package from Repository
        if dict_response['status'] == '0':
            package_data = base64.decodestring(dict_response['ode_file'])
            package_file_path = G.application.config.userResourcesDir / dict_response['ode_filename']

            # Save package in User ResourcesDir
            package_file = open(package_file_path, "wb")
            package_file.write(package_data)
            package_file.close()

            self.packagePath = package_file_path
                    
            # Load Package
            self.package = Package.load(self.packagePath)
            self.package.ode_id = ode_id
            self.package.ode_repository_uri = dict_response['ode_uri']

            if session.packageStore:
                session.packageStore.addPackage(self.package)
            else:
                session.packageStore = PackageStore()
                session.packageStore.addPackage(self.package)

            self.bindNewPackage(self.package, session)
            
            return (True, self.package.name)

        # Repository Error
        else:
            return (False, 'Repository Error: {}'.format(dict_response['description']))


    def render_GET(self, request):
        """
        Create a new package and redirect the webrowser to the URL for it
        """
        log.debug("render_GET" + repr(request.args))
        # Create new package
        session = request.getSession()
        template_base = self.config.templatesDir / (self.config.defaultContentTemplate + '.elt')
        
        if os.path.exists(template_base):
            package = session.packageStore.createPackageFromTemplate(template_base)
        else:
            package = session.packageStore.createPackage()

        if self.webServer.application.server and not session.user:
            request.setResponseCode(http.FORBIDDEN)
            return ''

        self.bindNewPackage(package, session)
        log.info("Created a new package name=" + package.name)
        # Tell the web browser to show it
        request.redirect(package.name.encode('utf8'))
        return ''
