import os
import datetime
from threading import Thread


store = []
replaced = []     # obj id to be deleted
obj_track = {}    # all objs are saved here   1:obj
d1 = r'C:\Users\emyli\AppData\Local\Google\Chrome\User Data\Default\Cache'
d2 = r'C:\Users\emyli\AppData\Local\Google\Chrome\User Data\Default\Code Cache\js'
d3 = r'C:\Users\emyli\AppData\Local\Google\Chrome\User Data\Default\Code Cache\wasm'
d4 = r'C:\Users\emyli\AppData\Local\Mozilla\Firefox\Profiles\4hqupym3.default\cache2\entries'
d5 = r'C:\Users\emyli\AppData\Local\Microsoft\Windows\INetCache'
d6 = r'C:\Users\emyli\AppData\Local\Microsoft\Windows\INetCache\Content.Outlook\7OQ81RH8'
stop = 0


class Cache:
    def __init__(self, cache_id, path):
        self.cache_id = cache_id
        self.path = path
        self.full_path = f'{path}/{cache_id}'
        self.mod_time = os.stat(self.full_path).st_mtime
        when = datetime.datetime.fromtimestamp(self.mod_time)
        if (datetime.datetime.now() - when) < datetime.timedelta(seconds=60):
            self.add_seq()
        self.check_path()

    def add_seq(self):
        store.append([self.cache_id, str(self.mod_time)])

    def check_path(self):
        while True:
            try:
                if self.mod_time != os.stat(self.full_path).st_mtime:
                    self.mod_time = os.stat(self.full_path).st_mtime
                    self.add_seq()
            except FileNotFoundError:
                print(f'{self.cache_id} Replaced')
                replaced.append(self.cache_id)
                break

    def __del__(self):
        print(f'{self.cache_id} Deleted')


class CacheDir:
    def __init__(self, path):
        self.path = path

        self.cur_list = set(self.get_files())
        while stop == 0:
            self.check_dir()

    def check_dir(self):
        dir_list = set(self.get_files())
        diff = dir_list - self.cur_list
        if len(diff) > 0:
            self.cur_list = set(set(self.get_files()))
            self.initialize(diff)

    def initialize(self, cache_list):
        for cache_id in cache_list:
            obj_track[cache_id] = Thread(target=Cache, args=(cache_id, self.path,))
            obj_track[cache_id].daemon = True
            obj_track[cache_id].start()

    def get_files(self):
        s = os.listdir(self.path)
        return [i for i in s if 'index' not in i]


def save_to_csv():
    file = open('cache_data.csv', 'a', encoding='utf-8')
    for line in store:
        file.write(','.join(line) + '\n')
    file.close()


if __name__ == '__main__':
    try:
        print('Running. . .')
        if not os.path.exists('cache_data.csv'):
            file1 = open('cache_data.csv', 'w', encoding='utf-8')
            file1.write('Key,Time\n')
            file1.close()

        ds = [d1, d2, d3, d4, d5, d6]
        for d in ds:
            obj_track[d] = Thread(target=CacheDir, args=(d,))
            obj_track[d].daemon = True
            obj_track[d].start()
        time_now = datetime.datetime.now()
        t = 1
        while True:       # Every 5 mins save a copy of the store
            if ((datetime.datetime.now() - time_now) > datetime.timedelta(minutes=5)) and (len(store) != 0):
                print(f'Saving {t}')
                t += 1
                save_to_csv()
                store = []
                time_now = datetime.datetime.now()
    except KeyboardInterrupt:
        print('Terminating...')
        stop = 1
        save_to_csv()
