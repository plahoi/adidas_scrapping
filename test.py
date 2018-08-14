from xvfbwrapper import Xvfb
from selenium import webdriver

vdisplay = Xvfb()
vdisplay.start()
driver = webdriver.Chrome()
driver.get('http://www.adidas.ru/krossovki-deerupt-runner/B41768.html')
print(driver.title)