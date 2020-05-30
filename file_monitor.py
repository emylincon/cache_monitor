import os
import datetime
import pandas as pd
from threading import Thread
from pathlib import *

store = []
replaced = []     # obj id to be deleted
obj_track = {}    # all objs are saved here   1:obj
d1 = r'C:\Users\emyli\AppData\Local\Google\Chrome\User Data\Default\Cache'
d2 = r'C:\Users\emyli\AppData\Local\Google\Chrome\User Data\Default\Code Cache\js'
d3 = r'C:\Users\emyli\AppData\Local\Google\Chrome\User Data\Default\Code Cache\wasm'
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
        store.append([self.cache_id, self.mod_time])

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
        print(f'{self.cache_id} removed')


class CacheDir:
    def __init__(self, path):
        self.path = path
        self.cur_list = set((x for x in Path(self.path) if x.is_file()))
        while stop == 0:
            self.check_dir()

    def check_dir(self):
        dir_list = set((x for x in Path(self.path) if x.is_file()))
        diff = dir_list - self.cur_list
        if len(diff) > 0:
            self.cur_list = set((x for x in Path(self.path) if x.is_file()))
            self.initialize(diff)

    def initialize(self, cache_list):
        for cache_id in cache_list:
            obj_track[cache_id] = Thread(target=Cache, args=(cache_id, self.path))
            obj_track[cache_id].daemon = True
            obj_track[cache_id].start()


if __name__ == '__main__':
    try:
        print('Running. . .')
        ds = [d1, d2, d3]
        for d in ds:
            obj_track[d] = Thread(target=CacheDir, args=(d))
            obj_track[d].daemon = True
            obj_track[d].start()
        store_copy = store[:]
        time_now = datetime.datetime.now()
        while True:       # Every 5 mins save a copy of the store
            if ((datetime.datetime.now() - time_now) > datetime.timedelta(minutes=5)) and (store_copy != store):
                print('saving...')
                df = pd.DataFrame(store, columns=['Key', 'Time'])
                df.to_csv('cache_data.csv')
                store_copy = store[:]
    except KeyboardInterrupt:
        print('Terminating...')
        stop = 1
        df = pd.DataFrame(store, columns=['Key', 'Time'])
        df.to_csv('cache_data.csv')
