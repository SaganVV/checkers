import tkinter
import turtle
import numpy as np

from time import sleep
from random import choice
from copy import deepcopy
from playsound import playsound

if __name__=='__main__':
    screen = turtle.Screen()
    screen.title('NARUTO TOP')
    screen.bgpic('background.gif')
    canvas = screen.getcanvas()
    screen.setup(800, 800)
    HEIGHT = screen.window_height()
    WIDTH = screen.window_width()
    SIZE_CELL = WIDTH/16
    screen.colormode(255)
    turtle.hideturtle()
    turtle.pensize(4)
    turtle.speed(0)
    turtle.delay(0.1)

def from_grid_to_pixel(x, y):
    return y*SIZE_CELL+SIZE_CELL/2, x*SIZE_CELL+SIZE_CELL/2,


def from_pixel_ro_grid(x, y):
    return int(y//SIZE_CELL), int(x//SIZE_CELL)


class Figure:

    def __init__(self, x, y, border_color='red', fill_color='black'):
        """ Конструктор
        :param x: координата x положення фігури
        :param y: координата y положення фігури
        :param border_color: колір фігури
        :param fill_color: колір заливки
        """
        self._x = x  # _x - координата x
        self._y = y  # _y - координата y
        self._visible = False  # _visible - чи є фіруга видимою на екрані
        self.fill_color = fill_color   # _color - колір фігури
        self.border_color = border_color

    def _draw(self, border_color, fill_color):
        """ Допоміжний віртуальний метод, що зображує фігуру заданим кольором
        Тут здійснюється лише декларація методу, а конкретна
        реалізація буде здійснюватися у конкретних нащадках

        """
        pass

    def show(self):
        """ Зображує фігуру на екрані """
        if not self._visible:
            self._visible = True
            self._draw(self.border_color, self.fill_color)

    def hide(self):
        """ Ховає фігуру (робить її невидимою на екрані) """
        if self._visible:
            self._visible = False
            # щоб сховати фігуру, потрібно
            # зобразити її кольором фону.
            self._draw('black', 'black')

    def set_position(self, x, y):
        is_visible = self._visible

        if is_visible:
            self.hide()
        self._x = x
        self._y = y
        if is_visible:
            self.show()

    def set_border_color(self, color):
        self.border_color = color

    def set_fill_color(self, color):
        self.fill_color = color


class Cell(Figure):
    def __init__(self, x, y, size, border_color='black', fill_color='black'):
        super().__init__(x, y, border_color, fill_color)
        self.__size = size

    def _draw(self, border_color, fill_color):
        left_x = self._x-self.__size//2
        left_y = self._y-self.__size//2
        turtle.up()
        turtle.hideturtle()
        turtle.color(border_color)
        turtle.fillcolor(fill_color)
        turtle.setpos(left_x, left_y)
        turtle.down()
        turtle.begin_fill()
        for i in range(4):
            turtle.forward(self.__size)
            turtle.left(90)
        turtle.end_fill()

    def draw_border(self, border_color, pensize=4):
        left_x = self._x-self.__size//2
        left_y = self._y-self.__size//2
        turtle.up()
        turtle.pensize(pensize)
        turtle.color(border_color)
        turtle.setpos(left_x, left_y)
        turtle.down()
        for i in range(4):
            turtle.forward(self.__size)
            turtle.left(90)
        turtle.pensize(1)


class Checker(Figure):
    def __init__(self, x, y,  size=SIZE_CELL//2, values=1):
        super().__init__(x, y, 'black', 'white' if values == 1 else 'red')
        self.__values = values
        self.__size = size
        self.__is_queen = False


    def get_values(self):
        return self.__values

    def _draw(self, border_color, fill_color):
        left_x = self._x
        left_y = self._y - self.__size
        turtle.speed(0)
        turtle.up()
        turtle.hideturtle()
        turtle.color(border_color)
        turtle.fillcolor(fill_color)
        turtle.setpos(left_x, left_y)
        turtle.down()
        turtle.begin_fill()
        turtle.circle(self.__size)
        turtle.end_fill()
        if self.__is_queen:
            turtle.up()
            left_y = self._y-self.__size/2
            turtle.up()
            turtle.pensize(1)
            turtle.setpos(left_x,left_y)
            turtle.down()
            turtle.circle(self.__size/2)

    def is_queen(self):
        return self.__is_queen

    def set_is_queen(self, bool):
        self.__is_queen = bool

    def __repr__(self):
        return f'{from_pixel_ro_grid(self._x, self._y)}, {self.fill_color}, {self.is_queen()}|'


class GameHandler:
    def __init__(self, with_bot = False):
        self.checker_dask_values = np.array([[1, 0, 1, 0, 1, 0, 1, 0],
                                             [0, 1, 0, 1, 0, 1, 0, 1],
                                             [1, 0, 1, 0, 1, 0, 1, 0],
                                             [0]*8, [0]*8,
                                             [0, -1, 0, -1, 0, -1, 0, -1],
                                             [-1, 0, -1, 0, -1, 0, -1, 0],
                                             [0, -1, 0, -1, 0, -1, 0, -1]])
        self.checker_dask = np.array([[Checker(*from_grid_to_pixel(i, j),
                                               values=self.checker_dask_values[i, j])
                                     if self.checker_dask_values[i, j] != 0 else 0
                                       for j in range(8)] for i in range(8)])

        self.board = np.array([[Cell(*from_grid_to_pixel(i, j), SIZE_CELL, fill_color='white'
                                if (i+j) % 2 != 0 else 'black') for j in range(8)] for i in range(8)])


        self.is_white_step = True
        self.coord_click = []
        self.__not_clear_border = []
        self.__turtle_writer = turtle.Turtle()
        self.__turtle_writer.speed(0)
        self.__turtle_writer.hideturtle()
        self.__with_bot = with_bot
        self.__can_kick_second_time = False
    def available_steps_for_one_checker(self, x, y):  # x, y - grid coordinates.
        val = self.checker_dask_values[x, y]
        checker = self.checker_dask[x, y]
        dask = np.array([[self.checker_dask_values[i, j] if 0 <= j <= 7 and 0 <= i <= 7 else 1000
                          for j in range(-2, 10)] for i in range(-2, 10)])
        avail_pos_for_kick = []
        avail_pos_without_kick = []
        if val == 1 or val == -1:
            for i in range(val, -val, -2*val):
                for j in range(-1, 2, 2):
                    if dask[x+i+2, y+j+2] == 0:
                        avail_pos_without_kick.append([x+i, y+j])
                    if dask[x+i+2, y+j+2] == -val:
                        if dask[x+2*i+2, y+2*j+2] == 0:
                            avail_pos_for_kick.append([x+2*i, y+2*j])
            if checker.is_queen():
                i = -val
                for j in range(-1, 2, 2):
                    if dask[x + i + 2, y + j + 2] == 0:
                        avail_pos_without_kick.append([x + i, y + j])
                    if dask[x + i + 2, y + j + 2] == -val:
                        if dask[x + 2 * i + 2, y + 2 * j + 2] == 0:
                            avail_pos_for_kick.append([x + 2 * i, y + 2 * j])
                #for i in range():
        return (avail_pos_for_kick, True) if len(avail_pos_for_kick)!=0 else (avail_pos_without_kick, False) # true if can kick

    def all_available_steps(self):
        val = 1 if self.is_white_step else -1
        all_available_steps_for_kick = {}
        all_available_steps_without_kick = {}
        is_kick = False
        for i in range(8):
            for j in range(8):
                if self.checker_dask_values[i,j]==val:
                    avail_pos, can_kick = self.available_steps_for_one_checker(i, j)
                    if len(avail_pos) != 0:
                        if can_kick:
                            all_available_steps_for_kick[(i, j)] = avail_pos
                            is_kick = True
                        else:
                            all_available_steps_without_kick[(i,j)] = avail_pos
        return all_available_steps_for_kick if len(all_available_steps_for_kick)!=0 else all_available_steps_without_kick, is_kick

    def draw_available_step(self, x, y):
        steps = self.available_steps_for_one_checker(x, y)[0]
        for coord in steps:
            self.board[coord[0], coord[1]].draw_border(border_color='yellow', pensize=4)
        self.__not_clear_border += steps

    def __show_checkers(self):
        for ln in self.checker_dask:
            for a in ln:
                if isinstance(a, Figure):
                    a.show()

    def __show_board(self):
        for i in self.board:
            for j in i:
                j.show()

    def move(self, pos_before, pos_after):  # grid coord
        x1, y1 = pos_before
        x2, y2 = pos_after

        checker, val = self.delete_checker(x1, y1)
        if (val==1 and x2==7) or (val==-1 and x2==0):
            checker.set_is_queen(True)
        checker.set_position(*from_grid_to_pixel(x2, y2))
        self.checker_dask[x2, y2] = checker

        self.checker_dask_values[x2, y2] = val
        x3, y3 = int((x1+x2)//2), int((y1+y2)//2)
        if abs(x1-x2) >= 2:
            ch, val = self.delete_checker(x3, y3)
            ch.hide()
        playsound('movement_01.mp3')

    def delete_checker(self, x, y):
        checker = deepcopy(self.checker_dask[x, y])
        self.checker_dask[x, y] = 0
        val = self.checker_dask_values[x, y]
        self.checker_dask_values[x, y] = 0
        return checker, val

    def __clear_all_border(self):
        for i in self.__not_clear_border:
            cell = self.board[i[0], i[1]]
            cell.draw_border(cell.border_color)
        self.__not_clear_border.clear()

    def __clear_border(self, x, y):  # grids
        self.board[x, y].draw_border(border_color=self.board[x, y].border_color)

    def save_game(self, file_name):
        checker_dask = deepcopy(self.checker_dask)
        dask = deepcopy(self.board)
        for line in checker_dask:
            for ch in line:
                if isinstance(ch, Checker):
                    ch._visible=False
        for line in dask:
            for cell in line:
                cell._visible=False
        np.savez(file_name, checker_dask_values=self.checker_dask_values, checker_dask = checker_dask, board = dask, is_white_step=np.array([self.is_white_step]))

    def load_game(self, file_name):
        try:
            save = np.load(f'{file_name}.npz', allow_pickle=True)
            turtle.clear()
            self.checker_dask = save['checker_dask']
            self.checker_dask_values = save['checker_dask_values']
            self.board = save['board']
            self.is_white_step = save['is_white_step'][0]
            self.__show_board()
            self.__show_checkers()
            self.step_color_write(-200,200)
        except FileNotFoundError as er:
            print(er.args)

    def step_color_write(self, x, y): # pixel coordinates
        self.__turtle_writer.clear()
        self.__turtle_writer.color('violet')
        self.__turtle_writer.up()
        self.__turtle_writer.setpos(x,y)
        self.__turtle_writer.down()
        if self.is_white_step:
            self.__turtle_writer.write('White step', font=('Arial', 20, 'normal'))
        else:
            self.__turtle_writer.write('Red step', font=('Arial', 20, 'normal'))

    def change_side(self):

        self.is_white_step = not self.is_white_step
        self.coord_click.clear()
        self.__clear_all_border()
        self.step_color_write(-200, 200)

    def __bot_step(self, x=None, y=None):
      #  sleep()
        if x is None and y is None:
            available_step, is_kick = self.all_available_steps()
            pos0 = choice(list(available_step.keys()))
            pos1 = choice(available_step[pos0])
            self.move(pos0, pos1)
        else:
            available_step, is_kick = self.available_steps_for_one_checker(x,y)
            pos1 = choice(available_step)
            self.move((x,y), pos1)
        if is_kick:
             can_kick_after_move = self.available_steps_for_one_checker(pos1[0],pos1[1])[1]
             if can_kick_after_move:
                 self.__bot_step(pos1[0], pos1[1])
             else:
                 self.change_side()
        else:
            self.change_side()

    def is_end_game(self):

        if np.count_nonzero(self.checker_dask_values == 1)==0:
            self.__turtle_writer.clear()
            self.__turtle_writer.write('RED WIN', font=('Arial', 20, 'normal'))
            screen.exitonclick()

        elif np.count_nonzero(self.checker_dask_values == -1)==0:
            self.__turtle_writer.clear()
            self.__turtle_writer.write('WHITE WIN', font=('Arial', 20, 'normal'))
            screen.exitonclick()

    def reset(self):
        turtle.clear()
        handler = GameHandler(with_bot=self.__with_bot)
        self.checker_dask_values = handler.checker_dask_values
        self.checker_dask = handler.checker_dask
        self.board = handler.board
        self.__show_board()
        self.__show_checkers()

    def click(self, x, y):
        color_from_bool = {True: 'white', False: 'red'}
        color_from_val = {1: 'white', -1: 'red'}
        steps = self.all_available_steps()[0]
        a, b = from_pixel_ro_grid(x, y)
        #  next line for understand, that you put on your color button
        self.is_end_game()

        is_check = self.checker_dask_values[a, b] == 1 or self.checker_dask_values[a, b] == -1
        if is_check and color_from_val[self.checker_dask_values[a, b]] != color_from_bool[self.is_white_step]:
            self.__clear_all_border()
            self.coord_click.clear()

            return None

        if len(self.coord_click) == 0 and is_check and (a,b) in steps:
            self.coord_click.append([a, b])

            self.board[a, b].draw_border('green', pensize=4)
            self.draw_available_step(a, b)
            self.__not_clear_border.append([a, b])


        elif len(self.coord_click) == 1:
            a0, b0 = self.coord_click[0]
            pos, is_kick = self.available_steps_for_one_checker(a0, b0)
            if [a, b] in pos:
                self.move([a0, b0], [a, b])

                # self.is_white_step = not self.is_white_step

                self.coord_click.clear()
                self.__clear_all_border()
                can_kick_after_first_kick = self.available_steps_for_one_checker(a,b)[1]

                if is_kick:
                    if can_kick_after_first_kick:

                        self.coord_click.append([a,b])
                        self.board[a, b].draw_border('green', pensize=4)
                        self.__not_clear_border.append([a,b])
                    else:
                        self.change_side()
                        if self.__with_bot:
                            self.__bot_step()
                else:
                    self.change_side()
                    if self.__with_bot:
                        self.__bot_step()
            else:
                self.coord_click.clear()
                self.__clear_all_border()


    def play(self):

        self.__show_board()
        self.__show_checkers()
        self.step_color_write(-200, 200)

        screen.onclick(fun=lambda x, y: self.click(x, y))

    def set_with_bot(self, is_bot):
        self.__with_bot = is_bot
if __name__ == '__main__':

    handler = GameHandler(with_bot=True)

    vs_2_people_button = tkinter.Button(text=" HumanVSHuman ", background="yellow", foreground="red",
             padx="40", pady="8",  font="16", command=lambda : handler.set_with_bot(False))
    vs_bot_button = tkinter.Button(     text="    Vs bot    ", background="yellow", foreground="red",
             padx="40", pady="8",  font="16", command=lambda : handler.set_with_bot(True))
    save_button = tkinter.Button(       text="     Save     ", background="yellow", foreground="red",
             padx="40", pady="8",  font="16", command=lambda : handler.save_game('save'))
    load_button = tkinter.Button(       text="Load last save", background="yellow", foreground="red",
             padx="40", pady="8", font="16", command=lambda : handler.load_game('save'))
    reset_button = tkinter.Button(      text="    Reset    ", background="yellow", foreground="red",
             padx="40", pady="8",  font="16", command=handler.reset)

    distans_betwen_button= 3*HEIGHT/40
    canvas.create_window(WIDTH/4,HEIGHT/10, window=vs_2_people_button)
    canvas.create_window(WIDTH/4,HEIGHT/10+distans_betwen_button, window=vs_bot_button)
    canvas.create_window(WIDTH/4,HEIGHT/10+2*distans_betwen_button, window=reset_button)
    canvas.create_window(WIDTH/4,HEIGHT/10+3*distans_betwen_button, window=save_button)
    canvas.create_window(WIDTH/4,HEIGHT/10+4*distans_betwen_button, window=load_button)

    handler.play()
    screen.mainloop()