import PySimpleGUI as sg
import logging

KEY_CLOSE = "CLOSE"
KEY_STEP = "STEP"
KEY_CELL = "CELL"
KEY_AUTO_CHECK = "AUTO"
KEY_SOLVE = "SOLVE"

table_0 = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, ],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, ],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, ],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, ],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, ],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, ],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, ],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, ],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, ],
]

table_1 = [
    [1, 3, 0, 0, 0, 0, 0, 0, 0, ],
    [0, 2, 0, 0, 0, 0, 0, 0, 0, ],
    [0, 0, 3, 0, 0, 0, 0, 0, 0, ],
    [0, 0, 0, 4, 0, 0, 0, 0, 0, ],
    [0, 0, 0, 0, 5, 0, 0, 0, 0, ],
    [0, 0, 0, 0, 0, 6, 0, 0, 0, ],
    [0, 0, 0, 0, 0, 0, 7, 0, 0, ],
    [0, 0, 0, 0, 0, 0, 0, 8, 0, ],
    [2, 0, 0, 0, 0, 0, 0, 0, 9, ],
]

table_2 = [
    [0, 0, 0, 0, 3, 5, 4, 7, 0, ],
    [0, 0, 0, 0, 7, 0, 0, 5, 0, ],
    [1, 5, 0, 0, 8, 0, 0, 0, 6, ],
    [0, 0, 0, 0, 0, 9, 0, 6, 2, ],
    [0, 0, 0, 0, 0, 0, 8, 0, 0, ],
    [2, 0, 0, 3, 0, 6, 0, 9, 0, ],
    [0, 0, 3, 0, 0, 7, 0, 1, 0, ],
    [6, 0, 4, 0, 0, 0, 7, 0, 0, ],
    [9, 0, 0, 0, 0, 0, 0, 0, 0, ],
]

table_3 = [
    [0, 4, 8, 0, 0, 0, 5, 0, 0, ],
    [7, 0, 0, 0, 0, 0, 0, 0, 0, ],
    [0, 0, 9, 0, 0, 6, 0, 4, 0, ],
    [0, 0, 0, 3, 0, 0, 0, 6, 8, ],
    [9, 3, 0, 0, 0, 0, 1, 0, 5, ],
    [0, 0, 0, 0, 1, 0, 0, 2, 0, ],
    [0, 0, 2, 0, 0, 5, 0, 0, 1, ],
    [0, 5, 0, 1, 0, 0, 3, 0, 0, ],
    [0, 0, 0, 2, 8, 0, 0, 0, 0, ],
]

def create_layout():
    layout = []
    for j in range(0,9):
        row = []
        for i in range(0,9):
            row.append(sg.Text(" ", background_color="white", text_color="black", border_width=1, key=f"{KEY_CELL}_{j}_{i}"))
            if i % 3 == 2 and i // 3 in (0, 1):
                row.append(sg.VSeparator())
        layout.append(row)
        if j % 3 == 2 and j // 3 in (0, 1):
            layout.append([sg.HSeparator()])
    layout.append([sg.Button("close", key=KEY_CLOSE),
                   sg.Button("step", key=KEY_STEP),
                   sg.Check("auto", key=KEY_AUTO_CHECK, enable_events=True),
                   sg.Button("BACK", key=KEY_SOLVE),
                   ])
    return layout



def get_box_index(j, i):
    return 3*(j//3) + i//3


class SudokuException(Exception):
    pass


class Sudoku:

    def __init__(self, table):
        self.table = table
        self.stepcount = 0
        self.fixed = [[False] * 9 for _ in range(9)]
        for i in range(0, 9):
            for j in range(0, 9):
                if self.table[j][i] > 0:
                    self.fixed[j][i] = True
        self.track_i = 0
        self.track_j = 0
        self.state = "FORWARD"

        self.row_sets = [self.row_set(j) for j in range(0,9)]
        self.col_sets = [self.col_set(i) for i in range(0,9)]
        self.box_sets = [self.box_set(i) for i in range(0,9)]

    def row_set(self, j):
        rs = {self.table[j][i] for i in range(0,9) if self.table[j][i]}
        return rs

    def col_set(self, i):
        cs = {self.table[j][i] for j in range(0,9) if self.table[j][i]}
        return cs

    def box_set(self, b):
        bi = b % 3
        bj = b // 3
        bs = {self.table[j][i]
              for j in range(3*bj, 3*bj+3)
              for i in range(3*bi, 3*bi+3)
              if self.table[j][i]}
        return bs

    def display_table(self, window):
        for j in range(0, 9):
            for i in range(0, 9):
                if self.table[j][i]:
                    fgcolor = "black"
                    if self.fixed[j][i]:
                        if self.track_i == i and self.track_j == j:
                            bgcolor = "orange"
                        else:
                            bgcolor = "grey"
                    else:
                        if self.track_i == i and self.track_j == j:
                            bgcolor = "yellow"
                        else:
                            bgcolor = "white"
                else:
                    if self.track_i == i and self.track_j == j:
                        bgcolor = "yellow"
                        fgcolor = "yellow"
                    else:
                        bgcolor = "white"
                        fgcolor = "white"
                window[f"{KEY_CELL}_{j}_{i}"].update(value=self.table[j][i],
                                                     background_color=bgcolor,
                                                     text_color=fgcolor)

    def next_cell(self):
        self.track_i += 1
        if self.track_i > 8:
            self.track_i = 0
            self.track_j += 1

    def prev_cell(self):
        self.track_i -= 1
        if self.track_i < 0:
            self.track_i = 8
            self.track_j -= 1

    def step_over_fixed(self):
        if self.fixed[self.track_j][self.track_i]:
            logging.debug(f"Fixed: {self.track_j}, {self.track_i}")
            if self.state == "FORWARD":
                self.next_cell()
            elif self.state == "BACKTRACK":
                self.prev_cell()
            return True
        else:
            return False

    def is_finished(self):
        return self.track_j > 8

    def is_no_solution(self):
        return self.track_j < 0

    def step(self):
        if self.is_finished():
            logging.warning("Finished")
            return False
        if self.is_no_solution():
            logging.warning("No Solution")
            return False
        self.stepcount += 1
        if self.step_over_fixed():
            return True
        val = self.table[self.track_j][self.track_i]
        if val:
            self.row_sets[self.track_j].remove(val)
            self.col_sets[self.track_i].remove(val)
            self.box_sets[get_box_index(self.track_j, self.track_i)].remove(val)
            self.table[self.track_j][self.track_i] = 0
        if val == 9:
            logging.debug(f"Backtrack: {self.track_j}, {self.track_i}")
            self.prev_cell()
            self.state = "BACKTRACK"
        else:
            self.state = "FORWARD"
            found = False
            while not found:
                val += 1
                if val > 9:
                    logging.debug(f"Backtrack: {self.track_j}, {self.track_i}")
                    self.prev_cell()
                    self.state = "BACKTRACK"
                    self.found = True
                    break
                if val in self.row_sets[self.track_j]:
                    logging.debug(f"step: {self.track_j}, {self.track_i}: {val} already in row")
                elif val in self.col_sets[self.track_i]:
                    logging.debug(f"step: {self.track_j}, {self.track_i}: {val} already in col")
                elif val in self.box_sets[get_box_index(self.track_j, self.track_i)]:
                    logging.debug(f"step: {self.track_j}, {self.track_i}: {val} already in box")
                else:
                    self.row_sets[self.track_j].add(val)
                    self.col_sets[self.track_i].add(val)
                    self.box_sets[get_box_index(self.track_j, self.track_i)].add(val)
                    self.table[self.track_j][self.track_i] = val
                    self.next_cell()
                    found = True
        return True


def main():
    level = logging.INFO
    fmt = '[%(levelname)s] %(asctime)s - %(message)s'
    logging.basicConfig(level=level, format=fmt)

    layout = create_layout()
    window = sg.Window(title="Sudoku Solver", layout=layout, finalize=True)
    table = Sudoku(table_2)

    table.display_table(window)

    timeout = None
    while True:
        event, value = window.read(timeout=timeout)
        if event == KEY_CLOSE or event == sg.WIN_CLOSED:
            break
        elif event == KEY_STEP:
            table.step()
            table.display_table(window)
        elif event == KEY_SOLVE:
            if table.is_finished():
                table.prev_cell()
                table.state="BACKTRACK"
                table.step()
                if window[KEY_AUTO_CHECK].get():
                    timeout = 0
            # logging.info("Start Solving")
            # while table.step():
            #     pass
            # logging.info("Solving ended")
            table.display_table(window)
        elif event == KEY_AUTO_CHECK:
            if window[KEY_AUTO_CHECK].get():
                timeout = 0
            else:
                timeout = None
        elif window[KEY_AUTO_CHECK].get():
            if table.is_finished() or table.is_no_solution():
                timeout = None
            else:
                while table.step():
                    if table.stepcount % 10000 == 0:
                        break
            table.display_table(window)

    window.close()


if __name__ == "__main__":
    main()