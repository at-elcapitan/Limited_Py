# AT PROJECT Limited 2022 - 2024; ATLB-v1.7.12.3
class FileError(Exception):
    def __init__(self, filename, type):
        match type:
            case "corrupt":
                self.message = 'file corrupted or filled incorrectly.'
            
            case 'notfound':
                self.message = 'file not found'

        self.filename = filename

        super().__init__(f'`{self.filename}` {self.message}')
