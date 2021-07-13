import pygame
from pygame import mixer
import math

pygame.init()
winW = 600
winH = 400
size = [winW, winH]
display = pygame.display.set_mode(size, 0, 32)

clock = pygame.time.Clock()
FPS = 60

game_over = False

player_idle_frames = []
player_run_frames = []

enemy_idle_frames = []
enemy_run_frames = []



idle_frames_src = [
    'player_animations/idle/idle_0.png',
    'player_animations/idle/idle_1.png',
    'player_animations/idle/idle_2.png'
]

run_frames_src = [
    'player_animations/run/run_0.png',
    'player_animations/run/run_1.png'
]

enemy_idle_frames_src = [
    'enemy_animations/idle/idle_0.png',
    'enemy_animations/idle/idle_1.png',
    'enemy_animations/idle/idle_2.png'
]

enemy_run_frames_src = [
    'enemy_animations/run/run_0.png',
    'enemy_animations/run/run_1.png'
]

enemies = []
track = []

time = 0

for path in idle_frames_src:
    image = pygame.image.load(path)
    image.set_colorkey((255, 255, 255))

    player_idle_frames.append(image)

for path in run_frames_src:
    image = pygame.image.load(path)
    image.set_colorkey((255, 255, 255))

    player_run_frames.append(image)


for path in enemy_idle_frames_src:
    image = pygame.image.load(path)
    image.set_colorkey((255, 255, 255))

    enemy_idle_frames.append(image)

for path in enemy_run_frames_src:
    image = pygame.image.load(path)
    image.set_colorkey((255, 255, 255))

    enemy_run_frames.append(image)


move_right = move_left = False

player_location = [50, 50]
player_y = 0
air_timer = 0

enemy_location = [50, 50]

true_scroll = [0, 0]
display_rend = pygame.Surface((300, 200))

player_rect = pygame.Rect(player_location[0], player_location[1],
                          player_idle_frames[0].get_width(), player_idle_frames[0].get_height())

running = False
player_cur_frame = 0

mixer.music.load('music.wav')
mixer.music.set_volume(1)
mixer.music.play(-1)

def load_map():
    f = open('map.txt', 'r')
    data = f.read()
    f.close()
    data = data.split('\n')
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map

game_map = load_map()
print(game_map)
grass_img = pygame.image.load('grass.png')
dirt_img = pygame.image.load('dirt.png')

background_obj = [[0.25, [120, 10, 70, 400]],
                  [0.25, [280, 30, 40, 400]],
                  [0.5, [30, 40, 40, 400]],
                  [0.5, [130, 90, 100, 400]],
                  [0.5, [300, 80, 120, 400]]]

def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def move(rect, movement, tiles):
    collision_types = {'top':False,'bot':False,'right':False,'left':False}
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)

    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        if movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True

    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bot'] = True
        if movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True

    return rect, collision_types

while True:
    display_rend.fill((145, 245, 255))

    true_scroll[0] += (player_rect.x-true_scroll[0]-152)/20
    true_scroll[1] += (player_rect.y - true_scroll[1] - 106) / 20
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])
    pygame.draw.rect(display_rend, (7, 80, 75), pygame.Rect(0, 120, 300, 80))
    for obj in background_obj:
        obj_rect = pygame.Rect(obj[1][0]-scroll[0]*obj[0],
                               obj[1][1]-scroll[1]*obj[0],
                               obj[1][2], obj[1][3])
        if obj[0] == 0.5:
            pygame.draw.rect(display_rend,(14,222,150), obj_rect)
        else:
            pygame.draw.rect(display_rend, (9, 91, 85), obj_rect)

    tile_rects = []
    y = 0

    for layer in game_map:
        #print(layer)
        x = 0
        for tile in layer:
            #print(x, y)
            if tile == '1':
                display_rend.blit(dirt_img, (x * 16 - scroll[0], y * 16 - scroll[1]))
            if tile == '2':
                display_rend.blit(grass_img, (x * 16 - scroll[0], y * 16 - scroll[1]))
            if tile != '0':
                tile_rects.append(pygame.Rect(x * 16, y * 16, 16, 16))
            x += 1
        y += 1

    player_movement = [0,0]
    if move_left:
        player_movement[0] -= 4
    if move_right:
        player_movement[0] += 4

    player_movement[1] += player_y
    player_y += 0.2
    if player_y > 3:
        player_y = 3


    player_rect, collissons = move(player_rect, player_movement, tile_rects)

    if collissons['left'] or collissons['right']:
        running = False
    else:
        if collissons['left'] == False and player_movement[0] < 0:
            running = True
        else:
            running = False
        if collissons['right'] == False and player_movement[0] > 0:
            running = True

    if player_movement[0] == 0:
        running = False

    if collissons['bot']:
        if air_timer > 5:
            bullet_sound = mixer.Sound('grass_1.wav')
            bullet_sound.play()
        air_timer = 0
        player_y = 0

    else:
        air_timer += 1


    if running == False:
        player_cur_frame += 5/FPS
        if player_cur_frame >= len(player_idle_frames):
            player_cur_frame = 0

        display_rend.blit(player_idle_frames[math.floor(player_cur_frame)], (player_rect.x - scroll[0],
                                     player_rect.y-scroll[1]))



    else:
        player_cur_frame += 10 / FPS
        if player_cur_frame >= len(player_run_frames):
            player_cur_frame = 0
        display_rend.blit(player_run_frames[math.floor(player_cur_frame)], (player_rect.x - scroll[0],
                                                                 player_rect.y - scroll[1]))


    track.append([player_rect.x, player_rect.y, running, math.floor(player_cur_frame)])
    if game_over == False:
        time += 1

    if time % 300 == 0:
        enemies.append(time)

    for enemy_time in enemies:
        enemy_location[0] = track[time-enemy_time][0]
        enemy_location[1] = track[time-enemy_time][1]


        if track[time-enemy_time][2]:
            display_rend.blit(enemy_run_frames[math.floor(track[time-enemy_time][3])], (enemy_location[0] - scroll[0],
                                                                                 enemy_location[1] - scroll[1]))
        else:
            display_rend.blit(enemy_idle_frames[math.floor(track[time - enemy_time][3])], (enemy_location[0] - scroll[0],
                                                                                    enemy_location[1] - scroll[1]))


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT and game_over == False:
                move_right = True
            if event.key == pygame.K_LEFT and game_over == False:
                move_left = True
            if event.key == pygame.K_UP and game_over == False:

                if air_timer < 6:
                    player_y = -5
                    bullet_sound = mixer.Sound('jump.wav')
                    bullet_sound.play()
            if event.key == pygame.K_SPACE and game_over == True:
                game_over = False
                time = 0
                player_location = [50, 50]
                track = []
                enemies = []

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                move_right = False
            if event.key == pygame.K_LEFT:
                move_left = False


    for e_time in enemies:

        e_rect = pygame.rect.Rect(track[time-e_time][0], track[time-e_time][1], 5, 13)
        pl_rect = pygame.rect.Rect(track[time-1][0], track[time-1][1], 5, 13)


        if pl_rect.colliderect(e_rect):
            game_over = True

    display.blit(pygame.transform.scale(display_rend, size), (0, 0))
    font = pygame.font.SysFont(None, 30)
    img = font.render(str(time), True, (255, 255, 255))
    text_rect = img.get_rect(center=(winW / 2, winH * 0.1))
    display.blit(img, text_rect)

    if game_over:
        font = pygame.font.SysFont(None, 30)
        img = font.render('Игра окончена! ', True, (255, 255, 255))
        text_rect = img.get_rect(center=(winW / 2, winH * 0.3))
        display.blit(img, text_rect)

        font = pygame.font.SysFont(None, 30)
        img = font.render('Нажмите [пробел] чтобы начать игру', True, (255, 255, 255))
        text_rect = img.get_rect(center=(winW / 2, winH * 0.5))
        display.blit(img, text_rect)


    pygame.display.update()
    clock.tick(FPS)