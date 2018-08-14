from AdidasDownloader import AdidasDownloader
from xvfbwrapper import Xvfb

# https://christopher.su/2015/selenium-chromedriver-ubuntu/

vdisplay = Xvfb()
vdisplay.start()
do = AdidasDownloader()
# https://www.adidas.ru/krossovki-deerupt-runner/B41768.html
# do.write_links_to_file('http://www.adidas.ru', 'adi_links.txt')
# do.write_links_to_file('http://www.adidas.ru/outlet', 'adi_links_outlet.txt')

# do.write_links_to_file('http://www.reebok.ru', 'rbk_links.txt')
# do.write_links_to_file('http://www.reebok.ru/outlet', 'rbk_links_outlet.txt')

do.download_html(['http://www.adidas.ru/krossovki-deerupt-runner/B41768.html'])
vdisplay.stop()