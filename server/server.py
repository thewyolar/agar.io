import socket
import random


WIDTH, HEIGHT = 800, 700
PLAYER_SIZE = 40
FOOD_SIZE, FOOD_QUANTITY = 10, 50
COLOURS = {'0': (255, 255, 0), '1': (255, 0, 0), '2': (0, 255, 0),
           '3': (0, 255, 255), '4': (128, 0, 128), '5': (0, 128, 0),
           '6': (0, 128, 128), '7': (0, 250, 154), '8': (148, 0, 211),
           '9': (30, 144, 255), '10': (238, 130, 238), '11': (255, 165, 0)}


class Food:
    def __init__(self, x, y, r, colour):
        self.x = x
        self.y = y
        self.r = r
        self.colour = colour

    # Возвращает формальное представление объекта
    def __str__(self):
        return str(self.x) + ":" + str(self.y) + ":" + str(self.r) + ":" + str(self.colour)


class Player:
    def __init__(self, conn, addr, x, y, r, colour):
        self.conn = conn
        self.addr = addr
        self.name = ''
        self.x = x
        self.y = y
        self.r = r
        self.colour = colour


    def __str__(self):
        return self.name + ":" + str(self.x) + ":" + str(self.y) + ":" + str(self.r) + ":" + self.colour


class Server:
    def __init__(self):
        self.HOST = socket.gethostbyname(socket.gethostname())
        self.PORT = 3510
        self.server_socket = None
        self.players = []
        self.foods = []
        print("Init server")

    def start(self):
        # создание сокета на сервере
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.setblocking(0)
        self.listen()

    def listen(self):
        self.server_socket.listen(5)
        print("listening")

        # создание стартового набора еды
        self.foods = [Food(random.randint(50, WIDTH - 50),
                                 random.randint(50, HEIGHT - 50),
                                 FOOD_SIZE,
                                 str(random.randint(0, 11)))
                         for _ in range(FOOD_QUANTITY)]

        while True:
            # проверка, есть ли желающие войти в игру
            try:
                new_socket, addr = self.server_socket.accept()
                print('Connected', addr)
                new_socket.setblocking(0)

                location = random.choice(self.foods)
                new_player = Player(new_socket, addr,
                                    location.x,
                                    location.y,
                                    PLAYER_SIZE,
                                    str(random.randint(0, 11)))

                self.foods.remove(location)
                self.players.append(new_player)

            except:
                pass

            # дополняем список еды
            new_foods = [Food(random.randint(0, WIDTH),
                                    random.randint(0, HEIGHT),
                                    FOOD_SIZE,
                                    str(random.randint(0, 11)))
                            for _ in range(FOOD_QUANTITY - len(self.foods))]

            self.foods = self.foods + new_foods

            # получение данных с клиента
            for player in self.players:
                try:
                    data = player.conn.recv(1024)
                    data = data.decode()

                    # пришло имя игрока
                    if data[0] == '.' and data[-1] == '.':
                        data = data[1:-1].split(' ')
                        player.name = data[0]
                        player.conn.send((str(player)).encode())
                    else:
                        data = data.split(':')
                        player.name = data[0]
                        player.x = int(data[1])
                        player.y = int(data[2])
                        player.r = int(data[3])
                        player.colour = data[4]
                except:
                    pass


            # процесс столкновения
            for player in self.players:
                for food in self.foods:
                    distance_x = food.x - player.x
                    distance_y = food.y - player.y

                    if (distance_x ** 2 + distance_y ** 2) ** 0.5 <= player.r:
                        player.r = round((player.r ** 2 + food.r ** 2) ** 0.5)
                        food.r = 0

                for other_player in self.players:
                    distance_x = other_player.x - player.x
                    distance_y = other_player.y - player.y

                    if (distance_x ** 2 + distance_y ** 2) ** 0.5 <= player.r and player.r > 1.1 * other_player.r:
                        player.r = round((player.r ** 2 + other_player.r ** 2) ** 0.5)
                        other_player.r = 0


            # создание ответа каждому игроку о всех игроков и всей еде
            players = '<' + (','.join(map(str, self.players))) + ">"
            foods = ';' + "<" + (','.join(map(str, self.foods))) + '>'
            answer = players + foods

            # отправка созданной строки
            for player in self.players:
                if player.conn is not None:
                    try:
                        player.conn.send(answer.encode())
                    except:
                        pass

            # чистим список от съеденных игроков
            for player in self.players:
                if player.r == 0:
                    player.conn.close()
                    self.players.remove(player)

            # чистим список от съеденной еды
            for i in self.foods:
                if i.r == 0:
                    self.foods.remove(i)

        self.server_socket.close()


if __name__ == "__main__":
    c = Server()
    c.start()
