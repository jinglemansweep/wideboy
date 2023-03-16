from wideboy.controller.display import Display


class Controller:
    def __init__(self, options: dict):
        self.display = Display(options=options.get("display"))
