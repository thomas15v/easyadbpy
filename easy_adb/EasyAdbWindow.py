# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2013 Thomas Vanmellaerts <tvanmellaerts@live.be>
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3, as published 
# by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

from locale import gettext as _

from gi.repository import Gtk # pylint: disable=E0611
import logging
logger = logging.getLogger('easy_adb')

from easy_adb_lib import Window
from easy_adb.AboutEasyAdbDialog import AboutEasyAdbDialog
from easy_adb.PreferencesEasyAdbDialog import PreferencesEasyAdbDialog

from easy_adb.ADBhandler import ADBhandler

import shlex, subprocess, os, time, re , string

# See easy_adb_lib.Window.py for more details about how this class works
class EasyAdbWindow(Window):
    __gtype_name__ = "EasyAdbWindow"
    
    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the main window"""
        super(EasyAdbWindow, self).finish_initializing(builder)

        self.AboutDialog = AboutEasyAdbDialog
        self.PreferencesDialog = PreferencesEasyAdbDialog

        # Code for other initialization actions should be added here.
        self.APKviewer = self.builder.get_object('treeview1')
        self.Devicelist = self.builder.get_object('treeview2')
        self.Devicelistdialog = self.builder.get_object('dialog1')
        self.Installapkdialog = self.builder.get_object('dialog2')
        self.APPselection = self.builder.get_object('treeview-selection2')
        self.Deviceid = self.builder.get_object('Deviceid')
        self.statusbar = self.builder.get_object('statusbar1')
        self.filenameentry = self.builder.get_object('entry1')

        self.Reinstall = self.builder.get_object('checkbutton1')
        self.SDCARD = self.builder.get_object('checkbutton2')

        self.ADB = ADBhandler()
        

        #//////////////////////APKLISt/////////////////////////
        self.tvcolumn = Gtk.TreeViewColumn('Application') #make kollom

        self.APKviewer.append_column(self.tvcolumn) # set kollom
        
        self.cell = Gtk.CellRendererText() #make new rendercell

        self.tvcolumn.pack_start(self.cell, True) #Start the rendercell

        self.tvcolumn.add_attribute(self.cell, 'text', 0) #Add the cell

        self.APKviewer.set_search_column(0)

        #//////////////////////Devicelist/////////////////////////
        self.tvcolumn = Gtk.TreeViewColumn('Devices') #make kollom

        self.Devicelist.append_column(self.tvcolumn) # set kollom

        self.cell = Gtk.CellRendererText() #make new rendercell

        self.tvcolumn.pack_start(self.cell, True) #Start the rendercell

        self.tvcolumn.add_attribute(self.cell, 'text', 0) #Add the cell

        self.Devicelist.set_search_column(0)
        
        self.on_Refresh_ADB_activate(None)
       

#EVENTS
        
    def button1_clicked_cb(self, widget):
        print "APK install button pressed"
        value = self.Installapkdialog.run()
        self.Installapkdialog.hide()
        time.sleep(1)
        filename = self.filenameentry.get_text()
        args = str
        
        if value == 1:
            if filename in ['', None] and not self.iffile(filename):
                print 'abborting'
                self.msgbox('You must select a file', '' , Gtk.MessageType.ERROR)
                return
            self.statusbar.push(0 ,'Installing...')

            if self.SDCARD.get_active() and self.Reinstall.get_active():
                args = '-rs'
            elif self.Reinstall.get_active():
                args = '-r'
            elif self.SDCARD.get_active():
                args = '-s'
            else:
                args = ''

            err = self.ADB.installAPK(filename, args) 
            if err == -1:
                dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, 'Application already exist!')
                dialog.format_secondary_text('Try to uninstall that application and try again.')
                dialog.run()
                dialog.hide()
            else:
                dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, 'LOOOOOOOOOOL UNHANDELED!!!')
                dialog.format_secondary_text("And this is the secondary text that explains things.")
                dialog.run()
                dialog.hide()
        
                print 'refresh apklist'
                self.UpdateAPPlist()

    def on_button2_clicked(self, widget):
        print "Pull APK button pressed"
        output =  self.getselectionname(self.APPselection)

        if not output == None:
            Parent, Child = output

            dialog = Gtk.FileChooserDialog("Please choose a location to save the application", self, Gtk.FileChooserAction.SAVE,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

            dialog.set_current_name(Child)
            filter_text = Gtk.FileFilter()
            filter_text.set_name("Android Package")
            filter_text.add_pattern("*.apk")

            value = dialog.run()
            dialog.hide()
            self.update()
            if value == -5:
                if Parent == 'DATA':
                    self.ADB.PullDATAAPK(Child, dialog.get_filename())
                elif Parent == 'SYSTEM':
                    self.ADB.PullSYSTEMAPK(Child, dialog.get_filename())
                elif Parent == 'SDCARD':
                    self.ADB.PullSDCARDAPK(Child, dialog.get_filename())
                else:
                    print 'Something went teribly wrong'
            
            
            

    def on_button3_clicked(self, widget):
        print "Uninstall APK button pressed"

        

    def on_button7_clicked(self, widget):
        print "Choose file button on INSTALLAPKDIALOG pressed"
        dialog = Gtk.FileChooserDialog("Please choose a file", self, Gtk.FileChooserAction.OPEN,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        filter_text = Gtk.FileFilter()
        filter_text.set_name("Android Package")
        filter_text.add_pattern("*.apk")
        dialog.add_filter(filter_text)
        value = dialog.run()
        
        filename = dialog.get_filename()
        if not filename == None:
            self.filenameentry.set_text(filename)
        else:
            self.filenameentry.set_text('')
        dialog.destroy()

    def on_Refresh_ADB_activate(self, widget):
        print "Refresh ADB client"

        try:
            count , treestore = self.ADB.getdevicelist()
        except OSError:
            print 'NO ADB FOUNDED! :@'
            self.msgbox('There is no ADB client founded on your computer', 'Please in install the client and try again!\nTry "sudo apt-get install android-tools-adb" in terminal', Gtk.MessageType.ERROR, Gtk.ButtonsType.OK)
            exit()
            return

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

        elif count == 0:
            self.msgbox('No android devices detected!', 'Connect and android device with USB debuging on!', Gtk.MessageType.ERROR)
            return

        elif count == 1:
             self.ADB.selectdevice(treestore)

        print self.ADB.Device, 'Selected'
        if self.ADB.SDK > 7:
            print 'The device has SDK version:', self.ADB.SDK
        else:
            print 'The device has SDK version:', self.ADB.SDK
            print 'No SDCARD apps wil be founded!'
        self.UpdateAPPlist()

    def UpdateAPPlist(self):
        treestore = Gtk.TreeStore(str)

        piter = treestore.append(None, ['DATA'])
        for child in self.ADB.GetDATAapplist():
            treestore.append(piter, [child])

        if self.ADB.SDK > 7:
            piter = treestore.append(None, ['SDCARD'])
            for child in self.ADB.GetSDCARDapplist():
                treestore.append(piter, [child])

        piter = treestore.append(None, ['SYSTEM'])
        for child in self.ADB.GetSYSTEMapplist():
            treestore.append(piter, [child])

        self.APKviewer.set_model(treestore)
        self.APKviewer.expand_all()

    def getselectionname(self, treeselection):
        model , select = treeselection.get_selected()
        if model.iter_has_child(select) == False:
            return model[model.iter_parent(select)][0] , model[select][0]

    def msgbox(self, message, secondary='', style=Gtk.MessageType.OTHER, button=Gtk.ButtonsType.OK):
        dialog = Gtk.MessageDialog(self, 0, style, button, message)
        dialog.format_secondary_text(secondary)
        returnvalue = dialog.run()
        dialog.hide()
        return returnvalue

    def iffile(self, filename):
        if not filename == None:
            return  os.path.isfile(filename)
        else:
            return False
    def clearup(self, string):
        returnstring =  re.sub('[%s]' % string.punctuation+string.digits, '', string).lower().replace('apk','')



