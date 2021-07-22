import json
import os

class FileDatabase(object):
    
    def __init__(self, folder, suffix="json"):
        self._folder = folder
        self._suffix = suffix
        
        self.load()
        
    def __get_name(self, file_name):
        file_split = file_name.split('.')
        if file_split[1] != self._suffix:
            return None
        return file_split[0]
        
    def __load_file(self, file_name):
        name = self.__get_name(file_name)
        if name is None:
            return None
        
        with open(self._folder + file_name, "r") as f:
            try:
                self._persistent_memory[name] = json.load(f)
            except json.JSONDecodeError:
                self._persistent_memory[name] = []
        
        
    def load(self):
        self._persistent_memory = {}
        
        with os.scandir(self._folder) as entries:
            for entry in entries:
                self.__load_file(entry.name)
                
    def __save_file(self, name, data):
        with open(self._folder + name + "." + self._suffix, "w") as f:
            json.dump(data, f, indent=4, sort_keys=True)
        
    def __remove_redundant_files(self):
        with os.scandir(self._folder) as entries:
            for entry in entries:
                name = self.__get_name(entry.name)
                if name != None and name not in self._persistent_memory:
                    os.remove(self._folder + entry.name)
                
    def save(self):
        for name, data in self._persistent_memory.items():
            self.__save_file(name, data)
            
        self.__remove_redundant_files()
            
    def get_file(self, name):
        if name in self._persistent_memory:
            return self._persistent_memory[name]
        return None
    
    def remove_file(self, name):
        self._persistent_memory.pop(name)
        
    def add_file(self, name, data):
        if name not in self._persistent_memory:
            self._persistent_memory[name] = data
        else:
            return None