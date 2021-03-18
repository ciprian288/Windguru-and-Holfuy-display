# standard imports
import datetime
import time
import os
from os import path
import platform
import signal
import pygame
from pygame.locals import QUIT, VIDEORESIZE, KEYDOWN, K_q
import requests

# local imports
import config

url_holfuy = "http://api.holfuy.com/live/?s={s}&pw={pw}&&m=JSON&tu=C&su=knots&batt"

def exit_gracefully(signum, frame):
    sys.exit(0)

signal.signal(signal.SIGTERM, exit_gracefully)

###############################################################################
class MyDisplay:
    screen = None

    def __init__(self):
        self.last_update_check = 0
        self.get_forecast()
        
        "Ininitializes a pygame screen using the framebuffer"
        if platform.system() == 'Darwin':
            pygame.display.init()
            driver = pygame.display.get_driver()
            print('Using the {0} driver.'.format(driver))
        else:
           
            disp_no = os.getenv("DISPLAY")
            if disp_no:
                print("X Display = {0}".format(disp_no))
                
            drivers = ['x11', 'fbcon', 'directfb', 'svgalib']
            found = False
            for driver in drivers:
                # Make sure that SDL_VIDEODRIVER is set
                if not os.getenv('SDL_VIDEODRIVER'):
                    os.putenv('SDL_VIDEODRIVER', driver)
                try:
                    pygame.display.init()
                except pygame.error:
                    print('Driver: {0} failed.'.format(driver))
                    continue
                found = True
                break

            if not found:
                print("No suitable video driver found!")
                raise Exception('No suitable video driver found!')
        
        #size = (800, 480)
        size = (pygame.display.Info().current_w, 
                pygame.display.Info().current_h)
        size_half = (int(pygame.display.Info().current_w * 0.5), 
                     int(pygame.display.Info().current_h * 0.5 + 50))

        if config.FULLSCREEN:
            self.screen = pygame.display.set_mode(size, pygame.NOFRAME)
            self.xmax = pygame.display.Info().current_w 
            self.ymax = pygame.display.Info().current_h 
            print("Framebuffer Size: %d x %d" % (size[0], size[1]))
            
        else:
            self.screen = pygame.display.set_mode(size_half, pygame.RESIZABLE)
            pygame.display.set_caption('WIND Dashboard')
            self.xmax = pygame.display.get_surface().get_width()
            self.ymax = pygame.display.get_surface().get_height()
            print(self.xmax, self.ymax)
                    
        # Clear the screen to start
        self.screen.fill((0, 0, 0))
        # Initialise font support
        pygame.font.init()
        # Render the screen
        pygame.mouse.set_visible(0)
        pygame.display.update()
        
        
    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."
    
    def deg_to_compass(self, degrees):
        val = int((degrees/22.5)+.5)
        dirs = ["N", "NNE", "NE", "ENE",
                "E", "ESE", "SE", "SSE",
                "S", "SSW", "SW", "WSW",
                "W", "WNW", "NW", "NNW"]
        return dirs[(val % 16)]

    def get_forecast(self):
        if (time.time() - self.last_update_check) > config.DS_CHECK_INTERVAL:
            self.last_update_check = time.time()
            #try:
            if not config.HOLFUY_API_KEY:
                url = 'https://www.windguru.cz/int/iapi.php?q=station_data_current&id_station={s}&date_format=Y-m-d%20H%3Ai%3As%20T&_mha=f4d18b6c'.format(s=config.ID_STATION)
                url_h = 'https://www.windguru.cz/station/{s}'.format(s=config.ID_STATION)
                headers = {'Referer' : url_h}
                self.wind = requests.get(url, headers = headers).json()
            
            else:
                querystring_h = {
                "s": config.ID_STATION,
                "pw": config.HOLFUY_API_KEY
                }
                self.wind = requests.request("GET", url_holfuy, params=querystring_h).json()                

        return True

    def holfuy(self):

        text_color = (255, 255, 255)
        font_name = "dejavusans"

        regular_font = pygame.font.SysFont(font_name, int(self.ymax * 0.16), bold=1)
        small_font = pygame.font.SysFont(font_name, int(self.ymax * 0.13), bold=1)
        error_font = pygame.font.SysFont(font_name, int(self.ymax * 0.05), bold=1)

        if self.xmax <= 1024:
            icon_wind_size = '400'
        else:
            icon_wind_size = '700'   
        
        if 'error' in self.wind.values() or 'error' in self.wind:

            text = "ERROR"
            text_render = error_font.render(text, True, (255, 0, 0))
            text_rect = text_render.get_rect(center=(self.xmax * 0.5, self.ymax * 0.2))
            self.screen.blit(text_render, text_rect)

            text = "Wrong wind data in config.py ."
            text_render = error_font.render(text, True, (255, 0, 0))
            text_rect = text_render.get_rect(center=(self.xmax * 0.5, self.ymax * 0.4))
            self.screen.blit(text_render, text_rect)
            
            logo = path.join(path.dirname(__file__), 'icons/logo/{}/wind.png'.format(icon_wind_size))
            logo_load = pygame.image.load(logo)
            self.screen.blit(logo_load, (self.xmax * 0.3, self.ymax * 0.5))
        
        elif not config.HOLFUY_API_KEY:
            wind_speed = self.wind['wind_avg']
            wind_gust = self.wind['wind_max']
            wind_dir = self.wind['wind_direction']

            if 0 <= wind_speed <= 14:
                text_regular = (51, 187, 255)
                icon = path.join(path.dirname(__file__), 'icons/blue/{}/{}.png'.format(icon_wind_size, self.deg_to_compass(wind_dir)))
            if 14.1 < wind_speed <= 17:
                text_regular = (97, 209, 97)
                icon = path.join(path.dirname(__file__), 'icons/green/{}/{}.png'.format(icon_wind_size, self.deg_to_compass(wind_dir)))
            if 17.1 < wind_speed <= 24:
                text_regular = (255, 182, 32)
                icon = path.join(path.dirname(__file__), 'icons/orange/{}/{}.png'.format(icon_wind_size, self.deg_to_compass(wind_dir)))
            if 24.1 < wind_speed <= 30:
                text_regular = (255, 102, 0)
                icon = path.join(path.dirname(__file__), 'icons/brown/{}/{}.png'.format(icon_wind_size, self.deg_to_compass(wind_dir)))
            if 30.1 < wind_speed <= 500:
                text_regular = (255, 182, 32)
                icon = path.join(path.dirname(__file__), 'icons/purple/{}/{}.png'.format(icon_wind_size, self.deg_to_compass(wind_dir)))

            text = ("{} knt").format(wind_speed)
            text_render = regular_font.render(text, True, text_regular)
            text_rect = text_render.get_rect(center=(self.xmax * 0.8, self.ymax * 0.18))
            self.screen.blit(text_render, text_rect)

            text = ("{} knt").format(wind_gust)
            text_render = regular_font.render(text, True, text_regular)
            text_rect = text_render.get_rect(center=(self.xmax * 0.8, self.ymax * 0.37))
            self.screen.blit(text_render, text_rect)
            
            text = "%s° " % wind_dir
            text_render = small_font.render(text, True, text_color)
            text_rect = text_render.get_rect(center=(self.xmax * 0.8, self.ymax * 0.58))
            self.screen.blit(text_render, text_rect)
        
            icon_load = pygame.image.load(icon).convert_alpha()
            self.screen.blit(icon_load, (self.xmax * 0.04, self.ymax * 0.08))
        
            kite_path = path.join(path.dirname(__file__), 'icons/logo/{}/windguru.png'.format(icon_wind_size))
            kite = pygame.image.load(kite_path)
            self.screen.blit(kite, (self.xmax * 0.6, self.ymax * 0.72))

        else:
            wind_speed = self.wind['wind']['speed']
            wind_gust = self.wind['wind']['gust']
            wind_dir = self.wind['wind']['direction']

            if 0 <= wind_speed <= 14:
                text_regular = (51, 187, 255)
                icon = path.join(path.dirname(__file__), 'icons/blue/{}/{}.png'.format(icon_wind_size, self.deg_to_compass(wind_dir)))
            if 14.1 < wind_speed <= 17:
                text_regular = (97, 209, 97)
                icon = path.join(path.dirname(__file__), 'icons/green/{}/{}.png'.format(icon_wind_size, self.deg_to_compass(wind_dir)))
            if 17.1 < wind_speed <= 24:
                text_regular = (255, 182, 32)
                icon = path.join(path.dirname(__file__), 'icons/orange/{}/{}.png'.format(icon_wind_size, self.deg_to_compass(wind_dir)))
            if 24.1 < wind_speed <= 30:
                text_regular = (255, 102, 0)
                icon = path.join(path.dirname(__file__), 'icons/brown/{}/{}.png'.format(icon_wind_size, self.deg_to_compass(wind_dir)))
            if 30.1 < wind_speed <= 500:
                text_regular = (255, 182, 32)
                icon = path.join(path.dirname(__file__), 'icons/purple/{}/{}.png'.format(icon_wind_size, self.deg_to_compass(wind_dir)))

            text = ("{} knt").format(wind_speed)
            text_render = regular_font.render(text, True, text_regular)
            text_rect = text_render.get_rect(center=(self.xmax * 0.8, self.ymax * 0.18))
            self.screen.blit(text_render, text_rect)

            text = ("{} knt").format(wind_gust)
            text_render = regular_font.render(text, True, text_regular)
            text_rect = text_render.get_rect(center=(self.xmax * 0.8, self.ymax * 0.37))
            self.screen.blit(text_render, text_rect)
            
            text = "%s° " % wind_dir
            text_render = small_font.render(text, True, text_color)
            text_rect = text_render.get_rect(center=(self.xmax * 0.8, self.ymax * 0.58))
            self.screen.blit(text_render, text_rect)
        
            icon_load = pygame.image.load(icon).convert_alpha()
            self.screen.blit(icon_load, (self.xmax * 0.04, self.ymax * 0.08))
        
            kite_path = path.join(path.dirname(__file__), 'icons/logo/{}/holfuy.png'.format(icon_wind_size))
            kite = pygame.image.load(kite_path)
            self.screen.blit(kite, (self.xmax * 0.6, self.ymax * 0.72))

        # Update the display
        pygame.display.update()     

########################################################################
# Create an instance of the lcd display class.
MY_DISP = MyDisplay()

RUNNING = True             # Stay running while True
SECONDS = 0                # Seconds Placeholder to pace display.

# Loads data from holfuy into class variables.
if MY_DISP.get_forecast() is False:
    print('Error: Wrong data for wind.')
    RUNNING = False

while RUNNING:
    MY_DISP.holfuy()
    # Look for and process keyboard events to change modes.
    for event in pygame.event.get():
        if event.type == QUIT:
            RUNNING = False
        if event.type == pygame.KEYDOWN:
            # On 'q' or keypad enter key, quit the program.
            if event.key == pygame.K_q:
                RUNNING = False    

    # Refresh the weather data once per minute.
    if int(SECONDS) == 0:
        MY_DISP.get_forecast()
            
    # Loop timer.
    pygame.time.wait(100)

pygame.quit()
