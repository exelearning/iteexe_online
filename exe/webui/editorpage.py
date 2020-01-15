# ===========================================================================
# eXe
# Copyright 2004-2006, University of Auckland
# Copyright 2004-2007 eXe Project, http://eXeLearning.org/
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
The EditorPage is responsible for managing user created iDevices
"""

import logging
from twisted.web.resource      import Resource
from exe.webui                 import common
from exe.engine.genericidevice import GenericIdevice
from exe.webui.editorpane      import EditorPane
from exe.webui.renderable      import RenderableResource
from exe.engine.package        import Package
from exe.engine.path           import Path
from exe.engine.field          import MultimediaField
from cgi                       import escape
from exe                       import globals as G

log = logging.getLogger(__name__)


class EditorPage(RenderableResource):
    """
    The EditorPage is responsible for managing user created iDevices
    create / edit / delete
    """

    name = 'editor'

    def __init__(self, parent):
        """
        Initialize
        """
        RenderableResource.__init__(self, parent)
        self.editorPane   = {}
        self.url          = ""
        self.elements     = []
        self.isNewIdevice = True
        #JR: Anado esta variable para que los genericos no se puedan previsualizar
        self.isGeneric    = False
        self.message      = ""
        
    def getChild(self, name, request):
        """
        Try and find the child for the name given
        """
        if name == "":
            return self
        else:
            return Resource.getChild(self, name, request)


    def process(self, request):
        """
        Process current package 
        """
        log.debug("process " + repr(request.args))

        if not G.application.config.username in self.editorPane:
            self.editorPane[G.application.config.username] = EditorPane(self)

        if "action" in request.args:

            self.editorPane[G.application.config.username].process(request,"old")

            if request.args["action"][0] == "changeIdevice":
                genericIdevices = G.application.ideviceStore.generic

                
                if not self.isNewIdevice:
                    ideviceId = self.editorPane[G.application.config.username].idevice.id
                    for idevice in genericIdevices:
                        if idevice.id == ideviceId:
                            break
                
                selected_idevice = request.args["object"][0].decode("utf-8")

                self.isGeneric = False
                for idevice in genericIdevices:
                    if idevice.title == selected_idevice:
                        self.isGeneric = True
                        self.isNewIdevice = False
                        self.editorPane[G.application.config.username].setIdevice(idevice)               
                        self.editorPane[G.application.config.username].process(request, "new")
                        break
                
        
            if request.args["action"][0] == "newIdevice" or "new" in request.args:
                self.__createNewIdevice(request)
            

            if request.args["action"][0] == "deleteIdevice":
                G.application.ideviceStore.delIdevice(self.editorPane[G.application.config.username].idevice)
                #Lo borramos tambien de la lista factoryiDevices
                idevice = self.editorPane[G.application.config.username].idevice
                exist = False
                for i in G.application.ideviceStore.getFactoryIdevices():
                    if i.title == idevice.title:
                        idevice.id = i.id
                        exist = True
                        break
                if exist:
                    G.application.ideviceStore.factoryiDevices.remove(idevice)
                G.application.ideviceStore.save()
                self.message = _("Done")
                self.__createNewIdevice(request) 
            
            if request.args["action"][0] == "new":
                if self.editorPane[G.application.config.username].idevice.title == "":
                    self.message = _("Please enter an idevice name.")
                else:
                    newIdevice = self.editorPane[G.application.config.username].idevice.clone()
                    #TODO could IdeviceStore set the id in addIdevice???
                    newIdevice.id = G.application.ideviceStore.getNewIdeviceId()
                    G.application.ideviceStore.addIdevice(newIdevice)
                    self.editorPane[G.application.config.username].setIdevice(newIdevice)
                    G.application.ideviceStore.save()
                    self.message = _("Settings Saved")
                    self.isNewIdevice = False
                
            if request.args["action"][0] == "save": 
                genericIdevices = G.application.ideviceStore.generic
                for idevice in genericIdevices:
                    if idevice.title == self.editorPane[G.application.config.username].idevice.title:
                        break
                copyIdevice = self.editorPane[G.application.config.username].idevice.clone()
                self.__saveChanges(idevice, copyIdevice)
                G.application.ideviceStore.save()
                self.message = _("Settings Saved")
            
            if request.args["action"][0] == "export":          
                filename = request.args["pathpackage"][0]
                self.__exportIdevice(filename)
            
            if request.args["action"][0] == "import":
                filename = request.args["pathpackage"][0]
                self.__importIdevice(filename)
        else:
            # New iDevice by default
            self.isNewIdevice = True
            self.editorPane[G.application.config.username].setIdevice(GenericIdevice("", "", "", "", ""))
            self.editorPane[G.application.config.username].process(request, "old")
        

            
    def __createNewIdevice(self, request):
        """
        Create a new idevice and add to idevicestore
        """
        idevice = GenericIdevice("", "", "", "", "")
        idevice.icon = ""
        idevice.id = G.application.ideviceStore.getNewIdeviceId()
        self.editorPane[G.application.config.username].setIdevice(idevice)
        self.editorPane[G.application.config.username].process(request, "new")      
        self.isNewIdevice = True
          
    def __saveChanges(self, idevice, copyIdevice):
        """
        Save changes to generic idevice list.
        """
        idevice.title    = copyIdevice._title
        idevice.author   = copyIdevice._author
        idevice.purpose  = copyIdevice._purpose
        idevice.tip      = copyIdevice._tip
        idevice.fields   = copyIdevice.fields
        idevice.emphasis = copyIdevice.emphasis
        idevice.icon     = copyIdevice.icon
        idevice.systemResources = copyIdevice.systemResources 
        
    def __importIdevice(self, filename):
        
        """
        import the idevices which are not existed in current package from another package
        """
        try:       
            newPackage = Package.load(filename)
        except:
            self.message = _("Sorry, wrong file format.")
            return
        
        if newPackage:   
            newIdevice = newPackage.idevices[-1].clone()
            for currentIdevice in G.application.ideviceStore.generic:
                if newIdevice.title == currentIdevice.title:
                    newIdevice.title += "1"
                    break
            G.application.ideviceStore.addIdevice(newIdevice) 
            G.application.ideviceStore.save()
        else:
            self.message = _("Sorry, wrong file format.")
        
    def __exportIdevice(self, filename):
        """
        export the current generic idevices.
        """
        if not filename.endswith('.idp'):
            filename = filename + '.idp'
        name = Path(filename).namebase
        package = Package(name)
        package.idevices.append(self.editorPane[G.application.config.username].idevice.clone())
        package.save(filename)
        
        
    def render_GET(self, request):
        """Called for all requests to this object"""
        
        # Processing 
        log.debug("render_GET")
        self.process(request)
        
        # Rendering
        html  = common.docType()
        html += "<html xmlns=\"http://www.w3.org/1999/xhtml\">\n"
        html += "<head>\n"
        html += "<style type=\"text/css\">\n"
        html += "@import url(/css/exe.css);\n"
        html += '@import url(/style/base.css);\n'
        html += "@import url(/style/standardwhite/content.css);</style>\n"
        html += '<script type="text/javascript" src="/scripts/authoring.js">'
        html += '</script>\n'
        html += '<script type="text/javascript" src="/scripts/common.js">'
        html += '</script>\n'
        html += '<script type="text/javascript" src="/scripts/editor.js">'
        html += '</script>\n'
        html += "<title>"+_("eXe : elearning XHTML editor")+"</title>\n"
        html += "<meta http-equiv=\"content-type\" content=\"text/html; "
        html += " charset=UTF-8\"></meta>\n";
        html += "</head>\n"
        html += "<body>\n"
        html += "<div id=\"main\"> \n"     
        html += "<form method=\"post\" action=\""+self.url+"\" "
        html += "id=\"contentForm\" >"  
        html += common.hiddenField("action")
        html += common.hiddenField("object")
        html += common.hiddenField("isChanged", "1") 
        if self.message != '':
            html += "<script>Ext.Msg.alert('"+_('Info')+"', '"+self.message+"');</script>"
        html += "<div id=\"editorButtons\"> \n"     
        html += self.renderList()
        html += self.editorPane[G.application.config.username].renderButtons(request)
        if self.isNewIdevice:
            html += "<br/>" + common.submitButton("delete", _("Delete"), 
                                                        False)
        else:
            html += '<br /><input type="button" class="button" onclick="deleteIdevice()" value="'+_("Delete")+'" />'
        html += '<br/><input class="button" type="button" name="save" '
        title = "none"
        if self.editorPane[G.application.config.username].idevice.edit == False:
            title = self.editorPane[G.application.config.username].idevice.title
            title = title.replace(" ", "+")
        html += 'onclick=saveIdevice("%s") value="%s"/>' % (escape(title), _("Save"))
        html += u'<br/><input class="button" type="button" name="import" ' 
        html += u' onclick="importPackage(\'package\')" value="%s" />'  % _("Import iDevice")
        html += u'<br/><input class="button" type="button" name="export" '
        html += u'onclick="exportPackage(\'package\',\'%d\')"' % self.isNewIdevice
        html += u' value="%s" />'  % _("Export iDevice")
        html += u'<br/><input class="button" type="button" name="quit" '
        #html += u'onclick="parent.Ext.getCmp(\'ideviceeditorwin\').close()"'        
        html += u'onclick="quitDialog()"'  
        html += u' value="%s" />\n'  % _("Quit")
        html += common.hiddenField("pathpackage")
        html += "</fieldset>"
        html += "</div>\n"
        html += self.editorPane[G.application.config.username].renderIdevice(request)
        html += "</div>\n"
        html += "<br/></form>\n"
        html += "</body>\n"
        html += "</html>\n"
        return html.encode('utf8')
    render_POST = render_GET


    def renderList(self):
        """
        Render the list of generic iDevice
        """
        html  = "<fieldset><legend><b>" + _("Edit")+ "</b></legend>"
        html += '<select onchange="submitIdevice();" name="ideviceSelect" id="ideviceSelect">\n'
        html += "<option value = \"newIdevice\" "
        if self.isNewIdevice:
            html += "selected "
        html += ">"+ _("New iDevice") + "</option>"
        for prototype in G.application.ideviceStore.generic:
            html += "<option value=\""+prototype.title+"\" "
            if self.editorPane[G.application.config.username].idevice.id == prototype.id:
                html += "selected "
            title = prototype.title
            if len(title) > 16:
                title = title[:16] + "..."
            html += ">" + title + "</option>\n"

        html += "</select> \n"
        html += "</fieldset>\n"
        self.message = ""
        return html
