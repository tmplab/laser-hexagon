# coding=UTF-8
'''
Etat global (anciennement singleton de la classe GameState + autres VARIABLES nécessaires partout)"
'''

from globalVars import *

# Etat global général
app_path = ""

# anciennement GameState
fs = GAME_FS_GAMEOVER
tdn_crash = 0	# compteur animation crash
pa = None
plyr = None
wall_ring_list = []
lvl = None
idx_lvl = 0
tdn_lvl_next = 0
score = None
spd_gens = None
