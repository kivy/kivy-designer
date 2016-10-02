import os

from designer.utils.utils import get_config_dir, get_fs_encoding


RECENT_FILES_NAME = 'recent_files'


class RecentManager(object):
    '''RecentManager is responsible for retrieving/storing the list of recently
       opened/saved projects.
    '''

    def __init__(self):
        super(RecentManager, self).__init__()
        self.list_projects = []
        self.max_recent_files = 10
        self.load_files()

    def add_path(self, path):
        '''To add file to RecentManager.
        :param path: path of project
        '''
        if isinstance(path, bytes):
            path = path.decode(get_fs_encoding()).encode(get_fs_encoding())

        _file_index = 0
        try:
            _file_index = self.list_projects.index(path)
        except:
            _file_index = -1

        if _file_index != -1:
            # If _file is already present in list_files, then move it to 0 index
            self.list_projects.remove(path)

        self.list_projects.insert(0, path)

        # Recent files should not be greater than max_recent_files
        while len(self.list_projects) > self.max_recent_files:
            self.list_projects.pop()

        self.store_files()

    def store_files(self):
        '''To store the list of files on disk.
        '''

        _string = ''
        for _file in self.list_projects:
            _string += _file + '\n'

        recent_file_path = os.path.join(get_config_dir(),
                                        RECENT_FILES_NAME)
        f = open(recent_file_path, 'w')
        f.write(_string)
        f.close()

    def load_files(self):
        '''To load the list of files from disk
        '''

        recent_file_path = os.path.join(get_config_dir(),
                                        RECENT_FILES_NAME)

        if not os.path.exists(recent_file_path):
            return

        f = open(recent_file_path, 'r')
        path = f.readline()

        while path != '':
            file_path = path.strip()
            if isinstance(file_path, bytes):
                file_path = file_path.decode(get_fs_encoding()).encode(
                    get_fs_encoding())
            if os.path.exists(file_path):
                self.list_projects.append(file_path)

            path = f.readline()

        f.close()
