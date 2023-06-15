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

import jwt
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
        # See if all out main pages are not showing
        # This is a twisted timer
        self.stopping = None
        self.integration = None
        self.mainpages = {}
        self.jwt_token=False

    def getChild(self, name, request):
        """
        Get the child page for the name given.
        This is called if our ancestors can't find our child.
        This is probably because the url is in unicode
        """
        session = request.getSession()
        # Provisional - TEST
        # Must be eliminated in the future
        # Login and import ode passing the parameter user
        if 'user' in request.args and request.args['user'][0]:
            session.setUser(request.args['user'][0])

        #TEST Moodle-eXe Integration
        self.integration = Integration()
        if self.integration.enabled_jwt == "1":
            if 'jwt_token' in request.args and request.args['jwt_token'][0]:
                self.jwt_token=request.args['jwt_token'][0]
            else:
                if not self.jwt_token:
                    raise Exception('jwt_token not found')
            try:
                jwt.decode(self.jwt_token,self.integration.jwt_secret_key, algorithms=self.integration.jwt_secret_hash)
            except Exception as e:
                return error.ForbiddenResource("JWT not valid")
        
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
            if not self.integration:
                self.integration = Integration()
            if self.integration.repo_name:
                repository = self.integration.repo_name
            else:
                repository = 'Unknown Repository'
            self.webServer.importode = ImportOdePage(self.webServer.root, repository, edit_ode_id)
            request.refresh('import?ode_id={}'.format(edit_ode_id))
            return self.webServer.importode

        # Importing and redirection
        if name == 'import' and 'ode_id' in request.args:
            edit_ode_id = request.args['ode_id'][0]
            # Integration (in case the user accesses this url directly)
            if not self.integration:
                self.integration = Integration()
            # Repository URL
            if self.integration:
                repository = self.integration.repo_name
            else:
                repository = "Unknown"
            # Check if ode_id is empty
            if edit_ode_id:
                import_ode_response = self.importOde(session, edit_ode_id,self.jwt_token)
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

                    self.webServer.importode = ImportOdePage(
                        self.webServer.root, repository, edit_ode_id, error=errormsx)
                    return self.webServer.importode
            else:
                errormsx = "The ode_id field is empty"
                self.webServer.importode = ImportOdePage(
                    self.webServer.root, repository, "None", error=errormsx)
                return self.webServer.importode

        # New package
        if name == '' or name == 'new_ode':
            if not self.integration:
                self.integration = Integration()
            if self.integration.enabled_jwt == "1":
                if name == '' or (name == 'new_ode' and not 'jwt_token' in request.args):            
                    return error.ForbiddenResource("New package not allowed")
                else:
                    return self
            else:
                return self

        # Existing package
        else:
            name = unicode(name, 'utf8')
            result = self.children.get(name)
            if result is not None:
                return result
            else:
                if session.uid in self.mainpages.keys():
                    if name in self.mainpages[session.uid].keys():
                        if self.jwt_token:
                            if not self.mainpages[session.uid][name].jwt_token:
                                self.mainpages[session.uid][name].jwt_token=self.jwt_token
                        return self.mainpages[session.uid][name]
                # This will just raise an error
                log.error("child %s not found. uri: %s" % (name, request.uri))
                log.error("Session uid: %s, Mainpages: %s" % (session.uid, self.mainpages))
                if not self.integration:
                    return error.NoResource("No such child resource %(resource)s. Try again clicking %(link)s" % {
                                        "resource": name.encode('utf-8'),
                                        "link": "<a href='%s' target='_top'>%s</a>" % ('/', 'eXe')})
                else:
                    return error.ForbiddenResource()

    def bindNewPackage(self, package, session,jwt_token=False):
        """
        Binds 'package' to the appropriate url
        and creates a MainPage instance for it
        and a directory for the resource files
        """
        log.debug("Mainpages: %s" % self.mainpages)

        session_mainpages = self.mainpages.get(session.uid)
        if session_mainpages:
            session_mainpages[package.name] = MainPage(None, package, session, self.webServer,jwt_token)
        else:
            self.mainpages[session.uid] = {package.name: MainPage(None, package, session, self.webServer,jwt_token)}
        log.debug("Mainpages: %s" % self.mainpages)

    def importOde(self, session, ode_id,jwt_token=False):
        """
        Import Package from Repository
        """
        response = self.integration.get_ode(ode_id,ode_user=session.user.name,jwt_token=jwt_token)
        # Manage Response
        if response and response[0]:
            dict_response = response[1]
        elif response and not response[0]:
            return (False, 'Error in response: {}'.format(response[1]))
        else:
            return (False, 'No response')

        # Import package from Repository
        if dict_response['status'] == '0':
            filename = dict_response['ode_filename']
            if '.zip' in filename:
                filename = filename[:-4]+'.elp'
            package_data = base64.decodestring(dict_response['ode_file'])
            package_file_path = session.user.root / filename

            # Save package in User ResourcesDir
            with open(package_file_path, 'wb') as package_file:
                # Write package
                try:
                    package_file.write(package_data)
                    write_error = False
                except:
                    write_error = True

            if package_file_path.exists() and not write_error:
                tmppackage = Package.load(package_file_path)
                newfile = session.user.root / tmppackage.name + ".elp"
                tmppackage.save(newfile)
                package_file_path = newfile
                tmppackage = None
                # Load Package and add ode_id and repository_url
                package = Package.load(package_file_path)
                package.ode_id = ode_id
                package.ode_repository_uri = self.integration.repo_home_url

                session.packageStore.addPackage(package)
                self.bindNewPackage(package, session,jwt_token)

                log_add_package_params = {
                    'session_user': session.user.name,
                    'package_ode_id':package.ode_id,
                    'package_ode_filename': package.name,
                    'package_path': package_file_path,
                    'ode_ide': dict_response['ode_id'],
                    'ode_uri': dict_response['ode_uri'],
                    'ode_filename': dict_response['ode_filename'],
                }
                self.integration.log_info_integration(
                    info='add_package_to_session:Package.load()',params=log_add_package_params)

                return (True, package.name)

            else:
                return (False, 'Error saving package to user directory')


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

        if not session.packageStore:
            session.packageStore = PackageStore()

        if os.path.exists(template_base):
            package = session.packageStore.createPackageFromTemplate(template_base, is_new_package=True)
        else:
            package = session.packageStore.createPackage()

        if self.webServer.application.server and not session.user:
            request.setResponseCode(http.FORBIDDEN)
            return ''
        if not self.integration:
            self.integration = Integration()
        if self.integration.enabled_jwt == "1":
            if 'jwt_token' in request.args and request.args['jwt_token'][0]:
                self.jwt_token=request.args['jwt_token'][0]
            else:
                if not self.jwt_token:
                    raise Exception('jwt_token not found')
            try:
                jwt.decode(self.jwt_token,self.integration.jwt_secret_key, algorithms=self.integration.jwt_secret_hash)
            except Exception as e:
                raise Exception('Error in the secret key. No match')

        self.bindNewPackage(package, session,self.jwt_token)
        log.info("Created a new package name=" + package.name)
        # Tell the web browser to show it
        request.redirect(package.name.encode('utf8'))
        return ''
