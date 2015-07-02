# coding=UTF-8
import pygame

# STDLIB
import math
import random
import itertools
import sys
import os
import thread
import time
import random
import weakref

from globalVars import *
import gstt
import playarea
import player
import score
import logo
import sounds

import frame
from vectors import Vector2D
import renderer
import dac
import levels
from gstt import idx_lvl


def CrashPlayer(crash_type):
	gstt.fs = GAME_FS_GAMEOVER
	gstt.tdn_crash = TDN_CRASH
	gstt.plyr.crash_type = crash_type
	sounds.play_sndfx_crash()
	sounds.play_sndfx_gameover()
	sounds.StopBGM()

def StartPlaying(first_time = False):
	gstt.score.Reset()
	gstt.fs = GAME_FS_PLAY
	gstt.tdn_crash = 0
	gstt.plyr.crash_type = 0
	gstt.wall_ring_list = []
	gstt.pa.CancelSideChange()
	gstt.lvl.Start(first_time)
	sounds.play_sndfx_go()
	sounds.PlayBGM(False,first_time)

def ChangeLevel(dlvl):
	gstt.idx_lvl = (gstt.idx_lvl + dlvl) % len(lvls)
	SelectLevel()
	StartPreview()
	sounds.play_sndfx_click()


def SelectLevel():
	gstt.lvl = lvls[gstt.idx_lvl]
	gstt.lvl.Init()

def StartPreview():
	gstt.wall_ring_list = []
	gstt.lvl.Start(True)
	sounds.PlayBGM(True,True)
	

def GenerateLevel():
	# Immobilisation génération si la scène se réarrange
	if gstt.pa.rearrange_sides == 0:
		if gstt.tdn_lvl_next <= 0:
			gstt.tdn_lvl_next = gstt.lvl.gen.next()
		gstt.tdn_lvl_next -= 1

def PurgeWallRingList():
	gstt.wall_ring_list = [wr for wr in gstt.wall_ring_list if not wr.IsFullyInBH()]
	
def MoveSpdGens():
	for spd_gen in gstt.spd_gens:
		spd_gen.Move()


def AnimateCrash():
	
	def AuxCrashOffsetValue(offset_max):
		return random.uniform(-offset_max,offset_max)
	
	# SECOUSSE DU CRASH
	offset_max = CRASH_SHAKE_MAX * gstt.tdn_crash / TDN_CRASH
	gstt.pa.xy_offset = Vector2D(AuxCrashOffsetValue(offset_max),AuxCrashOffsetValue(offset_max))
	
	# Explosion et feu
	if gstt.tdn_crash == TDN_CRASH - 30:
		gstt.plyr.Explode()
	
	if gstt.tdn_crash:
		gstt.tdn_crash -= 1

	
def dac_thread():
#	global PLAYERS, DRAW

	while True:
		try:

			d = dac.DAC(dac.find_first_dac())
			d.play_stream(laser)
#			simulator.play_stream(ps)

		except Exception as e:

			import sys, traceback
			print '\n---------------------'
			print 'Exception: %s' % e
			print '- - - - - - - - - - -'
			traceback.print_tb(sys.exc_info()[2])
			print "\n"
			pass

def DrawTestPattern(f):
	l,h = screen_size
	L_SLOPE = 30
	
	f.Line((0, 0), (l, 0), 0xFFFFFF)
	f.LineTo((l, h), 0xFFFFFF)
	f.LineTo((0, h), 0xFFFFFF)
	f.LineTo((0, 0), 0xFFFFFF)
	
	f.LineTo((2*L_SLOPE, h), 0)
	for i in xrange(1,7):
		c = (0xFF0000 if i & 1 else 0) | (0xFF00 if i & 2 else 0) | (0xFF if i & 4 else 0)
		f.LineTo(((2 * i + 1) * L_SLOPE, 0), c)
		f.LineTo(((2 * i + 2) * L_SLOPE, h), c)
	f.Line((l*.5, h*.5), (l*.75, -h*.5), 0xFF00FF)
	f.LineTo((l*1.5, h*.5), 0xFF00FF)
	f.LineTo((l*.75, h*1.5), 0xFF00FF)
	f.LineTo((l*.5, h*.5), 0xFF00FF)
		

app_path = os.path.dirname(os.path.realpath(__file__))

pygame.init()
sounds.InitSounds()
#sounds.LoadBGM("dischipo.ogg", [15,54,127])

screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Laser Hexagon")
clock = pygame.time.Clock()

fwork_holder = frame.FrameHolder()
#laser = renderer.LaserRenderer(fwork_holder, 0,12000,-36,-36, 16000, 12000)
laser = renderer.LaserRenderer(fwork_holder, 10000,12000,-28,-28, 16000, 10000)

thread.start_new_thread(dac_thread, ())


update_screen = False

gstt.pa = playarea.PlayArea()
gstt.plyr = player.Player(gstt.pa)
gstt.score = score.Score(gstt.pa)

keystates = pygame.key.get_pressed()
gstt.spd_gens = weakref.WeakSet()

#TODO : à placer ailleurs
lvls = [levels.LvlRoboRockerz(), levels.LvlGForce(), levels.LvlBeginner()]
SelectLevel()



gstt.fs = GAME_FS_MENU
StartPreview()

while gstt.fs != GAME_FS_QUIT:

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			gstt.fs = GAME_FS_QUIT
		#elif event.type ==
	
	keystates_prev = keystates[:]
	keystates = pygame.key.get_pressed()[:]

	# Code commun de test

	if keystates[pygame.K_UP]:
		gstt.pa.a_tilt -= 1
	elif keystates[pygame.K_DOWN]:
		gstt.pa.a_tilt += 1

	# Selon états du jeu
	if gstt.fs == GAME_FS_MENU:
		if keystates[pygame.K_ESCAPE] and not keystates_prev[pygame.K_ESCAPE]:
			gstt.fs = GAME_FS_QUIT
		# TODO : choisir le niveau et lancer le jeu
		if keystates[pygame.K_LEFT] and not keystates_prev[pygame.K_LEFT]:
			ChangeLevel(-1)
		if keystates[pygame.K_RIGHT] and not keystates_prev[pygame.K_RIGHT]:
			ChangeLevel(1)
		elif keystates[pygame.K_SPACE] and not keystates_prev[pygame.K_SPACE]:
			StartPlaying(True)

		# Défilement du niveau choisi, sans le joueur
		GenerateLevel()

		gstt.pa.MoveSideChanger()
		gstt.pa.Move()

		for wr in gstt.wall_ring_list:
			wr.Move()
			wr.RecalcAngles()

		MoveSpdGens()
		# Suppression des murs absorbés par le trou noir
		PurgeWallRingList()
		
		gstt.score.ZoomReset()

	elif gstt.fs == GAME_FS_PLAY:

# 		if keystates[pygame.K_PAGEUP] and not gstt.pa.rearrange_sides:
# 			gstt.pa.rearrange_sides = 1
# 			sounds.play_sndfx_area_resize(True)
# 		elif keystates[pygame.K_PAGEDOWN] and not gstt.pa.rearrange_sides:
# 			gstt.pa.rearrange_sides = -1
# 			sounds.play_sndfx_area_resize(True)
		
		#Génération des murs
		GenerateLevel()
		# Génération des données de collision "précédentes"
		#TODO : optimiser les recalculs de données internes. Peut-être plutôt à faire à l'initialisation
		for wr in gstt.wall_ring_list:
			wr.RecalcAngles()
			wr.UpdateCollisionData(gstt.plyr)

		# Déplacement scène APRES UpdateCollisionData()
		# (si jamais un mur latéral lié à la scène balaie le joueur, alors il faut
		# que le joueur soit poussé, donc que l'info de collision précédente le voit
		# du côté du mur AVANT mouvement).
		gstt.pa.MoveSideChanger()
		gstt.pa.Move()
		
		#Déplacement joueur
		gstt.plyr.MoveTurn(keystates[pygame.K_LEFT], keystates[pygame.K_RIGHT])
		
		
		# Déplacement et test collisions :
		# Collisions latérales :
		# le fait de traiter la collision entre déplacement angulaire et déplacement radial
		# sert à éviter un crash indésirable d'un joueur s'appuyant sur un mur latéral joint à un mur frontal.
		# Les autres techniques créent soit des crashes indésirables, soit des oublis de détection de crash
		side_collision_flag = False
		for wr in gstt.wall_ring_list:
			if wr.IsSideType():
				wr.MoveAngular()
				wr.RecalcAngles()
				idx_angle = wr.CollideWith(gstt.plyr)
				if not idx_angle is None:
					gstt.plyr.Repell(wr.RepellAngle(idx_angle))
					side_collision_flag = True
				wr.MoveRadial()
		# Il faut traiter les collisions avec tous les obstacles :
		# parfois, le joueur est repoussé successivement par 2 murs.

		# DETECTION D'UN ECRASEMENT :
		# si le joueur a été repoussé, alors s'il est toujours en collision
		# latérale avec un obstacle (à cette nouvelle position VS position du coup précédent),
		# alors il y a écrasement.
		if side_collision_flag:
			for wr in gstt.wall_ring_list:
				if wr.IsSideType():
					if not wr.CollideWith(gstt.plyr) is None:
						CrashPlayer(2)
						break
		# Collisions frontales : que avec les murs frontaux
		for wr in gstt.wall_ring_list:
			if not wr.IsSideType():
				wr.Move()
				wr.RecalcAngles()
				#wr.RecalcCachedPoints()
				if wr.CollideWith(gstt.plyr):
					CrashPlayer(1)
					# Impossible de faire break, sauf si on sort la partie traitement des murs
		
		MoveSpdGens()
		# Suppression des murs absorbés par le trou noir
		PurgeWallRingList()
							
		gstt.plyr.MoveSwap(keystates[pygame.K_SPACE] and not keystates_prev[pygame.K_SPACE])
		
		if keystates[pygame.K_DELETE]:
			CrashPlayer(1)

		# Chrono
		gstt.score.Increase()

		gstt.score.ZoomOut()
		
	elif gstt.fs == GAME_FS_GAMEOVER:
		gstt.pa.Move()
		AnimateCrash()
		# ATTENTION ! Il faut absolument rafraîchir les listes internes d'angles,
		# parce que la scène peut être en cours de réarrangement par augmentation du nombre de côtés.
		# Les listes d'angles non remises à jour pourraient avoir une longueur insuffisante,
		# d'où l'échec des méthodes Draw()
		for wr in gstt.wall_ring_list:
			wr.RecalcAngles()
		
		# Inactiver la relance de partie aussi pendant un bref temps après le crash.
		# (par exemple, compte à rebours de l'explosion non répétitive)
		if keystates[pygame.K_SPACE] and not keystates_prev[pygame.K_SPACE] and gstt.tdn_crash < TDN_CRASH // 2:
			StartPlaying(False)
		elif keystates[pygame.K_ESCAPE] and not keystates_prev[pygame.K_ESCAPE]:
			gstt.fs = GAME_FS_MENU
			StartPreview()
			# Option : son pour quitter

		gstt.score.ZoomIn()

	# Opérations d'affichage

	gstt.pa.Update3DEffectMatrix()

	screen.fill(0)

	fwork = frame.Frame()
	if keystates[pygame.K_t]:
		DrawTestPattern(fwork)
	else:
		display_plyr = gstt.fs == GAME_FS_PLAY or gstt.fs == GAME_FS_GAMEOVER
		gstt.pa.Draw(fwork)
		if display_plyr:
			gstt.plyr.Draw(fwork)
		for wr in gstt.wall_ring_list:
			wr.Draw(fwork)	
		if display_plyr:
			gstt.score.Draw(fwork)
		if gstt.fs == GAME_FS_MENU:
			logo.Draw(fwork)
	
	# Affecter la frame construite à l'objet conteneur de frame servant au système de rendu par laser
	fwork_holder.f = fwork

	if update_screen:
		update_screen = False
		fwork.RenderScreen(screen)
		pygame.display.flip()
	else:
		update_screen = True

	# Opérations d'animation autres
	gstt.plyr.AnimateAfter()
	
	
	# TODO : rendre indépendante la fréquence de rafraîchissement de l'écran par
	# rapport à celle de l'animation du jeu
	clock.tick(100)

pygame.quit()





