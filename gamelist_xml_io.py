from difflib import context_diff, Differ
import logging
from pprint import pprint
from xml.etree import ElementTree
PATH_TO_FILE = "G:/frontends/Emulation Station/.emulationstation/gamelists/mame/gamelist.xml"


REQUIRED_GAME_FIELDS = [
    'name',
    'desc',
    'image'
]


class GameListXML(object):

    GAME_FIELDS = [
        'name',
        'desc',
        'image',
        'rating',
        'releasedate',
        'developer',
        'publisher',
        'genre',
        'players'
    ]

    def __init__(self, path):
        self.path = path
        self.tree = None
        self.games = []
        self.read()

    def read(self):
        with open(self.path, mode="r", encoding="utf-8") as game_list:
            self.tree = ElementTree.parse(game_list)
        self.get_games()

    def save(self, update_data=None):
        if update_data:
            self.update_game(update_data)

        with open(self.path, mode="wb") as f:
            self.tree.write(f, encoding="utf-8")
        logging.info("Saved updated gamelist to {path}".format(path=self.path))

    def get_games(self):
        # TODO: replace games var with simple lookups in the XML. No need for this extra memory consumption
        for idx, game_node in enumerate(self.tree.findall('.//game')):
            game = {'index': idx}
            for field in self.GAME_FIELDS:
                try:
                    game[field] = game_node.find(field).text
                except AttributeError:
                    game[field] = None
            self.games.append(game)

    def get_game_info(self, title):
        logging.info("Getting information from XML for {title}".format(title=title))
        for idx, game_node in enumerate(self.tree.findall('.//game')):
            try:
                if game_node.findtext('name').lower() == title.lower():
                    # TODO: findtext(pattern) returns the value of the text attribute for the first subelement that matches the given pattern. If there is no matching element, this method returns None.
                    game = {}
                    for field in self.GAME_FIELDS:
                        try:
                            game[field] = game_node.find(field).text
                        except AttributeError:
                            game[field] = None
                    return game
            except AttributeError:
                # 'NoneType' object has no attribute 'lower'
                # game_node has no "name" node
                pass

    def get_game_by_rom_name(self, rom):
        for idx, game_node in enumerate(self.tree.findall('.//game')):
            if rom.lower() in game_node.find('path').text.lower():
                game = {}
                for field in self.GAME_FIELDS:
                    try:
                        game[field] = game_node.find(field).text
                    except AttributeError:
                        game[field] = None
                return game
        return None

    def get_all_game_titles(self):
        return [node.findtext('name') for node in self.tree.findall('game') if node.findtext('name') is not None]


    def show_diff(self, original, updated):
        print(original, updated)
        for key, value in updated.items():
            if original[key] != updated[key]:
                print(key)
                print("="*len(key))
                print('\tFrom: {original}'.format(original=original[key]))
                print()
                print('\tTo: {updated}'.format(updated=updated[key]))
                print()

    def update_game(self, data):
        game_nodes = [node for node in self.tree.findall('.//game') if node.find('name') is not None]
        game_node = [node for node in game_nodes if node.find('name').text.lower() == data['name'].lower()][0]
        for key, value in data.items():
            node = game_node.find(key)
            if node is not None:
                node.text = value
            else:
                node = ElementTree.SubElement(game_node, key)
                node.text = value

    def add_game_by_rom_name(self, rom):
        root = self.tree.getroot()
        game_node = ElementTree.SubElement(root, "game")
        path = ElementTree.SubElement(game_node, "path")
        path.text = './{rom}'.format(rom=rom)
