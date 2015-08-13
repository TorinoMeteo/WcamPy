import datetime as dt
import ephem
import xml.etree.ElementTree as ET
from fractions import Fraction
import ftplib 

Shutter_Speed = [6000000,5000000,4000000,3000000,2000000,1000000,0,5000000,250000,125000,100000,50000,25000,12500]

class XmlListConfig(list):
    def __init__(self, aList):
        for element in aList:
            if element:
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)


class XmlDictConfig(dict):
    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if len(element):
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                else:
                    aDict = {element[0].tag: XmlListConfig(element)}
                if len(element.items()):
                    aDict.update(dict(element.items()))
                self.update({element.tag: aDict})
            elif len(element.items()):
                self.update({element.tag: dict(element.items())})
            else:
                self.update({element.tag: element.text})

def GetSettings(FileName):
	tree = ET.parse(FileName)
	Settings = tree.getroot()
	xmldict = XmlDictConfig(Settings)
	return xmldict

def IsDayLight(Lat,Lon,Elev):
	Observer = ephem.Observer()
	Observer.lon = str(Lon)
	Observer.lat = str(Lat)
	Observer.elevation = int(Elev)
	Observer.horizon = '-6'
	start_date_time = ephem.localtime(Observer.next_rising(ephem.Sun(), use_center=True))
	stop_date_time = ephem.localtime(Observer.next_setting(ephem.Sun(), use_center=True))
	if (start_date_time > stop_date_time):
		start_date_time = ephem.localtime(Observer.previous_rising(ephem.Sun(), use_center=True))
	if (start_date_time < dt.datetime.now()) and ( dt.datetime.now() < stop_date_time):
		return True
	else:
		return False
def str2bool(v):
	if (v=="True"):
		return True
	else:
		return False

def SetCamera(cam,Settings):
        aux_spd = float(Shutter_Speed[int(Settings['shutter_speed'])])/1000000.0
        if aux_spd > 1.0:
                aux_fr = Fraction(1,int(aux_spd))
        elif aux_spd == 1.0:
                aux_fr = Fraction(1,2)
        elif aux_spd < 1.0 and aux_spd > 0:
                aux_fr = int(1/aux_spd)
        else:
                aux_fr = 30
        cam.framerate = aux_fr
        cam.shutter_speed = Shutter_Speed[int(Settings['shutter_speed'])]
        cam.resolution=(int(Settings['width']),int(Settings['height']))
        cam.iso=int(Settings['iso'])
        cam.awb_mode=str(Settings['awb_mode'])
        cam.brightness=int(Settings['brightness'])
        cam.contrast=int(Settings['contrast'])
        cam.meter_mode=str(Settings['meter_mode'])
        cam.exposure_compensation=int(Settings['exposure_compensation'])
        cam.exposure_mode=str(Settings['exposure_mode'])
        cam.hflip=str2bool(Settings['hflip'])
        cam.vflip=str2bool(Settings['vflip'])
        cam.denoise=str2bool(Settings['denoise'])
        cam.led=str2bool(Settings['led'])

def FTPupload(host, user, password, dir, filetoupload):
	ftpconn = ftplib.FTP(host)
	ftpconn.login(user, password)
	ftpconn.cwd(dir)
	fp = open(filetoupload,'rb')
	ftpconn.storbinary('STOR '+filetoupload, fp)
	fp.close()
	ftpconn.quit() 


