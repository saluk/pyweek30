"""
pyweek 30 castaway game
"""
import toga
from differentstrokes.gamestate import GameState
from differentstrokes.screens import Menu


class DifferentStrokes(toga.App):

    def set_screen(self, screen):
        screen.create_display(self.state)
        self.screen = screen
        self.main_window.content = self.screen

    def startup(self):
        """
        Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        self.state = GameState()
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.set_screen(Menu())
        self.main_window.show()


def main():
    return DifferentStrokes()
