import csv
import sys
import json
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QPushButton, QListWidget, QLabel


filesJunk = r'data\junk.csv'
filesStations = r'data\stations2.csv'
filesRequiredJunk = r'data\requiredItems.csv'


stations = {}
junks = {}
requirements = {}


class rqdJunk:
    def __init__(self, idJunk, name ,qtyreq):
        self.reqdJunkId   = idJunk
        self.reqdJunkName = name
        self.reqdJunkQty  = qtyreq


class station:
    def __init__(self, idNbr, name, level = 1):
        self.stationId    = idNbr
        self.stationName =  name
        self.stationLevel = level
        self.stationRequirements = []

    def addJunkReq(self, junkReq):
        self.stationRequirements.append(junkReq)

    def __str__(self):
        return self.stationId

    def getName(self):
        return self.stationName

    def printReqs(self):
        for req in self.stationRequirements:
            print(f'{req.reqdJunkName} x {req.reqdJunkQty}')

    def getReqs(self):
        return self.stationRequirements


class junk:
    def __init__(self, idNbr, name):
        self.junkId = idNbr
        self.junkName = name
    def __str__(self):
        return self.junkName

class quest:
    def __init__(self, idNbr, name, desc):
        self.id = idNbr
        self.name = name
        self.description = desc

class profile:
    def __init__(self, idNbr, name, level):
        self.id = idNbr
        self.name = name
        self.level = level
        self.stations = []
        self.questsActive = []
        self.questsCompleted = []

def loadData():
    #load stations
    with open(filesStations,newline = '') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            stations[row[0]] = station(row[0],row[1])

    with open(filesJunk,newline = '') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            junks[row[0]] = junk(row[0],row[1])
            print(junks[row[0]])

    with open(filesRequiredJunk,newline = '') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                #print(row)
                requirements[row[0]] = rqdJunk(row[0],row[1],row[2], row[3])
                print(requirements[row[0]])

def tryJson():
    with (open(r'data\stations.json') as json_file):
        data = json.load(json_file)

        for stationx in data:

            for level in stationx['levels']:
                stationName = f'{stationx["name"]} {level['level']}'
                newStation = station(stationx['id'], stationName)

                for itemReq in level['itemRequirements']:
                    newStation.addJunkReq(rqdJunk(itemReq['item']['id'], junks[itemReq['item']['id']], itemReq['quantity']))


                newStation.stationLevel = level['level']
                stations[stationName] = newStation


def loadItems():
    with open('data\\items.json', 'r', encoding='utf-8') as json_file:
        dataLoaded = json.load(json_file)

        for data in dataLoaded['data']:
            junks[data['id']] = junk(data['id'], data['name'])


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        #self.actionExit = self.findChild(QtWidgets.QAction, "actionExit")
        #self.actionExit.triggered.connect(self.closeEvent)


        self.setFixedWidth(800)
        self.setFixedHeight(600)
        self.setWindowTitle("My App")
        self.junkNeeded = {}

        self.stationWdgAvailableLabel = QLabel('Stations available', self)
        self.stationWdgAvailableLabel.move(10, 5)
        self.stationWdgAvailable = QListWidget(self)
        self.stationWdgAvailable.move(10, 30)
        self.stationWdgAvailable.resize(200, 200)
        self.stationWdgAvailable.itemClicked.connect(self.station_clicked)
        for station in stations:
            self.stationWdgAvailable.addItem(station)
        self.stationWdgAvailable.sortItems()

        #list all built stations
        self.stationWdgBuiltLabel = QLabel('Stations built', self)
        self.stationWdgBuiltLabel.move(310, 5)
        self.stationWdgBuilt = QListWidget(self)
        self.stationWdgBuilt.move(310, 30)
        self.stationWdgBuilt.resize(200, 200)
        self.stationWdgBuilt.itemClicked.connect(self.station_clicked)
        self.stationWdgBuilt.sortItems()

        # junk required for selected item
        self.junkNeededSelectedWdgLabel = QLabel('Junk needed (selected station)', self)
        self.junkNeededSelectedWdgLabel.move(10, 265)
        self.junkNeededSelectedWdgLabel.resize(150, 15)
        self.junkNeededSelectedWdg = QListWidget(self)
        self.junkNeededSelectedWdg.move(10, 290)
        self.junkNeededSelectedWdg.resize(320, 250)

        # list all junk required stations
        self.junkNeededWdgLabel = QLabel('Junk needed (all remamining)', self)
        self.junkNeededWdgLabel.move(300, 265)
        self.junkNeededWdgLabel.resize(150,15)
        self.junkNeededWdg = QListWidget(self)
        self.junkNeededWdg.move(300, 290)
        self.junkNeededWdg.resize(400, 250)
        self.recalcJunk()

        #button to mark station as built
        self.buttonskiAdd = QPushButton(text="Mark Built >>", parent=self)
        self.buttonskiAdd.move(220, 75)
        self.buttonskiAdd.resize(80,40)
        self.buttonskiAdd.clicked.connect(self.stationMarkBuilt)


        # button to mark station as unbuilt
        self.buttonskiRem = QPushButton(text="<< Remove", parent=self)
        self.buttonskiRem.move(220, 125)
        self.buttonskiRem.resize(80, 40)
        self.buttonskiRem.clicked.connect(self.removeBuilt)

        self.buttonskiLoad = QPushButton(text="Load profile", parent=self)
        self.buttonskiLoad.move(520, 125)
        self.buttonskiLoad.resize(80, 40)
        self.buttonskiLoad.clicked.connect(self.loadprofile)

        self.buttonskiSave = QPushButton(text="Save", parent=self)
        self.buttonskiSave.move(520, 175)
        self.buttonskiSave.resize(80, 40)
        self.buttonskiSave.clicked.connect(self.saveprofile)

    def saveprofile(self):
        stationsToSave = []
        for index in range(self.stationWdgBuilt.count()):
            stationsToSave.append(self.stationWdgBuilt.item(index).text())
            #stationsToSave[station.text()] = stations[station.text()]

        with open(r'data\profile.json', 'w', encoding='utf-8') as outfile:
            json.dump(stationsToSave, outfile, ensure_ascii=False, indent=4)

    def loadprofile(self):
        self.stationWdgBuilt.clear()
        with open(r'data\profile.json', 'r',
                  encoding='utf-8') as json_file:
            data = json.load(json_file)

        for station in data:
            item = stations[station]
            name = item.getName()
            self.stationWdgBuilt.addItem(item.getName())

            # iterate backwards to avoid index shifting issues
            for index in range(self.stationWdgAvailable.count() - 1, -1, -1):
                if self.stationWdgAvailable.item(index).text() == name:
                    self.stationWdgAvailable.takeItem(index)

            self.stationWdgAvailable.sortItems()
            self.recalcJunk()







    def recalcJunk(self):
        self.junkNeeded = {}
        itemsx = []
        for index in range(self.stationWdgAvailable.count()):
            itemsx.append(self.stationWdgAvailable.item(index).text())
        for line in itemsx:
            stationx = stations[line]
            for req in stationx.stationRequirements:
                if req.reqdJunkName in self.junkNeeded:
                    self.junkNeeded[req.reqdJunkName] += req.reqdJunkQty
                else:
                    self.junkNeeded[req.reqdJunkName] = req.reqdJunkQty
        self.junkNeededWdg.clear()
        for jnk in self.junkNeeded:
            self.junkNeededWdg.addItem(f'{jnk} x {self.junkNeeded[jnk]}')

        self.junkNeededWdg.sortItems()


    def stationMarkBuilt(self):
        items = self.stationWdgAvailable.selectedItems()
        for item in items:
            print(item)
            #i = stations[item.text()]
            self.stationWdgAvailable.takeItem(self.stationWdgAvailable.row(item))
            self.stationWdgBuilt.addItem(item)
        self.junkNeededSelectedWdg.clear()
        self.stationWdgBuilt.sortItems()
        self.recalcJunk()
        return

    def removeBuilt(self):
        items = self.stationWdgBuilt.selectedItems()
        for item in items:
            #i = stations[item.text()]
            self.stationWdgBuilt.takeItem(self.stationWdgBuilt.row(item))
            self.stationWdgAvailable.addItem(item)
        self.stationWdgAvailable.sortItems()
        self.recalcJunk()
        return


    def station_clicked(self, item):
        item = stations[item.text()]
        self.junkNeededSelectedWdg.clear()
        for req in item.stationRequirements:
            #print(req.reqdJunkName)
            self.junkNeededSelectedWdg.addItem(f'{req.reqdJunkName} {req.reqdJunkQty}')


        print('|---------' , item.getName() ,'---------|')
        item.printReqs()
        print('|----------------------------|')


def mainStart():
    loadItems()
    tryJson()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()



mainStart()



