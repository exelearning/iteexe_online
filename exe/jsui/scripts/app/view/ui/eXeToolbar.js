// ===========================================================================
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
// Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
//===========================================================================

Ext.define('eXe.view.ui.button', {
    extend: 'Ext.button.Button',
    alias: 'widget.accesskey_button',

    accesskey: null,

    beforeRender: function() {
        var me = this, pat, rep, key;

        if (me.accesskey) {
            pat = new RegExp(me.accesskey,'i');
            key = pat.exec(me.text);
            if (key) {
                rep = "<u>" + key + "</u>";
                me.text = me.text.replace(pat, rep);
            }
        }

        me.callParent();
    }
});

Ext.define('eXe.view.ui.menuitem', {
    extend: 'Ext.menu.Item',
    alias: 'widget.accesskey_menuitem',

    accesskey: null,

    beforeRender: function() {
        var me = this, pat, rep, key, keymap, html, parts, txt, instructions;

		html = me.text;
		parts = html.split('<span ');
		txt = parts[0];
		instructions = "";
		if (parts.length==2) instructions = '<span '+parts[1];

        if (me.accesskey) {
            pat = new RegExp(me.accesskey,'i');
            key = pat.exec(txt);
            if (key) {
	            rep = "<u>" + key + "</u>";
	            me.text = txt.replace(pat, rep) + instructions;
            }
	        keymap = new Ext.util.KeyMap({
	            target: me.up().el,
	            binding: {
	                key: me.accesskey,
	                fn: function() {
                        if (me.menu) {
                            me.activate();
                            me.expandMenu(0);
                            me.up().on({'beforeshow': function () { me.deactivate(); } });
                        }
                        else
                            me.onClick(Ext.EventObject);
                    },
	                defaultEventAction: 'stopEvent'
	            }
	        });
        }
        me.callParent();
    }
});

Ext.define('eXe.view.ui.eXeToolbar', {
    extend: 'Ext.toolbar.Toolbar',
    alias: 'widget.exetoolbar',

    initComponent: function() {
        var me = this;

        function getSRhelp(str){
            if (!str) var str = _("use the right arrow key");
            return '<span class="exe-sr-only"> ('+str+')</span>'
        }

        Ext.applyIf(me, {
            items: [
                {
                    xtype: 'fieldcontainer',
                    defaultType: 'label',
                    margin: '0 4 0 6',
                    items: [
                        {
                            html: '<img src="/images/exe_header_logo.png" alt="eXeLearning" width="21" height="20" />',
                            id: 'exe_online_header_logo'
                        }
                    ]
                },
                {
                    xtype: 'accesskey_button',
                    text: _('File'),
                    itemId: 'file',
                    accesskey: 'f',
                    menu: {
                        xtype: 'menu',
                        items: [
                            {
                                xtype: 'accesskey_menuitem',
                                text: _('Save draft'),
                                accesskey: 's',
                                tooltip: 'Ctrl+S',
                                itemId: 'file_save'
                            },
                            {
								xtype: 'menuseparator'
                            },
                            {
                                xtype: 'accesskey_menuitem',
                                text: _('Download'),
                                itemId: 'file_extract_all'
                            },
                            {
								xtype: 'menuseparator'
                            },
                            {
                                cls: 'exe-advanced',
                                xtype: 'accesskey_menuitem',
                                text: _('Import') + getSRhelp(),
                                hideOnClick: false,
                                accesskey: 'i',
                                menu: {
                                    xtype: 'menu',
                                    items: [
                                        {
                                            xtype: 'accesskey_menuitem',
                                            itemId: 'elp_import',
                                            accesskey: 'e',
                                            text: _('Project (.elp)')
                                        },
                                        {
                                            xtype: 'accesskey_menuitem',
                                            itemId: 'file_insert',
                                            accesskey: 'i',
                                            text: _('Insert elp in the current page')
                                        },
                                        {
                                            xtype: 'accesskey_menuitem',
                                            itemId: 'file_import_xliff',
                                            accesskey: 'x',
                                            text: _('XLIFF File')
                                        },
                                        {
                                            xtype: 'accesskey_menuitem',
			                                text: _('Metadata') + getSRhelp(),
			                                hideOnClick: false,
			                                accesskey: 'm',
                                            menu: {
                                                xtype: 'menu',
                                                items: [
			                                        {
			                                            xtype: 'accesskey_menuitem',
			                                            itemId: 'file_import_lom',
			                                            accesskey: 'l',
			                                            text: _('LOM')
			                                        },
                                                    {
                                                        xtype: 'accesskey_menuitem',
                                                        itemId: 'file_import_lomes',
                                                        accesskey: 'e',
                                                        text: _('LOM-ES')
                                                    }
                                                ]
                                            }
                                        }
                                    ]
                                }
                            },
                            {
                                xtype: 'accesskey_menuitem',
                                text: _('Export') + getSRhelp(),
                                hideOnClick: false,
                                accesskey: 'e',
                                menu: {
                                    xtype: 'menu',
                                    items: [
                                        {
                                	    xtype: 'accesskey_menuitem',
                                            cls: 'exe-advanced',
                                            text: _('Educational Standard') + getSRhelp(),
                                            hideOnClick: false,
                                            accesskey: 'e',
                                            menu: {
                                                xtype: 'menu',
                                                items: [
                                                    {
                                                        xtype: 'accesskey_menuitem',
                                                        text: _('Common Cartridge'),
                                                        accesskey: 'c',
                                                        itemId: 'file_export_cc'
                                                    },
                                                    {
                                                        xtype: 'accesskey_menuitem',
                                                        text: _('SCORM1.2'),
                                                        accesskey: 's',
                                                        itemId: 'file_export_scorm12'
                                                    },
                                                    {
                                                        xtype: 'accesskey_menuitem',
                                                        text: _('SCORM2004'),
                                                        accesskey: 'o',
                                                        itemId: 'file_export_scorm2004'
                                                    },
                                                    {
                                                        xtype: 'accesskey_menuitem',
                                                        text: _('IMS Content Package'),
                                                        accesskey: 'i',
                                                        itemId: 'file_export_ims'
                                                    }
                                                ]
                                            }
                                        },
                                        {
                                            cls: 'exe-advanced',
                                            xtype: 'accesskey_menuitem',
                                            text: _('Web Site') + getSRhelp(),
                                            hideOnClick: false,
                                            accesskey: 'w',
                                            menu: {
                                                xtype: 'menu',
                                                items: [
                                                    {
                                                        xtype: 'accesskey_menuitem',
                                                        text: _('Zip File'),
                                                        accesskey: 'z',
                                                        itemId: 'file_export_zip'
                                                    },
                                                    {
                                                		xtype: 'accesskey_menuitem',
                                                		text: _('Single Page'),
                                                		accesskey: 'p',
                                                		itemId: 'file_export_singlepage'
                                            	    }
                                                ]
                                            }
                                        },
                                        {
                                            cls: 'exe-advanced',
                                            xtype: 'accesskey_menuitem',
                                            text: _('Text File'),
                                            accesskey: 't',
                                            itemId: 'file_export_text'
                                        },
                                        {
                                            cls: 'exe-advanced',
                                            xtype: 'accesskey_menuitem',
                                            text: _('XLIFF'),
                                            accesskey: 'x',
                                            itemId: 'file_export_xliff'
                                        },
                                        {
                                            cls: 'exe-simplified',
                                            xtype: 'accesskey_menuitem',
                                            text: _('Web Site') + " (" + _('Self-contained Folder') + ")",
                                            accesskey: 't',
                                            itemId: 'file_export_website_b'
                                        },
                                        {
                                            cls: 'exe-simplified',
                                            xtype: 'accesskey_menuitem',
                                            text: _('Single Page'),
                                            accesskey: 't',
                                            itemId: 'file_export_singlepage_b'
                                        },
                                        {
                                            xtype: 'accesskey_menuitem',
                                            text: _('EPUB3'),
                                            accesskey: '3',
                                            itemId: 'file_export_epub3'
                                        },
                                        {
                                            cls: 'exe-advanced',
                                            xtype: 'accesskey_menuitem',
                                            itemId: 'file_extract',
                                            accesskey: 'e',
                                            text: _('Export the current page as elp')
                                        },
                                        {
                                            cls: 'exe-advanced',
                                            xtype: 'accesskey_menuitem',
                                            itemId: 'file_extract_SCORM',
                                            accesskey: 's',
                                            text: _('Export the current page as SCORM')
                                        },                                                                                
                                        {
                                            cls: 'exe-simplified',
                                            xtype: 'accesskey_menuitem',
                                            text: _('SCORM1.2'),
                                            accesskey: 't',
                                            itemId: 'file_export_scorm'
                                        },
                                        {
                                            cls: 'exe-simplified',
                                            xtype: 'accesskey_menuitem',
                                            text: _('IMS'),
                                            accesskey: 'i',
                                            itemId: 'file_export_ims'
                                        }
                                    ]
                                }
                            },
                            {
                                cls: 'exe-advanced',
                                xtype: 'accesskey_menuitem',
                                text: _('Publish') + getSRhelp(),
                                hideOnClick: false,
                                itemId: 'publish',
                                accesskey: 'l',
                                menu: {
                                    xtype: 'menu',
                                    items:
                                    [
                                        {
                                            xtype: 'accesskey_menuitem',
                                            text: config['publishLabel'],
                                            accesskey: 'P',
                                            itemId: 'file_export_procomun'
                                        },
                                    ]
                                },
                            },
                            {
                                cls: 'exe-advanced',
                                xtype: 'menuseparator'
                            },
                            {
                                xtype: 'accesskey_menuitem',
                                text: _('Print'),
                                accesskey: 'p',
                                tooltip: 'Ctrl+P',
                                itemId: 'file_print'
                            },
                            {
                                xtype: 'menuseparator'
                            },
                            {
                                xtype: 'accesskey_menuitem',
                                itemId: 'file_quit',
                                accesskey: 'q',
                                tooltip: 'Ctrl+Q',
                                text: _('Quit without saving')
                            }
                        ]
                    }
                },
                {
                    xtype: 'accesskey_button',
                    text: _('Tools'),
                    itemId: 'tools',
                    accesskey: 't',
                    menu: {
                        xtype: 'menu',
                        items: [
                            {
                                xtype: 'accesskey_menuitem',
                                itemId: 'tools_preferences',
                                accesskey: 'p',
                                text: _('Preferences')
                            },
                            {
                                xtype: 'accesskey_menuitem',
                                itemId: 'tools_preview',
                                accesskey: 'v',
                                text: _('Preview')
                            },                            
                            /* Disabled on this version: 
                            {
                                cls: 'exe-advanced',
                                xtype: 'accesskey_menuitem',
                                itemId: 'tools_idevice',
                                accesskey: 'i',
                                text: _('iDevice Editor')
                            },
                            */
                            {
                                cls: 'exe-advanced',
                                xtype: 'accesskey_menuitem',
                                itemId: 'tools_resourcesreport',
                                accesskey: 'r',
                                text: _('Resources Report')
                            },
                            {
                                xtype: 'accesskey_menuitem',
                                itemId: 'tools_refresh',
                                accesskey: 'r',
                                text: _('Refresh Display')
                            }
                        ]
                    }
                },
                {
                    // cls: 'exe-simplified', Remove // and this comment if styles_button_advanced_wrapper exists
                    xtype: 'accesskey_button',
                    text: _('Styles'),
                    accesskey: 's',
                    itemId: 'styles_button',
                    menu: {
                        xtype: 'menu',
	                    itemId: 'styles_menu'
                    }
                },
                /* Disabled on this version:
                {
                    cls: 'exe-advanced',
                    xtype: 'accesskey_button',
                    text: _('Styles'),
                    accesskey: 's',
                    itemId: 'styles_button_advanced_wrapper',
                    menu: {
                        xtype: 'menu',
	                    items: [
                            {
                            	xtype: 'accesskey_menuitem',
                                itemId: 'tools_stylemanager',
                                text: _('Style Manager')
                            },
                            {
                                xtype: 'accesskey_menuitem',
                                text: _('Styles'),
                                itemId: 'styles_button_advanced',
                                menu: {
                                    xtype: 'menu',
                                    itemId: 'styles_menu_advanced'
                                }
                            }
                        ]
                    }
                },
                */
                {
                    cls: 'exe-simplified',
                    xtype: 'accesskey_button',
                    text: _('Help'),
                    accesskey: 'h',
                    itemId: 'help_assistant_simplified'
                },
                {
                    cls: 'exe-advanced',
                    xtype: 'accesskey_button',
                    text: _('Help'),
                    itemId: 'help',
                    accesskey: 'h',
                    menu: {
                        xtype: 'menu',
                        items: [
                            {
                                xtype: 'accesskey_menuitem',
                                itemId: 'help_assistant',
                                accesskey: 'a',
                                text: _('Assistant')
                            },
                            {
                                xtype: 'menuseparator'
                            },
                            {
                                xtype: 'accesskey_menuitem',
                                itemId: 'help_tutorial',
                                id: 'help_tutorial_link',
                                accesskey: 't',
                                text: _('eXe Tutorial')
                            },
                            {
                                xtype: 'accesskey_menuitem',
                                itemId: 'help_notes',
                                id: 'help_notes_link',
                                accesskey: 'n',
                                text: _('Release Notes')
                            },
                            {
                                xtype: 'accesskey_menuitem',
                                itemId: 'help_legal',
                                id: 'help_legal_link',
                                accesskey: 'l',
                                text: _('Legal Notes')
                            },
                            {
                                xtype: 'menuseparator'
                            },
                            {
                                xtype: 'accesskey_menuitem',
                                itemId: 'help_website',
                                id: 'help_website_link',
                                accesskey: 'w',
                                text: _('eXe Web Site')
                            },
                            {
                                xtype: 'accesskey_menuitem',
                                itemId: 'help_issue',
                                id: 'help_issue_link',
                                accesskey: 'r',
                                text: _('Report an Issue')
                            },
                            /* To review:
							{
                                xtype: 'accesskey_menuitem',
                                itemId: 'help_forums',
                                id: 'help_forums_link',
                                accesskey: 'f',
                                text: _('eXe Forums')
                            },
							*/
                            {
                                xtype: 'menuseparator'
                            },
                            {
                                xtype: 'accesskey_menuitem',
                                itemId: 'help_about',
                                id: 'help_about_link',
                                accesskey: 'a',
                                text: _('About eXe')
                            }
                        ]
                    }
                },
                '->',
                // Size of Project
                {
                    xtype: 'fieldcontainer',
                    defaultType: 'label',
                    margin: '0 30 0 0',
                    items: [
                        {
                            xtype: 'label',
                            html: _('Project size:')+' ',
                            itemId: 'project_size_label',
                            id: 'project_size_label'
                        },
                        {
                            xtype: 'label',
                            html: 'placeholder',
                            itemId: 'project_size',
                            id: 'project_size'
                        },
                        {
                            xtype: 'label',
                            html: 'maxsize',
                            itemId: 'project_max_size',
                            id: 'project_max_size',
                            hidden: true
                        }
                    ]
                }, 
                // Advanced user and Preview button
                '->',
                // Advanced user
                {
                    xtype: 'fieldcontainer',
					defaultType: 'checkboxfield',
					margin: '0 30 0 0',
					items: [
                        {
                            boxLabel: _('Advanced mode'),
                            tooltip: _('Checking this option will show more elements in the menus (File, Tools...) and the Properties tab.'),
                            name: 'advanced_toggler',
                            inputValue: '1',
                            id: 'advanced_toggler',
                            // checked: true,
							listeners : {
                                change: function(e, newValue) {

                                    let status=null
                                    newValue ? status=1 : status = 0
                                    nevow_clientToServerEvent('saveEXeUIversion',this,'',status)
                                    									// Refresh some components
                                    // Refresh some components
									eXe.app.getController("Toolbar").eXeUIversionSetStatus(Ext.getCmp("advanced_toggler").getValue());
									try {
										Ext.getCmp("exe-viewport").doLayout();
									} catch(e) {}
                                }
                            }
                        }
                    ]
                },
                // Preview button
                {
					xtype: 'fieldcontainer',
					defaultType: 'button',
					margin: '0 10 0 0',
                    items: [
                        {
                            xtype: 'button',
                            text: _('Preview'),
                            itemId: 'tools_preview_button'
                        }
                    ]
                },
                // Preview button
                {
					xtype: 'fieldcontainer',
					defaultType: 'button',
					margin: '0 10 0 0',
                    items: [
                        {
                            xtype: 'button',
                            text: _('Finish'),
                            itemId: 'file_export_procomun_b',
                            cls: 'file_export_finish_btn'
                        }
                    ]
                }
            ]
        });

        me.callParent(arguments);

        // Advanced user
		// Get the cookie or set the default value (simplified)
		// var eXeUIversion = Ext.util.Cookies.get('eXeUIversion');
		// if (!eXeUIversion) eXeUIversion = 'simplified';
		// Check the Advanced option or add the simplified class to the BODY tag
        /*
        if (eXeUIversion=='advanced') {
		Ext.getCmp("advanced_toggler").setValue(true);
		} else {
			Ext.select("BODY").addCls('exe-simplified');
        }
        */
		// / Advanced user
    }
});


// Save reminder (#287)
Ext.define('eXeSaveReminder', {
    singleton: true,
    // Time between messages (in messages)
    delay: eXe.app.config.autosaveTime,
    // Timeout ID to the following warning
    currentTimeout: null,
    // Flag to control wheter the message should be shown or not
    active: true,
    // Flag to control wheter the dialog is already open or not
    isOpen: false,
    /**
     * Initialization function.
     *
     * @returns {void}
     */
    init: function() {
        // If the delay is 0, don't do anything at all
        if (this.delay == 0) {
            this.active = false;
        // If it is any other thing, start the checks
        } else {
            this.active = true;
            this.scheduleDirtyCheck();
        }
    },
    /**
     * Schedules the next check to see if the package
     * has been changed.
     *
     * @returns {void}
     */
    scheduleDirtyCheck: function () {
        // Check only if there isn't a warning already scheduled
        if (this.currentTimeout === null) {
            setTimeout(function() {
                eXe.app.getController('Toolbar').checkDirty(
                    'eXeSaveReminder.scheduleDirtyCheck()',
                    'eXeSaveReminder.scheduleSaveWarning()'
                );
            }, 5000);
        }
    },
    /**
     * Clear scheduled warning if there is one.
     *
     * @returns {void}
     */
    clearScheduledSaveWarning: function () {
        if (this.currentTimeout !== null) {
            clearTimeout(this.currentTimeout);
            this.currentTimeout = null;
        }
    },
    /**
     * Schedule a new save warning (for the delay configured in the class).
     *
     * @returns {void}
     */
    scheduleSaveWarning: function () {
        // First of all, clear the previous one
        this.clearScheduledSaveWarning();
        // And schedule a new one
        this.currentTimeout = setTimeout(this.showSaveWarning.bind(this), (this.delay * 60 * 1000));
    },
    /**
     * Show a save reminder to allow the user to save its work.
     *
     * @returns {void}
     */
    showSaveWarning: function() {
        // If the reminder isn't active or there is one already open,
        // don't do anything at all (in the case there is already one open
        // the next one will be scheduled after this is closed)
        if (!this.active || this.isOpen) {
            return;
        }

        // Check to see if there is any window currently open
        var hasWindow = false;
        Ext.each(Ext.ComponentQuery.query('window'), function(win) {
            if (win.isVisible() && !win.collapsed) {
                hasWindow = true;

                // Returning false cause the foreach loop to stop
                return false;
            }
        });

        // If there is no window open
        if (!hasWindow) {
            this.isOpen = true;

            Ext.MessageBox.show({
                title: _("Warning!"),
                msg: _("You've been working for a long time without saving.")
                    + '<br /><br />'
                    + _("Do you want to save now?")
                    + '<br /><br /><label for="hide_eXeSaveReminder"><input type="checkbox" id="hide_eXeSaveReminder" /> '
                    + _("Hide until the application is closed")
                    + '</label>',
                buttons: Ext.MessageBox.OKCANCEL,
                scope: this,
                modal: false,
                fn: function(btn) {
                    this.isOpen = false;

                    if(btn == 'ok') {
                        if (Ext.query("#hide_eXeSaveReminder")[0].checked) {
                            this.active = false;
                        }

                        // Save
                        eXe.app.getController('Toolbar').fileSave();
                    }

                    this.clearScheduledSaveWarning();
                    if (this.active) {
                        this.scheduleDirtyCheck();
                    }
                }
            });
        } else {
            this.clearScheduledSaveWarning();
            this.scheduleDirtyCheck();
        }
    }
});
// When ready, initialize the save reminder
Ext.onReady(eXeSaveReminder.init, eXeSaveReminder);

// Initialize the text in project_size label
Ext.onReady(function () {
    // DOM and Framework are ready...
    eXe.app.getController("Toolbar").eXeUIGetSizeProject();
    eXe.app.getController("Toolbar").eXeUIGetMaxSizeProject();
});