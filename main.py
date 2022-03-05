import random
import time
import queue
from threading import Thread

import keyboard
import numpy as np
import pyautogui
import win32api
import win32con
from pyautogui import *

import keypress
import PathFinder
import ImageRecognition


bot_click_cords = {
    "right": (1020, 580),
    "left": (895, 580),
    "up": (955, 515),
    "down": (955, 645)
}
room_start_cords = {
    "dungeon": (30, 10)
}

class Bot:
    def __init__(self):
        self.bot_cords = [28, 11]
        self.status_t1 = False
        self.bot = None
        self.target_location = None
        self.t1 = Thread(target=self.find_path)

    def move(self, direction):
        if direction == "right":
            self.bot_cords[0] = self.bot_cords[0] + 1
            keypress.press("d")

        if direction == "left":
            self.bot_cords[0] = self.bot_cords[0] - 1
            keypress.press("a")

        if direction == "up":
            self.bot_cords[1] = self.bot_cords[1] - 1
            keypress.press("w")

        if direction == "down":
            self.bot_cords[1] = self.bot_cords[1] + 1
            keypress.press("s")

    def click(self, direction):
        x = bot_click_cords[direction][0]
        y = bot_click_cords[direction][1]

        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)  # Press mouse down
        time.sleep(0.01)  # Wait for the game to register the click
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)  # Release mouse

    def attack(self, repeat):
        cords = self.target_location  # Enemy direction in coordinates
        print(cords)
        for i in range(repeat):
            if cords[0] == 1:
                self.click("left")

            if cords[0] == -1:
                self.click("right")

            if cords[1] == 1:
                self.click("up")

            if cords[1] == -1:
                self.click("down")

            time.sleep(1.2)

    def start_t1(self):
        if self.t1.is_alive():
            pass
        else:
            print("starting t1")
            self.status_t1 = True
            self.t1 = Thread(target=self.find_path)
            self.t1.start()
            print("t1 started")

    def stop_t1(self):
        self.status_t1 = False

    def find_path(self):
        while self.status_t1:
            self.bot = PathFinder.Visualization()
            self.bot.main(True, "Dungeon.txt")
            self.status_t1 = False
        print("t1 stopped")

    def add_start(self, x, y):
        return self.bot.add_start(x, y)

    def add_end(self, x, y):
        return self.bot.add_end(x, y)

    def clear_path_and_load(self, file):
        self.bot.clear_path_and_load(file)

    def start_finding(self):
        return self.bot.start_finding()

    def get_path(self):
        return self.bot.get_path()

    def is_bot(self):
        return self.bot

    def move_bot_to_cords(self, cords):  # cords are path to enemy
        current_x, current_y = cords[0]  # Bot is currently here
        if len(cords) == 1:
            return 0
        if len(cords) == 2:  # If enemy is 1 block away from bot
            self.target_location = (cords[0][0] - cords[1][0], cords[0][1] - cords[1][1])  # Is direction where enemy is
            return 1

        cords.pop(0)  # Remove bot location from move list

        self.target_location = cords.pop(-1)  # Remove target location from cords and add it to target_location
        self.target_location = (cords[-1][0] - self.target_location[0], cords[-1][1] - self.target_location[1])
        print(f"Path: {cords} Target: {self.target_location}")
        for x, y in cords:
            print(f"Moving to {x, y}")
            if x < current_x:
                self.move("left")

            if x > current_x:
                self.move("right")

            if y < current_y:
                self.move("up")

            if y > current_y:
                self.move("down")

            current_x, current_y = x, y
            time.sleep(0.5)
        return 1

    def get_entity_cords(self):
        pixel_cords = ImageRecognition.get_targets()  # Get list of coordinates in pixels
        cords = []
        last = 0, 0
        for x, y in pixel_cords:

            x += 22  # correcting image location to entity location
            y += 76

            x = 960 - x  # calculating distance to bot
            y = 550 - y  # old 580

            x = x / 65  # dividing by game block width to get coordinates
            y = y / 65

            x = round(x)   # Round values
            y = round(y)

            x = self.bot_cords[0] - x  # Calculate real coordinates based on player location
            y = self.bot_cords[1] - y

            if abs(last[0]) + abs(last[1]) < abs(x) + abs(y):
                cords = x, y
            last = x, y

        return cords

    def calculate_direction(self, cords):
        cords = (self.bot_cords[0] - cords[0], self.bot_cords[1] - cords[1])
        return cords


def run_bot():


    bot = Bot()
    bot.start_t1()

    run = True
    time.sleep(5)

    while run:
        finished = False
        if bot.is_bot():
            entity_cords = bot.get_entity_cords()
            bot.add_start(bot.bot_cords[0], bot.bot_cords[1])
            if bot.add_start(bot.bot_cords[0], bot.bot_cords[1]) == 1:
                if entity_cords:
                    if bot.add_end(entity_cords[0], entity_cords[1]) == 1:
                        if bot.start_finding():
                            path = bot.get_path()
                            if path:
                                if bot.move_bot_to_cords(path) == 1:
                                    bot.clear_path_and_load("Dungeon.txt")
                                    entity_cords = bot.get_entity_cords()
                                    if bot.calculate_direction(entity_cords) == entity_cords:
                                        bot.attack(5)
                                        finished = True
                                    else:
                                        bot.move_bot_to_cords(path)

                                else:
                                    bot.clear_path_and_load("Dungeon.txt")

        if finished:
            time.sleep(1)
        time.sleep(0.1)


def run_bot1():
    bot = Bot()
    bot.start_t1()

    run = True
    time.sleep(5)

    while run:
        finished = False
        find_target = True
        find_path = False
        move_to_target = False
        check_enemy = False
        attack = False
        collect = False

        while bot.is_bot():
            while find_target:
                print("Finding target...")
                entity_cords = bot.get_entity_cords()
                if len(entity_cords) > 0:
                    print(f"Found target: {entity_cords} and adding start and end location")
                    print(f"Bot cords: {bot.bot_cords}")
                    if bot.bot_cords[0] == entity_cords[0] and bot.bot_cords[1] == entity_cords[1]:
                        continue
                    if bot.add_start(bot.bot_cords[0], bot.bot_cords[1]) == 1 and bot.add_end(entity_cords[0], entity_cords[1]) == 1:
                        print("Added start")
                        print("Added end")
                        find_path = True
                        find_target = False
                time.sleep(1)

            while find_path:
                print("Finding path to target")
                if bot.start_finding():
                    path = bot.get_path()
                    print(f"Found path: {path}")
                    if path:
                        move_to_target = True
                        find_path = False
                time.sleep(1)

            while move_to_target:
                print(f"move_to_target {path}")
                if bot.move_bot_to_cords(path) == 1:
                    bot.clear_path_and_load("Dungeon.txt")
                    check_enemy = True
                    move_to_target = False
                else:
                    find_target = True
                    move_to_target = False

            while check_enemy:
                print("Checking if enemy is still there")
                entity_cords = bot.get_entity_cords()
                print(f"Got cords {entity_cords}")
                if bot.calculate_direction(entity_cords) == bot.target_location:
                    print("Enemy is still there")
                    attack = True
                    check_enemy = False
                else:
                    print("Enemy is not there")
                    attack = False
                    collect = False
                    check_enemy = False

                    find_target = True

            while attack:
                print("Attacking enemy")
                bot.attack(4)
                finished = True
                attack = False

            while collect:
                pass

            if finished:
                print("Finished cycle")
                print("Waiting...")

                finished = False
                find_target = True

                time.sleep(2)

            print("Waiting...")
            time.sleep(1)




if __name__ == '__main__':
    run_bot1()
