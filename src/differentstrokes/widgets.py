import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class ScreenButton:
    def __init__(self, name, screen, image=None, box=None):
        self.name = name
        self.screen = screen
        self.image = image
        self.box = box

    def make_button(self):
        box = button = toga.Button(
            self.name,
            on_press=self.click_button
        )
        if self.image:
            box = toga.Box(style=Pack(direction=ROW))
            box.add(
                toga.widgets.imageview.ImageView(
                    toga.Image('resources/images/'+self.image),
                    style=Pack(width=48, height=48)
                )
            )
            box.add(button)
        return box

    def click_button(self, widget):
        widget.app.set_screen(self.screen)


class Screen(toga.Box):
    def setup_buttons(self):
        self.buttons = []

    def create_display(self, state):
        self.setup_buttons()
        button_box = toga.Box(style=Pack(direction=COLUMN))
        self.add(button_box)
        self.add_buttons(button_box)

    def add_buttons(self, box=None):
        print(self, self.buttons)
        if not box:
            box = self
        for button in self.buttons:
            b = button.make_button()
            if button.box:
                button.box.add(b)
            else:
                box.add(b)


class MessageScreen(Screen):
    def __init__(self, message=''):
        self.message = message

    def create_display(self, state):
        super().__init__(style=Pack(padding=100, direction=COLUMN))
        self.add(toga.Label(state.format_message(self.message)))
        super().create_display(state)


class MultipleMessageScreen(MessageScreen):
    messages = []

    def lastbutton(self):
        return None

    def setup_buttons(self):
        assert self.lastbutton()
        if self.messages:
            self.buttons = [ScreenButton("Continue", self)]
        else:
            self.buttons = [self.lastbutton()]

    def create_display(self, state):
        self.message = self.messages[0]
        self.messages = self.messages[1:]
        super().create_display(state)