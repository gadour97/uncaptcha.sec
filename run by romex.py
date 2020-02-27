import time
import pyautogui
import speech_recognition as sr
import os
import subprocess
from queryAPI import bing, google, ibm

''' You'll need to update based on the coordinates of your setup '''
FIREFOX_ICON_COORDS = (1347, 	 125) # Location of the Firefox icon on the side toolbar (to left click)
PRIVATE_COORDS		= (1291,  259) # Location of "Open a new Private Window"
PRIVATE_BROWSER 	= (1228, 379) # A place where the background of the Private Window will be
PRIVATE_COLOR		= '#25003E'  # The color of the background of the Private Window
SEARCH_COORDS 		= (303, 110) # Location of the Firefox Search box
REFRESH_COORDS      = (85, 122) # Refresh button
GOOGLE_LOCATION     = (18, 81) # Location of the Google Icon after navigating to google.com/recaptcha/api2/demo
GOOGLE_COLOR 		= '#4285F4'  # Color of the Google Icon
CAPTCHA_COORDS		= (59, 535) # Coordinates of the empty CAPTCHA checkbox
CHECK_COORDS 		= (58, 542) # Location where the green checkmark will be
CHECK_COLOR 		= '#009E55'  # Color of the green checkmark
AUDIO_COORDS		= (164, 739) # Location of the Audio button
DOWNLOAD_COORDS		= (228, 602) # Location of the Download button
FINAL_COORDS  		= (203, 542) # Text entry box
VERIFY_COORDS 		= (296, 650) # Verify button
CLOSE_LOCATION		= (1351, 44)

DOWNLOAD_LOCATION = "~/Downloads/"
''' END SETUP '''

r = sr.Recognizer()

def runCommand(command):
	''' Run a command and get back its output '''
	proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
	return proc.communicate()[0].split()[0]

def waitFor(coords, color):
	''' Wait for a coordinate to become a certain color '''
	pyautogui.moveTo(coords)
	numWaitedFor = 0
	while color != runCommand("eval $(xdotool getmouselocation --shell); xwd -root -silent | convert xwd:- -depth 8 -crop \"1x1+$X+$Y\" txt:- | grep -om1 '#\w\+'"):
		time.sleep(.1)
		numWaitedFor += 1
		if numWaitedFor > 25:
			return -1
	return 0

def downloadCaptcha():
	''' Navigate to demo site, input user info, and download a captcha. '''
	print("Opening Firefox")
	pyautogui.moveTo(FIREFOX_ICON_COORDS)
	pyautogui.leftClick()
	time.sleep(.3)
	pyautogui.moveTo(PRIVATE_COORDS)
	pyautogui.click()
	time.sleep(.5)


	print("Visiting Demo Site")
	pyautogui.moveTo(SEARCH_COORDS)
	pyautogui.click()
	pyautogui.typewrite('www.google.com/recaptcha/api2/demo', interval=0.13)
	pyautogui.press('enter')
	time.sleep(5)
	# Check if the page is loaded...
	pyautogui.moveTo(GOOGLE_LOCATION)


	print("Downloading Captcha")

	pyautogui.moveTo(CAPTCHA_COORDS)
	pyautogui.click()
	time.sleep(2)
	pyautogui.moveTo(AUDIO_COORDS)
	pyautogui.click()
	time.sleep(2)
	pyautogui.moveTo(DOWNLOAD_COORDS)
	pyautogui.click()
	time.sleep(2)
	pyautogui.moveTo(1024, 477)#saveas
	pyautogui.rightClick()
	time.sleep(2)
	pyautogui.moveTo(1046, 636)#saveas
	pyautogui.leftClick()
	time.sleep(2)
	pyautogui.moveTo(1242, 48)#save
	time.sleep(2)
	pyautogui.leftClick()
	time.sleep(1)
	pyautogui.moveTo(93, 78)#backtocaptchasite
	pyautogui.leftClick()
	time.sleep(2)

	return 0



def runCap():

		print("Removing old files...")
		os.system('rm ./audio.wav 2>/dev/null') # These files may be left over from previous runs, and should be removed just in case.
		os.system('rm ' + DOWNLOAD_LOCATION + 'audio.mp3 2>/dev/null')
		# First, download the file
		downloadResult = downloadCaptcha()
		if downloadResult == 2:
			pyautogui.moveTo(CLOSE_LOCATION)
			pyautogui.click()
			return 2
		elif downloadResult == -1:
			pyautogui.moveTo(CLOSE_LOCATION)
			pyautogui.click()
			return 3


		# Convert the file to a format our APIs will understand
		print("Converting Captcha...")
		os.system('ffmpeg -i ~/Downloads/audio.mp3 ~/uncaptcha2/audio.wav 2>/dev/null')
		with sr.AudioFile('audio.wav') as source:
			audio = r.record(source)

		print("Submitting To Speech to Text:")
		determined = google(audio) # Instead of google, you can use ibm or bing here
		print(determined)

		print("Inputting Answer")
		# Input the captcha
		pyautogui.moveTo(FINAL_COORDS)
		pyautogui.click()
		time.sleep(.5)
		pyautogui.typewrite(determined, interval=.03)
		time.sleep(.5)
		pyautogui.moveTo(VERIFY_COORDS)
		pyautogui.click()
		time.sleep(2)
		pyautogui.moveTo(72,606)
		pyautogui.leftClick()

		return 3




if __name__ == '__main__':
	success = 0
	fail = 0
	allowed = 0

	# Run this forever and print statistics
	while True:
		res = runCap()
		if res == 3:
			success += 1
		elif res == 2: # Sometimes google just lets us in
			allowed += 1
		else:
			fail += 1

		print("SUCCESSES: " + str(success) + " FAILURES: " + str(fail) + " Allowed: " + str(allowed))
		pyautogui.moveTo(CLOSE_LOCATION)
		pyautogui.click()
