from tkinter import *
from tkinter import font
from tkinter import ttk
import gamelist_xml_io
from PIL import Image, ImageTk

ES_BASE_DIR = "G:/frontends/Emulation Station/"


class GameInformationPane(object):
    def __init__(self, mainframe):
        self.name = StringVar()
        self.rating = StringVar()
        self.developer = StringVar()
        self.publisher = StringVar()
        self.genre = StringVar()
        self.players = StringVar()
        self.description = StringVar()
        self.photo = None   # see http://stackoverflow.com/questions/17760871/python-tkinter-photoimage

        # Create widgets
        self.snapshot = ttk.Label(mainframe, image=self.photo)
        self.snapshot.grid(row=1, column=0, rowspan=20, sticky=N+W)
        ttk.Label(mainframe, textvariable=self.name, font=appTitleFont).grid(row=1, column=1, sticky=N+W)

        ttk.Label(mainframe, text="Rating:").grid(row=3, column=1)
        ttk.Label(mainframe, textvariable=self.rating, wraplength=600, justify=LEFT, anchor=W).grid(row=3, column=2)

        ttk.Label(mainframe, text="Developer:").grid(row=4, column=0)
        ttk.Label(mainframe, textvariable=self.developer).grid(row=4, column=1)

        ttk.Label(mainframe, text="Publisher:").grid(row=5, column=0)
        ttk.Label(mainframe, textvariable=self.publisher).grid(row=5, column=1)

        ttk.Label(mainframe, text="Genre:").grid(row=6, column=0)
        ttk.Label(mainframe, textvariable=self.genre).grid(row=6, column=1)

        ttk.Label(mainframe, text="Players:").grid(row=7, column=0)
        ttk.Label(mainframe, textvariable=self.players).grid(row=7, column=1)

        ttk.Label(mainframe, textvariable=self.description, wraplength=600, justify=LEFT, anchor=W).grid(row=2, column=1, sticky=N+W)

        # Set data to first game in tree list
        game_list_tree.selection_set(game_list_tree.get_children()[0])

    def update_to_selected_game(self, event):
        index = game_list_tree.item(game_list_tree.selection()[0], 'text')
        self.name.set(games[index]['name'])
        self.rating.set(games[index]['rating'])
        self.developer.set(games[index]['developer'])
        self.publisher.set(games[index]['publisher'])
        self.genre.set(games[index]['genre'])
        self.players.set(games[index]['players'])
        self.description.set(games[index]['desc'])

        if not games[index]['image'] is None:
            file_path = games[index]['image'].replace("~/", "")
        else:
            # TODO: show "no screenshot
            pass
        image = Image.open(ES_BASE_DIR + file_path)
        image.thumbnail((256, 256), Image.ANTIALIAS)
        self.photo = ImageTk.PhotoImage(image)
        self.snapshot['image'] = self.photo

root = Tk()


root.title("ES scraper")
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
root.resizable(True, False)

appTitleFont = font.Font(size=16, weight="bold")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=N+W)
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

# Build game list tree
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
game_list_tree.grid(column=0, row=0, columnspan=3, sticky=N+W)

# Build scraping elements
ttk.Label(mainframe, text="Scrape for ...", font=appTitleFont).grid(row=1, column=3)
for idx, field in enumerate(gamelist_xml_io.GAME_FIELDS):
    Checkbutton(mainframe, text=field).grid(row=2+idx, column=3)


for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5, sticky=N+W)

root.mainloop()