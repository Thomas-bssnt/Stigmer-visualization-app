import tkinter as tk
import tkinter.ttk as ttk
from json import load
from math import sqrt
from os import scandir

import numpy as np


class GameSelectionBar(ttk.Frame):
    def __init__(self, parent, **kwargs):
        self.parent = parent
        super().__init__(parent, **kwargs)

        self.map_type = tk.StringVar()
        self.rule_number = tk.StringVar()
        self.selected_game = tk.StringVar()

        frm_info = ttk.Frame(master=self)
        ttk.Label(
            master=frm_info,
            text="Map:",
        ).grid(row=0, column=0)
        ttk.Combobox(
            master=frm_info,
            state="readonly",
            textvariable=self.map_type,
            values=["", "R", "1", "2"],
            width=3,
        ).grid(row=0, column=1)
        ttk.Label(
            master=frm_info,
            text="Rule:",
        ).grid(row=1, column=0)
        ttk.Combobox(
            master=frm_info,
            state="readonly",
            textvariable=self.rule_number,
            values=["", "1", "2", "3", "4"],
            width=3,
        ).grid(row=1, column=1)

        frm_game_selection = ttk.Frame(master=self)
        ttk.Label(
            master=frm_game_selection,
            text="Game:",
        ).grid(row=0, column=0)
        self.cbb_game = ttk.Combobox(
            master=frm_game_selection,
            postcommand=self.update_cbb_game_values,
            state="readonly",
            textvariable=self.selected_game,
            width=14,
        )
        self.cbb_game.grid(row=0, column=1)
        ttk.Button(
            master=frm_game_selection,
            text="Select game",
            command=parent.load_game,
        ).grid(row=1, column=1, sticky="e")

        frm_info.grid(row=0, column=0, sticky="w")
        frm_game_selection.grid(row=0, column=1, sticky="e")

        self.columnconfigure((0, 1), weight=1)

    def update_cbb_game_values(self):
        self.cbb_game["values"] = [
            game
            for game in self.parent.games
            if (self.map_type.get() in {game[11], ""} and self.rule_number.get() in {game[8], ""})
        ]


class Map(ttk.Frame):
    def __init__(self, parent, **kwargs):
        self.parent = parent
        super().__init__(parent, **kwargs)

        self.lbl_map = [
            [tk.Label(master=self) for _ in range(parent.in_data["mapSize"])] for _ in range(parent.in_data["mapSize"])
        ]
        for row in range(len(self.lbl_map)):
            for column in range(len(self.lbl_map[0])):
                self.lbl_map[row][column].grid(row=row, column=column, sticky="nsew")
                self.lbl_map[row][column]["relief"] = "solid"
                self.lbl_map[row][column]["borderwidth"] = 1

        for i in range(len(self.lbl_map)):
            ttk.Label(
                master=self,
                text=i + 1,
            ).grid(row=i, column=len(self.lbl_map))
            ttk.Label(
                master=self,
                text=i + 1,
            ).grid(row=len(self.lbl_map), column=i)

        for i in range(len(self.lbl_map) + 1):
            self.rowconfigure(i, weight=1, minsize=30)
            self.columnconfigure(i, weight=1, minsize=30)

    def put_values_map(self):
        for row in range(len(self.lbl_map)):
            for column in range(len(self.lbl_map[0])):
                self.lbl_map[row][column]["text"] = self.parent.in_data["map"][row][column]

    def update_map_colors(self):
        for row in range(len(self.lbl_map)):
            for column in range(len(self.lbl_map[0])):
                if self.parent.mode.get():
                    proportion = self.parent.proportion_visits[self.parent.round.get(), row, column]
                else:
                    proportion = self.parent.proportion_stars[self.parent.round.get(), row, column]
                r, g, b = self.get_color(sqrt(proportion))
                self.lbl_map[row][column]["background"] = f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def get_color(proportion):
        if proportion <= 0.5:
            color = 255 - round(proportion * 255 / 0.5)
            return 255, color, color
        else:
            color = round((1 - proportion) * 255 / 0.5)
            return color, 0, 0


class Bottom(ttk.Frame):
    def __init__(self, parent, **kwargs):
        self.parent = parent
        super().__init__(parent, **kwargs)

        frm_buttons = ttk.Frame(master=self)
        self.btn_previous = ttk.Button(
            master=frm_buttons,
            text="-",
            command=parent.previous_round,
            state="disable",
            width=3,
        )
        self.btn_previous.grid(row=0, column=1)
        self.btn_restart = ttk.Button(
            master=frm_buttons,
            text="↺",
            command=parent.restart_round,
            state="disable",
            width=3,
        )
        self.btn_restart.grid(row=0, column=0)
        self.btn_play = ttk.Button(
            master=frm_buttons,
            text="▶",
            command=parent.play,
            state="disable",
            width=3,
        )
        self.btn_play.grid(row=0, column=2)
        self.btn_next = ttk.Button(
            master=frm_buttons,
            text="+",
            command=parent.next_round,
            state="disable",
            width=3,
        )
        self.btn_next.grid(row=0, column=3)
        self.rbt_stars = ttk.Radiobutton(
            master=frm_buttons,
            text="Stars",
            variable=parent.mode,
            value=0,
            command=parent.map.update_map_colors,
            state="disable",
        )
        self.rbt_stars.grid(row=1, column=0, columnspan=2, sticky="w")
        self.rbt_visits = ttk.Radiobutton(
            master=frm_buttons,
            text="Visits",
            variable=parent.mode,
            value=1,
            command=parent.map.update_map_colors,
            state="disable",
        )
        self.rbt_visits.grid(row=1, column=2, columnspan=2, sticky="w")

        frm_round = ttk.Frame(master=self)
        ttk.Label(master=frm_round, text="Round: ").grid(row=0, column=0, sticky="e")
        self.lbl_round = ttk.Label(master=frm_round, width=2)
        self.lbl_round.grid(row=0, column=1, sticky="w")

        frm_info = ttk.Frame(master=self)
        ttk.Label(master=frm_info, text="Session: ").grid(row=0, column=0, sticky="e")
        ttk.Label(master=frm_info, text="Game: ").grid(row=1, column=0, sticky="e")
        ttk.Label(master=frm_info, text="Group: ").grid(row=2, column=0, sticky="e")
        ttk.Label(master=frm_info, text="Rule: ").grid(row=3, column=0, sticky="e")
        ttk.Label(master=frm_info, text="Map: ").grid(row=4, column=0, sticky="e")
        ttk.Label(master=frm_info, text="Number: ").grid(row=5, column=0, sticky="e")
        self.lbl_session = ttk.Label(master=frm_info, width=2)
        self.lbl_game = ttk.Label(master=frm_info, width=2)
        self.lbl_group = ttk.Label(master=frm_info, width=2)
        self.lbl_rule = ttk.Label(master=frm_info, width=2)
        self.lbl_map = ttk.Label(master=frm_info, width=2)
        self.lbl_number = ttk.Label(master=frm_info, width=2)
        self.lbl_session.grid(row=0, column=1, sticky="w")
        self.lbl_game.grid(row=1, column=1, sticky="w")
        self.lbl_group.grid(row=2, column=1, sticky="w")
        self.lbl_rule.grid(row=3, column=1, sticky="w")
        self.lbl_map.grid(row=4, column=1, sticky="w")
        self.lbl_number.grid(row=5, column=1, sticky="w")

        frm_buttons.grid(row=0, column=0, padx=10, pady=5, sticky="nw")
        frm_round.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        frm_info.grid(row=0, column=2, padx=10, pady=5, sticky="e")

        self.columnconfigure((0, 1, 2), weight=1)

    def update_frm_info_text(self):
        self.lbl_session["text"] = self.parent.in_data["sessionNumber"]
        self.lbl_game["text"] = self.parent.in_data["gameNumber"]
        self.lbl_group["text"] = self.parent.in_data["groupId"]
        self.lbl_rule["text"] = self.parent.in_data["ruleNumber"]
        self.lbl_map["text"] = self.parent.in_data["mapType"]
        self.lbl_number["text"] = self.parent.in_data["mapNumber"]

    def update_lbl_round_text(self):
        self.lbl_round["text"] = self.parent.round.get()

    def activate_frm_buttons(self):
        self.btn_previous["state"] = "active"
        self.btn_restart["state"] = "active"
        self.btn_play["state"] = "active"
        self.btn_next["state"] = "active"
        self.rbt_stars["state"] = "active"
        self.rbt_visits["state"] = "active"


class MainApplication(ttk.Frame):
    def __init__(self, parent, path_data, **kwargs):
        self.parent = parent
        super().__init__(parent, **kwargs)

        self.path_data = path_data
        self.games = self.get_list_games()

        file_name = "S01-A1-R1-MR-01"
        path_in_file = path_data + f"Session_{file_name[1:3]}/In/{file_name}.json"
        with open(path_in_file) as in_file:
            self.in_data = load(in_file)

        self.proportion_visits = None
        self.proportion_stars = None

        self.mode = tk.IntVar()
        self.round = tk.IntVar()
        self.mode.set(0)
        self.round.set(0)

        self.gameSelectionBar = GameSelectionBar(self)
        self.map = Map(self)
        self.bottom = Bottom(self)

        self.gameSelectionBar.grid(row=0, padx=10, pady=10, sticky="nsew")
        self.map.grid(row=1, padx=10, pady=10, sticky="nsew")
        self.bottom.grid(row=2, padx=10, pady=(0, 10), sticky="nsew")

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.running = False
        self.play_loop()

    def get_list_games(self):
        games = []
        for f in scandir(self.path_data):
            if f.is_dir() and f.name.startswith("Session"):
                for g in scandir(f.path + "/Out"):
                    if g.is_file() and g.name.endswith(".csv"):
                        games.append(g.name[:-4])
        return sorted(games)

    def load_game(self):
        game_name = self.gameSelectionBar.selected_game.get()

        if game_name:  # if a game is selected

            path_in_file = self.path_data + f"Session_{game_name[1:3]}/In/{game_name}.json"
            with open(path_in_file) as in_file:
                self.in_data = load(in_file)

            path_out_file = self.path_data + f"Session_{game_name[1:3]}/Out/{game_name}.csv"
            with open(path_out_file, "r") as out_file:
                out_data = np.genfromtxt(out_file, dtype=None, delimiter=",", skip_header=1, encoding=None)

            cells_played = np.zeros(
                (self.in_data["numberRounds"] + 1, self.in_data["mapSize"], self.in_data["mapSize"]), dtype=float
            )
            total_cells_played = np.zeros(self.in_data["numberRounds"] + 1)
            stars_played = np.zeros(
                (self.in_data["numberRounds"] + 1, self.in_data["mapSize"], self.in_data["mapSize"]), dtype=float
            )
            total_stars_played = np.zeros(self.in_data["numberRounds"] + 1)
            for round_number, _, mapX, mapY, _, numberStars, _ in out_data:
                cells_played[round_number, mapY, mapX] += 1
                total_cells_played[round_number] += 1
                stars_played[round_number, mapY, mapX] += numberStars
                total_stars_played[round_number] += numberStars

            cells_played_cum = np.cumsum(cells_played, axis=0)
            total_cells_played_cum = np.cumsum(total_cells_played)
            stars_played_cum = np.cumsum(stars_played, axis=0)
            total_stars_played_cum = np.cumsum(total_stars_played)

            self.proportion_visits = cells_played_cum
            self.proportion_stars = stars_played_cum
            for round_number in range(1, self.in_data["numberRounds"] + 1):
                self.proportion_visits[round_number] /= total_cells_played_cum[round_number]
                self.proportion_stars[round_number] /= total_stars_played_cum[round_number]

            self.bottom.update_frm_info_text()
            self.restart_round()
            self.map.put_values_map()

    def next_round(self):
        if self.round.get() != self.in_data["numberRounds"]:
            self.round.set(self.round.get() + 1)
            self.map.update_map_colors()
            self.bottom.update_lbl_round_text()

    def previous_round(self):
        if self.round.get() != 0:
            self.round.set(self.round.get() - 1)
            self.map.update_map_colors()
            self.bottom.update_lbl_round_text()

    def play(self):
        if self.running:
            self.running = False
        else:
            self.running = True

    def play_loop(self):
        if self.running:
            if self.round.get() != self.in_data["numberRounds"]:
                self.next_round()
            else:
                self.running = False
        self.parent.after(300, self.play_loop)

    def restart_round(self):
        self.running = False
        self.round.set(0)
        self.bottom.activate_frm_buttons()
        self.bottom.update_lbl_round_text()
        self.map.update_map_colors()


def app(path_data):
    root = tk.Tk()
    root.title("Stigmer")
    MainApplication(root, path_data).pack(fill=tk.BOTH, expand=True)
    root.mainloop()
