import os
import sys
import inspect
import processing
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.utils import iface
from qgis.core import *
from qgis.gui import *

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]      

class converter(QWidget):
    def __init__(self, parent=None):
        self.iface = iface
        QWidget.__init__(self, parent)
        self.layout = QVBoxLayout()

        # Add the radio buttons
        self.point = QPushButton("Les points")

        # Connect radio buttons to our functions
        self.point.clicked.connect(self.main_func)

        #Add the widgets to the layout:
        self.layout.addWidget(self.point)

        #Set the layout:
        self.setLayout(self.layout)  
        self.setWindowTitle("Fichier KMZ")

    def initGui(self):
      icon = os.path.join(os.path.join(cmd_folder, 'logo.jpg')) # add the logo to the plugin
      self.action = QAction(QIcon(icon), 'Converter kmz shp', self.iface.mainWindow())
      self.action.triggered.connect(self.run)
      self.iface.addPluginToMenu('&Converter kmz shp', self.action)
      self.iface.addToolBarIcon(self.action)

    def unload(self):
      self.iface.removeToolBarIcon(self.action)
      self.iface.removePluginMenu('Converter kmz shp', self.action)  
      del self.action

    def run(self):
        self.iface.messageBar().pushMessage("L'extension 'Converter kmz shp' a été lancée")
        button.show() #shows our widgets
        button.activateWindow() ## met le widget au premier plan
      
            
    def main_func(self, on):
        self.close()
        print("entering get names")
        main()
            


button = converter()
button.show()


########## MAIN FUNCTION ########## 
    
def main():
    iface.messageBar().pushMessage('La trame commence')
    get_names_group()
    
    path_sodiac = "L:/DPG/Stratégie/SIG/Cartes dynamiques/GEO intranet/SIDOM/Données/SODIAC.shp"
    vlayer = QgsVectorLayer(path_sodiac, "SODIAC", "ogr")
    
    if not vlayer.isValid():
        print("Layer failed to load!")
    else:
        QgsProject.instance().addMapLayer(vlayer)

    layer_to_paste = QgsProject.instance().mapLayersByName('SODIAC')[0]
    
    with edit(layer_to_paste):
        for layer_to_copy in QgsProject.instance().mapLayers().values():
            if layer_to_copy.name() != "SODIAC" :
                print("would copy", layer_to_copy.name())
                copying(layer_to_copy.name())
            else :
                print ("selected layer ensemble")
 
 
    #####
def get_names_group():
    root = QgsProject.instance().layerTreeRoot()
    the_group = root.findGroup("SODIAC_PATRIMOINE")
        
    if the_group is not None :
        for child in the_group.children():
            layer = QgsProject.instance().mapLayersByName(child.name())

            if layer[0].geometryType() == QgsWkbTypes.PointGeometry : ## on ne veut récupérer que les couches points
                func_convert(child.name(), child)
            else : 
                print(layer[0], " not a point geom")
        root.removeChildNode(the_group)
    else :  # if the_group is not None 
        print("Le groupe n'a pas été trouvé")
                


    ##### CONVERT KMZ TO SHP #####
def func_convert(layer_name, child):
    
    layer = QgsProject.instance().mapLayersByName(layer_name)[0]
    iface.setActiveLayer(layer)
    
    myfilepath= iface.activeLayer().dataProvider().dataSourceUri()
    (myDirectory,nameFile) = os.path.split(myfilepath)
    
    file_name = layer_name #+ '.shp'
    myfilepath = myDirectory + r'/SHP/' + file_name

    _writer = QgsVectorFileWriter.writeAsVectorFormat(layer,myfilepath,'utf-8',driverName='ESRI Shapefile')
    
    path = myfilepath.rsplit('/', 1)[0] + "/"
        
    vlayer = QgsVectorLayer(path, file_name, "ogr")
        
    if not vlayer.isValid():
        print("Layer failed to load! ", layer_name)
    else:       
        # déplacer la couche en dehors du groupe
        root = QgsProject.instance().layerTreeRoot()
        
        mygroup = root.findGroup("SODIAC_PATRIMOINE")
        
        parentGroup = mygroup.parent()
        groupIndex=-1
        for child in parentGroup.children():
            groupIndex+=1
            if mygroup == child:
                break
        QgsProject.instance().addMapLayer(vlayer, False)
        parentGroup.insertChildNode(groupIndex, QgsLayerTreeLayer(vlayer))        

  
    ## fonction copier toutes les valeurs des couches dans ensemble.shp
def copying (layer_to_copy):

    layer = QgsProject.instance().mapLayersByName(layer_to_copy)[0]
    iface.setActiveLayer(layer)
    
    layer_to_paste = QgsProject.instance().mapLayersByName('SODIAC')[0]
    features = []
    for feature in layer.getFeatures():
        features.append(feature)
        
    data_provider = layer_to_paste.dataProvider()
    data_provider.addFeatures(features)
        
    QgsProject.instance().removeMapLayer(layer)
