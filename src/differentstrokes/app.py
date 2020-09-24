"""
pyweek 30 castaway game
"""
import toga
from differentstrokes.widgets import clear_widget
from differentstrokes.gamestate import GameState
from differentstrokes.screens import Menu


def all_children(w):
    l = w.children[:]
    if l:
        for c in w.children:
            l.extend(all_children(c))
    return l


class DifferentStrokes(toga.App):
    screen = None
    def set_screen(self, screen):
        print("set", screen)
        screen.game = self
        
        if screen != self.screen:
            self.screen = screen
            self.set_screen_child(screen)

        clear_widget(screen)
        screen.create_display(self.state)

    def set_screen_child(self, screen):
        clear_widget(self.main_box)
        self.main_box.refresh()
        self.main_box.add(screen)
        self.main_box.refresh()

    def set_screen_replace(self, screen):
        self.main_window.content = screen

    def startup(self):
        """
        Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        self.state = GameState()
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_box = toga.Box()
        self.main_window.content = self.main_box
        self.set_screen(Menu())
        self.main_window.show()


def main():
    return DifferentStrokes()
