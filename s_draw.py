# -*- coding: utf-8 -*-
"""
/***************************************************************************
 sDraw
                                 A QGIS plugin
 This plugin draws spatially ballanced samples
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-07-03
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Jared Spaulding - WEST
        email                : jspaulding@west-inc.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMessageBox

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .s_draw_dialog import sDrawDialog
import os.path
import os, sys
import subprocess
import datetime
import csv

class sDraw:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'sDraw_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&SDraw')

        self.dlg = sDrawDialog()

        self.dlg.btn_draw.clicked.connect(self.draw)

        self.dlg.rejected.connect(self.close)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('sDraw', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/s_draw/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Draw spatially balanced samples'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&SDraw'),
                action)
            self.iface.removeToolBarIcon(action)

    def popCbType(self):
        types = ["BAS", "SSS", "GRTS", "SRS", "HIP"]
        for i, t in enumerate(types):
            self.dlg.cb_type.insertItem(i, t)

    def close(self):
        self.dlg.cb_type.clear()
        self.dlg.close()

    def draw(self):
        # Check to make sure all parameters are filled
        if self.dlg.le_n.text() != "" and self.dlg.cb_layer.currentLayer() != None:

            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            # Start a subprocess that calls the SDraw script
            process = subprocess.Popen([os.environ['R_HOME'] + "/Rscript.exe", self.plugin_dir + "/s_draw.r", 
                self.dlg.le_n.text(), self.dlg.cb_type.currentText(), self.dlg.cb_layer.currentLayer().source()], 
                stdout=subprocess.PIPE, startupinfo=si)

            result = []
            self.dlg.progressBar.setRange(0,100)
            self.dlg.progressBar.setValue(0)

            while process.stdout is not None:

                # Update spinner on one step:
                # It will update only when any line was printed to stdout!
                self.dlg.progressBar.setValue(self.dlg.progressBar.value() + 1)
                # Read each line:

                line = process.stdout.readline()
                # Add line in list and remove carriage return

                result.append(line.decode('UTF-8').rstrip('\r'))

                # When no lines appears:
                if not line:
                    print("\n")
                    process.stdout.flush()
                    break

            # Wait for the process to finish
            process.wait()
            self.dlg.progressBar.setValue(100)

            try:
                # Get filename from results 
                file = ""
                for line in result:
                    if "[1] " in line:
                        file = line
                        file = file.split('[1] ')[1]
                        file = file.replace('"', '')

                # get the directory of the chosen file
                layerDir = self.dlg.cb_layer.currentLayer().source().replace("\\", ",")

                # split the directory up into parts
                layerDir = layerDir.replace("/", ",")
                layerDir = layerDir.split(",")
                dirs = layerDir[:-1]

                # Assemble a uniform path from all the parts 
                if len(dirs) != 0:
                    path = ""
                    for element in dirs:
                        path += element + "/"

                # join the file path returned from R with the directory path and add extension
                path = os.path.join(path, file, ".shp")

                # Remove additional "\" join method adds
                path = path.replace('\\', '')

                # Have to use below method to get rid of the carridge  return
                # rstrip() doesnt work nor does replace
                path = path.splitlines()[0] + path.splitlines()[1]
                print(path)
                self.iface.addVectorLayer(path, "", "ogr")

                self.close()
            except:
                msg = QMessageBox()
                data = ""
                for i in result:
                    data = data + i
                msg.setText("An unexpected error has occured: " + data)
                msg.exec_()

        else:
            msg = QMessageBox()
            msg.setText("All fields are required")
            msg.exec_()

    def run(self):
        """Run method that performs all the real work"""

        if os.environ.get('R_HOME') is not None:
            # Populate type combo box
            self.popCbType()

            # show the dialog
            self.dlg.show()
        else:
            msg = QMessageBox()
            msg.setText("Environment variable 'R_HOME' could not be found. Make sure it is installed correctly. QGIS restart required.")
            msg.exec_()
