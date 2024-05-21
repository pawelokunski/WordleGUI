from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QMessageBox, QMenu, QMenuBar, QVBoxLayout
from PyQt5.QtCore import QSize, Qt
import random
import sys


class LiteralnieFunGame(QWidget):
    def __init__(self):
        super().__init__()

        self.game_over = None
        self.expert_mode = False
        self.setWindowTitle("Literalnie.fun")
        self.setFixedSize(500, 600)  # Rozmiar okna
        self.setStyleSheet("background-color: gray;")
        main_layout = QVBoxLayout()

        self.menu_bar = QMenuBar()
        self.create_menu()
        main_layout.setMenuBar(self.menu_bar)

        self.grid_layout = QGridLayout()
        self.create_grid()
        main_layout.addLayout(self.grid_layout)

        self.setLayout(main_layout)

        self.current_row = 0
        self.current_col = 0

        self.valid_words = self.load_words("wyrazy_piecioliterowe.txt")

        self.start_new_game()
        self.letters_good_position = ['-', '-', '-', '-', '-']
        self.letters_bad_position = []
    def create_grid(self):
        self.buttons = []
        for row in range(6):
            button_row = []
            for col in range(5):
                button = QPushButton()
                button.setFixedSize(QSize(80, 80))  # Ustalony rozmiar przycisków
                button.setStyleSheet("background-color: #333; border: 1px solid gray; color: white; font-size: 24px;")
                self.grid_layout.addWidget(button, row, col)
                button_row.append(button)
            self.buttons.append(button_row)

    def create_menu(self):
        game_menu = self.menu_bar.addMenu("Gra")
        new_game_action = game_menu.addAction("Nowa gra")
        help_action = game_menu.addAction("Pokaż pomoc")
        self.expert_action = game_menu.addAction("Włącz tryb ekspert")
        new_game_action.triggered.connect(self.start_new_game)
        help_action.triggered.connect(self.show_help)
        self.expert_action.triggered.connect(self.turn_expert)

    def keyPressEvent(self, event):
        if self.game_over:
            return

        if event.modifiers() & Qt.AltModifier:
            polish_letters = {
                Qt.Key_A: 'Ą', Qt.Key_C: 'Ć', Qt.Key_E: 'Ę', Qt.Key_L: 'Ł',
                Qt.Key_N: 'Ń', Qt.Key_O: 'Ó', Qt.Key_S: 'Ś', Qt.Key_X: 'Ź',
                Qt.Key_Z: 'Ż'
            }
            if event.key() in polish_letters:
                self.set_letter(polish_letters[event.key()])

        elif event.key() in range(Qt.Key_A, Qt.Key_Z + 1):
            letter = event.text().upper()
            self.set_letter(letter)

        elif event.key() == Qt.Key_Backspace:
            self.remove_letter()

        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.check_word()

    def set_letter(self, letter):
        if self.current_col < 5:
            self.buttons[self.current_row][self.current_col].setText(letter)
            self.current_col += 1

    def remove_letter(self):
        if self.current_col > 0:
            self.current_col -= 1
            self.buttons[self.current_row][self.current_col].setText("")

    def check_word(self):
        if self.current_col == 5:
            word = ''.join(self.buttons[self.current_row][col].text() for col in range(5))
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

                self.change_colors(typed_word=word)
                if word == self.current_word:
                    self.show_message("Koniec gry", "Wygrałeś!")
                    self.game_over = True  # Ustaw stan gry na zakończony
                else:
                    self.current_row += 1
                    self.current_col = 0
                    if self.current_row == 6:
                        self.show_message("Koniec gry", f"Przegrałeś:(\nSłowo w tej grze to {self.current_word}")
                        self.game_over = True  # Ustaw stan gry na zakończony
            else:
                self.show_message("Niepoprawne słowo", "Wprowadź prawidłowe słowo.")
        else:
            self.show_message("Niepoprawne słowo", "Wprowadź pięcioliterowe słowo")

    def change_colors(self, typed_word):
        changed_positions = []
        for i, letter in enumerate(typed_word):
            if letter == self.current_word[i]:
                changed_positions.append(i)
                self.buttons[self.current_row][i].setStyleSheet("background-color: green; border: 1px solid gray; color: white; font-size: 24px;")
                if self.expert_mode:
                    self.letters_good_position[i] = letter
        self.letters_bad_position = []
        for i, letter in enumerate(typed_word):
            if i not in changed_positions and letter in self.current_word:

                correct_count = self.current_word.count(letter)
                typed_count = sum(1 for pos in changed_positions if self.current_word[pos] == letter) + typed_word[
                                                                                                    :i].count(letter)

                if typed_count < correct_count:
                    self.buttons[self.current_row][i].setStyleSheet(
                        "background-color: orange; border: 1px solid gray; color: white; font-size: 24px;")
                    if letter not in self.letters_bad_position and self.expert_mode:
                        self.letters_bad_position.append(letter)
        print(self.letters_good_position)
        print(self.letters_bad_position)

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
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()

    def turn_expert(self):
        if self.current_row != 0:
            self.show_message("Błąd", "Nie możesz zmieniać trybu ekspert w trakcie rozgrywki")
            return
        if self.expert_mode:
            self.expert_mode = False
            self.expert_action.setText("Włącz tryb ekpert")
        else:
            self.expert_mode = True
            self.expert_action.setText("Wyłącz tryb ekspert")

    def start_new_game(self):

        self.current_row = 0
        self.current_col = 0
        self.game_over = False
        self.create_grid()

        for row in self.buttons:
            for button in row:
                button.setText("")
        self.letters_good_position = ['-', '-', '-', '-', '-']
        self.letters_bad_position = []
        self.current_word = random.choice(list(self.valid_words))
        print(self.current_word)

    def show_help(self):
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
    app = QApplication(sys.argv)
    game = LiteralnieFunGame()
    game.show()
    sys.exit(app.exec())