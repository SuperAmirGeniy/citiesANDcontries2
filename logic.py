import sqlite3  
from config import *  
import matplotlib  
matplotlib.use('Agg')  
import matplotlib.pyplot as plt  
import cartopy.crs as ccrs  
import cartopy.feature as cfeature  
from geopy.distance import geodesic  

class DB_Map():  
    def __init__(self, database):   
        self.database = database  
    
    def create_user_table(self):  
        conn = sqlite3.connect(self.database)  
        with conn:  
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (  
                                user_id INTEGER,  
                                city_id TEXT,  
                                FOREIGN KEY(city_id) REFERENCES cities(id)  
                            )''')  
            conn.commit()  

    def add_city(self, user_id, city_name):  
        conn = sqlite3.connect(self.database)  
        with conn:  
            cursor = conn.cursor()  
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))  
            city_data = cursor.fetchone()  
            if city_data:  
                city_id = city_data[0]  
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))  
                conn.commit()  
                return 1  
            else:  
                return 0  

    def select_cities(self, user_id):  
        conn = sqlite3.connect(self.database)  
        with conn:  
            cursor = conn.cursor()  
            cursor.execute('''SELECT cities.city   
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id  
                            WHERE users_cities.user_id = ?''', (user_id,))  

            cities = [row[0] for row in cursor.fetchall()]  
            return cities  

    def get_coordinates(self, city_name):  
        conn = sqlite3.connect(self.database)  
        with conn:  
            cursor = conn.cursor()  
            cursor.execute('''SELECT lat, lng  
                            FROM cities  
                            WHERE city = ?''', (city_name,))  
            coordinates = cursor.fetchone()  
            return coordinates  

    def create_graph(self, path, cities, marker_color='blue'):  # Добавим параметр для цвета маркера  
        ax = plt.axes(projection=ccrs.PlateCarree())  
        ax.add_feature(cfeature.OCEAN, facecolor='lightblue')  # Заливка океанов  
        ax.add_feature(cfeature.LAND, facecolor='lightgreen')  # Заливка континентов  
        
        for city in cities:  
            lat, lon = self.get_coordinates(city)  
            plt.plot([lon], [lat],  
                     color=marker_color, linewidth=2, marker='o',  
                     transform=ccrs.Geodetic())  

            plt.text(lon - 3, lat - 12, city,  
                     horizontalalignment='right',  
                     transform=ccrs.Geodetic())  
        plt.savefig(path)  
                
    def draw_distance(self, city1, city2):  
        coords1 = self.get_coordinates(city1)  
        coords2 = self.get_coordinates(city2)  
        
        if coords1 and coords2:  
            # Вычисляем расстояние  
            distance = geodesic(coords1[::-1], coords2[::-1]).kilometers  
            print(f"Расстояние между {city1} и {city2}: {distance:.2f} км")  
            
            # Создаем график с расстоянием  
            ax = plt.axes(projection=ccrs.PlateCarree())  
            ax.add_feature(cfeature.OCEAN, facecolor='lightblue')  
            ax.add_feature(cfeature.LAND, facecolor='lightgreen')  

            plt.plot([coords1[1], coords2[1]], [coords1[0], coords2[0]], color='red', linewidth=2)  
            plt.text((coords1[1] + coords2[1]) / 2, (coords1[0] + coords2[0]) / 2,   
                     f"{distance:.2f} км", horizontalalignment='center',   
                     transform=ccrs.Geodetic())  
            plt.title(f"Расстояние между {city1} и {city2}: {distance:.2f} км")  
            plt.savefig('distance_map.png')  

if __name__=="__main__":  
    m = DB_Map(DATABASE)  
    m.create_graph('img.png',['Sochi', 'Moscow'], marker_color='red')  # Пример использования цвета  
    m.draw_distance('Sochi', 'Moscow')  # Пример вычисления и отображения расстояния