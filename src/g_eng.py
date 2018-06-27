# -*- coding: utf-8 -*-
"""
Created on Tue May 22 22:15:01 2018

@author: Mauro
"""

import random
import copy

import snake
import poly
import vec
import bfh

#==============================================================================
# Game Engine class
#   the class manages the game, score, collisions, ...
#==============================================================================

class GameEngine:
    
    def __init__(self):
        # creates a snake, which is positioned in the center and with 4 
        # segments in the -x direction
        self.snake = snake.Snake()

        # create the bounding box, the variable is used to test border
        # collisions
        self.bbox_size = 3
        self.bbox = poly.create_cube4d(vec.V4(0, 0, 0, 0), self.bbox_size * 2, "black")
        
        # add a food hypercube
        self.food = self.initialize_food()
        
        # game state
        self.state = "run"
        
        # score (sum of the cubes)
        self.score = 0
        
        # the list of polygons to be drawn
        self.p_list = []
        self.generate_plist()
    
    def generate_plist(self):
        # reset the polygon list
        self.p_list = []
        
        # add the bbox
        self.p_list.append(self.bbox)
        
        # add the food
        self.p_list.append(self.food)
        
        # add the snake cubes
        for cube in self.snake.p_list:
            self.p_list.append(cube)
    
    def initialize_food(self):
        # give random coordinates for the food
        def generate_rand_point():
            coords = []
            for i in range(4):
                coords.append(random.randrange(-self.bbox_size + 1, self.bbox_size - 1))
            return vec.V4(coords)
        
        invalid_position = True
        while invalid_position:
            food_point = generate_rand_point()
            invalid_position = False
            
            # search if the food collides with the snake
            for p in self.snake.p_list:
                if self.intersect(food_point, p):
                    invalid_position = True
                    break   
                
        return poly.create_cube4d(food_point, 0.9, "blue")
    
    
    def intersect(self, point, polygon):
        # the polygon stores the biggest and smallest vertex in the first 2
        # elements, is dependent on the create cube function tho, it could be
        # solved by the max and min functions
        pbbox_low = polygon.v_list[0]
        pbbox_high = polygon.v_list[1]
        
        for i in range(4):
            if not (point[i] > pbbox_low[i] and point[i] < pbbox_high[i]):
                return False
        return True
    
    def check_collision(self):
        # make the snake move in the next cube
        self.snake.move()
        
        # have to make the bbox bigger by one unit so that the program can 
        # use the intersect function
        ext_bbox = copy.deepcopy(self.bbox)
        ext_bbox.v_list[0] = self.bbox.v_list[0] - vec.V4(1,1,1,1)
        ext_bbox.v_list[1] = self.bbox.v_list[1] + vec.V4(1,1,1,1)
        
        # if is outside of the bbox
        if not self.intersect(self.snake.head_pos, ext_bbox):
            return "out_bbox"
        
        # if the snake got food
        if self.intersect(self.snake.head_pos, self.food):
            return "food"
        
        # if the snake crosses itself
        for p in self.snake.p_list[:-1]:
            if self.intersect(self.snake.head_pos, p):
                return "snake"
            
        # else no collisions
        return "none"
    
    def evaluate_collision(self, collision):
        # decide what to do in case of collision
        
        # out of bounding box or collision with itself will make a game over
        if collision == "out_bbox" or collision == "snake":
            self.state = "game_over"
            
        elif collision == "food":
            self.snake.add_segment()
            self.food = self.initialize_food()
            self.score += 1

    def routine(self):
        # the game routine, checks the collision which will "move" the snake
        # evaluates it and generates the new plist
        c = self.check_collision()
        self.evaluate_collision(c)
        self.generate_plist()
        
    def write_frame(self, filename):
        c_pol = 0
        with open(filename, "wb") as f:
            bf = bfh.BinaryFile(f)
            bf.write("I", len(self.p_list))
            for p in self.p_list:
                p.as_bytes(bf)
                c_pol += 1
        print("written {} polyigons".format(c_pol))
    
    def read_frame(self, filename):
        with open(filename, "rb") as f:
            bf = bfh.BinaryFile(f)
            # read length
            p_list_len = bf.read("I")
            
            self.p_list = [poly.Polygon() for i in range(p_list_len)]
            
            for p in self.p_list:
                p.interpret_bytes(bf)
            
            
if __name__ == "__main__":
    geng = GameEngine()
    geng.routine()

    geng.write_frame("./frame_test.sk4") 
    geng.read_frame("./frame_test.sk4")            