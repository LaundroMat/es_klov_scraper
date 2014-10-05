from tkinter import *
from tkinter import font
from tkinter import ttk
import gamelist_xml_io
from PIL import Image, ImageTk

ES_BASE_DIR = "G:/frontends/Emulation Station/"


class GameInformationPane(object):
    def __init__(self, mainframe):
        self.frame = ttk.Frame(mainframe)

        self.game_name = StringVar()
        self.game_description = StringVar()
        self.photo = None   # see http://stackoverflow.com/questions/17760871/python-tkinter-photoimage

        # Create widgets
        ttk.Label(mainframe, textvariable=self.game_name, font=appTitleFont).grid(column=0, row=1, sticky=(N, W))
        ttk.Label(mainframe, textvariable=self.game_description, wraplength=600, justify=LEFT).grid(column=0, row=2, sticky=(N, W))
        self.snapshot = ttk.Label(mainframe, image=self.photo)
        self.snapshot.grid(column=1, row=0, rowspan=4, sticky=(N, W))

        # Set data to first game in tree list
        game_list_tree.selection_set(game_list_tree.get_children()[0])

    def update_to_selected_game(self, event):
        index = game_list_tree.item(game_list_tree.selection()[0], 'text')
        self.game_name.set(games[index]['name'])
        self.game_description.set(games[index]['desc'])

        file_path = games[index]['image'].replace("~/", "")
        image = Image.open(ES_BASE_DIR + file_path)
        self.photo = ImageTk.PhotoImage(image)
        self.snapshot['image'] = self.photo

root = Tk()


root.title("ES scraper")
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
root.resizable(True, True)

appTitleFont = font.Font(size=16, weight="bold")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

game_list_tree = ttk.Treeview(mainframe, columns=tuple(gamelist_xml_io.REQUIRED_GAME_FIELDS))
game_list_tree['show'] = 'headings'
for heading in gamelist_xml_io.REQUIRED_GAME_FIELDS:
    game_list_tree.heading(heading, text=heading)

tree = gamelist_xml_io.open_gamelist_xml()
games = gamelist_xml_io.get_games(tree)

for g in games:
    game_list_tree.insert('', 'end', text=g['index'], values=tuple(g[key] for key in gamelist_xml_io.REQUIRED_GAME_FIELDS if key in g.keys()))

game_info_window = GameInformationPane(mainframe)

game_list_tree.bind("<<TreeviewSelect>>", game_info_window.update_to_selected_game)
game_list_tree.grid(column=0, row=0, sticky=W)

for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

root.mainloop()