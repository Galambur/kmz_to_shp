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
      icon = os.path.join(os.path.join(cmd_folder, 'logo.png')) # add the logo to the plugin
      self.action = QAction(QIcon(icon), 'Convertisseur kmz shp', self.iface.mainWindow())
      self.action.triggered.connect(self.run)
      self.iface.addPluginToMenu('&Convertisseur kmz shp', self.action)
      self.iface.addToolBarIcon(self.action)

    def unload(self):
      self.iface.removeToolBarIcon(self.action)
      self.iface.removePluginMenu('Convertisseur kmz shp', self.action)  
      del self.action

    def run(self):
        self.iface.messageBar().pushMessage("L'extension 'Convertisseur kmz shp' a été lancée")
        button.show() #shows our widgets
        button.activateWindow() ## met le widget au premier plan
      
            
    def main_func(self, on):
        self.close()
        main()
            


button = converter()
button.show()


########## MAIN FUNCTION ########## 
    
def main():
    iface.messageBar().pushMessage('La trame commence')
    test = get_names_group("SODIAC_PATRIMOINE")
    
    if test == False : ## on n'a pas trouvé de groupe avec le nom cherché : on ne continue pas le programme
        print("stop car pas de groupe trouvé")
    else : ## il y a bien un groupe avec le nom cherché
        opening("L:/DPG/Stratégie/SIG/Cartes dynamiques/GEO intranet/SIDOM/Données/SODIAC.shp", "SODIAC")

        layer_to_paste = QgsProject.instance().mapLayersByName('SODIAC')[0]
        
        with edit(layer_to_paste):
            for layer_to_copy in QgsProject.instance().mapLayers().values():
                if layer_to_copy.name() != "SODIAC" : # on évite de copier puis enlever la couche dans laquelle on colle
                    copying(layer_to_copy.name())
                else :
                    print ("selected layer to paste")
        
        delete_duplicate('L:/DPG/Stratégie/SIG/Cartes dynamiques/GEO intranet/SIDOM/Données/SODIAC.shp', "L:/DPG/Stratégie/SIG/Cartes dynamiques/GEO intranet/SIDOM/Données/SODIAC_CLEAN.shp")
 
 
    #####
def get_names_group(group_name):
    root = QgsProject.instance().layerTreeRoot()
    the_group = root.findGroup(group_name)
        
    if the_group is not None : ## le groupe existe bien
        for child in the_group.children():
            layer = QgsProject.instance().mapLayersByName(child.name())

            if layer[0].geometryType() == QgsWkbTypes.PointGeometry : ## on ne veut récupérer que les couches points
                func_convert(child.name(), child)
            else : 
                print(layer[0], " not a point geom")
        root.removeChildNode(the_group)
        return True
    else :  # if the_group is not None 
        return False


    ##### CONVERT KMZ TO SHP #####
def func_convert(layer_name, child):
    
    layer = QgsProject.instance().mapLayersByName(layer_name)[0] # on réfcupère la couche avec le nom qu'on a recu
    iface.setActiveLayer(layer)
    
    myfilepath= iface.activeLayer().dataProvider().dataSourceUri()
    (myDirectory,nameFile) = os.path.split(myfilepath) ## récupération du chemin et du nom du fichier
    
    file_name = layer_name
    myfilepath = myDirectory + r'/SHP/' + file_name

    _writer = QgsVectorFileWriter.writeAsVectorFormat(layer,myfilepath,'utf-8',driverName='ESRI Shapefile') ## création du fichier
    
    path = myfilepath.rsplit('/', 1)[0] + "/" # on se débarasse du nom du fichier pour garder juste le chemin
        
    vlayer = QgsVectorLayer(path, file_name, "ogr")
        
    if not vlayer.isValid():
        print("Layer failed to load! ", layer_name)
    else:       
        # déplacer la couche en dehors du groupe
        root = QgsProject.instance().layerTreeRoot()
        
        mygroup = root.findGroup("SODIAC_PATRIMOINE")
        
        ## on ouvre le fichier converti et on le déplace en dehors du groupe
        parentGroup = mygroup.parent()
        groupIndex=-1
        for child in parentGroup.children():
            groupIndex+=1
            if mygroup == child:
                break
        QgsProject.instance().addMapLayer(vlayer, False)
        parentGroup.insertChildNode(groupIndex, QgsLayerTreeLayer(vlayer))



    ## fonction pour ouvrir une couche à partir d'un chemin
def opening(path, name):
    ## ouvrir la couche
    vlayer = QgsVectorLayer(path_sodiac, name, "ogr")
        
    if not vlayer.isValid():
        print("Layer failed to load!")
    else:
        QgsProject.instance().addMapLayer(vlayer)
  
  
  
    ## fonction copier toutes les valeurs d'une couches dans une autre
def copying (layer_to_copy):

    ## sélection de la couche qui porte le nom qu'on reçoit
    layer = QgsProject.instance().mapLayersByName(layer_to_copy)[0]
    iface.setActiveLayer(layer)
    
    ## copie des valeurs de la couche ci dessus dans l'autre couche
    layer_to_paste = QgsProject.instance().mapLayersByName('SODIAC')[0]
    features = []
    for feature in layer.getFeatures(): ## récupère toutes les features de la couche à copier
        features.append(feature)
        
    data_provider = layer_to_paste.dataProvider()
    data_provider.addFeatures(features) ## colle
        
    QgsProject.instance().removeMapLayer(layer) ## retire la couche copiée de la légende
    
    
def delete_duplicate(layer_to_clean, output):
    
    processing.run("qgis:deleteduplicategeometries", {'INPUT':layer_to_clean,'OUTPUT':output}) #utilise les paths des couche
    
    ## ouverture de la couche nettoyée
    path = "L:/DPG/Stratégie/SIG/Cartes dynamiques/GEO intranet/SIDOM/Données/SODIAC_CLEAN.shp"
    opening(path, "SODIAC_CLEAN")
#    vlayer = QgsVectorLayer(path, "SODIAC_CLEAN", "ogr")
#    if not vlayer.isValid():
#        print("Layer failed to load!")
#    else:
#        QgsProject.instance().addMapLayer(vlayer)
