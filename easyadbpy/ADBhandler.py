# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

from gi.repository import Gtk
import shlex, subprocess

#ADB CLASS
class ADBhandler:
    Device = None
    SDK = int

    def getdevicelist(self):
        devicelist =  subprocess.check_output(['adb', 'devices'])
        devicelist = devicelist.replace('List of devices attached', '')
        treestore = Gtk.TreeStore(str)
        count = 0
        device = str
        for text in devicelist.splitlines():
           if not 'list of atached devices' in text and text.split():
                treestore.append(None, [text])
                device = text
                count += 1
        if count > 1:
            return count , treestore
        else:
            return count , device

    def selectdevice(self, device):
        self.Device = device.split()[0]
        self.SDK = self.GetAndroidSDK()
        
    def GetDATAapplist(self):
        return self.GetFilelist('/data/app/*.apk')

    def GetSYSTEMapplist(self):
        return self.GetFilelist('/system/app/*.apk')

    def GetSDCARDapplist(self):
        self.GetAndroidSDK()
        returnstring = list()
        for text in self.GetFilelist('/mnt/asec/'):
            returnstring.append(text + '.apk')
        return returnstring
       
    def GetFilelist(self, path):
        p = subprocess.Popen(['adb -s %s shell' % self.Device], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        p.stdin.write('su \n')  
        p.stdin.write('ls %s | xargs -n1 basename \n' % path) 
        p.stdin.write('exit \n')
        p.stdin.write('exit \n')  
        output , err = p.communicate()
        returnstring = list()
        for text in output.split():
            if not text in ['su', 'ls', '|', 'xargs', '-n1', 'basename', path, 'exit' , '#', '$', 'shell@android:/','root@android:/']: 
                returnstring.append(text)
        return returnstring

    def installAPK(self, filename):
        output = subprocess.Popen(['adb install %s' % filename] ,stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        output , err = output.communicate()
        print output
        if '[INSTALL_FAILED_ALREADY_EXISTS]' in output:
            print 'Aplication is already installed'
            return -1
        return None

    def PullSYSTEMAPK(self, apkname, location):
        subprocess.Popen(['adb pull /system/app/%s %s' % (apkname, location)] ,stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)

    def PullDATAAPK(self, apkname, location):
        subprocess.Popen(['adb pull /data/app/%s %s' % (apkname, location)] ,stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
   
    def PullSDCARDAPK(self, apkname, location):
        subprocess.Popen(['adb pull /mnt/asec/%s/pkg.apk %s' % (apkname.replace('.apk',''), location)] ,stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)

    def GetAndroidSDK(self):
        if not self.Device == None:
            value = subprocess.check_output(['adb -s %s shell cat /system/build.prop | grep ro.build.version.sdk' % self.Device], shell=True)
            return int(value.split('=')[1])
        else:
            raise exception('No Device selected')
