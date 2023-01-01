import socket
import pygame


FPS = 144
WIDTH, HEIGHT = 800, 700
COLOURS = {'0': (255, 255, 0), '1': (255, 0, 0), '2': (0, 255, 0),
           '3': (0, 255, 255), '4': (128, 0, 128), '5': (0, 128, 0),
           '6': (0, 128, 128), '7': (0, 250, 154), '8': (148, 0, 211),
           '9': (30, 144, 255), '10': (238, 130, 238), '11': (255, 165, 0)}


class Player:
    def __init__(self, name, x, y, r, colour):
        self.name = name
        self.x = x
        self.y = y
        self.r = r
        self.colour = colour
        self.speed = 3

    def __str__(self):
        return self.name + ":" + str(self.x) + ":" + str(self.y) + ":" + str(self.r)

    def update(self, name, x, y, r, colour):
        self.name = name
        self.x = x
        self.y = y
        self.r = r
        self.colour = colour

    def draw(self):
        if self.r != 0:
            pygame.draw.circle(screen, COLOURS[self.colour], (self.x, self.y), self.r)
            write_name(self.x, self.y, self.r, self.name)
            score = score_player.render(f"Score = {self.r}", True, "white")
            screen.blit(score, (0, 0))

    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and self.x - self.speed - self.r >= 0:
            self.x -= self.speed

        if keys[pygame.K_RIGHT] and self.x + self.r * 2 / 2 < WIDTH:
            self.x += self.speed

        if keys[pygame.K_UP] and self.y - self.speed - self.r >= 0:
            self.y -= self.speed

        if keys[pygame.K_DOWN] and self.y + self.r * 2 / 2 < HEIGHT:
            self.y += self.speed


def write_name(x, y, r, name):
    font = pygame.font.SysFont("comicsans", r - 25)
    text = font.render(name, True, (0, 0, 0))
    rect = text.get_rect(center=(x, y))
    screen.blit(text, rect)


# отбор игроков и мобов из строки
def selection(string):
    left_border = None
    for i in range(len(string)):
        if string[i] == '<':
            left_border = i
        if string[i] == '>' and left_border is not None:
            right_border = i
            result = string[left_border + 1:right_border]
            return result


def draw_enemies(data):
    for i in range(len(data)):
        j = data[i].split(':')
        if len(j) == 5:
            n = j[0]
            x = int(j[1])
            y = int(j[2])
            r = int(j[3])
            c = COLOURS[j[4]]
            pygame.draw.circle(screen, c, (x, y), r)
            write_name(x, y, r, n)
        else:
            x = int(j[0])
            y = int(j[1])
            r = int(j[2])
            c = COLOURS[j[3]]
            pygame.draw.circle(screen, c, (x, y), r)


# новое состояние игрового поля
def redrawWindow(MyPlayer, players, foods):
    MyPlayer.move()
    screen.blit(bg, (0, 0))
    MyPlayer.draw()
    draw_enemies(players + foods)
    pygame.display.flip()


def main():
    my_name = input("Введите имя: ")

    # создание сокета клиента и подключение к серверу
    HOST = socket.gethostbyname(socket.gethostname())
    PORT = 3510
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    client_socket.connect((HOST, PORT))

    # отправляем серверу свой ник
    client_socket.send(('.' + my_name + '.').encode())

    # получение данных об игроке
    data = client_socket.recv(1024).decode()
    data = data.split(":")

    # создание игрока по полученным данным
    MyPlayer = Player(data[0], int(data[1]), int(data[2]), int(data[3]), data[4])

    clock = pygame.time.Clock()
    running = True
    while running:
        clock.tick(FPS)

        # отправка данных клиента на сервер
        client_socket.send(str(MyPlayer).encode())

        # получение данных с сервера
        try:
            data = client_socket.recv(2 ** 20)
            data = data.decode()
            data = data.split(";")
        except:
            pass

        # обработка данных с сервера
        players = selection(data[0]).split(',')
        foods = selection(data[1]).split(',')

        for player in players:
            player = player.split(":")
            if player[0] == MyPlayer.name:
                MyPlayer.update(player[0], int(player[1]), int(player[2]), int(player[3]), player[4])

        draw_enemies(players + foods)
        redrawWindow(MyPlayer, players, foods)

        # обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()

# создание окна игры
pygame.font.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")
bg = pygame.image.load("background.jpg")
score_player = pygame.font.SysFont("comicsans", 25)

if __name__ == "__main__":
    main()
