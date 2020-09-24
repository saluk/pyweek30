import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from differentstrokes.widgets import ScreenButton, Screen, MessageScreen, MultipleMessageScreen

opening_message = """
Different Strokes(v0.0.1) - A castaway game about ordinary people
 - photos sourced from https://generated.photos/
"""

"""
[*] menu
    [*] intro
    [*] name screen
    [*] intro2
    day planner
        cast list
        location scheduler
        day processor
            notifications
        overnight
            notifications
"""


class Menu(MessageScreen):
    def __init__(self):
        super().__init__()
        self.message = "Different Strokes - Manage your group of castaways with different backgrounds"

    def setup_buttons(self):
        self.buttons = [
            ScreenButton("New Game - Intro", Intro()),
            ScreenButton("New Game - No Intro", CastNames()),
            ScreenButton("Load Game", MessageScreen('This is not yet implemented'))
        ]
    


class Intro(MultipleMessageScreen):
    messages = [
        'A tour group vacationing in Alaska have taken\n a charter boat to the Aleutian islands',
        'On the way, their tour guide begins having a seizure.',
        'The group tries to help, but he falls overboard with a\n few of the tourists, never to be seen again.',
        'Unfamiliar with the workings of the boat and running low\n on fuel, they manage to pull aground on one of the islands.',
        'The radio is dead and the boat wont float.\n These castaways will have to survive until help arrives.'
    ]

    def lastbutton(self):
        return ScreenButton('Begin Game', CastNames())


class Intro2(MultipleMessageScreen):
    messages = [
        '{c1}: "What are we going to do?"\n\
{c2}: "I have some scouting experience"\n\
{c3}: "I\'ve watched a lot of Survivor"\n\
{c1}: "I don\'t think that is the same at all"\n',
        '{c4}: "We have to get through this somehow."\n\
{c5}: "I\'m scared but I\'ll help as much as I can"\n\
{c1}: "So what now then?"'
    ]

    def lastbutton(self):
        return ScreenButton('Decide', PlannerScreen())


class CastNames(Screen):
    def __init__(self):
        super().__init__(style=Pack(padding=50, direction=COLUMN))

    def create_display(self, state):
        self.state = state
        state.new_game()
        self.add(toga.Label("Name your castaways"))
        cast_box = toga.Box(style=Pack(direction=COLUMN))
        self.cast = []
        for cast in state.get_cast():
            info_box = toga.Box(style=Pack(direction=ROW))
            cast_box.add(info_box)
            left_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
            right_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
            info_box.add(left_box)
            info_box.add(right_box)

            img = cast['img']
            left_box.add(
                toga.widgets.imageview.ImageView(
                    toga.Image('resources/images/'+img),
                    style=Pack(width=48, height=48, direction=COLUMN)
                )
            )
            self.cast.append(
                toga.TextInput(initial=cast['name'], placeholder='Enter Name')
            )
            right_box.add(self.cast[-1])
        self.add(cast_box)
        button = toga.Button('Save', on_press=self.next, style=Pack(padding_bottom=0))
        self.add(button)

    def next(self, widget):
        for i, widget in enumerate(self.cast):
            self.state.rename_cast(i, widget.value)
        widget.app.set_screen(Intro2())


class PlannerScreen(Screen):
    def __init__(self):
        super().__init__(style=Pack(padding=50, direction=COLUMN))

    def create_display(self, state):
        self.state = state
        self.add(
            toga.Label(state.format_message(
                'It is {daytime} on day {day}. You have {unassigned} cast \n\
away{unassigned_plural} to assign. Where would you like to assign them?'
            ))
        )
        super().create_display(state)

    def setup_buttons(self):
        class ProceedButton(ScreenButton):
            def click_button(o, widget):
                screen = MultipleMessageScreen('')
                def lastbutton():
                    return ScreenButton('Next', PlannerScreen())
                screen.lastbutton = lastbutton
                screen.messages = self.state.progress()
                widget.app.set_screen(screen)

        self.buttons = []
        for location in self.state.get_visible_locations():
            self.buttons.append(
                ScreenButton(
                    location['name'] +
                    self.state.get_assigned_actions_msg(location),
                    LocationScreen(self.state, location)
                )
            )
        self.buttons.append(
            ProceedButton("Proceed with assigned actions", None)
        )


class LocationScreen(MessageScreen):

    def __init__(self, state, location):
        self.state = state
        self.location = location
        self.message = 'What do you want to do here?'
        super().__init__(self.message)

    def setup_buttons(self):
        self.buttons = [
            ScreenButton('Back', PlannerScreen())
        ]
        for action in self.state.get_actions(self.location):
            members = list(self.state.get_assigned_cast(
                location=self.location, action=action
            ))
            label = action.capitalize()
            if members:
                nl, nlp = self.state.name_list(members)
                label += "({0})".format(nl)
            self.buttons.append(
                ScreenButton(label, ActionScreen(
                    self.state, action, self.location
                ))
            )


class ActionScreen(MessageScreen):
    def __init__(self, state, action, location):
        self.action = action
        self.state = state
        self.location = location
        super().__init__("Who do you want to assign to {0} at {1}".format(
            action, location['name']
        ))

    def setup_buttons(self):
        total = toga.Box(style=Pack(direction=ROW))
        col1 = toga.Box(style=Pack(direction=COLUMN, padding=20))
        col1.add(toga.Label('People to add to this action'))
        col2 = toga.Box(style=Pack(direction=COLUMN, padding=20))
        col2.add(toga.Label('Currently assigned'))
        total.add(col1)
        total.add(col2)
        self.add(total)

        class AssignButton(ScreenButton):
            def __init__(o, name, image):
                o.name = name
                o.image = image
                o.screen = ActionScreen(self.state, self.action, self.location)
                o.box = col1
            
            def click_button(o, widget):
                self.assign(o.image)
                super().click_button(widget)

        class RemoveButton(ScreenButton):
            def __init__(o, name, image):
                o.name = name
                o.image = image
                o.screen = ActionScreen(self.state, self.action, self.location)
                o.box = col2
            
            def click_button(o, widget):
                self.remove_assignment(o.image)
                super().click_button(widget)
    
        self.buttons = [
            ScreenButton('Back', LocationScreen(self.state, self.location))
        ]
        for cast in self.state.get_unassigned_cast():
            self.buttons.append(
                AssignButton(cast['name'], cast['img'])
            )
        for cast in self.state.get_assigned_cast(self.location):
            self.buttons.append(
                RemoveButton(cast['name'], cast['img'])
            )

    def assign(self, img):
        self.state.assign_cast(img, self.location, self.action)

    def remove_assignment(self, img):
        self.state.remove_cast(img, self.location, self.action)


class CastScreen(Screen):
    def setup_buttons(self):
        self.buttons = [ScreenButton("Restart", Menu())]

    def create_display(self, state):
        super().__init__(style=Pack(padding=50, direction=COLUMN))
        self.add(toga.Label("Castaway Community"))
        cast_box = toga.Box(style=Pack(direction=COLUMN))
        # cast_scroll = toga.widgets.scrollcontainer.ScrollContainer(
        #     content=cast_box,
        #     style=Pack(height=200)
        # )
        for cast in state.get_cast():
            info_box = toga.Box(style=Pack(direction=ROW))
            cast_box.add(info_box)
            left_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
            right_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
            info_box.add(left_box)
            info_box.add(right_box)

            img = cast['img']
            left_box.add(toga.Label('Name: {}'.format(cast['name'])))
            left_box.add(
                toga.widgets.imageview.ImageView(
                    toga.Image('resources/images/'+img),
                    style=Pack(width=48, height=48, direction=COLUMN)
                )
            )
            right_box.add(toga.Label('Stats'))
            right_box.add(toga.Label('Age: {}'.format(cast['age'])))
        self.add(cast_box)
        super().create_display(state)
