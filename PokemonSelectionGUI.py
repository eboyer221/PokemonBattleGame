import io
import tkinter as tk
from tkinter import *
from tkinter import ttk
import random
import pandas as pd
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageTk
import requests
import json
from tkinter import messagebox

import main
# from BattleFrame import BattleFrame
from main import Pokemon, pokedex


class Player:
    def __init__(self, name, pokemon):
        self.name = name
        self.pokemon = pokemon
        self.frame = None
    def attack(self, other_player):
        other_player.pokemon.life_points = max(other_player.pokemon.life_points - self.pokemon.hit_power, 0)
        messagebox.showinfo("Attack!", f"{self.pokemon.name} attacks!")
        messagebox.showinfo("Life Power Lost!", f"{other_player.pokemon.name} loses life power!")
        messagebox.showinfo("Life Power", f"{other_player.pokemon.name} life power is {other_player.pokemon.life_points}!")
        return other_player.pokemon.lifepoints > 0


class PokemonGame:
    def __init__(self):
        self.df = self.pokedex()
        # main window of game
        self.root = tk.Tk()
        self.root.title("Pokedex")

        # Player
        self.player = None

        # Enemy
        self.enemy = None

        # Player Pokemon Image
        self.player_pokemon_img = None

        # Enemy Pokemon
        self.enemy_pokemon = None

        # Enemy Pokemon Image
        self.enemy_pokemon_img = None

        # BattleFrame
        self.battle_frame = None

        # FleeButton
        self.flee_button = None

        # AttackButton
        self.attack_button = None

        ##### Pokedex Table #######
        self.pokemon_selection = Label(self.root, text="Pokemon Selection", bg="lightgrey")
        self.pokemon_selection.grid(row=0, column=1, columnspan=4, padx=5, pady=5)

        # Type Selection dropdown menu
        # Label for Type Selection
        ttk.Label(self.root, text="Type:",
                  font=("Times New Roman", 10)).grid(column=1,
                                                     row=1, padx=1, pady=2)
        self.n = tk.StringVar()
        self.type_selection = ttk.Combobox(self.root, width=10,
                                           textvariable=self.n)

        # Adding combobox drop down list
        self.type_selection['values'] = (' -All-',
                                         ' Normal',
                                         ' Fire',
                                         ' Water',
                                         ' Electric',
                                         ' Grass',
                                         ' Ice',
                                         ' Fighting',
                                         ' Poison',
                                         ' Ground',
                                         ' Flying',
                                         ' Psychic',
                                         'Bug',
                                         'Rock',
                                         'Ghost',
                                         'Dragon',
                                         'Dark',
                                         'Steel',
                                         'Fairy'
                                         )

        self.type_selection.grid(column=2, row=1)

        # Shows -All- as a default value
        self.type_selection.current(0)
        # Adding trace to the combobox
        self.n.trace('w', lambda *args: self.filter_table())

        # Search box for Pokemon
        ttk.Label(self.root, text="Name:",
                  font=("Times New Roman", 10)).grid(column=3,
                                                     row=1, padx=10, pady=2)
        self.name_text = tk.StringVar()
        self.name = tk.Entry(self.root, width=20, textvariable=self.name_text)
        self.name.grid(column=4, row=1, padx=1, pady=2)
        self.name_text.trace('w', lambda *args: self.filter_table())

        ###Pokedex Table###
        # create a frame for the pokedex table with a horizontal scrollbar
        self.table_frame = tk.Frame(self.root)
        self.table_frame.grid(row=2, column=1, columnspan=4, rowspan=2, padx=1, pady=1)

        self.xscrollbar = tk.Scrollbar(self.table_frame, orient='horizontal')
        self.xscrollbar.pack(side='bottom', fill='x')

        # create the tkinter window and table
        self.tree = ttk.Treeview(self.table_frame, xscrollcommand=self.xscrollbar.set, show='headings')

        self.tree['columns'] = self.df.columns

        # create a dictionary to map column names to column indices
        self.column_dict = {col: i for i, col in enumerate(self.df.columns)}

        # add the pokedex columns to the Treeview widget
        for col in self.df.columns:
            self.tree.column(self.column_dict[col], width=80, stretch=True)
            self.tree.heading(self.column_dict[col], text=col)
        # configure the scrollbar to scroll the treeview widget
        self.xscrollbar.config(command=self.tree.xview)
        self.tree.pack(side='left')
        # set padx=0 to remove horizontal padding
        self.table_frame.grid_columnconfigure(0, weight=1, pad=0)
        self.filter_table()

        # Select Button
        Button(self.root, text="Select Your Pokemon", command=lambda: self.show_pokemon_info()).grid(row=4, column=1,
                                                                                                     columnspan=3,
                                                                                                     pady=20)

        self.root.mainloop()

    # create pokedex dataframe

    def pokedex(self, url='https://pokemondb.net/pokedex/all'):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'id': 'pokedex'})
        headers = []
        for th in table.find('thead').find_all('th'):
            headers.append(th.text.strip())
        headers.append('image_url')
        rows = []
        for tr in table.find('tbody').find_all('tr'):
            row = []
            for td in tr.find_all('td'):
                row.append(td.text.strip())
            row.append(tr.find("img")['src'])
            rows.append(row)
        df = pd.DataFrame(rows, columns=headers)
        df = df.rename(columns={'#': 'Number', 'Sp. Atk': 'Special_Attack', 'Sp. Def': 'Special_Defense'})
        return df

    # create function to filter pokedex table based on search
    def filter_table(self):
        selected_type = self.type_selection.get()
        print(selected_type)
        search_text = self.name_text.get()

        if selected_type == ' -All-':
            filtered_df = self.df
        else:
            filtered_df = self.df[self.df['Type'].str.contains(selected_type)]
        search_df = self.df
        if search_text:
            search_df = self.df[self.df['Name'].str.startswith(search_text, na=False)]

        # search_df = self.df[self.df['Name'].str.startswith(search_text, na=False)]
        self.tree.delete(*self.tree.get_children())

        for i, row in pd.merge(filtered_df, search_df, how='inner', on=['Number']).iterrows():
            self.tree.insert('', 'end', values=tuple(row))

    def show_pokemon_info(self):
        # Get the selected Pokemon from the Treeview widget
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])  # Get the first selected item
            values = item['values']  # Get the values of the selected item
            pokemon_data = self.df.loc[
                self.df['Name'] == values[1]]  # Get the row of the selected Pokemon from the dataframe
            self.player = Player("User", Pokemon(pokemon_data))
            # main.cached_player = self.player
            # main.cached_players = ("player", self.player, self.root)
            info_window = main.display_pokemon("player", self.player, self.root)

            # Create a Battle button that closes the window and sets the pokemon_name variable
            # battle_button = tk.Button(info_window, text="Battle", command=main.display_pokemon("enemy", self.enemy, self.root))
            # battle_button = tk.Button(info_window, text="Battle", command=self.show_pokemon_info())
            # battle_button.grid(row=5, column=1)

            # Battle Button
            Button(self.root, text="Battle", command=lambda: self.start_battle()).grid(row=10, column=1, columnspan=3,
                                                                                       pady=20)

            # Make the window stay open until the user closes it
            # info_window.mainloop()
            # info_window.grab_set()
            # info_window.protocol("WM_DELETE_WINDOW", lambda: self.close_window(info_window))
            return info_window
        else:
            # If no Pokemon is selected, show an error message
            tk.messagebox.showerror("Error",
                                    "Please click on the Pokemon you want to select in the table before pressing the Select button.")

    def close_window(self, window):
        window.grab_release()
        window.destroy()

    def flee(self, info_window, root):
        for window in main.cached_windows:
            window.destroy()
        self.attack_button.grid_remove()
        self.flee_button.grid_remove()

    def move_set(self):
        def move_set(pokemon_name):
            with open('pokemon.json', 'r') as moves_data:
                data = json.load(moves_data)
            for pokemon in data:
                if pokemon['name'] == pokemon_name:
                    return pokemon['abilities']
            return None

    def start_battle(self):
        # print("Choose your Pokemon:")
        self.enemy = Player("enemy", Pokemon(pokedex.sample()))

        # print out their basic info
        self.player.pokemon.say_hi()
        self.enemy.pokemon.say_hi()
        # Attack Button
        self.attack_button = Button(self.root,
                                    text="Attack",
                                    command=lambda: main.handle_attack_click(self.player, self.enemy))
        self.attack_button.grid(row=10, column=1, columnspan=3, pady=20)

        # Create the BattleFrame and hide the current frame
        # self.battle_frame = BattleFrame(self.root, self.player, self.enemy)
        info_window = main.display_pokemon("enemy", self.enemy, self.root)

        # Flee Button
        self.flee_button = Button(self.root, text="Flee", command=lambda: self.flee(info_window, self.root))
        self.flee_button.grid(row=10, column=0, columnspan=3, pady=20)
        # info_window.grab_set()
        # info_window.protocol("WM_DELETE_WINDOW", lambda: self.close_window(info_window))
        return info_window


if __name__ == "__main__":
    PokemonGame()

