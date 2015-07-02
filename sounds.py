# coding=UTF-8
'''
Created on 17 janv. 2015

@author: pclf
'''

import pygame
import os
import random
import gstt
from globalVars import *


def LoadSound(file_name):
	return pygame.mixer.Sound(os.path.join(gstt.app_path, os.path.join("Sounds", file_name)))

def InitSounds():
	global sndfx_click
	global sndfx_crash, sndfx_gameover, sndfx_go
	global sndfx_swap, sndfx_area_resize_smooth, sndfx_area_resize_sudden
	
	sndfx_click = LoadSound("SM_click_row.ogg")

	sndfx_crash = [
		(LoadSound("OH_death.ogg"), 3)
	# Rajouter autres sons et leur probabilité d'apparition	
		]
	sndfx_gameover = [
		(LoadSound("OH_gameOver.ogg"), 3)
		]
	sndfx_go = [
		(LoadSound("OH_go.ogg"), 3)
		]
	sndfx_swap = LoadSound("SM_Clap.ogg")
	sndfx_area_resize_smooth = LoadSound("PorteDoom.ogg")
	sndfx_area_resize_sudden = LoadSound("SM_expand.ogg")

# TODO : routine de choix aléatoire commune
def play_sndfx_crash():
	pygame.mixer.Channel(0).play(sndfx_crash[0][0])

def play_sndfx_gameover():
	pygame.mixer.Channel(1).play(sndfx_gameover[0][0])

def play_sndfx_go():
	pygame.mixer.Channel(1).play(sndfx_go[0][0])

def play_sndfx_swap():
	pygame.mixer.Channel(0).play(sndfx_swap)

def play_sndfx_click():
	pygame.mixer.Channel(0).play(sndfx_click)

def play_sndfx_area_resize(smooth):
	pygame.mixer.Channel(2).play(sndfx_area_resize_smooth if smooth else sndfx_area_resize_sudden)

def LoadBGM(file_name,pm_start_times):
	global start_times, first_play
	
	pygame.mixer_music.load(os.path.join(gstt.app_path, os.path.join("Musics", file_name)))
	start_times = pm_start_times
	first_play = True

def PlayBGM(dimmed = False, first_play = False):
	global start_times
	start_time = start_times[0] if first_play else random.choice(start_times)
	if NO_BGM:
		pygame.mixer_music.stop()
	else:
		pygame.mixer.music.set_volume(0.2 if dimmed else 1.0)
		pygame.mixer_music.play(-1, start_time)

def StopBGM():
	pygame.mixer_music.stop()
