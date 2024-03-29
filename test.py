import pygame
import os
import sys
import random

pygame.init()
pygame.mixer.init()
pygame.display.set_caption('Pygame')
size = WIDTH, HEIGHT = 1600, 900
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
FPS = 60
clock = pygame.time.Clock()
stay_event = pygame.USEREVENT + 1
pygame.time.set_timer(stay_event, 50)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)

    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_music(name, colorkey=None):
    fullname = os.path.join('music', name)

    if not os.path.isfile(fullname):
        print(f"Файл с музыкой '{fullname}' не найден")
        sys.exit()

    pygame.mixer.music.load(fullname)


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    fon = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    image_start = pygame.transform.scale(load_image("start.png"), (300, 150))
    start_rect = image_start.get_rect()
    start_rect.center = (800, 400)
    screen.blit(image_start, (650, 320))
    image_settings = pygame.transform.scale(load_image('settings.png'), (300, 150))
    settings_rect = image_settings.get_rect()
    settings_rect.center = (800, 600)
    screen.blit(image_settings, (650, 500))
    image_title = pygame.transform.scale(load_image('title.png'), (1000, 150))
    screen.blit(image_title, (310, 50))
    volume = 0.5
    count = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_EQUALS:
                    volume = min(1.0, volume + 0.1)
                    pygame.mixer.music.set_volume(volume)
                elif event.key == pygame.K_MINUS:
                    volume = max(0.0, volume - 0.1)
                    pygame.mixer.music.set_volume(volume)
                elif event.key == pygame.K_p:
                    if count == 0:
                        pygame.mixer.music.pause()
                        count += 1
                    else:
                        pygame.mixer.music.unpause()
                        count -= 1
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_rect.collidepoint(mouse_pos):
                    return  # начинаем игру
                elif settings_rect.collidepoint(mouse_pos):
                    settings()
        pygame.display.flip()
        clock.tick(FPS)


def settings():
    running = True
    volume = 0.5
    count = 0
    font = pygame.font.Font(None, 30)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    if count == 0:
                        pygame.mixer.music.pause()
                        count += 1
                    else:
                        pygame.mixer.music.unpause()
                        count -= 1
        keys = pygame.key.get_pressed()
        if keys[pygame.K_EQUALS]:
            volume = min(1.0, volume + 0.01)
            pygame.mixer.music.set_volume(volume)
        elif keys[pygame.K_MINUS]:
            volume = max(0.0, volume - 0.01)
            pygame.mixer.music.set_volume(volume)

        volume_text = font.render(f'Громкость: {int(volume * 100)}%', True, (255, 165, 0))
        lines = [
            'Правила: "=/+" - увеличение громкости, "-" - уменьшение.',
            'Чтобы остановить/производить мелодию нужно нажать "P"(англ.)',
            '------------------------------------------------------------',
            'Чтобы пройти игру вам нужно спасти принцессу из замка,',
            'преодолевая разные трудности на своем пути.',
            'Но можете не переживать, проиграть нельзя, потому что',
            'властелин времени похитил почти все время у Бога этой игры,',
            'и поэтому он не успел создать монстров, чтобы играть было еще',
            'увлекательнее!'
        ]
        screen.fill((0, 0, 0))  # Черный фон
        screen.blit(volume_text, (10, screen.get_height() - 30))  # Текст громкости в левом нижнем углу
        otstup = 50
        for line in lines:
            text = font.render(line, True, (255, 165, 0))
            screen.blit(text,
                        (screen.get_width() // 2 - text.get_width() // 2, screen.get_height() // 2 - 300 + otstup))
            otstup += 50

        pygame.display.flip()
        clock.tick(30)


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_image = {
    'wall': load_image('wall1.bmp'),
    'grass': (load_image('grass1.png'), load_image('grass2.bmp')),
    'plants': (load_image('flower1.png'), load_image('flower2.png'), load_image('flower3.png'), load_image('tree.png'),
               load_image('kust.png')),
    'tower': load_image('tower.png'),
    'vorota': load_image('vorota.png'),
    'princess': load_image('tower_with_princess.jpg')
}
tile_width = tile_height = 50
tile_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()
princess_group = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tile_group, all_sprites)
        self.image = tile_image[tile_type]
        if tile_type == 'wall' or tile_type == 'tower':
            wall_group.add(self)
            self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        elif tile_type == 'vorota':
            wall_group.add(self)
            self.image = tile_image[tile_type]
            self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        elif tile_type == 'grass':
            r = random.randint(0, 1)
            self.image = tile_image[tile_type][r]
            self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        elif tile_type == 'plants':
            rand = random.randint(0, 9)
            if rand < 5:
                self.image = tile_image[tile_type][rand]
                if rand != 4 and rand != 3:
                    self.rect = self.image.get_rect().move(tile_width * pos_x + 20, tile_height * pos_y + 20)
                else:
                    self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
            else:
                r = random.randint(0, 1)
                self.image = tile_image['grass'][r]
                self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        elif tile_type == 'princess':
            princess_group.add(self)
            self.image = tile_image[tile_type]
            self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


player_group = pygame.sprite.Group()
images_stay = [load_image('HeroStop1.png'), load_image('HeroStop2.png'), load_image('HeroStop3.png'),
               load_image('HeroStop4.png'), load_image('HeroStop5.png'), load_image('HeroStop6.png')]
images_move_right = [load_image('HeroMoveRight1.png'), load_image('HeroMoveRight2.png')]


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.images_stay = images_stay
        self.current_image = 0
        self.image = self.images_stay[self.current_image]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    def update(self):
        self.current_image = (self.current_image + 1) % len(self.images_stay)
        self.image = self.images_stay[self.current_image]


player = None


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('grass', x, y)
                Tile('plants', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == 'W':
                Tile('wall', x, y)
                Tile('tower', x, y)
            elif level[y][x] == '@':
                Tile('grass', x, y)
                new_player = Player(x, y)
            elif level[y][x] == 'O':
                Tile('wall', x, y)
                Tile('vorota', x, y)
            elif level[y][x] == 'Q':
                Tile('grass', x, y)
                Tile('princess', x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


def win():
    font = pygame.font.Font(None, 40)
    lines = ['{----------------------}',
             'Поздравляем! Рыцарь спас принцессу!',
             'Рыцарь и принцесса объявили народу свою любовь',
             'и свадьба была у них самая прекрасная из распрекрасных.',
             'Они жили долго и счастливо, заботясь друг о друге,',
             'помогая крестьянам и защищая свое королевство от любых опасностей.',
             'Их история стала легендой, передаваемой из поколения в поколение,',
             'напоминая всем о том, что любовь, доброта и храбрость всегда побеждают!',
             '{----------------------}'
             ]
    screen.fill((0, 0, 0))  # Черный фон
    otstup = 50
    for line in lines:
        text = font.render(line, True, (255, 165, 0))
        screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, screen.get_height() // 2 - 300 + otstup))
        otstup += 50

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.flip()

    terminate()


if __name__ == '__main__':
    mouse_image = load_image('arrow.png')
    mouse = pygame.sprite.Sprite()
    mouse.image = mouse_image
    mouse.rect = mouse_image.get_rect()
    all_sprites.add(mouse)
    pygame.mouse.set_visible(True)
    load_music('music_fon.mp3')
    pygame.mixer.music.play(-1)

    volume = 0.5
    count = 0

    player, level_x, level_y = generate_level(load_level('level.txt'))
    camera = Camera()
    start_screen()
    running = True
    superman = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    if count == 0:
                        pygame.mixer.music.pause()
                        count += 1
                    else:
                        pygame.mixer.music.unpause()
                        count -= 1

            if event.type == pygame.MOUSEMOTION:
                mouse.rect.topleft = event.pos

        keys = pygame.key.get_pressed()

        if keys[pygame.K_EQUALS]:
            volume = min(1.0, volume + 0.01)
            pygame.mixer.music.set_volume(volume)
        elif keys[pygame.K_MINUS]:
            volume = max(0.0, volume - 0.01)
            pygame.mixer.music.set_volume(volume)

        if player is not None:
            if pygame.sprite.spritecollideany(player, wall_group) is None:
                if keys[pygame.K_LEFT]:
                    if keys[pygame.K_UP]:
                        player.rect.top -= 5
                        if pygame.sprite.spritecollideany(player, wall_group):
                            player.rect.top += 5
                    elif keys[pygame.K_DOWN]:
                        player.rect.top += 5
                        if pygame.sprite.spritecollideany(player, wall_group):
                            player.rect.top -= 5
                    player.rect.right -= 5
                    if pygame.sprite.spritecollideany(player, wall_group):
                        player.rect.right += 5
                elif keys[pygame.K_RIGHT]:
                    if keys[pygame.K_UP]:
                        player.rect.top -= 5
                        if pygame.sprite.spritecollideany(player, wall_group):
                            player.rect.top += 5
                    elif keys[pygame.K_DOWN]:
                        player.rect.top += 5
                        if pygame.sprite.spritecollideany(player, wall_group):
                            player.rect.top -= 5
                    player.rect.right += 5
                    if pygame.sprite.spritecollideany(player, wall_group):
                        player.rect.right -= 5
                elif keys[pygame.K_UP]:
                    if keys[pygame.K_LEFT]:
                        player.rect.right -= 5
                        if pygame.sprite.spritecollideany(player, wall_group):
                            player.rect.right += 5
                    elif keys[pygame.K_RIGHT]:
                        player.rect.right += 5
                        if pygame.sprite.spritecollideany(player, wall_group):
                            player.rect.right -= 5
                    player.rect.top -= 5
                    if pygame.sprite.spritecollideany(player, wall_group):
                        player.rect.top += 5
                elif keys[pygame.K_DOWN]:
                    if keys[pygame.K_LEFT]:
                        player.rect.right -= 5
                        if pygame.sprite.spritecollideany(player, wall_group):
                            player.rect.right += 5
                    elif keys[pygame.K_RIGHT]:
                        player.rect.right += 5
                        if pygame.sprite.spritecollideany(player, wall_group):
                            player.rect.right -= 5
                    player.rect.top += 5
                    if pygame.sprite.spritecollideany(player, wall_group):
                        player.rect.top -= 5
                if pygame.sprite.spritecollideany(player, princess_group):
                    win()

        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)

        fon_game = pygame.transform.scale(load_image('fon_game.jpg'), (WIDTH, HEIGHT))
        screen.blit(fon_game, (0, 0))
        all_sprites.draw(screen)
        all_sprites.update()
        tile_group.draw(screen)
        player_group.draw(screen)
        player_group.update()

        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()
