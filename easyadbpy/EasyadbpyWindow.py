# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

from locale import gettext as _

from gi.repository import Gtk # pylint: disable=E0611
import logging
logger = logging.getLogger('easyadbpy')

from easyadbpy_lib import Window
from easyadbpy.AboutEasyadbpyDialog import AboutEasyadbpyDialog
from easyadbpy.PreferencesEasyadbpyDialog import PreferencesEasyadbpyDialog

from easyadbpy.ADBhandler import ADBhandler
#from easyadbpy.Handyfunctions import Handyfunctions

import shlex, subprocess

# See easyadbpy_lib.Window.py for more details about how this class works
class EasyadbpyWindow(Window):
    __gtype_name__ = "EasyadbpyWindow"
    
    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the main window"""
        super(EasyadbpyWindow, self).finish_initializing(builder)

        self.AboutDialog = AboutEasyadbpyDialog
        self.PreferencesDialog = PreferencesEasyadbpyDialog

        # Code for other initialization actions should be added here.
        self.APKviewer = self.builder.get_object('treeview1')
        self.Devicelist = self.builder.get_object('treeview2')
        self.Devicelistdialog = self.builder.get_object('dialog1')
        self.APPselection = self.builder.get_object('treeview-selection2')
        self.Deviceid = self.builder.get_object('Deviceid')
        self.statusbar = self.builder.get_object('statusbar1')
        self.ADB = ADBhandler()
                    

        #//////////////////////APKLISt/////////////////////////
        self.tvcolumn = Gtk.TreeViewColumn('Application') #make kollom

        self.APKviewer.append_column(self.tvcolumn) # set kollom
        
        self.cell = Gtk.CellRendererText() #make new rendercell

        self.tvcolumn.pack_start(self.cell, True) #Start the rendercell

        self.tvcolumn.add_attribute(self.cell, 'text', 0) #Add the cell

        self.APKviewer.set_search_column(0)

        # Allow sorting on the column
        self.tvcolumn.set_sort_column_id(0) #kollom sorteren bij kollom 1

        # Allow drag and drop reordering of rows
        self.APKviewer.set_reorderable(True)

        
        #//////////////////////Devicelist/////////////////////////
        self.tvcolumn = Gtk.TreeViewColumn('Devices') #make kollom

        self.Devicelist.append_column(self.tvcolumn) # set kollom
        
        self.cell = Gtk.CellRendererText() #make new rendercell

        self.tvcolumn.pack_start(self.cell, True) #Start the rendercell

        self.tvcolumn.add_attribute(self.cell, 'text', 0) #Add the cell

        self.Devicelist.set_search_column(0)

        # Allow sorting on the column
        self.tvcolumn.set_sort_column_id(0) #kollom sorteren bij kollom 1

        # Allow drag and drop reordering of rows
        self.Devicelist.set_reorderable(True)

        self.on_Refresh_ADB_activate(None)

#EVENTS
        
    def button1_clicked_cb(self, widget):
        print "APK install button pressed"
        dialog = Gtk.FileChooserDialog("Please choose a file", self, Gtk.FileChooserAction.OPEN,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        filter_text = Gtk.FileFilter()
        filter_text.set_name("Android Package")
        filter_text.add_pattern("*.apk")
        dialog.add_filter(filter_text)
        
        value = dialog.run()
        dialog.hide()
        print value
        if value == -5:
            self.statusbar.push(0 ,'Installing...')
            err = self.ADB.installAPK(dialog.get_filename()) 
            if err == -1:
                dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, 'Application already exist!')
                dialog.format_secondary_text('Try to uninstall that application and try again.')
                dialog.run()
                dialog.hide()
            else:
                dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, message)
                dialog.format_secondary_text("And this is the secondary text that explains things.")
                dialog.run()
                dialog.hide()
            
    
    def on_button2_clicked(self, widget):
        print "Pull APK button pressed"
        print self.getselectionname(self.APPselection)

    def on_button3_clicked(self, widget):
        print "Uninstall APK button pressed"

    def on_Refresh_ADB_activate(self, widget):
        print "Refresh ADB client"
        count , treestore = self.ADB.getdevicelist()
        if count > 1:
            self.Devicelist.set_model(treestore)
            output = self.Devicelistdialog.run()
            if output == -4:
                self.Devicelistdialog.hide()
            elif output == 1:
                model , select = self.Deviceid.get_selected()
                returnvalue = model.get_value(select, 0)
                self.ADB.selectdevice(returnvalue)
                self.Devicelistdialog.hide()
                                
            elif output ==-1:
                self.Devicelistdialog.hide()
            else:
                self.Devicelistdialog.hide()
        else:
             self.ADB.selectdevice(treestore)

        print self.ADB.Device, 'Selected'
        self.UpdateAPPlist()

    def UpdateAPPlist(self):
        treestore = Gtk.TreeStore(str)

        piter = treestore.append(None, ['DATA'])
        for child in self.ADB.GetDATAapplist():
            treestore.append(piter, [child])
        if self.ADB.GetAndroidSDK() > 7:
            piter = treestore.append(None, ['SDCARD'])
            for child in self.ADB.GetSDCARDapplist():
                treestore.append(piter, [child])
        piter = treestore.append(None, ['SYSTEM'])
        for child in self.ADB.GetSYSTEMapplist():
            treestore.append(piter, [child])

        self.APKviewer.set_model(treestore)

    def getselectionname(self, treeselection):
        model , select = treeselection.get_selected()
        node = model.get_iter_first()
        returnvalue = model[select][0]
        print model[node][0]
        return returnvalue




