

class preException(Exception):
    def __init__(self, pre: str, *args):
        self.pre = pre
        super().__init__(*args)

    def __str__(self):
        return self.pre + ': ' + ' '.join(self.args)