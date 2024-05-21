import gi
import random
import sys

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

class LiteralnieFunGame(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Literalnie.fun")
        self.set_default_size(500, 600)
        self.set_resizable(False)
        self.game_over = None
        self.expert_mode = False

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        self.menu_bar = Gtk.MenuBar()
        self.create_menu()
        vbox.pack_start(self.menu_bar, False, False, 0)

        self.grid_layout = Gtk.Grid()
        vbox.pack_start(self.grid_layout, True, True, 0)
        self.get_style_context().add_class("window")

        self.current_row = 0
        self.current_col = 0

        self.valid_words = self.load_words("wyrazy_piecioliterowe.txt")

        self.letters_good_position = ['-', '-', '-', '-', '-']
        self.letters_bad_position = []
        self.current_word = random.choice(list(self.valid_words))
        print(self.current_word)
        self.create_grid()
        # self.start_new_game()

        self.connect("key-press-event", self.on_key_press)

    def create_grid(self):
        self.buttons = []
        for row in range(6):
            button_row = []
            for col in range(5):
                button = Gtk.Button(label="")
                button.set_size_request(80, 80)
                button.get_style_context().add_class("button")
                button.get_style_context().add_class("black")
                self.grid_layout.attach(button, col, row, 1, 1)
                button_row.append(button)
            self.buttons.append(button_row)
        self.grid_layout.show_all()

    def create_menu(self):
        game_menu = Gtk.Menu()
        game_item = Gtk.MenuItem(label="Gra")
        game_item.set_submenu(game_menu)
        self.menu_bar.append(game_item)

        new_game_action = Gtk.MenuItem(label="Nowa gra")
        help_action = Gtk.MenuItem(label="Pokaż pomoc")
        self.expert_action = Gtk.MenuItem(label="Włącz tryb ekspert")

        new_game_action.connect("activate", self.start_new_game)
        help_action.connect("activate", self.show_help)
        self.expert_action.connect("activate", self.turn_expert)

        game_menu.append(new_game_action)
        game_menu.append(help_action)
        game_menu.append(self.expert_action)
        game_menu.show_all()

    def on_key_press(self, widget, event):
        if self.game_over:
            return
        keyval = Gdk.keyval_name(event.keyval)
        forbidden_chars = ['equal', 'backslash', 'Escape', 'grave', 'Tab', 'minus', 'bracketleft', 'bracketright',
                           'apostrophe', 'semicolon', 'comma', 'period', 'slash', 'Left', 'Down', 'Up', 'Right', 'Home',
                           'End', 'Delete',
                           'Greek_pi', 'oe', 'eogonek', 'copyright', 'ssharp', 'leftarrow', 'downarrow', 'rightarrow',
                           'oacute', 'thorn',
                           'lstroke', 'ellipsis', 'rightsinglequotemark', 'eng', 'ae', 'eth', 'sacute', 'aogonek',
                           'zabovedot', 'zacute',
                           'cacute', 'doublelowquotemark', 'rightdoublequotemark', 'nacute', 'mu']
        if event.state & Gdk.ModifierType.MOD1_MASK:
            polish_letters = {
                'a': 'Ą', 'c': 'Ć', 'e': 'Ę', 'l': 'Ł',
                'n': 'Ń', 'o': 'Ó', 's': 'Ś', 'x': 'Ź',
                'z': 'Ż'
            }
            if keyval in polish_letters:
                self.set_letter(polish_letters[keyval])
        elif keyval == 'BackSpace':
            self.remove_letter()

        elif keyval in ['Return', 'KP_Enter']:
            self.check_word()

        elif keyval.isalpha() and keyval not in forbidden_chars:
            letter = keyval.upper()
            self.set_letter(letter)

    def set_letter(self, letter):
        if self.current_col < 5:
            button = self.buttons[self.current_row][self.current_col]
            button.set_label(letter)
            button.show()
            self.current_col += 1

    def remove_letter(self):
        if self.current_col > 0:
            self.current_col -= 1
            self.buttons[self.current_row][self.current_col].set_label("")

    def check_word(self):
        if self.current_col == 5:
            word = ''.join(self.buttons[self.current_row][col].get_label() for col in range(5))
            if self.is_valid_word(word):
                if self.expert_mode:
                    for letter in self.letters_bad_position:
                        if letter not in word:
                            self.show_message("Błąd", "Nie użyto wszystkich liter")
                            return
                    for i, letter in enumerate(self.letters_good_position):
                        if letter != '-':
                            if word[i] != letter:
                                self.show_message("Błąd", "Nie użyto wszystkich liter")
                                return

                self.change_colors(word)
                if word == self.current_word:
                    self.show_message("Koniec gry", "Wygrałeś!")
                    self.game_over = True
                else:
                    self.current_row += 1
                    self.current_col = 0
                    if self.current_row == 6:
                        self.show_message("Koniec gry", f"Przegrałeś:(\nSłowo w tej grze to {self.current_word}")
                        self.game_over = True
            else:
                self.show_message("Niepoprawne słowo", "Wprowadź prawidłowe słowo.")
        else:
            self.show_message("Niepoprawne słowo", "Wprowadź pięcioliterowe słowo")

    def change_colors(self, typed_word):
        changed_positions = []
        current_word_letter_count = {}

        for i, letter in enumerate(self.current_word):
            if letter == typed_word[i]:
                self.buttons[self.current_row][i].get_style_context().remove_class("green")
                self.buttons[self.current_row][i].get_style_context().remove_class("orange")
                self.buttons[self.current_row][i].get_style_context().add_class("green")
                changed_positions.append(i)
                if self.expert_mode:
                    self.letters_good_position[i] = letter

        for letter in self.current_word:
            if letter in current_word_letter_count:
                current_word_letter_count[letter] += 1
            else:
                current_word_letter_count[letter] = 1

        for i in changed_positions:
            current_word_letter_count[self.current_word[i]] -= 1

        self.letters_bad_position = []

        for i, letter in enumerate(typed_word):
            if i not in changed_positions:
                if letter in self.current_word and current_word_letter_count[letter] > 0:
                    self.buttons[self.current_row][i].get_style_context().remove_class("green")
                    self.buttons[self.current_row][i].get_style_context().remove_class("orange")
                    self.buttons[self.current_row][i].get_style_context().add_class("orange")
                    current_word_letter_count[letter] -= 1
                    if self.expert_mode and letter not in self.letters_bad_position:
                        self.letters_bad_position.append(letter)
                else:
                    self.buttons[self.current_row][i].get_style_context().remove_class("green")
                    self.buttons[self.current_row][i].get_style_context().remove_class("orange")

    def is_valid_word(self, word):
        return word in self.valid_words

    def load_words(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as file:
                return {line.strip().upper() for line in file}
        except FileNotFoundError:
            self.show_message("Błąd", f"Plik {filename} nie został znaleziony.")
            sys.exit()

    def show_message(self, title, message):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, title)
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def turn_expert(self, widget):
        if self.current_row != 0:
            self.show_message("Błąd", "Nie możesz zmieniać trybu ekspert w trakcie rozgrywki")
            return
        if self.expert_mode:
            self.expert_mode = False
            self.expert_action.set_label("Włącz tryb ekspert")
        else:
            self.expert_mode = True
            self.expert_action.set_label("Wyłącz tryb ekspert")

    def start_new_game(self, widget=None):
        self.current_row = 0
        self.current_col = 0
        self.game_over = False
        # self.create_grid()

        for row in self.buttons:
            for button in row:
                button.set_label("")
                button.get_style_context().remove_class("orange")
                button.get_style_context().remove_class("black")
                button.get_style_context().remove_class("green")
                button.get_style_context().add_class("black")

        self.letters_good_position = ['-', '-', '-', '-', '-']
        self.letters_bad_position = []
        self.current_word = random.choice(list(self.valid_words))
        print(self.current_word)

    def show_help(self, widget):
        self.show_message("Pomoc",
                          "Wpisz dowolne pięcioliterowe słowo za pomocą klawiatury i naciśnij enter, by spróbować odgadnąć hasło.\n"
                          "Jeżeli pomylisz literę, możesz ją cofnąć za pomocą Backspace\n"
                          "Polskie znaki koniecznie wpisuj z użyciem lewego ALT\n"
                          "Po każdej próbie, litery zostaną zaznaczone:\n"
                          "- na zielono, jeśli występuje w haśle w tym samym miejscu\n"
                          "- na żółto, jeśli występuje w haśle, ale w innym miejscu\n"
                          "- brak podświetlenia świadczy o braku występowania litery w końcowym haśle\n"
                          "Na odgadnięcie hasła masz 6 prób.\n"
                          "Jeżeli chcesz się sprawdzić w trudniejszym zadaniu, możesz włączyć tryb dla eksperta, "
                          "który spowoduje, że dotychczas znalezione litery musisz użyć w kolejnym odgadywanym słowie. "
                          "Jednak tryb ten możesz włączyć tylko na początku rozgrywki\n"
                          "Powodzenia!")

if __name__ == "__main__":
    css = b"""
    .window{
        background: gray;
    }
    .button {
        border: 1px solid gray;
        color: white;
        font-size: 24px; 
        padding: 25px; 
        margin: 7px;
        min-width: 35px;
    }
    .black {
        background: #333;
    }
    .green {
        background: green;
    }
    .orange {
        background: orange;
    }
    """

    style_provider = Gtk.CssProvider()
    style_provider.load_from_data(css)

    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        style_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    app = LiteralnieFunGame()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
