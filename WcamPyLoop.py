import datetime as dt
import Functions as  F
import picamera
from fractions import Fraction
import syslog 
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color

#syslog.syslog('WcamPi Main Loop Started') 
cam = picamera.PiCamera()
Settings = F.GetSettings('/boot/WcamPy_Settings.xml')
DaySettings = F.GetSettings('/boot/WcamPy_CamDaySettings.xml')
NightSettings = F.GetSettings('/boot/WcamPy_CamNightSettings.xml')

last_run = dt.datetime(1970,1,1,0,0,0)
last_info = dt.datetime.now()
while True:
	if F.IsDayLight(Settings['Latitude'],Settings['Longitude'],Settings['Elevation']):
		shottime = int(DaySettings['ShotInterval'])
	else:
		shottime = int(NightSettings['ShotInterval'])

	if (int((dt.datetime.now() - last_run).total_seconds()) > shottime):
		if F.IsDayLight(Settings['Latitude'],Settings['Longitude'],Settings['Elevation']):
#			syslog.syslog(syslog.LOG_INFO, 'Setting Day Parameters')
			F.SetCamera(cam,DaySettings)
		else:
#			syslog.syslog(syslog.LOG_INFO, 'Setting Night Parameters')
			F.SetCamera(cam,NightSettings)
#		syslog.syslog(syslog.LOG_INFO, 'Taking Photo')
		cam.capture(Settings['FTPFile'])

		img = Image(filename=Settings['FTPFile'])
		OverImg = Image(filename='/boot/TMLogo.png')

		draw = Drawing()
		draw.composite(operator='over',left=img.width - OverImg.width - 5,top=5,width=OverImg.width,height=OverImg.height,image=OverImg)
		draw(img)

                draw = Drawing()
                draw.fill_color = Color('blue')
		draw.fill_opacity = 0.5
		draw.rectangle(0,img.height - 30,img.width,img.height)
                draw(img)

		draw = Drawing()
		draw.font = 'wandtests/assets/League_Gothic.otf'
		draw.font_size = 20
		draw.fill_color = Color('white')
		draw.text_alignment = 'left'
		draw.text(5, img.height - 5, Settings['Description'])
		draw(img)

		draw = Drawing()
		draw.font = 'wandtests/assets/League_Gothic.otf'
		draw.font_size = 20
		draw.fill_color = Color('white')
		draw.text_alignment = 'right'
		draw.text(img.width - 5, img.height - 5, dt.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
		draw(img)

		img.format = 'jpeg'
		img.save(filename=Settings['FTPFile'])

#		syslog.syslog(syslog.LOG_INFO, 'Uploading Photo')
		F.FTPupload(Settings['FTPServer'],Settings['FTPUser'],Settings['FTPPass'],Settings['FTPDir'],Settings['FTPFile'])
		syslog.syslog(syslog.LOG_INFO, 'Done')
		last_run = dt.datetime.now()

	if (int((dt.datetime.now() - last_info).total_seconds()) > 120):
#		syslog.syslog(syslog.LOG_INFO, 'Running: next Shot in: '+str(shottime - int((dt.datetime.now() - last_run).total_seconds())) + ' seconds')
 		last_info = dt.datetime.now()

