amplification = 1000
map_coords = (-38.808,175.152,-37.462,177.358)
map_center = ((map_coords[3]+map_coords[1])/2,(map_coords[2]+map_coords[0])/2)
map_coords = "("+str(map_coords[0])+","+str(map_coords[1])+","+str(map_coords[2])+","+str(map_coords[3])+")"
map_points_type = ["city","town","village"]

url = "http://overpass-api.de/api/interpreter?"


def query_string(type,key,value,coords):
     return(type+"['"+key+"'='"+value+"']"+coords+";out;")

coast_query = "(way['natural'='coastline'](-38.808,175.152,-37.462,177.358);>;);out;"

query = ""
for t in range(len(map_points_type)):
    query += query_string("node","place",map_points_type[t],map_coords)

import urllib2


data_coast = urllib2.urlopen(url+coast_query)
data_towns = urllib2.urlopen(url+query)
xml_nodes = data_towns.read()
xml_coast = data_coast.read()

import xml.etree.ElementTree as xml

root = xml.fromstring(xml_nodes)
#root = tree.getroot()
#print root
nodes = {}
counter = 0
for n in root.findall("node"):
    counter += 1
    nodes[counter] = {"id":int(n.attrib["id"]),"x":float(n.attrib["lon"]),"y":float(n.attrib["lat"])}
    for t in n.findall("tag"):
        if t.attrib["k"] == "name":
            nodes[counter]["name"] = t.attrib["v"]
        if t.attrib["k"] == "place":
            nodes[counter]["type"] = t.attrib["v"]
#print nodes

coast_nodes = {}
coast_lines = {}
root = xml.fromstring(xml_coast)
for n in root.findall("node"):
    coast_nodes[int(n.attrib["id"])] = {"x":float(n.attrib["lon"]),"y":float(n.attrib["lat"])}
counter = 0
for w in root.findall("way"):
    coast_lines[counter] = []
    for n in w.findall("nd"):
        coast_lines[counter].append(int(n.attrib["ref"]))
    counter += 1

from direct.showbase.ShowBase import ShowBase
from TimCam import TimCam
from pandac.PandaModules import NodePath, TextNode, TransparencyAttrib, GeomNode
from panda3d.core import LineSegs


class MapGen(ShowBase):
    def __init__(self,nodes):
        ShowBase.__init__(self)
        base.disableMouse()
        cam = TimCam()
        self.place_markers(nodes)
        self.line_coast()
        self.line_border()

    def place_markers(self,nodes):
        for n in range(len(nodes)):
            town_node = NodePath("town")
            town = loader.loadModel("models/infantry_counter.egg")
            x = (nodes[n+1]["x"]-map_center[0])*amplification
            y = (nodes[n+1]["y"]-map_center[1])*amplification
            town.setPos(x,y,0)
            if nodes[n+1]["type"] == "city":
                scale = 12
            elif nodes[n+1]["type"] == "town":
                scale = 7
            elif nodes[n+1]["type"] == "village":
                scale = 4
            town.setScale(scale,scale,scale)
            town.reparentTo(town_node)
            town_node.reparentTo(render)

            text_node = TextNode("town_text_node")
            text_node.setText(nodes[n+1]["name"])
            text_node_path = town.attachNewNode(text_node)
            text_node_path.setPos(1,0,0)
            text_node_path.setHpr(0,-90,0)
            text_node_path.setScale(scale/2)
            text_node_path.setTransparency(TransparencyAttrib.MAlpha)
            text_node.setTextColor(0.8, 0.1, 0.1, 1)
            text_node.setAlign(TextNode.ALeft)

    def line_coast(self):
        for l in range(len(coast_lines)):
            line = LineSegs()
            line.setColor(0,0,0, 1)
            line.setThickness(2)
            for n in range(len(coast_lines[l])):
                x = (coast_nodes[coast_lines[l][n]]["x"]-map_center[0])*amplification
                y = (coast_nodes[coast_lines[l][n]]["y"]-map_center[1])*amplification
                print x,y
                if n == 0:
                    line.moveTo(x,y,0)
                else:
                    line.drawTo(x,y,0)
            line_node = line.create()
            node_path = NodePath(line_node)
            node_path.reparentTo(render)

    def line_border(self):
        line = LineSegs()
        line.setColor(0,0,0, 1)
        line.setThickness(5)
        x1 = (175.152-map_center[0])*amplification
        x2 = (177.358-map_center[0])*amplification
        y1 = (-38.808-map_center[1])*amplification
        y2 = (-37.462-map_center[1])*amplification
        line.moveTo(x1,y1,0)
        line.drawTo(x1,y2,0)
        line.drawTo(x2,y2,0)
        line.drawTo(x2,y1,0)
        line.drawTo(x1,y1,0)
        line_node = line.create()
        node_path = NodePath(line_node)
        node_path.reparentTo(render)


app = MapGen(nodes)
app.setFrameRateMeter(True)
app.run()
