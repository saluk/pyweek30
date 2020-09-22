import random
import names

allskills = [
    "firemaking",
    "trapsetting",
    "constitution",
    "exploration",
    "navigation",
    "tools",
    "maintenance",
    "engineering",
    "physicality"
]

location_adjectives = [
    'sandy',
    'starting',
    'creepy',
    'stretchy',
    'meandering',
    'slippery',
    'rocky',
    'fascinating',
    'expansive',
    'watery',
    'jagged',
    'green',
    'blue',
    'black'
]

location_types = {
    'beach':    {'explore': 0.50, 'explore_max': 1},
    'shore':    {'explore': 0.20, 'explore_max': 1},
    'rock':     {'explore': 0.30, 'explore_max': 1},
    'trees':    {'explore': 0.10, 'explore_max': 1},
    'woodland': {'explore': 0.15, 'explore_max': 1},
    'marsh':    {'explore': 0.20, 'explore_max': 1},
    'swamp':    {'explore': 0.20, 'explore_max': 1},
    'path':     {'explore': 0.90, 'explore_max': 1},
    'hill':     {'explore': 0.70, 'explore_max': 1},
    'mountain': {'explore': 0.10, 'explore_max': 1},
    'volcano':  {'explore': 0.10, 'explore_max': 1},
}


actions = {}


class GameState:
    def __init__(self):
        for a in dir(self):
            if a.startswith("a_"):
                actions[a[2:]] = {'test': getattr(self, a)}
            if a.startswith("r_"):
                actions[a[2:]]['result'] = getattr(self, a)
        self.new_game()

    def new_game(self):
        self.data = {
            'cast': [
            ],
            'locations': [
            ],
            'day': 1,
            'time': 'morning'
        }
        self.populate_cast()
        self.populate_locations()

    def populate_cast(self):
        chosen = set()
        while len(chosen) < 5:
            age = random.choice('yac')
            s = random.choice('mf')
            num = random.randint(1,{
                'c': 5,
                'a': 10,
                'y': 10
            }[age])
            img = age+s+str(num)+'.jpg'
            if img in chosen:
                continue
            chosen.add(img)
            num_age = random.randint(
                {'c': 6, 'a': 40, 'y': 18}[age],
                {'c': 9, 'a': 56, 'y': 30}[age])
            skills = []
            for i in range(random.randrange(1,3)):
                skills.append(random.choice([
                    {
                        'skill': skill,
                        'level': random.randint(1, 3),
                        'discovery': 0
                    } for skill in allskills if skill not in skills
                ]))
            self.data['cast'].append({
                'img': img,
                'age': num_age,
                'name': names.get_first_name(gender=s),
                'gender': s,
                'sexuality': random.choice(['hetero', 'homo', 'bi', 'fluid', 'ace']),
                'skills': skills,
                'assigned': False
            })
    
    def populate_locations(self):
        start = None
        for i in range(10):
            if not start:
                location_type = 'beach'
                x = random.choice([-10, 10])
                y = random.choice([-10, 10])
            else:
                location_type = random.choice(list(location_types.keys()))
                x = random.randint(-10, 10)
                y = random.randint(-10, 10)
            settings = location_types[location_type]
            loc = {
                'name': '{} {}'.format(
                    random.choice(location_adjectives),
                    location_type
                ),
                'type': location_type,
                'active': False,
                'position': [x, y],
                'found': [],
                'structures': [],
                'connected': [],
                'assigned': {}
            }
            self.data['locations'].append(loc)
            self.data['locations'][-1].update(settings)
            if not start:
                start = self.data['locations'][-1]
                start['active'] = True

    def get_cast(self):
        for cast in self.data['cast']:
            yield cast

    def get_cast_by_img(self, img):
        for cast in self.data['cast']:
            if cast['img'] == img:
                return cast

    def get_unassigned_cast(self):
        for cast in self.data['cast']:
            if not cast['assigned']:
                yield cast

    def get_assigned_cast_msg(self, location):
        members = [self.get_cast_by_img(img) for img in location['assigned']]
        if not members:
            return ''
        nl, nlp = self.name_list(members)
        return '\nCurrently {0} are assigned here.'.format(nl)

    def assign_cast(self, img, location, action):
        location['assigned'][action] = location['assigned'].get(action, [])
        location['assigned'][action].append(img)
        self.get_cast_by_img(img)['assigned'] = {
            'location_index': self.get_location_index(location),
            'action': action.lower()
        }

    def remove_cast(self, img, location, action):
        location['assigned'][action].remove(img)
        self.get_cast_by_img(img)['assigned'] = False

    def get_assigned_cast(self, location=None, action=None):
        for cast in self.data['cast']:
            if not cast['assigned']:
                continue
            if (
                (not location or
                 cast['assigned']['location_index'] ==
                    self.get_location_index(location)) and
                (not action or cast['assigned']['action'] == action.lower())
            ):
                yield cast

    def get_location_index(self, location):
        for i, loc in enumerate(self.data['locations']):
            if loc == location:
                return i

    def get_visible_locations(self):
        for location in self.data['locations']:
            if location['active']:
                yield location

    def get_invisible_locations(self):
        for location in self.data['locations']:
            if not location['active']:
                yield location

    def rename_cast(self, i, name):
        self.data['cast'][i]['name'] = name

    def format_message(self, string):
        unassigned = [x for x in self.data['cast'] if not x['assigned']]
        data = {
            'c1': self.data['cast'][0]['name'],
            'c2': self.data['cast'][1]['name'],
            'c3': self.data['cast'][2]['name'],
            'c4': self.data['cast'][3]['name'],
            'c5': self.data['cast'][4]['name'],
            'daytime': self.data['time'],
            'day': self.data['day'],
            'unassigned': len(unassigned),
            'unassigned_plural': 's' if len(unassigned) > 1 else ''
        }
        return string.format(**data)

    def name_list(self, members):
        if len(members) == 1:
            return members[0]['name'], 's'
        if len(members) == 2:
            return '{} and {}'.format(
                members[0]['name'], members[1]['name']
            ), ''
        else:
            s = ', '.join([m['name'] for m in members[:-1]])
            s += ' and {}'.format(members[-1]['name'])
            return s, ''

    def get_actions(self, location):
        for action in actions:
            d = actions[action]
            if d['test'](location):
                yield action

    def get_assigned_actions_msg(self, location):
        cur_actions = {}
        for cast in self.get_assigned_cast(location):
            action = cast['assigned']['action']
            if action not in cur_actions:
                cur_actions[action] = []
            cur_actions[action].append(cast)
        if not cur_actions:
            return ''
        s = ' ('
        for action in cur_actions:
            nl, nlp = self.name_list(cur_actions[action])
            s += '{0} are going to {1}. '.format(
                nl, action.lower()
            )
        return s[:-1]+')'

    def progress(self):
        messages = []
        for location in self.data['locations']:
            for action in location['assigned']:
                members = [
                    self.get_cast_by_img(img)
                    for img in location['assigned'][action]
                ]
                msg = actions[action]['result'](location, members)
                messages.append(msg)
            location['assigned'] = {}
        for cast in self.get_cast():
            cast['assigned'] = False

        if self.data['time'] == 'morning':
            self.data['time'] = 'evening'
        elif self.data['time'] == 'evening':
            self.data['time'] = 'night'
        elif self.data['time'] == 'night':
            self.data['time'] = 'morning'
            self.data['day'] += 1 
            messages.append("The castaways sleep through the night")
        if not messages:
            return ["Nothing happened."]
        return messages

    def a_explore(self, location):
        return {'min': 1, 'max': 2}

    def r_explore(self, location, members):
        nl, nlp = self.name_list(members)
        failmsg = "{0} explore{1} {2}, but find no new areas.".format(nl, nlp, location['name'])
        if len(location['connected']) >= location['explore_max']:
            return failmsg
        if random.random() >= location['explore']:
            return failmsg
        if not list(self.get_invisible_locations()):
            return failmsg
        new_location = random.choice(list(self.get_invisible_locations()))
        new_location['active'] = True
        successmsg = "{0} explore{1} {2}. They find {3}!".format(
            nl, nlp, location['name'], new_location['name']
        )
        return successmsg
