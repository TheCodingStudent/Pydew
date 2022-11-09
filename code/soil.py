import pygame
from settings import *
from pytmx.util_pygame import load_pygame
from support import *
from random import choice


class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['soil']


class WaterTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['soil water']


class SoilLayer:
    def __init__(self, all_sprites):
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()

        self.soil_surf = pygame.image.load('../graphics/soil/o.png').convert_alpha()
        self.soil_surfs = import_folder_dict('../graphics/soil/')
        self.water_surfs = import_folder('../graphics/soil_water')
        self.create_soil_grid()
        self.create_hits_rects()

    def create_soil_grid(self):
        ground = pygame.image.load('../graphics/world/ground.png')
        h_tiles = ground.get_width() // TILE_SIZE
        v_tiles = ground.get_height() // TILE_SIZE

        self.grid = [
            [[] for col in range(h_tiles)]
            for row in range(v_tiles)
        ]

        for x, y, _ in load_pygame('../data/map.tmx').get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append('F')
    
    def create_hits_rects(self):
        self.hit_rects = []
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'F' in cell:
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.hit_rects.append(rect)
    
    def get_hit(self, point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE
                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()
                    if self.raining:
                        self.water_all()
    
    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell:
                    tile_type = ''
                    if 'X' in self.grid[index_row-1][index_col]: tile_type += 't'
                    if 'X' in self.grid[index_row+1][index_col]: tile_type += 'b'
                    if 'X' in row[index_col+1]: tile_type += 'r'
                    if 'X' in row[index_col-1]: tile_type += 'l'
                    tile_type = 'o' if not tile_type else tile_type

                    SoilTile(
                        (index_col * TILE_SIZE, index_row * TILE_SIZE),
                        self.soil_surfs[tile_type], [self.all_sprites, self.soil_sprites]
                    )
    
    def water(self, target_pos):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                self.grid[y][x].append('W')

                WaterTile(
                    soil_sprite.rect.topleft,
                    choice(self.water_surfs), [self.all_sprites, self.water_sprites]
                )
    
    def remove_water(self):
        for sprite in self.water_sprites.sprites():
            sprite.kill()
        
        for row in self.grid:
            for cell in row:
                if 'W' in cell: cell.remove('W')
    
    def water_all(self):
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell and 'W' not in cell:
                    cell.append('W')
                    WaterTile(
                        (index_col * TILE_SIZE, index_row * TILE_SIZE),
                        choice(self.water_surfs),
                        [self.all_sprites, self.water_sprites]
                    )