import pygame as pg
import sqlite3 as sql


class RtfClicker:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.display_size = (800, 600)
        self.screen = pg.display.set_mode(self.display_size)
        pg.display.set_caption("РтФ-коин")
        self.clock = pg.time.Clock()
        self.background = pg.image.load("assets/background.png").convert()
        self.background = pg.transform.scale(self.background, self.display_size)
        self.buttons = {
            "main_bg": SpriteButton("assets/main_btn_circle.png", x=self.screen.get_width() // 2 - 150,
                                    y=self.screen.get_height() // 2 - 150, width=300, height=300),
            "main": SpriteButton("assets/obabkov.png", x=self.screen.get_width() // 2 - 100,
                                 y=self.screen.get_height() // 2 - 100, width=200, height=200,
                                 func=self.button_action)
        }
        self.sprites = {
            "main_btn_circle": pg.image.load("assets/main_btn_circle.png").convert(),
            "brain_count_icon": pg.image.load("assets/brain.png").convert_alpha(),
            "energy_icon": pg.image.load("assets/energy.png").convert_alpha()
        }
        self.big_font = pg.font.SysFont("Inter", 65)

        self.db_conn = sql.connect('userdata.db')
        self.db_cursor = self.db_conn.cursor()
        try:
            userdata = ''
            for field in self.db_cursor.execute('''SELECT * FROM UserData''').fetchone():
                userdata += f'{str(field)} | '
            print(f'Userdata: {userdata}')
        except sql.OperationalError:
            self.db_create_tables()

        self.balance = self.fetch_userdata('Balance')

        self.time_since_autosave = 0

    def button_action(self):
        print("Button pressed!")
        self.balance += 1

    def db_create_tables(self):
        self.db_cursor.execute('''CREATE TABLE "UserData" (
        	"ID"	INTEGER,
        	"Username"	TEXT NOT NULL,
        	"Balance"	REAL,
        	PRIMARY KEY("ID")
        )''')

    def fetch_userdata(self, field):
        return self.db_cursor.execute(f'''SELECT {field} from UserData''').fetchone()[0]

    def update_userdata(self, field, value):
        self.db_cursor.execute(f'''UPDATE UserData SET {field} = {value}''')



    def run(self):
        while True:
            active_btn = None
            for button in self.buttons.values():
                if button.rect.collidepoint(pg.mouse.get_pos()):
                    button.hover(self.screen)
                    active_btn = button
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    pg.quit()
                    exit()
                if e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                    if active_btn is not None and active_btn.rect.collidepoint(e.pos):
                        active_btn.pressed()

            self.screen.blit(self.background, (0, 0))

            for button in self.buttons.values():
                button.draw(self.screen)
            self.screen.blit(self.big_font.render(str(int(self.balance)), True, (255, 255, 255)), (self.display_size[0] // 2, 80))
            self.screen.blit(pg.transform.scale(self.sprites["brain_count_icon"], (60, 60)), (self.display_size[0]//2 - 80, 70))
            pg.display.flip()

            self.clock.tick(60)


class Button:
    def __init__(self, width=100, height=50, x=0, y=0, can_hover=True, color=pg.Color(100, 100, 100),
                 hover_color=pg.Color(200, 200, 200), func=None):
        self.width = width
        self.height = height
        self.pos = (x, y)
        self.can_hover = can_hover
        self.color = color
        self.hover_color = hover_color
        self.func = func  # Store the function
        self.rect = pg.Rect(*self.pos, self.width, self.height)

    def draw(self, surface):
        pg.draw.rect(surface, self.color, self.rect)

    def hover(self, surface):
        if self.can_hover:
            pg.draw.rect(surface, self.hover_color, self.rect)

    def pressed(self):
        if self.func:  # Call the function if it exists
            self.func()


class SpriteButton(Button):
    def __init__(self, src, image_offset=(0, 0), image_scale=1, transparent_base=True, **kwargs):
        super().__init__(**kwargs)
        self.transparent_base = transparent_base
        self.img = pg.image.load(src)
        self.img.convert()

        # Calculate the new size of the image
        img_width, img_height = self.img.get_size()
        aspect_ratio = img_width / img_height

        if self.width / self.height < aspect_ratio:
            new_width = self.width
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = self.height
            new_width = int(new_height * aspect_ratio)

        self.img = pg.transform.scale(self.img, (new_width * image_scale, new_height * image_scale))
        self.img_rect = self.img.get_rect()

        print(self.img_rect.center)
        print(image_offset)
        self.img_rect.center = sum_coords(self.rect.center, image_offset)
        print(self.img_rect.center)

    def draw(self, surface):
        if not self.transparent_base:
            pg.draw.rect(surface, self.color, self.rect)
        surface.blit(self.img, self.img_rect)



def sum_coords(xy1: tuple, xy2: tuple):
    return tuple(map(sum, zip(xy1, xy2)))


if __name__ == '__main__':
    game = RtfClicker()
    game.run()
