// ===========================================================================
// eXe
// Copyright 2012, Pedro Peña Pérez, Open Phoenix IT
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
//===========================================================================

Ext.define('eXe.controller.Toolbar', {
    extend: 'Ext.app.Controller',
    requires: [
        'eXe.view.forms.PreferencesPanel',
        'eXe.view.forms.StyleManagerPanel',
        'eXe.view.forms.TemplateManagerPanel',
        'eXe.view.forms.ValidatePanel'
    ],
	refs: [{
        ref: 'recentMenu',
        selector: '#file_recent_menu'
    },{
    	ref: 'stylesMenu',
    	selector: '#styles_menu'
    },{
    	ref: 'stylesMenuAdvanced',
    	selector: '#styles_menu_advanced'
    },{
    	ref: 'templatesMenu',
    	selector: '#templates_menu'
    }
    ],
    init: function() {
        this.control({
            '#file': {
                click: this.focusMenu
            },
            '#tools': {
                click: this.focusMenu
            },
            '#styles_button': {
                click: this.focusMenu
            },
            '#templates_button': {
                click: this.focusMenu
            },
            '#help': {
                click: this.focusMenu
            },
        	'#file_new': {
        		click: this.fileNew
        	},
            '#file_new_window': {
                click: this.fileNewWindow
            },
        	'#file_open': {
        		click: this.fileOpen
            },
            '#elp_import': {
                click: this.importOpenPackage
            },
        	'#file_recent_menu': {
        		beforerender: this.recentRender
            },
            '#advanced_toggler':{
                render : this.eXeUIversionCheck
            },
        	'#file_recent_menu': {
        		beforerender: this.recentRender
        	},
        	'#styles_button': {
        		beforerender: this.stylesRender
        	},
        	'#styles_button_advanced': {
        		beforerender: this.stylesRenderAdvanced
        	},
        	'#templates_button': {
        		beforerender: this.templatesRender
        	},
        	'#file_recent_menu > menuitem': {
        		click: this.recentClick
            },
            '#templates_button': {
        		beforerender: this.templatesRender
            },
        	'#styles_button': {
                beforerender: this.stylesRender,
                click: { fn: this.stylesRender, async: false }
            },
            '#styles_button_advanced_wrapper': {
                click: { fn: this.stylesRenderAdvanced, async: false }
            },
        	'#styles_button_advanced': {
                beforerender: this.stylesRenderAdvanced
            },
        	'#styles_menu > menuitem': {
        		click: this.stylesClick
        	},
        	'#styles_menu_advanced > menuitem': {
        		click: this.stylesClickAdvanced
        	},
        	'#templates_menu > menuitem': {
        		click: this.templatesClick
        	},
        	'#file_save': {
        		click: this.fileSave
        	},
        	'#file_save_as': {
        		click: this.fileSaveAs
        	},
        	'#template_save': {
        		click: this.templateSave
        	},
            '#file_print': {
                click: this.filePrint
            },
            '#file_export_cc': {
                click: { fn: this.processExportEvent, exportType: "commoncartridge" }
            },
            '#file_export_scorm12': {
                click: { fn: this.processExportEvent, exportType: "scorm1.2" }
            },
            '#file_export_scorm2004': {
                click: { fn: this.processExportEvent, exportType: "scorm2004" }
            },
            '#file_export_agrega': {
                click: { fn: this.processExportEvent, exportType: "agrega" }
            },
            '#file_export_ims': {
                click: { fn: this.processExportEvent, exportType: "ims" }
            },
            '#file_export_website': {
                click: { fn: this.processExportEvent, exportType: "webSite" }
            },
            // Advanced user
            '#file_export_scorm': {
                click: { fn: this.processExportEvent, exportType: "scorm1.2" }
            },
            '#file_export_website_b': {
                click: { fn: this.processExportEvent, exportType: "zipFile" }
            },
            '#file_export_singlepage_b': {
                click: { fn: this.processExportEvent, exportType: "singlePage" }
            },
            // / Advanced user
            '#file_export_procomun': {
                click: { fn: this.processExportEvent, exportType: "procomun" }
            },
            '#file_export_zip': {
                click: { fn: this.processExportEvent, exportType: "zipFile" }
            },
            '#file_export_singlepage': {
                click: { fn: this.processExportEvent, exportType: "singlePage" }
            },
            '#file_export_text': {
                click: { fn: this.processExportEvent, exportType: "textFile" }
            },
            '#file_export_epub3': {
                click: { fn: this.processExportEvent, exportType: "epub3" }
            },
            '#file_export_xliff': {
                click: this.exportXliff
            },
            '#file_import_xliff': {
                click: this.importXliff
            },
            '#file_import_html': {
                click: this.importHtml
            },
            '#file_import_lom': {
                click: { fn: this.importLom, metadataType: "lom" }
            },
            '#file_import_lomes': {
                click: { fn: this.importLom, metadataType: "lomEs" }
            },
            '#file_insert': {
                click: this.insertPackage
            },
            '#file_extract': {
                click: {fn: this.extractPackage, all: 0 }
            },
            '#file_extract_all': {
                click: {fn: this.extractPackage, all: 1 }
            },
            '#file_extract_SCORM': {
                click: this.extractSCORM 
            },
            '#file_quit': {
                click: this.fileQuit
            },
            '#tools_idevice': {
                click: this.toolsIdeviceEditor
            },
            '#tools_stylemanager': {
                click: this.toolsStyleManager
            },
            '#tools_templatemanager': {
                click: this.toolsTemplateManager
            },
            '#tools_preferences': {
                click: this.toolsPreferences
            },
            '#tools_resourcesreport': {
            	click: { fn: this.processExportEvent, exportType: "csvReport" }
            },
            '#tools_preview': {
                click: { fn: this.processBrowseEvent, url: location.href + '/preview' }
            },
            '#tools_preview_button': {
                click: { fn: this.processBrowseEvent, url: location.href + '/preview' }
            },
            '#file_export_procomun_b': {
                click: { fn: this.processExportEvent, exportType: "procomun" }
            },            
            '#logout_user_buttom': {
                click: this.doLogout
            },
            '#tools_refresh': {
                click: this.toolsRefresh
            },
            '#help_tutorial': {
                click: { fn: this.processBrowseEvent, url: 'https://exelearning.net/en/help/' }
            },
            '#help_assistant': {
                click: this.assistantPage
            },
            '#help_assistant_simplified': {
                click: this.assistantPage
            },
             '#help_notes': {
                click: { fn: this.releaseNotesPage }
            },
            '#help_legal': {
                click: this.legalPage
            },
            '#help_website': {
                click: { fn: this.processBrowseEvent, url: 'https://exelearning.net/en/' }
            },
            '#help_issue': {
                click: { fn: this.processBrowseEvent, url: 'https://github.com/exelearning/iteexe/issues' }
            },
            '#help_forums': {
                click: { fn: this.processBrowseEvent, url: 'https://exelearning.net/en/forums-eng/' }
            },
            '#help_about': {
                click: this.aboutPage
            }
        });

        this.keymap_config = [
			{
				key: Ext.EventObject.N,
				ctrl: true,
                alt: true,
				handler: function() {
				 this.fileNew();
				},
				scope: this,
				defaultEventAction: "stopEvent"
			},
			{
				key: Ext.EventObject.W,
				ctrl: true,
                alt: true,
				handler: function() {
				 this.fileNewWindow();
				},
				scope: this,
				defaultEventAction: "stopEvent"
			},
			{
			     key: Ext.EventObject.O,
			     ctrl: true,
			     handler: function() {
			          this.fileOpen();
			     },
			     scope: this,
			     defaultEventAction: "stopEvent"
			},
			{
				key: Ext.EventObject.S,
				ctrl: true,
				handler: function() {
				 this.fileSave();
				},
				scope: this,
				defaultEventAction: "stopEvent"
			},
			{
			     key: Ext.EventObject.P,
			     ctrl: true,
			     handler: function() {
			          this.filePrint();
			     },
			     scope: this,
			     defaultEventAction: "stopEvent"
			},
			{
			     key: Ext.EventObject.Q,
			     ctrl: true,
			     handler: function() {
			          this.fileQuit();
			     },
			     scope: this,
			     defaultEventAction: "stopEvent"
			},
			{
			     key: Ext.EventObject.F,
			     alt: true,
			     handler: function() {
			          this.showMenu(Ext.ComponentQuery.query('#file')[0]);
			     },
			     scope: this,
			     defaultEventAction: "stopEvent"
			},
			{
			     key: Ext.EventObject.T,
			     alt: true,
			     handler: function() {
			          this.showMenu(Ext.ComponentQuery.query('#tools')[0]);
			     },
			     scope: this,
			     defaultEventAction: "stopEvent"
			},
			{
			     key: Ext.EventObject.S,
			     alt: true,
			     handler: function() {
			          var selector = '#styles_button';
			          if (document.body.className.indexOf("exe-advanced")!=-1) selector += '_advanced_wrapper';
			          this.showMenu(Ext.ComponentQuery.query(selector)[0]);
			     },
			     scope: this,
			     defaultEventAction: "stopEvent"
			},
			{
			     key: Ext.EventObject.H,
			     alt: true,
			     handler: function() {
			          this.showMenu(Ext.ComponentQuery.query('#help')[0]);
			     },
			     scope: this,
			     defaultEventAction: "stopEvent"
			},
            {
	            key: Ext.EventObject.F5,
	            handler: function() {
	                 this.toolsRefresh();
	            },
	            scope: this,
	            defaultEventAction: "stopEvent"
			}
        ];
        var keymap = new Ext.util.KeyMap(Ext.getBody(), this.keymap_config);
    },

    eXeUIversionCheck : function(){
        nevow_clientToServerEvent('eXeUIVersionCheck',this)
    },
    exeUIsetInitialStatus : function(value){
        advancedModePreferenceValue = value;
    },
    eXeUIGetSizeProject : function(){
        nevow_clientToServerEvent('eXeUIGetSizeProject',this)
    },
    eXeUIGetMaxSizeProject : function(){
        nevow_clientToServerEvent('eXeUIGetMaxSizeProject',this)
    },
    eXeUISetSizeProject : function(value){
        var e1 = Ext.getCmp("project_size");
        var t1 = value;
        e1.update(value);
        try {
            var e2 = Ext.getCmp("project_max_size");    
            if (typeof(e2)=='undefined'||typeof(e2.html)=='undefined'){
                return;
            }
            var t2 = e2.html;
            if (typeof(t2)=='undefined'||t2==""||t2=="undefined") {
                return;
            }
            var t = _("%s of %s");
                t = t.replace("%s",t1);
                t = t.replace("%s",t2);
            e1.setText(t);            
        }catch(e){}
    },
    eXeUISetMaxSizeProject : function(value){
        Ext.getCmp("project_max_size").update(value);
    },

    exeUIalert : function(){
        Ext.Msg.alert(
            _('Info'),
            _('Checking this option will show more elements in the menus (File, Tools...) and the Properties tab.')
        );

    },
    eXeUIversionSetStatus : function(newValue){
        eXe.app.getController("Toolbar").eXeUIGetSizeProject();
        var e = Ext.getCmp("project_size");
        if(e&&e.text&&e.text.indexOf("MB")>0){
            var t = e.text;
                t = t.split(" ");
                t = t[0];
            var projectSize = parseInt(t);
            if (isNaN(projectSize)) return;
            var projectMaxSize = parseInt(Ext.getCmp("project_max_size").html.replace(/[^0-9]/g,''));
            if (projectSize >= projectMaxSize){
                Ext.getCmp("project_size_label").addCls("max-size-exceeded");
                Ext.getCmp("project_size").addCls("max-size-exceeded");
                // Ext.getCmp("project_max_size").addCls("max-size-exceeded");
            }
            else {
                Ext.getCmp("project_size_label").removeCls("max-size-exceeded");
                Ext.getCmp("project_size").removeCls("max-size-exceeded");
                // Ext.getCmp("project_max_size").removeCls("max-size-exceeded");
            }
        }

        advancedModePreferenceValue = newValue;
        let descriptionLabel = Ext.DomQuery.select("label[for=pp_description]");
        let contentPanel = false; // The main content. It should always exist.
        let iframe = document.getElementsByTagName('iframe');
        if (iframe.length==1) {
            iframe = iframe[0];
            let doc = iframe.contentWindow.document;
            if (doc.body && typeof(doc.body.className)=="string" && doc.body.className!="") {
                contentPanel = doc.body;
            }
        }

        if (newValue == 0) {
            Ext.select("BODY").removeCls('exe-advanced');
            Ext.select("BODY").addCls('exe-simplified');
            // Remove the advanced CSS class from the content panel
            if (contentPanel!=false) {
                contentPanel.className = contentPanel.className.replace(" exe-advanced","");
                // If the current iDevice is a JavaScript one and has tabs, show the first one:
                if (typeof(iframe.contentWindow["$exeAuthoring"])!='undefined')  iframe.contentWindow.$exeAuthoring.iDevice.tabs.restart();
            }
            // Change some strings:
            if (descriptionLabel && descriptionLabel.length==1) descriptionLabel[0].innerHTML = _("General description") + ":";
            // Show Properties - Package
            let e1 = document.getElementById("eXePropertiesTab");
            if (e1) {
                let e2 = e1.getElementsByTagName("button");
                for (let i=0;i<e2.length;i++){
                    if (e2[i].className=="x-tab-center") {
                        let span = e2[i].getElementsByTagName("span");
                        if (span.length==2 && span[0].innerHTML==_("Package")) e2[i].click();
                    }
                }
            }
        } else {
            // Ext.util.Cookies.set('eXeUIversion', 'advanced');
            Ext.select("BODY").removeCls('exe-simplified');
            Ext.select("BODY").addCls('exe-advanced');
            // Add the advanced CSS class to the content panel
            if (contentPanel!=false && contentPanel.className.indexOf(' exe-advanced')==-1) contentPanel.className += ' exe-advanced';
            // Change some strings:
            if (descriptionLabel && descriptionLabel.length==1) descriptionLabel[0].innerHTML = _("General") + ":";
        }
        // Refresh some components
        try {
            Ext.getCmp("exe-viewport").doLayout();
        } catch(e) {}
    },
    focusMenu: function(button) {
        button.menu.focus();
    },

    showMenu: function(button) {
		button.showMenu();
        button.menu.focus();
    },

    fileNewWindow: function() {
        window.open("/");
    },

    assistantPage: function() {
        if (typeof(eXeAssistantPageIsOpen)!='undefined' && eXeAssistantPageIsOpen==true) {
            eXeAssistantPage.close(true);
            return;
        }
        eXeAssistantPage = new Ext.Window ({
            height: eXe.app.getMaxHeight(700),
            width: 650,
            height: 500,
            modal: false,
            minimizable: true,
            id: 'assistantwin',
            title: _("Assistant"),
            items: {
                xtype: 'uxiframe',
                src: '/tools/assistant',
                height: '100%'
            },
            listeners: {
                minimize: function(win,obj) {
                    var cls = document.body.className;
                    var elm = Ext.select("BODY");
                    if (cls.indexOf("exe-window-minified")==-1) elm.addCls('exe-window-minified');
                    else elm.removeCls('exe-window-minified');
                    Ext.getCmp("assistantwin").doLayout();
                },
                'close': function(){
                    eXeAssistantPageIsOpen = false;
                }
            }
        });
        eXeAssistantPageIsOpen = true;
        eXeAssistantPage.show();
    },

    aboutPage: function() {
        var about = new Ext.Window ({
          height: eXe.app.getMaxHeight(700),
          width: 420,
          modal: true,
          resizable: false,
          id: 'aboutwin',
          title: _("About"),
          items: {
              xtype: 'uxiframe',
              src: '/about',
              height: '100%'
          }
        });
        about.show();
    },

    releaseNotesPage: function() {
        var about = new Ext.Window ({
          height: eXe.app.getMaxHeight(700),
          width: 900,
          modal: true,
          resizable: false,
          id: 'releasenoteswin',
          title: _("Release notes"),
          items: {
              xtype: 'uxiframe',
              src: '/release-notes',
              height: '100%'
          }
        });
        about.show();
    },

    // jrf - legal notes
    legalPage: function() {
        var legalnotes = new Ext.Window ({
          height: eXe.app.getMaxHeight(700),
          width: 420,
          modal: true,
          resizable: false,
          id: 'legal',
          title: _("Legal Notes"),
          items: {
              xtype: 'uxiframe',
              src: '/legal',
              height: '100%'
          }
        });
        legalnotes.show();
    },

    browseURL: function(url) {
        nevow_clientToServerEvent('browseURL', this, '', url);
    },

    processBrowseEvent: function(menu, item, e, eOpts) {
        // this.browseURL(e.url)
        var html = document.getElementsByTagName("HTML");
            html = html[0];
        if (typeof(html.lang)=='string') {
            // Open eXeLearning.net in the right language
            var websiteTranslations = [
                'es',
                'ca',
                'eu',
                'gl'
            ];
            if (websiteTranslations.indexOf(html.lang)!=-1) {
				// URL list
				var i18n = {
					es : [
						"ayuda",
						"forums"
					],
					ca : [
						"ajuda",
						"forums-2"
					],
					eu : [
						"jaitsi",
						"forums-3"
					],
					gl : [
						"axuda",
						"forums-gl"
					]					
				}
				var base = "https://exelearning.net/";
				if (html.lang!="es") base += html.lang+"/";
				var url = i18n[html.lang];	
					
				if (e.url=="https://exelearning.net/en/help/") e.url = base+url[0]+"/";
				else if (e.url=="https://exelearning.net/en/") e.url = base;
				else if (e.url=="https://exelearning.net/en/forums-eng/") e.url = base+url[1]+"/";
            }
        }
        window.open(e.url)
    },

    toolsRefresh: function() {
        eXe.app.reload();
    },

    toolsPreferences: function(newVersionWarning) {
        var toolsPreferencesWasClosed = function(){}
        // Show the "New eXeLearning version" warning after closing the preferences dialog
        if (newVersionWarning==true) {
            toolsPreferencesWasClosed = function(){
                eXe.app.showNewVersionWarning();
            }
        }
        var preferences = new Ext.Window ({
	          height: 420,
	          width: 650,
	          modal: true,
	          id: 'preferenceswin',
	          title: _("Preferences"),
	          layout: 'fit',
	          items: [{
                xtype: 'preferences'
              }],
              listeners:{
                close: toolsPreferencesWasClosed
              }
	        }),
            formpanel = preferences.down('form');
        formpanel.load({url: 'preferences', method: 'GET'});
        preferences.show();
	},

    packagePropertiesCompletion: function(export_type, filename, properties) {
        // Create the window to ask for the values
        var validate = new Ext.Window({
            width: 650,
            modal: true,
            id: 'validatewin',
            title: _("Export"),
            layout: 'fit',
            items: [{
                xtype: 'validate',
                exportType: export_type,
                fileIsSaved: (filename != ''),
                shownProperties: properties.split(',')
            }]
        });

        // Get the form panel
        var formpanel = validate.down('form');

        // Preload the values for the form (in case a property has actually been established
        // but the value is not valid for the selected export type)
        formpanel.load({
            url: location.pathname + "/properties",
            params: formpanel.getForm().getFieldValues(),
            method: 'GET'
        });
        validate.show();
    },

    // Launch the iDevice Editor Window
	toolsIdeviceEditor: function() {
		// To review
		return false;
		// / To review
        var editor = new Ext.Window ({
          height: eXe.app.getMaxHeight(700),
          width: 800,
          modal: true,
          id: 'ideviceeditorwin',
          title: _("iDevice Editor"),
          items: {
              xtype: 'uxiframe',
              src: '/editor',
              height: '100%'
          },
          listeners: {
            'beforeclose': function(win) {
                Ext.Msg.show( {
                    title: _('Confirm'),
                    msg: _('If you have made changes and have not saved them, they will be lost. Do you really want to quit?'),
                    //scope: this,
                    //modal: true,
                    buttons: Ext.Msg.YESNO,
                    fn: function(button) {
                        if (button === 'yes') {
                            editor.doClose();
                        }
                    }
                });
                return false;
            }
          }
        });
        editor.show();
	},

	// JRJ: Launch the Style Manager Window
	toolsStyleManager: function() {
        var stylemanager = new Ext.Window ({
          maxHeight: eXe.app.getMaxHeight(800),
          width: 500,
          modal: true,
          autoShow: true,
          autoScroll: true,
          id: 'stylemanagerwin',
          title: _("Style Manager"),
          layout: 'fit',
          items: {
              xtype: 'stylemanager'
          }
        });
        stylemanager.show();
	},
	// Launch the Template Manager
	toolsTemplateManager: function() {
        var templatemanager = new Ext.Window ({
          maxHeight: eXe.app.getMaxHeight(800),
          width: 500,
          modal: true,
          autoShow: true,
          autoScroll: true,
          id: 'templatemanagerwin',
          title: _("Template Manager"),
          layout: 'fit',
          items: {
              xtype: 'templatemanager'
          }
        });
        templatemanager.show();
	},

    fileQuit: function() {
		Ext.Msg.show( {
			title: _('Confirm'),
			msg: _('Exit without saving changes and go back to %s (home page)?').replace("%s",config['publishLabel']),
			//scope: this,
			//modal: true,
			buttons: Ext.Msg.YESNO,
			fn: function(button) {
				if (button === 'yes') {
					eXe.app.getController('Toolbar').saveWorkInProgress()
					Ext.util.Cookies.clear('eXeSaveReminderPreference');
					eXe.app.quitWarningEnabled = false;
					Ext.get('loading-mask').fadeIn();
					Ext.get('loading').show();
					window.location.href = config['publishHomeURL'];
				}
			}
		});
	},

    doQuit: function() {
        Ext.util.Cookies.clear('eXeSaveReminderPreference');
        eXe.app.quitWarningEnabled = false;
        nevow_clientToServerEvent('quit', this, '');
        Ext.get('loading-mask').fadeIn();
        Ext.get('loading').show();
    },

    doLogout: function() {
        Ext.util.Cookies.clear();
        eXe.app.quitWarningEnabled = false;
        if (window.config.saml == 1) {
            // saml (google) logout
            nevow_clientToServerEvent('logout', this, '');
            /*
            var google_logout_url = "https://www.google.com/accounts/Logout";
            gw = window.open(google_logout_url);
            */
            /*
            var google_logout_url = "https://www.google.com/accounts/Logout";
            var google_appengine_url = "https://appengine.google.com/_ah/logout";
            var continue_get = "?continue=";
            window.location.href = google_logout_url+continue_get+google_appengine_url+continue_get+window.origin+"/quit"
            */
        } else {
            // htpasswd logout
            url = window.origin.split("//");
            ventana = window.open(url[0]+"//logout@"+url[1]);
            ventana.close();
            nevow_clientToServerEvent('logout', this, '');
            window.location.href = window.origin;
        }
    },

    insertPackage: function() {
        var f = Ext.create("eXe.view.filepicker.FilePicker", {
            type: eXe.view.filepicker.FilePicker.modeOpen,
            title: _("Select package to insert"),
            remote: true,
            modal: true,
            scope: this,
            callback: function(fp) {
                if (fp.status == eXe.view.filepicker.FilePicker.returnOk) {
                    if (!fp.file.loaded)  {
                        fp.file.loaded = true;
                        Ext.Msg.wait(new Ext.Template(_('Inserting package: {filename}')).apply({filename: fp.file.path}));
                        nevow_clientToServerEvent('insertPackage', this, '', fp.file.path);
                    }
                }
            }
        });
        f.appendFilters([
            { "typename": _("eXe Package Files"), "extension": "*.elp", "regex": /.*\.elp$/ },
            { "typename": _("All Files"), "extension": "*.*", "regex": /.*$/ }
            ]
        );
        f.show();
    },
    
    importOpenPackage: function() {
        var fp = Ext.create("eXe.view.filepicker.FilePicker", {
            type: eXe.view.filepicker.FilePicker.modeOpen,
            title: _("Select package to import and Open"),
            remote: true,
            modal: true,
            scope: this,
            callback: function(fp) {
                if (fp.status == eXe.view.filepicker.FilePicker.returnOk) {
                    if (!fp.file.loaded)
                    {
                        fp.file.loaded = true;
                        Ext.Msg.wait(new Ext.Template(_('Loading package: {filename}')).apply({filename: fp.file.name}));
                        nevow_clientToServerEvent('loadPackage', this, '', fp.file.path);
                    }
                }
            }
        });
        fp.appendFilters([
            { "typename": _("eXe Package Files"), "extension": "*.elp", "regex": /.*\.elp$/ },
            { "typename": _("All Files"), "extension": "*.*", "regex": /.*$/ }
        ]);
        fp.show();
    },

	extractPackage: function(menu, item, e) {
        var f = Ext.create("eXe.view.filepicker.FilePicker", {
            type: eXe.view.filepicker.FilePicker.modeSave,
            title: _("Save extracted package as"),
            remote: true,
            modal: true,
            scope: this,
            callback: function(fp) {
                if (fp.status == eXe.view.filepicker.FilePicker.returnOk || fp.status == eXe.view.filepicker.FilePicker.returnReplace) {
                    Ext.Msg.wait(new Ext.Template(_('Extracting package: {filename}')).apply({filename: fp.file.path}));
                    if (e && e.all && e.all == 1) {
                        nevow_clientToServerEvent('extractPackage', this, '', fp.file.path, fp.status == eXe.view.filepicker.FilePicker.returnReplace, e.all)
                    } else {
                        nevow_clientToServerEvent('extractPackage', this, '', fp.file.path, fp.status == eXe.view.filepicker.FilePicker.returnReplace)
                    }
                }
            }
        });
        f.appendFilters([
            { "typename": _("eXe Package Files"), "extension": "*.elp", "regex": /.*\.elp$/ },
            { "typename": _("All Files"), "extension": "*.*", "regex": /.*$/ }
            ]
        );
        f.show();
	},

    extractSCORM: function() {
        var f = Ext.create("eXe.view.filepicker.FilePicker", {
            type: eXe.view.filepicker.FilePicker.modeSave,
            title: _("Save extracted SCORM package as"),
            remote: true,
            modal: true,
            scope: this,
            callback: function(fp) {
                if (fp.status == eXe.view.filepicker.FilePicker.returnOk || fp.status == eXe.view.filepicker.FilePicker.returnReplace) {
                    Ext.Msg.wait(new Ext.Template(_('Extracting package: {filename}')).apply({filename: fp.file.path}));
                        nevow_clientToServerEvent('extractSCORM', this, '', fp.file.path, fp.status == eXe.view.filepicker.FilePicker.returnReplace)
               }   
            }
        });
        f.appendFilters([
            { "typename": _("SCORM Files"), "extension": "*.zip", "regex": /.*\.zip$/ },
            { "typename": _("All Files"), "extension": "*.*", "regex": /.*$/ }
            ]
        );
        f.show();
	},

    importHtml: function(){
        var fp = Ext.create("eXe.view.filepicker.FilePicker", {
            type: eXe.view.filepicker.FilePicker.modeGetFolder,
            title: _("Select the parent folder for import."),
            modal: true,
            scope: this,
            callback: function(fp) {
                if (fp.status == eXe.view.filepicker.FilePicker.returnOk || fp.status == eXe.view.filepicker.FilePicker.returnReplace) {
                    nevow_clientToServerEvent('importPackage', this, '', 'html', fp.file.path);
                }
            }
        });
        fp.show();
	},

    importHtml2: function(path) {
        var fp = Ext.create("eXe.view.filepicker.FilePicker", {
            type: eXe.view.filepicker.FilePicker.modeOpen,
            title: _("Select the entry point for import."),
            modal: true,
            scope: this,
            callback: function(fp) {
                if (fp.status == eXe.view.filepicker.FilePicker.returnOk) {
                    nevow_clientToServerEvent('importPackage', this, '', 'html', path, fp.file.path);
                }
            }
        });
        fp.appendFilters([
            { "typename": _("HTML Files"), "extension": "*.html", "regex": /.*\.htm[l]*$/i },
            { "typename": _("All Files"), "extension": "*.*", "regex": /.*$/ }
        ]);
        fp.show();
    },

    importLom: function(menu, item, e) {
        var fp = Ext.create("eXe.view.filepicker.FilePicker", {
            type: eXe.view.filepicker.FilePicker.modeOpen,
            title: _("Select LOM Metadata file to import."),
            remote: true,
            modal: true,
            scope: this,
            callback: function(fp) {
                if (fp.status == eXe.view.filepicker.FilePicker.returnOk) {
                    nevow_clientToServerEvent('importPackage', this, '', e.metadataType, fp.file.path);
                }
            }
        });
        fp.appendFilters([
            { "typename": _("XML Files"), "extension": "*.xml", "regex": /.*\.xml$/i },
            { "typename": _("All Files"), "extension": "*.*", "regex": /.*$/ }
        ]);
        fp.show();
    },

    updateImportProgressWindow: function(msg) {
        if (!this.importProgressDisabled)
            this.importProgress.updateText(msg);
    },

    initImportProgressWindow: function(title) {
        this.importProgressDisabled = false;
        this.importProgress = Ext.Msg.show( {
            title: title,
            msg: _("Waiting progress..."),
            scope: this,
            modal: true,
            buttons: Ext.Msg.CANCEL,
            fn: function(button) {
                if (button == "cancel")    {
                    this.importProgressDisabled = true;
                    Ext.Msg.show( {
                        title: _("Cancel Import?"),
                        msg: _("There is an ongoing import. Do you want to cancel?"),
                        scope: this,
                        modal: true,
                        buttons: Ext.Msg.YESNO,
                        fn: function(button2) {
	                        if (button2 == "yes")
	                            nevow_clientToServerEvent('cancelImportPackage', this, '');
	                        else
	                            this.initImportProgressWindow(title);
                        }
                    });
                }
            }
        });
    },

    closeImportProgressWindow: function() {
        this.importProgress.destroy();
    },

	importXliff: function() {
        var fp = Ext.create("eXe.view.filepicker.FilePicker", {
            type: eXe.view.filepicker.FilePicker.modeOpen,
            title: _("Select Xliff file to import"),
            remote: true,
            modal: true,
            scope: this,
            callback: function(fp) {
                if (fp.status == eXe.view.filepicker.FilePicker.returnOk) {
                    var preferences = new Ext.Window ({
                      height: 220,
                      width: 650,
                      modal: true,
                      id: 'xliffimportwin',
                      title: _("XLIFF Import Preferences"),
                      items: {
                          xtype: 'uxiframe',
                          src: '/xliffimportpreferences?path=' + fp.file.path,
                          height: '100%'
                      }
                    });
                    preferences.show();
                }
            }
        });
        fp.appendFilters([
            { "typename": _("XLIFF Files"), "extension": "*.xlf", "regex": /.*\.xlf$/ },
            { "typename": _("All Files"), "extension": "*.*", "regex": /.*$/ }
        ]);
        fp.show();
	},

    exportXliff: function() {
        this.saveWorkInProgress();
        var fp = Ext.create("eXe.view.filepicker.FilePicker", {
            type: eXe.view.filepicker.FilePicker.modeSave,
            title: _("Export to Xliff as"),
            remote: true,
            modal: true,
            scope: this,
            callback: function(fp) {
                if (fp.status == eXe.view.filepicker.FilePicker.returnOk || fp.status == eXe.view.filepicker.FilePicker.returnReplace) {
                    var preferences = new Ext.Window ({
                        modal: true,
                        id: 'xliffexportwin',
                        layout: 'fit',
                        items: [{
                            xtype: 'form',
                            layout: 'anchor',
                            defaults: {
                                labelWidth: 130,
                                margin: 10
                            },
                            items: [
                                {
                                    xtype: 'combobox',
                                    inputId: 'source',
                                    fieldLabel: _("Select source language"),
                                    allowBlank: false,
                                    value: eXe.app.config.lang,
                                    queryModel: 'local',
                                    displayField: 'text',
                                    valueField: 'source',
                                    store: langsStore
                                },
                                {
                                    xtype: 'combobox',
                                    inputId: 'target',
                                    fieldLabel: _("Select target language"),
                                    allowBlank: false,
                                    value: 'eu',
                                    queryModel: 'local',
                                    displayField: 'text',
                                    valueField: 'target',
                                    store: langsStore
                                },
                                {
                                    xtype: 'checkbox',
                                    inputId: 'copy',
                                    fieldLabel: _('Copy source also in target'),
                                    valueField: 'copy',
                                    checked: true,
                                    tooltip: _("If you don't choose this "
+ "option, target field will be empty. Some Computer Aided Translation tools "
+ "(e.g. OmegaT) just translate the content of the target field. If you are "
+ "using this kind of tools, you will need to pre-fill the target field with a copy "
+ "of the source field.")
                                },
                                {
                                    xtype: 'checkbox',
                                    inputId: 'cdata',
                                    fieldLabel: _('Wrap fields in CDATA'),
                                    valueField: 'cdata',
                                    tooltip: _('This option will wrap all '
+ 'the exported fields in CDATA sections. This kind of sections are not '
+ 'recommended by XLIFF standard but it could be a good option if you want to '
+ 'use a pre-process tool (i.g.: Rainbow) before using the Computer Aided '
+ 'Translation software.')
                                }
                            ],
                            buttons: [
                                {
                                    text: _('Cancel'),
                                    handler: function() {
                                        this.up('window').close();
                                    }
                                },
                                {
                                    text: _('Ok'),
                                    handler: function() {
                                        var form = this.up('form').getForm();

                                        if (form.isValid()) {
                                            var values = form.getValues();

                                            nevow_clientToServerEvent(
                                                'exportXliffPackage',
                                                this,
                                                '',
                                                fp.file.path,
                                                values['source'],
                                                values['target'],
                                                values['copy'] !== undefined,
                                                values['cdata'] !== undefined
                                            );
                                            this.up('window').close();
                                        }
                                    }
                                }
                            ]
                        }],
                        title: _("XLIFF Export Preferences")
					});
                    preferences.show();
                }
            }
        });
        fp.appendFilters([
            { "typename": _("XLIFF Files"), "extension": "*.xlf", "regex": /.*\.xlf$/ },
            { "typename": _("All Files"), "extension": "*.*", "regex": /.*$/ }
        ]);
        fp.show();
    },

    processExportEvent: function(menu, item, e, eOpts) {
        this.saveWorkInProgress();

        // Tools - Resources Report should have no validation
        if (e.exportType=="csvReport") {
            this.exportPackage(e.exportType, "");
            return;
        } else if (e.exportType=="procomun") {
            if (config['publishLabel']=='Procomún') {
                nevow_clientToServerEvent('showMetadataWarning', this, '', 'procomun');
            } else {
                procomunProcessExportEvent = this; // To review (this is global...)
                Ext.Msg.show( {
                    title: _('Confirm'),
                    msg: _('Publish on %s?').replace("%s",config['publishLabel']) + '<br /><br />' + _('Please check the Properties tab contents (title, authorship, license...).'),
                    //scope: this,
                    //modal: true,
                    buttons: Ext.Msg.YESNO,
                    fn: function(button) {
                        if (button === 'yes') {
                            // nevow_clientToServerEvent('validatePackageProperties', procomunProcessExportEvent, '', 'procomun');
                            procomunProcessExportEvent.exportProcomun();
                        }
                    }
                });
            }
            return;
        }

        // Check if we need to show a warning if the package has metadata
        nevow_clientToServerEvent('showMetadataWarning', this, '', e.exportType);
    },

    /**
     * Shows a message warning the user that the current package has metadata
     * information in it before exporting it.
     *
     * @param {string} exportType
     *      The export type selected by the user.
     *
     * @returns {void}
     */
    showMetadataWarning: function(exportType) {
        // Show the warning alerting the user of the package's metadata
        Ext.Msg.show({
            title: _('Warning'),
            msg: _('This package has metadata. You might be exporting incorrect information included by the original author. Go to Properties to edit it.')
                + '<br /><br />'
                + _('Do you want to export the package with the current metadata?')
                + '<br /><br />'
                + '<label for="metadata-warning-hide"><input type="checkbox" id="metadata-warning-hide" /> '
                + _("Don't show this warning again")
                + '</label>',
            scope: this,
            modal: true,
            buttons: Ext.Msg.YESNO,
            fn: function(button) {
                // Only continue the export process if the user has clicked on Yes
                if (button == 'yes') {
                    this.processExportEventValidationStep(exportType);
                }

                // Either way, check if the user wants to hide the warning
                if (Ext.query('#metadata-warning-hide')[0].checked) {
                    this.hideMetadataWarningForever();
                }
            }
        });
    },

    /**
     * Hides the metadata warning on export for the user.
     */
    hideMetadataWarningForever: function() {
        nevow_clientToServerEvent('hideMetadataWarningForever');
    },

    processExportEventValidationStep: function(exportType) {
        nevow_clientToServerEvent('validatePackageProperties', this, '', exportType);
    },

    exportProcomun: function() {
        // Check if the maximun project size is exceeded
        if (Ext.getCmp("project_size").hasCls("max-size-exceeded")) {
            Ext.Msg.show( {
                title: _('Warning'),
                msg: _('The project exceeds the maximum size limit. Try removing some large files before publishing.')
            });
            return;
        }        
        this.saveWorkInProgress();
        Ext.Msg.show({
            title: _('Publishing...'),
            msg: _('Exporting package as SCORM 1.2...'),
            width: 300,
            progress: true,
            progressText: '0%',
            closable: false,
            draggable: false
        });
        nevow_clientToServerEvent('exportProcomun', this, '');
    },

    getProcomunAuthToken: function(url) {
        Ext.Msg.show({
            title: _('You must authorize eXe Learning to publish content into your Procomún account'),
            msg: _('Are you sure you want to start authorization process?'),
            scope: this,
            modal: true,
            buttons: Ext.Msg.YESNO,
            fn: function(button) {
                if (button == "yes") {
                    var authwindow = new Ext.Window ({
                        height: eXe.app.getMaxHeight(700),
                        width: 800,
                        modal: true,
                        id: 'oauthprocomun',
                        title: _("Procomún OAuth"),
                        items: {
                            xtype: 'uxiframe',
                            src: url,
                            height: '100%'
                        },
                    });
                    authwindow.show();
                }
            }
        });
    },

    showOAuthError: function(packageName) {
        Ext.Msg.show({
            title: _("Error"),
            msg: _('Error exporting package "%s" to Procomún.').replace("%s",packageName)
                + '<br />'
                + _('If you have problems publishing or you want to complete your cataloguing later, close this dialogue, export as SCORM 2004 and upload the generated zip file to Procomún.'),
            scope: this,
            modal: true,
            buttons: Ext.Msg.OK
        });
    },

	exportPackage: function(exportType, exportDir) {
	    if (exportType == 'webSite' || exportType == 'printSinglePage' || exportType == 'ipod' ) {
	        if (exportDir == '') {
                var fp = Ext.create("eXe.view.filepicker.FilePicker", {
		            type: eXe.view.filepicker.FilePicker.modeGetFolder,
		            title: _("Select the parent folder for export."),
		            modal: true,
		            scope: this,
		            callback: function(fp) {
		                if (fp.status == eXe.view.filepicker.FilePicker.returnOk || fp.status == eXe.view.filepicker.FilePicker.returnReplace) {
		                	// Show exporting message
		                	Ext.Msg.wait(_('Please wait...'));
		                	nevow_clientToServerEvent('exportPackage', this, '', exportType, fp.file.path)
		                }
		            }
		        });
	            fp.show();
	        }
	        else {
	            // use the supplied exportDir, rather than asking.
	            nevow_clientToServerEvent('exportPackage', this, '', exportType, exportDir)
            }
            exportType == 'singlePage'
	    } else if(exportType == "textFile"){
                var fp = Ext.create("eXe.view.filepicker.FilePicker", {
                    type: eXe.view.filepicker.FilePicker.modeSave,
                    title: _("Export text package as"),
                    remote: true,
                    modal: true,
                    scope: this,
                    callback: function(fp) {
                        if (fp.status == eXe.view.filepicker.FilePicker.returnOk || fp.status == eXe.view.filepicker.FilePicker.returnReplace) {
                        	// Show exporting message
		                	Ext.Msg.wait(_('Please wait...'));
                            nevow_clientToServerEvent('exportPackage', this, '', exportType, fp.file.path)
                        }
                    }
                });
		        fp.appendFilters([
		            { "typename": _("Text File"), "extension": "*.txt", "regex": /.*\.txt$/ },
		            { "typename": _("All Files"), "extension": "*.*", "regex": /.*$/ }
		            ]
		        );
                fp.show();
	    } else if(exportType == "csvReport"){
            var fp = Ext.create("eXe.view.filepicker.FilePicker", {
                type: eXe.view.filepicker.FilePicker.modeSave,
                title: _("Save package resources report as"),
                remote: true,
                modal: true,
                scope: this,
                callback: function(fp) {
                    if (fp.status == eXe.view.filepicker.FilePicker.returnOk || fp.status == eXe.view.filepicker.FilePicker.returnReplace) {
                    	// Show exporting message
	                	Ext.Msg.wait(_('Please wait...'));
                        nevow_clientToServerEvent('exportPackage', this, '', exportType, fp.file.path)
                    }
                }
            });
	        fp.appendFilters([
	            { "typename": _("CSV File"), "extension": "*.csv", "regex": /.*\.csv$/ },
	            { "typename": _("All Files"), "extension": "*.*", "regex": /.*$/ }
	            ]
	        );
            fp.show();
        } else if(exportType == "epub3"){
                var fp = Ext.create("eXe.view.filepicker.FilePicker", {
                    type: eXe.view.filepicker.FilePicker.modeSave,
                    title: _("Export EPUB3 package as"),
                    remote: true,
                    modal: true,
                    scope: this,
                    callback: function(fp) {
                        if (fp.status == eXe.view.filepicker.FilePicker.returnOk || fp.status == eXe.view.filepicker.FilePicker.returnReplace) {
                        	// Show exporting message
                            Ext.Msg.wait(_('Please wait...'));
    	                	nevow_clientToServerEvent('exportPackage', this, '', exportType, fp.file.path)
                        }
                    }
                });
                fp.appendFilters([
                    { "typename": _("EPUB3 File"), "extension": "*.epub", "regex": /.*\.epub$/ },
                    { "typename": _("All Files"), "extension": "*.*", "regex": /.*$/ }
                    ]
                );
                fp.show();
        } else if(exportType == 'procomun') {
            this.exportProcomun();
	    } else {
            var title;
	        if (exportType == "scorm1.2" || exportType == 'scorm2004'|| exportType == 'agrega')
	            title = _("Export SCORM package as");
	        else if (exportType == "ims")
	            title = _("Export IMS package as");
	        else if (exportType == "zipFile")
                title = _("Export Website package as");
            else if (exportType == 'singlePage')
                title == _("Export Single Page package as");
	        else if (exportType == "commoncartridge")
	            title = _("Export Common Cartridge as");
	        else
	            title = _("INVALID VALUE PASSED TO exportPackage");

            var fp = Ext.create("eXe.view.filepicker.FilePicker", {
	            type: eXe.view.filepicker.FilePicker.modeSave,
	            title: title,
                remote: true,
	            modal: true,
	            scope: this,
	            callback: function(fp) {
	                if (fp.status == eXe.view.filepicker.FilePicker.returnOk || fp.status == eXe.view.filepicker.FilePicker.returnReplace) {
	                	// Show exporting message
                        Ext.Msg.wait(_('Please wait...'));
                        nevow_clientToServerEvent('exportPackage', this, '', exportType, fp.file.path)
	                }
	            }
	        });
	        fp.appendFilters([
	            { "typename": _("SCORM/IMS/ZipFile"), "extension": "*.zip", "regex": /.*\.zip$/ },
	            { "typename": _("All Files"), "extension": "*.*", "regex": /.*$/ }
	            ]
	        );
	        fp.show();
	    }
	},// exportPackage()

    filePrint: function() {
	   // filePrint step#1: create a temporary print directory,
       // and return that to filePrint2, which will then call exportPackage():
	   var tmpdir_suffix = ""
	   var tmpdir_prefix = "eXeTempPrintDir_"
	   nevow_clientToServerEvent('makeTempPrintDir', this, '', tmpdir_suffix,
	                        tmpdir_prefix, "eXe.app.getController('Toolbar').filePrint2")
	   // note: as discussed below, at the end of filePrint3_openPrintWin(),
	   // the above makeTempPrintDir also removes any previous print jobs
	},

	filePrint2: function(tempPrintDir, printDir_warnings) {
	   if (printDir_warnings.length > 0) {
	      Ext.Msg.alert("", printDir_warnings)
       }
       //make tempPrintDir
       this.exportPackage('printSinglePage', tempPrintDir);
       //go to url
       actualurl = location.href.split("/");
       proyectName = actualurl.pop();
       webPrintDir = tempPrintDir.split("/").slice(3,5).join("/");
       printurl = webPrintDir+"/"+proyectName;
       this.processBrowseEvent(false, false, {url: printurl});
    },

    recentRender: function() {
    	Ext.Ajax.request({
    		url: location.pathname + '/recentMenu',
    		scope: this,
    		success: function(response) {
				var rm = Ext.JSON.decode(response.responseText),
					menu = this.getRecentMenu(), text, item, previtem;
    			for (i in rm) {
    				text = rm[i].num + ". " + rm[i].path
                    previtem = menu.items.getAt(rm[i].num - 1);
    				if (previtem && previtem.text[1] == ".") {
    					previtem.text = text
    				}
    				else {
	    				item = Ext.create('Ext.menu.Item', { text: text });
	    				menu.insert(rm[i].num - 1, item);
    				}
    			}
    		}
    	})
    	return true;
    },

    stylesRender: function(updateFromTheOtherMenu=false, mouse, a=true) {
        Ext.Ajax.request({
    		url: location.pathname + '/styleMenu',
            scope: this,
            async: a.async,
    		success: function(response) {
                var styles = Ext.JSON.decode(response.responseText), menu, i, item;
                menu = Ext.ComponentQuery.query("#styles_button")[0].menu;
                if (updateFromTheOtherMenu) {
                    menu.removeAll();
                }
    			for (i = styles.length-1; i >= 0; i--) {
                    item = Ext.create('Ext.menu.CheckItem', { text: styles[i].label, itemId: styles[i].style, checked: styles[i].selected });
    				menu.insert(0, item);
    			}
    		}
    	})
    	return true;
    },

    stylesRenderAdvanced: function(updateFromTheOtherMenu=false, mouse, a=true) {
        Ext.Ajax.request({
    		url: location.pathname + '/styleMenu',
            scope: this,
            async: a.async,
    		success: function(response) {
                var styles = Ext.JSON.decode(response.responseText), menu, i, item;
                menu = Ext.ComponentQuery.query("#styles_button_advanced")[0].menu;
                if (updateFromTheOtherMenu) {
                    menu.removeAll();
                }
    			for (i = styles.length-1; i >= 0; i--) {
                    item = Ext.create('Ext.menu.CheckItem', { text: styles[i].label, itemId: styles[i].style, checked: styles[i].selected });
                    menu.insert(0, item);
    			}
    		}
    	})
    	return true;
    },

    templatesRender: function() {
    	Ext.Ajax.request({
    		url: location.pathname + '/templateMenu',
    		scope: this,
    		success: function(response) {
				var templates = Ext.JSON.decode(response.responseText),
					menu = this.getTemplatesMenu(), i, item;
					menu.removeAll();
				if (templates.length == 0) {
					item = Ext.create('Ext.menu.Item', {text: _("No templates available"), disabled: true});
					menu.insert(0, item);
				} else {
	    			for (i = templates.length-1; i >= 0; i--) {
	    				item = Ext.create('Ext.menu.Item', { text: templates[i].label, path: templates[i].template });
	    				menu.insert(0, item);
	    			}
				}
    		}
    	})
    	return true;
    },


    recentClick: function(item) {
    	if (item.itemId == "file_clear_recent") {
    		nevow_clientToServerEvent('clearRecent', this, '');
    		var menu = this.getRecentMenu(),
    			items = menu.items.items.slice(),
    			i = 0,
    			len = items.length;
    		for (; i < len; i++)
    			if (items[i].text[1] == ".")
    				menu.remove(items[i], true);
    	}
    	else
    		this.askDirty("eXe.app.getController('Toolbar').fileOpenRecent2('" + item.text[0] + "');")
    },

    executeStylesClick: function(item) {
		for (var i = item.parentMenu.items.length-1; i >= 0; i--) {
			if (item.parentMenu.items.getAt(i) != item)
				item.parentMenu.items.getAt(i).setChecked(false);
		}
		item.setChecked(true);
		item.parentMenu.hide();
		item.parentMenu.hide();

        var authoring = Ext.ComponentQuery.query('#authoring')[0].getWin();
        if (authoring)
            authoring.submitLink("ChangeStyle", item.itemId, 1);

        // Update the advanced menu
        eXe.controller.Toolbar.prototype.stylesRenderAdvanced(true);
    },

    executeStylesClickAdvanced: function(item) {
		for (var i = item.parentMenu.items.length-1; i >= 0; i--) {
			if (item.parentMenu.items.getAt(i) != item)
				item.parentMenu.items.getAt(i).setChecked(false);
		}
		item.setChecked(true);
		item.parentMenu.hide();
		item.parentMenu.parentMenu.hide();

        var authoring = Ext.ComponentQuery.query('#authoring')[0].getWin();
        if (authoring)
            authoring.submitLink("ChangeStyle", item.itemId, 1);

        // Update the advanced menu
        eXe.controller.Toolbar.prototype.stylesRender(true);
    },

    executeStylesClickAdvanced: function(item) {
		for (var i = item.parentMenu.items.length-1; i >= 0; i--) {
			if (item.parentMenu.items.getAt(i) != item)
				item.parentMenu.items.getAt(i).setChecked(false);
		}
		item.setChecked(true);
		item.parentMenu.hide();
		item.parentMenu.parentMenu.hide();

        var authoring = Ext.ComponentQuery.query('#authoring')[0].getWin();
        if (authoring)
            authoring.submitLink("ChangeStyle", item.itemId, 1);

        // Update the Styles menu
        eXe.controller.Toolbar.prototype.stylesRenderAdvanced(true);
    },

    stylesClick: function(item) {
        var ed = this.getTinyMCEFullScreen();
        if(ed!="") {
            ed.execCommand('mceFullScreen');
            setTimeout(function(){
                eXe.controller.Toolbar.prototype.executeStylesClick(item);
            },500);
        } else this.executeStylesClick(item);
    },

    stylesClickAdvanced: function(item) {
        var ed = this.getTinyMCEFullScreen();
        if(ed!="") {
            ed.execCommand('mceFullScreen');
            setTimeout(function(){
                eXe.controller.Toolbar.prototype.executeStylesClick(item);
            },500);
        } else this.executeStylesClickAdvanced(item);
    },

    executeTemplatesClick: function(path) {
    	nevow_clientToServerEvent('loadTemplate', this, '', path)
    },

    templatesClick: function(item) {
    	// Sometimes it gets parsed twice, sometimes three times
    	// This makes it impossible for us to use "\"
    	// It will be transformed later according to the users OS
    	this.askDirty("eXe.app.getController('Toolbar').executeTemplatesClick('" + item.path.replace(/\\/g, '/') + "');")
    },

	fileOpenRecent2: function(number) {
        Ext.Msg.wait(_('Loading package...'));
	    nevow_clientToServerEvent('loadRecent', this, '', number)
	},

    fileNew: function() {
    	// Ask the server if the current package is dirty
    	this.askDirty("eXe.app.gotoUrl('/')");
	},

    fileOpen: function() {
    	this.askDirty("eXe.app.getController('Toolbar').fileOpen2()");
    },

    fileOpen2: function() {
		var f = Ext.create("eXe.view.filepicker.FilePicker", {
			type: eXe.view.filepicker.FilePicker.modeOpen,
			title: _("Open File"),
			modal: true,
			scope: this,
			callback: function(fp) {
                if (fp.status == eXe.view.filepicker.FilePicker.returnOk) {
                    Ext.Msg.wait(new Ext.Template(_('Loading package: {filename}')).apply({filename: fp.file.path}));
		    		nevow_clientToServerEvent('loadPackage', this, '', fp.file.path);
                }
		    }
		});
		f.appendFilters([
			{ "typename": _("eXe Package Files"), "extension": "*.elp", "regex": /.*\.elp$/ },
			{ "typename": _("All Files"), "extension": "*.*", "regex": /.*$/ }
			]
		);
		f.show();
    },

    checkDirty: function(ifClean, ifDirty) {
    	nevow_clientToServerEvent('isPackageDirty', this, '', ifClean, ifDirty)
	},

	askSave: function(onProceed) {
		Ext.Msg.show({
			title: _("Save Package first?"),
			msg: _("The current package has been modified and not yet saved. Would you like to save it?"),
			scope: this,
			modal: true,
			buttons: Ext.Msg.YESNOCANCEL,
			fn: function(button, text, opt) {
				if (button == "yes")
					this.fileSave(onProceed);
				else if (button == "no")
                    eval(onProceed);
			}
		});
	},

    getTinyMCEFullScreen: function(){
        var ifs = document.getElementsByTagName("IFRAME");
        if (ifs.length==1) {
            var d = ifs[0].contentWindow;
            var ed = "";
            if (typeof(d.tinyMCE)!='undefined' && d.tinyMCE.activeEditor) ed = d.tinyMCE.activeEditor;
            if (ed!="" && ed.id=="mce_fullscreen") {
                return ed;
            }
        }
        return "";
    },

    executeFileSave: function (onProceed,export_type_name) {
        if (!onProceed || (onProceed && typeof(onProceed) != "string")) {
            var onProceed = '';
        }

        eXeSaveReminder.clearScheduledSaveWarning();
        eXeSaveReminder.scheduleDirtyCheck();

        nevow_clientToServerEvent(
            'getPackageFileName',
            this,
            '',
            'eXe.app.getController("Toolbar").fileSave2',
            onProceed,
            export_type_name
        );
    },

	fileSave: function(onProceed, export_type_name) {
        var ed = this.getTinyMCEFullScreen();
        if(ed!="") {
            ed.execCommand('mceFullScreen');
            setTimeout(function(){
                eXe.controller.Toolbar.prototype.executeFileSave(onProceed);
            },500);
        } else if(typeof(export_type_name) == 'string'){
            this.executeFileSave(onProceed,export_type_name);
        }else{
            this.executeFileSave(onProceed,"");
        }

	},

	fileSave2: function(filename, onDone, export_type_name) {

	    if (filename) {
	        this.saveWorkInProgress();
	        // If the package has been previously saved/loaded
	        // Just save it over the old file

	        if (export_type_name === "") {
                Ext.Msg.wait(new Ext.Template(_('Saving package...')).apply());
                if (onDone){
                    nevow_clientToServerEvent('savePackage', this, '', '', onDone);
                }else{
                    nevow_clientToServerEvent('savePackage', this, '');
                }
	        } else {
                nevow_clientToServerEvent('savePackage', this, '','','',export_type_name);
	        }
	    } else {
	        // If the package is new (never saved/loaded) show a
            // fileSaveAs dialog
	        this.fileSaveAs(onDone)
	    }
	},

	templateSave: function(onProceed) {
        var ed = this.getTinyMCEFullScreen();
        if(ed!="") {
            ed.execCommand('mceFullScreen');
            setTimeout(function(){
                eXe.controller.Toolbar.prototype.executeTemplateSave(onProceed);
            },500);
        } else this.executeTemplateSave(onProceed);
	},

    executeTemplateSave: function(onProceed) {
		Ext.Msg.show({
			prompt: true,
			title: _('Title for template:'),
			msg: _('Enter the new name for template:'),
			buttons: Ext.Msg.OKCANCEL,
			multiline: false,
			scope: this,
			fn: function(button, text) {
				if (button == "ok")	{
					if (text) {
						if (!onProceed || (onProceed && typeof(onProceed) != "string"))
					        var onProceed = '';
						nevow_clientToServerEvent('saveTemplate', this, '', text, onProceed);
					}
		    	}
			}
		});

    },

	// Called by the user when they want to save their package
	executeFileSaveAs: function(onDone) {
		var f = Ext.create("eXe.view.filepicker.FilePicker", {
			type: eXe.view.filepicker.FilePicker.modeSave,
			title: _("Save file"),
			modal: true,
			scope: this,
			callback: function(fp) {
                // No debe mostrar el filepicker cuando guardamos un paquete
			    if (fp.status == eXe.view.filepicker.FilePicker.returnOk || fp.status == eXe.view.filepicker.FilePicker.returnReplace) {
			        this.saveWorkInProgress();
                    Ext.Msg.wait(_('Saving package...'));
			        if (onDone && typeof(onDone) == "string") {
			            nevow_clientToServerEvent('savePackage', this, '', f.file.path, onDone)
			        } else {
			            nevow_clientToServerEvent('savePackage', this, '', f.file.path)
			        }
			    } else {
                    Ext.defer(function() {
				        eval(onDone);
                    }, 500);
			    }
			}
		});
		f.appendFilters([
			{ "typename": _("eXe Package Files"), "extension": "*.elp", "regex": /.*\.elp$/ },
			{ "typename": _("All Files"), "extension": "*.*", "regex": /.*$/ }
			]
		);
		f.show();
	},

    fileSaveAs: function(onDone) {
        var ed = this.getTinyMCEFullScreen();
        if(ed!="") {
            ed.execCommand('mceFullScreen');
            setTimeout(function(){
                eXe.controller.Toolbar.prototype.executeFileSaveAs(onDone);
            },500);
        } else this.executeFileSaveAs(onDone);
    },

	// Submit any open iDevices
	saveWorkInProgress: function() {
	    // Do a submit so any editing is saved to the server
        var authoring = Ext.ComponentQuery.query('#authoring')[0].getWin();
        if (authoring && authoring.getContentForm) {
		    var theForm = authoring.getContentForm();
            if (theForm) {
                try {
                    $exeAuthoring.iDevice.save();
                } catch(e) {
                    console.warn("Error saving iDevice");
                }

                theForm.submit();
            }
        }
    },

    askDirty: function(nextStep) {
    	this.checkDirty(nextStep, 'eXe.app.getController("Toolbar").askSave("'+nextStep+'")');
    }
});
