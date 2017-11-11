# coding: utf-8

'''MiniMapTry

pygameお試し作品。
ミニマップ上を動く。

========================================
バージョン1.0(2015-08-12)
    完成。
バージョン1.1(2017-09-22)
    久々に開いてdocとか書いた。
    macに対応(マウス押下で動かせるように)。
    昔を懐かしむ意味もこめてリファクタリングはしない。
'''

import pygame, sys, time
from pygame.locals import *
import os

scr_rect = Rect(0,0,640,480)
gs = 32

def img_load(name):
    return pygame.image.load('01_data' + os.sep + name + '.png').convert_alpha()

def main():
    # 画面を作る
    pygame.init()
    screen = pygame.display.set_mode(scr_rect.size)
    pygame.display.set_caption('Map Sample')
    # マップチップロード
    Chizu.images[0] = img_load('chip0')
    Chizu.images[1] = img_load('chip1')
    Chizu.images[2] = img_load('chip2')
    Chizu.images[3] = img_load('chip3')
    Chizu.images[4] = img_load('chip4')
    Chizu.images[5] = img_load('chip5')
    Chizu.images[6] = img_load('chip6')
    Chizu.images[7] = img_load('chip7')
    Chizu.images[8] = img_load('chip8')
    Chizu.images[9] = img_load('chip9')
    Chizu.images[10] = img_load('chip10')
    # マップデータを読み込む
    chizu = Chizu('chizu2')
    # プレイヤーデータを読み込んで、画像分割、画像の左上の座標取得までする
    player = Player('me', (4, 4))

    clock = pygame.time.Clock()

    while True:
        clock.tick(60)
        # プレイヤーの画像、4枚のどれなのか計算し該当する画像を self.image に格納
        player.update(chizu)
        # 現在のオフセットを計算
        offset = calc_offset(player)
        # オフセットを参考に、画面にマップとプレイヤーを描画
        chizu.draw(screen, offset)
        player.draw(screen, offset)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_F4 and bool(event.mod & KMOD_ALT)):
                sys.exit()

def calc_offset(player):
    offsetx = player.rect.topleft[0] - scr_rect.width // 2
    offsety = player.rect.topleft[1] - scr_rect.height // 2
    return offsetx, offsety

def split_128x32(img):
    img_lis = []
    for foo in range(0, 128, 32):
        surface = pygame.Surface((32,32))
        surface.blit(img, (0,0), (foo,0,32,32))
        surface.set_colorkey(surface.get_at((0,0)), RLEACCEL)
        surface.convert()
        img_lis.append(surface)
    return img_lis

class Chizu:
    # ロードしたイメージを格納
    images = [None] * 20
    def __init__(self, name):
        self.name = name
        self.col = 0
        self.row = 0
        self.chizu_lis = []
        self.load()
    def load(self):
        fi = '01_data' + os.sep + self.name + '.map'
        f = open(fi)
        lines = f.readlines()
        col_str, row_str = lines[0].split()
        self.col, self.row = int(col_str), int(row_str)
        self.default = int(lines[1])
        for line in lines[2:]:
            line = line.rstrip()
            self.chizu_lis.append([int(foo) for foo in line.split()])
        f.close()
    def draw(self, screen, offset):
        # オフセット取得
        offsetx, offsety = offset
        # マップデータ上でどの座標から始まり、どの座標で終わるのか計算
        startx = offsetx // gs
        endx = startx + scr_rect.width // gs + 1
        starty = offsety // gs
        endy = starty + scr_rect.height // gs + 1
        # 対応するマップチップを描画していく
        for x in range(startx, endx):
            for y in range(starty, endy):
                # 座標がマップの0座標より下、あるいは…… self.col - 1 って何だ?
                # -> あー、そっか。マップファイルの行・列は1から9だけど、リスト化したら0から8だから1を引くんだ。
                if x < 0 or y < 0 or x > self.col - 1 or y > self.row - 1:
                    screen.blit(self.images[self.default], (x * gs - offsetx, y * gs - offsety))
                else:
                    screen.blit(self.images[self.chizu_lis[y][x]], (x * gs - offsetx, y * gs - offsety))
    def is_movable(self, x, y):
        if x < 0 or y < 0 or x > self.col - 1 or y > self.row - 1:
            return False
        if self.chizu_lis[y][x] == 0:
            return False
        return True

class Player:
    animcycle = 12
    frame = 0
    # ピクセルベース: フレームあたりの移動ピクセル数
    speed = 4
    def __init__(self, name, position):
        self.name = name
        self.images = split_128x32(img_load(name))
        self.image = self.images[0]
        self.x, self.y = position[0], position[1]
        self.rect = self.image.get_rect(topleft = (self.x * gs, self.y * gs))
        # ピクセルベース: 移動速度と移動判定
        self.vx, self.vy = 0, 0
        self.moving = False
    def update(self, chizu):
        if self.moving == True:
            # 移動中ならマスに収まるまで移動を続ける
            self.rect.move_ip(self.vx, self.vy)
            if self.rect.left % gs == 0 and self.rect.top % gs == 0:
                self.moving = False
                self.x = self.rect.left // gs
                self.y = self.rect.top // gs
        else:

            # macのためマウス操作に対応
            #     左押下:左へ 左右押下:上へ 右押下:右へ スクロールボタン押下:下へ
            mouse_pressed = pygame.mouse.get_pressed()

            # キー入力があったら移動開始
            if (pygame.key.get_pressed()[K_UP]
                    or (mouse_pressed[0] and mouse_pressed[2])):
                if chizu.is_movable(self.x, self.y - 1):
                    self.vx, self.vy = 0, -self.speed
                    self.moving = True
            elif (pygame.key.get_pressed()[K_RIGHT]
                    or mouse_pressed[2]):
                if chizu.is_movable(self.x + 1, self.y):
                    self.vx, self.vy = +self.speed, 0
                    self.moving = True
            elif (pygame.key.get_pressed()[K_DOWN]
                    or mouse_pressed[1]):
                if chizu.is_movable(self.x, self.y + 1):
                    self.vx, self.vy = 0, +self.speed
                    self.moving = True
            elif (pygame.key.get_pressed()[K_LEFT]
                    or mouse_pressed[0]):
                if chizu.is_movable(self.x - 1, self.y):
                    self.vx, self.vy = -self.speed, 0
                    self.moving = True

        self.frame += 1
        self.image = self.images[self.frame // self.animcycle % 4]
    def draw(self, screen, offset):
        offsetx, offsety = offset
        px = self.rect.topleft[0]
        py = self.rect.topleft[1]
        screen.blit(self.image, (px - offsetx, py - offsety))


if __name__ == '__main__':
    main()
