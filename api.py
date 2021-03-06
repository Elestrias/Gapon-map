import pygame
import requests
import sys
import os

import math

from common.distance import lonlat_distance
from common.geocoder import geocode as reverse_geocode
from common.business import find_business

# Подобранные констатны для поведения карты.
LAT_STEP = 0.001  # Шаги при движении карты по широте и долготе
LON_STEP = 0.001
coord_to_geo_x = 0.0000428  # Пропорции пиксельных и географических координат.
coord_to_geo_y = 0.0000428


def ll(x, y):
    return "{0},{1}".format(x, y)



# Параметры отображения карты:
# координаты, масштаб, найденные объекты и т.д.

class MapParams(object):
    # Параметры по умолчанию.
    def __init__(self):
        self.lat = 55.729738  # Координаты центра карты на старте.
        self.lon = 37.664777
        self.zoom = 15  # Масштаб карты на старте.
        self.type = "map"  # Тип карты на старте.

        self.search_result = None  # Найденный объект для отображения на карте.
        self.use_postal_code = False

    # Преобразование координат в параметр ll
    def ll(self):
        return ll(self.lon, self.lat)

    # Обновление параметров карты по нажатой клавише.
    def update(self, event, mp):
        if event.key == pygame.K_PAGEDOWN and mp.zoom != 0:
            mp.zoom -= 1
        if event.key == pygame.K_PAGEUP and mp.zoom != 18:
            mp.zoom += 1
        if event.type == pygame.KEYUP:
            if event.key == 49:
                mp.type = 'map'
            elif event.key == 50:
                mp.type = 'sat'
            elif event.key == 51:
                mp.type = 'sat,skl'
        elif event.type == pygame.KEYDOWN:
            if event.__dict__['key'] == 276:
                mp.lat -= LAT_STEP * 2 ** (15 - self.zoom)
            if event.__dict__['key'] == 273:
                mp.lon += LON_STEP * 2 ** (15 - self.zoom)
            if event.__dict__['key'] == 274:
                mp.lon -= LON_STEP * 2 ** (15 - self.zoom)
            if event.__dict__['key'] == 275:
                mp.lat += LAT_STEP * 2 ** (15 - self.zoom)
            if mp.lat == -180:
                mp.lat = 179.999
            elif mp.lat == 180:
                mp.lat = -179.999
            if mp.lon == -180:
                mp.lon = 179.999
            elif mp.lon == 180:
                mp.lon = -179.999

    # Преобразование экранных координат в географические.
    def screen_to_geo(self, pos):
        dy = 225 - pos[1]
        dx = pos[0] - 300
        lx = self.lon + dx * coord_to_geo_x * math.pow(2, 15 - self.zoom)
        ly = self.lat + dy * coord_to_geo_y * math.cos(math.radians(self.lat)) * math.pow(2, 15 - self.zoom)
        return lx, ly

    # еще несколько функций


# Создание карты с соответствующими параметрами.
def load_map(mp):
    map_file = show_map(mp.lat, mp.lon, mp.type, mp.zoom)
    return map_file


def show_map(lat, lon, map_type="map", zoom=10,  add_params=None):
    if lon and lat:
        map_request = "http://static-maps.yandex.ru/1.x/?ll={lat},{lon}&z={zoom}&l={map_type}".format(**locals())
    else:
        map_request = "http://static-maps.yandex.ru/1.x/?l={map_type}".format(**locals())

    if add_params:
        map_request += "&" + add_params
    response = requests.get(map_request)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

    # Запишем полученное изображение в файл.
    map_file = "map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)
    return map_file


def main():
    # Инициализируем pygame
    pygame.init()
    screen = pygame.display.set_mode((600, 450))

    # Заводим объект, в котором будем хранить все параметры отрисовки карты.
    mp = MapParams()

    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:  # Выход из программы
            break
        elif event.type == pygame.KEYUP:  # Обрабатываем различные нажатые клавиши.
            mp.update(event, mp)
        elif event.type == pygame.KEYDOWN:
            mp.update(event, mp)
        # другие eventы

        # Загружаем карту, используя текущие параметры.
        map_file = load_map(mp)

        # Рисуем картинку, загружаемую из только что созданного файла.
        screen.blit(pygame.image.load(map_file), (0, 0))

        # Переключаем экран и ждем закрытия окна.
        pygame.display.flip()

    pygame.quit()
    # Удаляем за собой файл с изображением.
    os.remove(map_file)


if __name__ == "__main__":
    main()
