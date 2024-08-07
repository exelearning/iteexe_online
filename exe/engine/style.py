#!/usr/bin/python
#-*- coding: utf-8 -*-

"""
JRJ: Representación de un estilo
(Display of styles)
"""


import logging
from exe.engine.persist   import Persistable
from xml.dom              import minidom
from exe                  import globals as G
import collections
import chardet
if hasattr(collections, 'OrderedDict'):
    OrderedDict = collections.OrderedDict
else:
    import ordereddict
    OrderedDict = ordereddict.OrderedDict

log = logging.getLogger(__name__)

# ===========================================================================
class Style(Persistable):
    """
    Clase base para todos los estilos
    (Base class for all styles)
    """

    # Atributos (attributes)
    # xml node : [ label , 0=textfield 1=textarea , order into form]
    _attributespre ={

                   'version': ['Version',0,3],
                   'compatibility': ['Compatibility',0,2],
                   'author': ['Author',1,4],
                   'author-url': ['Author URL',0,5],
                   'license': ['License',1,6],
                   'license-url': ['License URL',0,7],
                   'description': ['Description',1,1],
                   'extra-head': ['Extra head',1,8],
                   'edition-extra-head': ['Extra head (when editing)',1,8],
                   'jquery': ['Path to jQuery (if different)',0,10],
                   'extra-body': ['Extra body',1,9],
                   'edition-extra-body': ['Extra body (when editing)',1,9],
                   'name': ['Name',0,0]
                   }

    _attributesCode = ['extra-head', 'edition-extra-head', 'extra-body', 'edition-extra-body']
    _attributes= OrderedDict(sorted(_attributespre.items(), key=lambda t: t[1][2]))



    def __init__(self, styleDir):
        """Initialize a new Style"""
        log.debug("Creating Style")
        self._styleRootDir  = styleDir.dirname()
        if self._styleRootDir.split("/")[-2] == "webui":
            self._webRootPath   = "/style/"
        else:
            self._webRootPath   = "/style_user_{}/".format(G.application.config.username)
        self._webPath       = self._webRootPath+styleDir.basename()
        self._styleDir      = styleDir
        self._name          = styleDir.basename()
        self._dirname       = styleDir.basename()
        self._version       = '0.0'
        self._compatibility = '7.1'
        self._author        = ''
        self._author_url    = ''
        self._license       = ''
        self._license_url   = ''
        self._description   = ''
        self._extra_head    = ''
        self._edition_extra_head    = ''
        self._jquery        = True
        self._extra_body    = ''
        self._edition_extra_body    = ''
        self._validConfig   = False
        self._isStyleDesignerCompatible = False
        self._valid         = False
        self._checkValid()
        self._loadStyle()

    def _loadStyle(self):
        try:
            if self._valid:
                configStyle = self._styleDir/'config.xml'
                if configStyle.exists():
                    configdata = open(configStyle).read()
                    try:
                        newconfigdata = configdata.decode()
                    except UnicodeDecodeError:
                        configcharset = chardet.detect(configdata)
                        newconfigdata = configdata.decode(configcharset['encoding'], 'replace')
                    xmldoc = minidom.parseString(newconfigdata)
                    theme = xmldoc.getElementsByTagName('theme')
                    if (len(theme) > 0):
                        for attribute in self._attributes.keys():
                            rpattribute='_'+attribute.replace('-', '_')
                            attr = theme[0].getElementsByTagName(attribute)
                            if (len(attr) > 0):
                                attrName = attr[0].nodeName
                                if (len(attr[0].childNodes) > 0):
                                    attrValue = attr[0].firstChild.nodeValue
                                    if hasattr(self, rpattribute):
                                        setattr(self, rpattribute, attrValue)

                    self._validConfig = True

                    # Check it is compatible with the Style Designer
                    cssFile = self._styleDir/'content.css'
                    if cssFile.exists():
                        cssFileContent = open(cssFile).read()
                        requiredString = "/* eXeLearning Style Designer Compatible Style */";

                        position = cssFileContent.find(requiredString)                        
                        if (position==0):
                            self._isStyleDesignerCompatible = True
        except:
            self._valid=False

    def _checkValid(self):
        content = self._styleDir/'content.css'
        if content.exists():
            self._valid = True
        else:
            self._valid = False


    # Métodos públicos de acceso
    # (Public access methods)
    def isValid(self):
        return self._valid

    def hasValidConfig(self):
        return self._validConfig

    def isStyleDesignerCompatible(self):
        return self._isStyleDesignerCompatible

    def get_style_root_dir(self):
        return self._styleRootDir

    def get_web_root_path(self):
        return self._webRootPath

    def get_web_path(self):
        return self._webPath

    def get_style_dir(self):
        return self._styleDir

    def get_name(self):
        return _(self._name)

    def get_dirname(self):
        return self._dirname

    def get_version(self):
        return self._version

    def get_compatibility(self):
        return self._compatibility

    def get_author(self):
        return self._author

    def get_author_url(self):
        return self._author_url

    def get_license(self):
        return self._license

    def get_license_url(self):
        return self._license_url

    def get_description(self):
        return self._description

    def get_extra_head(self):
        return self._extra_head

    def get_edition_extra_head(self):
        return self._edition_extra_head

    def get_jquery(self):
        return self._jquery

    def get_extra_body(self):
        return self._extra_body

    def get_edition_extra_body(self):
        return self._edition_extra_body


    def renderPropertiesHTML(self):
        html = ''
        for attribute in self._attributes.keys():
            if hasattr(self, '_'+attribute.replace('-', '_')) and getattr(self, '_'+attribute.replace('-', '_')) != '':
                html += '<p><strong>' + _(self._attributes[attribute]) + ': </strong>'
                if attribute in self._attributesCode:
                    html += '<code>' + getattr(self, '_'+attribute.replace('-', '_')).replace('<', '&lt') + '</code>' + '</p>'
                else:
                    html += getattr(self, '_'+attribute.replace('-', '_')).replace('\n','<br/>') + '</p>'
        return html

    def renderPropertiesJSON(self):
        properties = []
        for attribute in self._attributes.keys():
                if attribute in self._attributesCode:
                    value = getattr(self, '_'+attribute.replace('-', '_')).replace('"',"'")
                else:
                    value = getattr(self, '_'+attribute.replace('-', '_'))
                properties.append({'name': _(self._attributes[attribute][0]),'value':value,'format':self._attributes[attribute][1],'nxml':attribute})
        #add dirname to properties
        properties.append({'name':'dirname', 'nxml':'dirname','value':self._dirname,'format':2})
        return properties

    def __str__(self):
        string = ''
        for attribute in self._attributes.keys():
            if hasattr(self, '_'+attribute.replace('-', '_')) and getattr(self, '_'+attribute.replace('-', '_')) != '':
                string += _(self._attributes[attribute]) + ': ' + getattr(self, '_'+attribute.replace('-', '_')) + '\n'
        return string

    def __cmp__(self, other):
        return cmp(self._name, other._name)


# ==========================================
