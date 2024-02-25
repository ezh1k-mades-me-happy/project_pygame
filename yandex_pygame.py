import pygame
import os
import sys

pygame.init()
pygame.mixer.init()
pygame.display.set_caption('Pygame')
size = WIDTH, HEIGHT = 1600, 900
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
FPS = 60
clock = pygame.time.Clock()


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

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
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
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_EQUALS:
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

        volume_text = font.render(f'Громкость: {int(volume * 100)}%', True, (255, 165, 0))
        rules = font.render('Правила: равно - увеличение громкости, минус - уменьшение. Чтобы остановить/производить мелодию нужно нажать "P"(англ.)', True, (255, 165, 0))

        screen.fill((0, 0, 0))  # Черный фон
        screen.blit(volume_text, (10, screen.get_height() - 30))  # Текст громкости в левом нижнем углу
        screen.blit(rules, (
        screen.get_width() // 2 - rules.get_width() // 2, screen.get_height() // 2))  # Центрированный текст правил

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
    'wall': load_image('wood.png'),
    'empty': load_image('grass1.png'),
}
player_image = load_image('mar.png')
tile_width = tile_height = 50
tile_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tile_group, all_sprites)
        self.image = tile_image[tile_type]
        if tile_type == 'wall':
            wall_group.add(self)
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


player_group = pygame.sprite.Group()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)


player = None


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
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


if __name__ == '__main__':
    mouse_image = load_image('arrow.png')
    mouse = pygame.sprite.Sprite()
    mouse.image = mouse_image
    mouse.rect = mouse_image.get_rect()
    all_sprites.add(mouse)
    pygame.mouse.set_visible(True)
    load_music('music_fon.mp3')
    pygame.mixer.music.play(-1)

    player, level_x, level_y = generate_level(load_level('level.txt'))
    camera = Camera()
    start_screen()
    running = True
    superman = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if player is not None:
                if pygame.sprite.spritecollideany(player, wall_group) is None:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                        player.rect.top += 50
                        if pygame.sprite.spritecollideany(player, wall_group):
                            player.rect.top -= 50
                    if event.type == pygame.KEYUP and event.key == pygame.K_UP:
                        player.rect.top -= 50
                        if pygame.sprite.spritecollideany(player, wall_group):
                            player.rect.top += 50
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                        player.rect.right -= 50
                        if pygame.sprite.spritecollideany(player, wall_group):
                            player.rect.right += 50
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                        player.rect.right += 50
                        if pygame.sprite.spritecollideany(player, wall_group):
                            player.rect.right -= 50
            if event.type == pygame.MOUSEMOTION:
                mouse.rect.topleft = event.pos
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)

        fon_game = pygame.transform.scale(load_image('fon_game.jpg'), (WIDTH, HEIGHT))
        screen.blit(fon_game, (0, 0))
        all_sprites.draw(screen)
        all_sprites.update()
        tile_group.draw(screen)
        player_group.draw(screen)

        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()
