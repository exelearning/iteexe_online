// ===========================================================================
// eXeLearning
// Copyright 2014, Mercedes Cotelo Lois
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
// Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//===========================================================================
Ext.define('eXe.controller.StyleManager', {
    extend: 'Ext.app.Controller',

    requires: ['eXe.view.forms.StyleManagerPanel'],

    init: function() {
        this.control({
            '#return_styles_list': {
                click:  function (element, record, item, index, e, eOpts) {
                    this.triggerAction(element, 'doList');
                },
            },
            '#styles_repository': {
                click:  function (element, record, item, index, e, eOpts) {
                    this.triggerAction(element, 'doStylesRepository');
                },
            },
            '#style_import_from_url': {
                click:  function (element, record, item, index, e, eOpts) {
                    this.triggerAction(element, 'doStyleImportURL');
                },
            },
            '#import_style' : {
                click: function(element, record, item, index, e, eOpts) {
                    this.triggerImportStyle(element);
                }
            },
            '#create_new_style' : {
                click: function(element) {
                    styleDesignerWindow = window.open("/tools/style-designer/previews/website/");
                    this.triggerClose(element);
                }
            },
            // Actions performed on styles can be triggered by multiple buttons (one for each style),
            // so they cannot be selected by id, but by the custom attribute 'button_class'
            'button[button_class=properties_style]': {
                click:  function(element, record, item, index, e, eOpts) {
                    this.triggerActionOnStyle(element, 'doProperties');
                },
            },
            'button[button_class=edit_style]': {
                click:  function (element) {
                    // eXe.app.getController('Toolbar').styleDesigner.editStyle(element.value);
                    // We check if the Style is compatible with the tool
                    console.log("StyleManager", window)
                    data_value = Ext.JSON.decode(element.value);
                    if (data_value["userStyle"]) {
                        if (config && config["user_style"]) {
                            content_url = config["user_style"]+"/"+data_value["name"]+"/content.css";
                        } else if (opener.config && opener.config["user_style"]) {
                            content_url = opener.config["user_style"]+"/"+data_value["name"]+"/content.css";
                        }
                    } else {
                        content_url = "/style/"+data_value["name"]+"/content.css";
                    }
                    Ext.Ajax.request({
                        url: content_url,
                        scope: this,
                        success: function(response) {
                            var res = response.responseText;
                            if (res.indexOf("/* eXeLearning Style Designer Compatible Style */")!=0) {
                                Ext.Msg.alert("", _("Cannot edit the Style. It is not compatible with the Style Designer."));
                            } else {
                                // If it's compatible, we open the Style designer
                                styleDesignerWindow = window.open("/tools/style-designer/previews/website/?style="+data_value["name"]+
                                                                    "&userstyle="+data_value["userStyle"]);
                                this.triggerClose(element);
                            }
                        },
                        error: function(){
                            Ext.Msg.alert(_('Error'), _("An unknown error occurred."));
                        }
                    });
                },
            },
            'button[button_class=pre_export_style]': {
                click:  function (element, record, item, index, e, eOpts) {
                    this.triggerActionOnStyle(element, 'doPreExport');
                },
            },
            'button[button_class=export_style]': {
                click: function(element, record, item, index, e, eOpts) {
                    this.triggerExportStyle(element);
                }
            },
            'button[button_class=delete_style]': {
                click:  function(element, record, item, index, e, eOpts) {

                    if (typeof(element.itemId)!='undefined' && typeof(exe_style)!='undefined') {
                        var currentStyle = exe_style.split("/");
                        if (currentStyle.length==4) {
                            currentStyle = currentStyle[2];
                            var selectedStyle = element.itemId.replace("delete_style","");
                            if (currentStyle==selectedStyle) {
                                Ext.Msg.alert(_('Information'), _('Cannot delete the current style.'));
                                return;
                            }
                        }
                    }

                    this.triggerDeleteStyle(element);
                }
            },
            // There is an 'Import style' button for each style in the repository styles list
            'button[button_class=repository_style_import]' : {
                click: function(element, record, item, index, e, eOpts) {
                    this.triggerImportRepositoryStyle(element);
                }
            },
        });
    },

    /**
     * Set the value of the hidden field 'action' and submit form to server
     *
     * @param element        Clicked element of the WebUI
     * @param actionString   Value to be set on the 'action' hidden field.
     *                       Determines the action to be performed in the server side
     */
    triggerAction: function(element, actionString) {
        var formpanel = element.up('form');
        var form, action;

        form = formpanel.getForm();
        action = form.findField('action');
        action.setValue(actionString);
        form.submit({
            success: function() {
                //formpanel.reload();
            },
            failure: function(form, action) {
                Ext.Msg.alert(_('Error'), action.result.errorMessage);
            },
        });
    },

    /**
     * Set the value of the hidden fields 'action' and 'style', and submit form to server
     *
     * @param element        Clicked element of the WebUI
     * @param actionString   Value to be set on the 'action' hidden field.
     *                       Determines the action to be performed in the server side
     */
    triggerActionOnStyle: function(element, actionString) {
        var formpanel = element.up('form');
        var form, action, style;

        form = formpanel.getForm();
        action = form.findField('action');
        style = form.findField('style');

        action.setValue(actionString);
        style.setValue(element.value);
        form.submit({
            success: function() {
                //formpanel.reload();
            },
            failure: function(form, action) {
                Ext.Msg.alert(_('Error'), action.result.errorMessage);
            }
        });
    },

    /**
     * Open FilePicker window to select ZIP file, set 'action', and 'style' fields and submit form
     *
     * @param button  Clicked button
     */
    triggerImportStyle: function(button) {
        var formpanel = button.up('form'),
            form = formpanel.getForm(),
            action = form.findField('action'),
            filename = form.findField('filename');
        var fp = Ext.create("eXe.view.filepicker.FilePicker", {
            type: eXe.view.filepicker.FilePicker.modeOpen,
            title: _("Select ZIP Style file to import."),
            remote: eXe.app.config.server,
            modal: true,
            scope: this,
            uploaded: false,
            callback: function(fp) {
                if (!fp.uploaded && (fp.status == eXe.view.filepicker.FilePicker.returnOk || fp.status == eXe.view.filepicker.FilePicker.returnReplace)) {
                    filename.setValue(fp.file.path);
                    fp.uploaded = true;
                    form.submit({
                        success: function() {
                            //formpanel.reload();
                        },
                        failure: function(form, action) {
                            Ext.Msg.alert(_('Error'), action.result.errorMessage);
                        }
                    });
                }
            }
        });

        action.setValue('doImport');

        fp.appendFilters([
            { "typename": _("ZIP Style"), "extension": "*.zip", "regex": /.*\.zip$/ },
            { "typename": _("All Files"), "extension": "*.*", "regex": /.*$/ }
        ]);
        fp.show();
    },

    /**
     * Open FilePicker window to select ZIP file, set 'action', 'filename' and 'style' fields and submit form
     *
     * @param button  Clicked button, its value is the name of the selected style
     */
    triggerExportStyle: function(button) {
        // Open a File Picker window, to let the user chose the target ZIP file
        // set 'action' field value to 'doImport', 'filename' to the selected file path,
        // 'style' to the clicked style and submit form to server
        var formpanel = button.up('form'),
            form = formpanel.getForm(),
            action = form.findField('action'),
            filename = form.findField('filename'),
            dirname = form.findField('dirname'),
            style = form.findField('style'),
            xdata = form.findField('xdata'),
            namefilexport = button.value;

        for (var i=0; i<form._fields.items.length;i++) {
            f = form._fields.items[i];
        }
        action.setValue('doExport');
        style.setValue(button.value);


        var fp = Ext.create("eXe.view.filepicker.FilePicker", {
            type: eXe.view.filepicker.FilePicker.modeSave,
            title: _("Export to ZIP Style as"),
            filename: dirname.value,
            remote: true,
            modal: true,
            scope: this,
            callback: function(fp) {
                if (fp.status == eXe.view.filepicker.FilePicker.returnOk || fp.status == eXe.view.filepicker.FilePicker.returnReplace)
                    Ext.Msg.wait(_('Please wait...'));
                    nevow_clientToServerEvent('exportPackage', this, '', 'zipStyle', fp.file.path, fp.filename);
                }
        });
        fp.appendFilters([
            { "typename": _("ZipFile"), "extension": "*.zip", "regex": /.*\.zip$/ },
            { "typename": _("All Files"), "extension": "*.*", "regex": /.*$/ }
        ]);
        fp.show();
    },

    /**
     * Set 'action' and 'style' fields values and submit form
     *
     * @param button  Clicked button, its value is the name of the selected style
     */
    triggerDeleteStyle: function(button) {
        // Open a confirmation window. If user confirms the deletion,
        // set 'action' field value to 'doDelete', 'style' to the clicked style
        // and submit form to server
        var formpanel = button.up('form'),
            form = formpanel.getForm(),
            action = form.findField('action'),
            style = form.findField('style');

        action.setValue('doDelete');
        style.setValue(button.value);
        data = Ext.JSON.decode(button.value);
        Ext.Msg.show({
            title: _("Delete style?"),
            msg: _("Do you want to delete this style?") + " - " + data["name"],
            scope: this,
            modal: true,
            buttons: Ext.Msg.YESNOCANCEL,
            fn: function(button, text, opt) {
                if (button == "yes") {
                    form.submit({
                        success: function() {
                            //formpanel.reload();
                        },
                        failure: function(form, action) {
                            Ext.Msg.alert(_('Error'), action.result.errorMessage);
                        }
                    });
                }
            }
        });
    },

    /**
     * Set 'action' and 'style' fields values and submit form
     *
     * @param button  Clicked button, its value is the name of the repository style to be imported
     */
    triggerImportRepositoryStyle: function(button) {
        // Set 'action' field value to 'doStyleImportRepository',
        // 'style_name' to the clicked style and submit form to server
        var formpanel = button.up('form');
        var form = formpanel.getForm();
        var action = form.findField('action');
        var style_name = form.findField('style_name');

        action.setValue('doStyleImportRepository');
        style_name.setValue(button.value);
        form.submit({
            success: function() {
                //formpanel.reload();
            },
            failure: function(form, action) {
                Ext.Msg.alert(_('Error'), action.result.errorMessage);
            }
        });
    },

    triggerClose: function(button) {
        var panel = button.up('form').up();
        panel.close();
    }
});
