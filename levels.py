# coding=UTF-8
'''
Created on 11 janv. 2015

@author: pclf
'''

from globalVars import *
import itertools
import math
import obstacle
import random
import gstt
# import playarea
# import player
import sounds
import lvltools as lvt
from lvltools import zero_speed_gen


def GenRREnterSeq1(thickness=0):
	n = random.randint(4,6)
	for _ in xrange(n):
		idx = random.randint(0,5)
		choix = random.randint(0,2)

		if choix:
			walls = lvt.MakeDashMaskEx(idx, 1, random.randint(2,3), False, 6)
		else:
			c_size = 5 if random.randint(0,1) else 3
			walls = lvt.MakeDashMaskEx(idx, c_size , 6, False, 6)
		lvt.SpawnFrontalWallRingEx(walls, thickness, 0, lvt.MainSpeedGen())
		yield lvt.GetIntThicknessPlusSectorTime(thickness, 5)

def GenRRStdSeq():
	# Des C5/6 avec ou sans stries et des triples C opposés (façon Super Hexagon),
	# des doubles spirales minces.
	n = random.randint(10,12)
	while n > 0:
		choix = random.randint(0,6)
		idx = random.randint(0,5)
		if choix < 2:
			lvt.SpawnFrontalWallRingEx(lvt.MakeDashMaskEx(idx, 1, 2, False, 6), 0, 0, lvt.MainSpeedGen())
			yield lvt.GetIntThicknessPlusSectorTime(0, 4.5)
			n -= 1
		elif choix < 4:
			lvt.SpawnFrontalWallRingEx(lvt.MakeDashMaskEx(idx, 5, 6, False, 6), 0, 0, lvt.MainSpeedGen())
			yield lvt.GetIntThicknessPlusSectorTime(0, 4.5)
			n -= 1
		elif choix == 5:
			for t in lvt.GenTripleRandomOpposedCShapeBG(lvt.MainSpeedGen(), 1.8, 0, 0):
				yield t
			n -= 2
		else:
			yield lvt.MakeSpiralZeroWidth(idx, 3, 6, random.randint(0,1), lvt.GetSectorTime()* lvt.MainSpeedGen().cur()*1.1, 10, \
											lvt.MainSpeedGen()) + 50
			n -= 6
			
def GenRRAltSeq():
	# Des pointillés 2 ou 3
	# Des gros pointillés 2 ou 3 suivi de leur inversion
	# Des C5 aléatoires
	# Des C4 solos
	# Des C4 opposés
	# Des C4 décalés
	thickness = 40
	n = random.randint(7,10)
	

	while n > 0:
		if random.randint(0,9):
			#Le + fréquent : des murs simples
			idx = random.randint(0,5)
			choix = random.randint(0,9)
			if choix < 4:
				# Pointillés simples ou doublés de leur inverse
				period = random.randint(2,3)
				if choix < 2:
					lvt.SpawnFrontalWallRingEx(lvt.MakeDashMaskEx(idx, 1, period, False, 6), thickness, 1, lvt.MainSpeedGen())
					yield lvt.GetIntThicknessPlusSectorTime(thickness, 4.5)
				else:
					walls = lvt.MakeDashMaskEx(idx, 1, period, random.randint(0,1), 6)
					yield lvt.SpawnShapeThenOpposed(walls, 1.5 * thickness,1.5, thickness, 4.5)
					
# 					thickness2 = 1.5 * thickness
# 					walls = lvt.MakeDashMaskEx(idx, 1, period, random.randint(0,1), 6)
# 					lvt.SpawnFrontalWallRingEx(walls, thickness2 , 1, lvt.MainSpeedGen())
# 					yield lvt.GetIntThicknessPlusSectorTime(thickness2, 1.5)
# 					lvt.SpawnFrontalWallRingEx(lvt.InvertMask(walls), thickness , 1, lvt.MainSpeedGen())
# 					yield lvt.GetIntThicknessPlusSectorTime(thickness, 4.5)
				n -= 1
			elif choix < 7:
				lvt.SpawnFrontalWallRingEx(lvt.MakeDashMaskEx(idx, 5, 6, False, 6), thickness , 1, lvt.MainSpeedGen())
				yield lvt.GetIntThicknessPlusSectorTime(0, 5)
				n -= 1
			else:
				lvt.SpawnFrontalWallRingEx(lvt.MakeDashMaskEx(idx, 4, 6, False, 6), thickness , 1, lvt.MainSpeedGen())
				yield lvt.GetIntThicknessPlusSectorTime(0, 5)
				n -= 1
		else:
			#Répétitions
			choix = random.randint(0,1)
			if choix:
				# Longue séquence : les C4 opposés
				for t in lvt.GenMultipleRandomOposedC4BG(lvt.MainSpeedGen(), 6, 2, thickness, 1): yield t
				n -= 5
			else:
				# Longue séquence : les C4 décalés
				for t in lvt.GenMultipleRandomShiftingCBG(lvt.MainSpeedGen(), 8, 2, 1.2, thickness, 1): yield t
				n -= 6
			
def GenRRRotatingWallSeq1():
	'''
	Des alternances de murs fixes et rotatifs (rotation différée)
	'''
	n=random.randint(3,4)
	time_space = lvt.GetIntThicknessPlusSectorTime(0, 5)
	while n > 0:
		idx = random.randint(0,5)
		lvt.SpawnCShapeBG(idx, lvt.MainSpeedGen(), 0, 0)
		yield time_space
		idx = random.randint(0,5)
		lvt.SpawnCShapeFree(idx, 6, 0, lvt.MainSpeedGen(), \
				lvt.DeferredStartAngularSpeedGen(gstt.play_area_rsize/2, random.uniform(-1,1)))
		yield time_space
		n -= 1
	# une séquence de clôture
	choix = random.randint(0,2)
	#choix = 0
	
	idx = random.randint(0,5)
	if choix:
		dtheta = lvt.GetSectorByThicknessAngularSpd(1, gstt.play_area_rsize/2 - player_r)
		if random.randint(0,1):
			dtheta *= -1
		if choix==1:
			walls = lvt.MakeDashMaskEx(idx, 1, 2, False, 6)
		else:
			walls = lvt.MakeDashMaskEx(idx, 3, 6, False, 6)
			dtheta *= 2
		lvt.SpawnFrontalWallRingEx(walls, 0 , 0, lvt.MainSpeedGen())
		lvt.SpawnFrontalWallRingEx(lvt.InvertMask(walls), 0 , 0, lvt.MainSpeedGen(),\
				0, False, 0, lvt.DeferredStartAngularSpeedGen(gstt.play_area_rsize/2, dtheta, True))
		yield time_space
	else:
		walls = lvt.MakeDashMaskEx(idx, 1, 3, False, 6)
		dtheta = lvt.GetSectorByThicknessAngularSpd(.5, gstt.play_area_rsize/4 - player_r + 75)
		for i in [-1,1]:
			lvt.SpawnFrontalWallRingEx(walls, 120 , 1, lvt.MainSpeedGen(),\
					 0, False, -60 * i, lvt.DeferredStartAngularSpeedGen(gstt.play_area_rsize/4, dtheta * i))
		yield lvt.GetIntThicknessPlusSectorTime(120, 5)
		
def GenRRRotatingWallSeq2():
	'''
	Les 3 'C' en rotation
	'''
	# anciennement GenTripleRandomCShapeFree()
	for i in xrange(0,3):
		side_count = random.randint(4,7)
		theta = random.randint(0,360)
		dtheta = random.uniform(-1,1)
		SpawnCShapeFree(0, side_count, theta, lvt.MainSpeedGen(), lvt.ConstantSpeedGen(dtheta))
		yield 80

# juste pour test. A faire évoluer
def SpawnCShapeFree(idx, side_count, theta, r_spd_gen, theta_spd_gen):
	walls = lvt.MakeCShapeMask(idx, side_count)
	gstt.wall_ring_list.append(
							obstacle.FrontalWallRing(play_area_rsize,theta,r_spd_gen,theta_spd_gen,False,walls))


def GenRRRotatingWallSeq3():
	'''
	Les "ciseaux"
	'''
	for da in [-.4,.4]:
		gstt.wall_ring_list.append(
						obstacle.SideWallRing(play_area_rsize,300,0,lvt.MainSpeedGen(),lvt.ConstantSpeedGen(da),False,[1,0,1,0,1,0]))
	yield lvt.GetIntThicknessPlusSectorTime(300, 3)
	


def GenRRRotatingWallSeq4():
	'''
	Un "cercle" avec une petitt ouverture, en rotation !
	'''
	time_space = lvt.GetIntThicknessPlusSectorTime(0, 8)
	
	yield time_space
	lvt.SpawnFrontalWallRingEx(lvt.MakeDashMaskEx(0, 22, 24, False, 24), 0, 0, lvt.MainSpeedGen(),\
			0,False,random.randint(0,359))
	yield time_space

def GenRRSquareSeq(thickness):
	# Mur avant réarrangement = pointillés
	idx = random.randint(0,1)
	lvt.SpawnFrontalWallRingEx(lvt.MakeDashMaskEx(idx, 1, 2, False, 6), thickness, 1, lvt.MainSpeedGen())
	yield lvt.GetIntThicknessPlusSectorTime(thickness, 4.5)
	gstt.pa.ScheduleSideChange(100,-2)
	# Attendre un temps suffisant avant de générer la suite pour ne pas la voir
	# apparaître tant que le réarrangement ne s'est pas fait
	yield 100
	# On est dans la zone carrée
	
	#thickness = 40
	n = random.randint(15,20)
	while n > 0:
		if random.randint(0,9):
			#Le + fréquent : des murs simples
			idx = random.randint(0,3)
			choix = random.randint(0,4)
			if choix < 2:
				# 'C' ou pointillés
				if choix:
					walls = lvt.MakeDashMaskEx(idx, 1, 4, True, 4)
				else:
					walls = lvt.MakeDashMaskEx(idx, 1, 2, False, 4)
				lvt.SpawnFrontalWallRingEx(walls, thickness, 1, lvt.MainSpeedGen())
				yield lvt.GetIntThicknessPlusSectorTime(thickness, 2.4)
				n -= 1
			elif choix == 2:
				# alternance de pointillés
				for i in xrange(2):
					lvt.SpawnFrontalWallRingEx(lvt.MakeDashMaskEx(idx + i, 1, 2, False, 4), thickness, 1, lvt.MainSpeedGen())
					yield lvt.GetIntThicknessPlusSectorTime(thickness, 2)
				yield lvt.GetIntThicknessPlusSectorTime(0, 3)
				n -= 1
			elif choix == 3:
				for t in lvt.GenTripleRandomOpposedCShapeBG(lvt.MainSpeedGen(), 1, thickness, 1, 4):
					yield t
				n -= 3
			else:
				# alternance de 'L'
				for i in xrange(random.randint(5,8)):
					lvt.SpawnFrontalWallRingEx(lvt.MakeDashMaskEx(idx + i, 2, 4, False, 4), thickness, 1, lvt.MainSpeedGen())
					yield lvt.GetIntThicknessPlusSectorTime(thickness, 1.2)
				#yield lvt.GetIntThicknessPlusSectorTime(thickness, 1)
				lvt.SpawnFrontalWallRingEx(lvt.MakeDashMaskEx(idx + i-2, 2, 4, False, 4), 2*thickness, 1, lvt.MainSpeedGen())
				yield lvt.GetIntThicknessPlusSectorTime(thickness, 4)
				n -= 8
					
	yield 100
	
	lvt.SpawnFrontalWallRingEx(lvt.MakeDashMaskEx(5, 1, 6, True, 6), thickness, 1, lvt.MainSpeedGen())
	gstt.pa.ScheduleSideChange(100,2)

	
	yield lvt.GetIntThicknessPlusSectorTime(thickness, 4.5)

	# TEST
	yield 100
	

def ChooseThickness():
	return 40 if random.randint(0,1) else 0	

# Essai d'implémentation de niveaux sous forme de classes présentant les mêmes méthodes
# - Instancier un (unique) objet pour initialiser le niveau (musique, couleurs, vitesse joueur...
# - méthode Start() pour (re-)lancer
# - fonction génératrice
class LvlRoboRockerz(object):
	def __init__(self):
		self.BLACK_HOLE_COLOR = 0xFFFF00
		self.SPOKE_COLOR = 0xFF
		self.PLAYER_COLOR = 0xFF0000
		self.PLAYER_FLASH_COLOR = 0xFFFFFF
		self.LINKED_WALL_COLOR = 0xFFFF
		self.FREE_WALL_COLOR = 0xFF00FF
	
	def Init(self):
		'''Initialiser le jeu sur ce niveau'''
		gstt.plyr.absdtheta = 4
		gstt.pa.main_speed = 2	# 2 par défaut
		sounds.LoadBGM("Robot_Rockerz.ogg", [28,3,54,67,86])
		# TODO : s'occuper des couleurs : avoir des couleurs variables (les couleurs par défaut ne servant qu'à les initialiser)

	def Start(self, first_time=True):
		'''Relancer le niveau'''
		gstt.pa.side_count = 6
		gstt.pa.dtheta = 0
		self.gen = GenRoboRockerz(first_time)	


# Définition d'un niveau ou des séquences : sous forme d'un générateur.
# Peut-être par la suite retourner directement soit None, soit un mur à ajouter,
# soit un autre objet qui agirait sur le jeu (pour changer les faces, les vitesses...)
# + simple : yield retourne le délai avant prochain traitement
# (envoi d'un mur ou modif d'un paramètre : vitesse, nb faces...)
def GenRoboRockerz(first_time):
	dft_thickness = ChooseThickness()
	
	if first_time:
		for t in GenRREnterSeq1(dft_thickness): yield t
		yield 50

	while True:
		
		
		if random.randint(0,1):
			gen = GenRRStdSeq()
			dft_thickness = 0
		else:
			gen = GenRRAltSeq()
			dft_thickness = 40
		for t in gen: yield t

		choix = random.randint(0,4)
		#choix = 0
		
		if choix == 0:
			# Séquence pentagonale ou carrée
			gen = GenRRSquareSeq(dft_thickness)
			for t in gen: yield t
			
		else:
			# Hexagone qui s'ouvre en pointillés,
			# puis 1 des 4 séquences de murs spéciaux
			
			# Test StopStart
			idx = random.randint(0,1)
			lvt.SpawnFrontalWallRingEx(lvt.MakeDashMaskEx(idx, 1, 2, False, 6), \
								0, 0, \
								lvt.MainSpeedGen())
			lvt.SpawnFrontalWallRingEx(lvt.MakeDashMaskEx(idx+1, 1, 2, False, 6), \
								0, 0, \
								lvt.StopRestartSpeedGen(gstt.play_area_rsize/2,80,1))
			
			yield 150
	
	
			gen = [GenRRRotatingWallSeq1(),GenRRRotatingWallSeq2(),GenRRRotatingWallSeq3(),GenRRRotatingWallSeq4()][random.randint(0,3)]
			#gen = GenRRRotatingWallSeq1()
			for t in gen: yield t
		

		gstt.pa.dtheta = .3 * random.randint(-2,2)
		
		
class LvlGForce(object):
	def __init__(self):
		self.BLACK_HOLE_COLOR = 0xFFFFFF
		self.SPOKE_COLOR = 0xFF00
		self.PLAYER_COLOR = 0xFFFF00
		self.PLAYER_FLASH_COLOR = 0xFFFFFF
		self.LINKED_WALL_COLOR = 0xFFFF00
		self.FREE_WALL_COLOR = 0xFF0000
	
	def Init(self):
		'''Initialiser le jeu sur ce niveau'''
		gstt.plyr.absdtheta = 4
		gstt.pa.main_speed = 4	# 2 par défaut
		sounds.LoadBGM("cpumood.ogg", [8.2,100,204])

	def Start(self, first_time):
		'''Relancer le niveau'''
		gstt.pa.side_count = 4
		gstt.pa.dtheta = 0
		self.gen = GenGForce(first_time)	

def GenGForceStd(count, altern_mode, invert, tight_spacing, preview):
	side_count = gstt.pa.GetCurrentSideCount()
	# Annonce oprionnelle de la séquence
	if preview:
		mask_full = [True,True,True,True]
		for i in xrange(4):
			if (i & altern_mode) != invert:
				gstt.wall_ring_list.append(
						obstacle.SideWallRing(play_area_rsize ,20 ,0,lvt.MainSpeedGen(),
						lvt.SinusAngularSpeedGen(0.5, 0, 5),
						False, mask_full,None, None)
						)
			else:
				gstt.wall_ring_list.append(
						obstacle.SideWallRing(play_area_rsize ,20 ,0,lvt.MainSpeedGen(),
						zero_speed_gen,
						True, mask_full,None, None)
						)
			yield 8 if tight_spacing else 14
	yield 50
	# Séquence proprement dite
	for i in xrange(count):
		idx = random.randint(0,side_count-1)
		if (i & altern_mode) != invert:
			lvt.SpawnFrontalWallRingEx(lvt.MakeCShapeMask(idx, side_count) ,25, 1, lvt.MainSpeedGen(),\
					0,False,0,lvt.SinusAngularSpeedGen(random.uniform(1,2), random.randint(0,359), 1.5))
		else:
			lvt.SpawnFrontalWallRingEx(lvt.MakeCShapeMask(idx, side_count) ,25, 1, lvt.MainSpeedGen())
		yield lvt.GetIntThicknessPlusSectorTime(25, 1.5 if tight_spacing else 3.2)
	
	yield 100
		# Gérer Incongruence et Scissors à part

def GenGForceIncongruence(count):
	side_count = gstt.pa.GetCurrentSideCount()
	# Annonce systématique de la séquence
	for i in xrange(4):
		dtheta_gen = lvt.SinusAngularSpeedGen(0.5, 0, 5) if i & 1 else zero_speed_gen
		side_count = random.randint(4,6)
		mask_full = lvt.MakeDashMaskEx(0,side_count,side_count,False,side_count)
		gstt.wall_ring_list.append(
				obstacle.SideWallRing(play_area_rsize ,20 ,0,lvt.MainSpeedGen(),
				dtheta_gen,
				False, mask_full,None, None)
				)
		yield 14
	yield 50
	# Séquence proprement dite
	for i in xrange(count):
		dtheta_gen = lvt.SinusAngularSpeedGen(random.uniform(1,2), random.randint(0,359), 1.5) if i & 1 else zero_speed_gen
		side_count = random.randint(4,6)
		idx = random.randint(0,side_count-1)
		lvt.SpawnFrontalWallRingEx(lvt.MakeCShapeMask(idx, side_count) ,25, 1, lvt.MainSpeedGen(),\
				0,False,0,dtheta_gen)
		yield lvt.GetIntThicknessPlusSectorTime(25, 3.2)
	
	yield 100
		# Gérer Incongruence et Scissors à part

def GenGForceScissors(count):
	# Annonce systématique de la séquence
	dtheta_gen = lvt.SinusAngularSpeedGen(0.5, 0, 5)
	mask_full = [True,True,True,True]
	gstt.wall_ring_list.append(
			obstacle.SideWallRing(play_area_rsize ,100 ,0,lvt.MainSpeedGen(),
			lvt.SinusAngularSpeedGen(0.5, 0, 5),
			False, mask_full,None, None)
			)
	yield 100
	
	# Séquence proprement dite
	for i in xrange(count):
		dtheta_gen = lvt.ConstantSpeedGen((1-2*random.randint(0,1))*1.2)#lvt.SinusAngularSpeedGen(1, random.randint(45,135), .3)
		idx = random.randint(0,3)
		# Partie mobile
		gstt.wall_ring_list.append(
				obstacle.SideWallRing(play_area_rsize ,400 ,0,lvt.MainSpeedGen(),
				dtheta_gen,
				False, lvt.MakeDashMaskEx(idx,random.randint(1,2),4,False,4),None, None)
				)
		# Partie fixe
		idx = random.randint(0,3)
		gstt.wall_ring_list.append(
				obstacle.SideWallRing(play_area_rsize ,400 ,0,lvt.MainSpeedGen(),
				zero_speed_gen,
				True, lvt.MakeDashMaskEx(idx,random.randint(1,2),2,False,4),None, None)
				)
		yield lvt.GetIntThicknessPlusSectorTime(400,1.5)
	yield 100

def GenGForce(first_time):
	dtheta_abs = .6
	while True:
		gstt.pa.dtheta = (-1 + 2*random.randint(0,1))*dtheta_abs
		# Alternance 1/1
		for t in GenGForceStd(10, 1, random.randint(0,1),False,False): yield t
		# Au choix les différentes séquences
		choix = random.randint(0,4)
		if choix==0:
			# Double
			gen = GenGForceStd(12, 2, random.randint(0,1),False,True)
		elif choix==1:
			# Dizzy
			gen = GenGForceStd(12, 0, True,False,True)
		elif choix==2:
			# Incongruence
			gen = GenGForceIncongruence(12)
		elif choix==3:
			gen = GenGForceScissors(8)
		else: # choix==4:
			# Assault
			gen = GenGForceStd(12, 0, False,True,True)

		for t in gen: yield t
		
		yield 100
		if dtheta_abs <= 1.2:
			dtheta_abs += .1
		
class LvlBeginner(object):
	def __init__(self):
		self.BLACK_HOLE_COLOR = 0xFF0000
		self.SPOKE_COLOR = 0xFF0000
		self.PLAYER_COLOR = 0xFF00
		self.PLAYER_FLASH_COLOR = 0xFFFFFF
		self.LINKED_WALL_COLOR = 0xFFFFFF
		self.FREE_WALL_COLOR = 0xFF00
	
	def Init(self):
		'''Initialiser le jeu sur ce niveau'''
		gstt.plyr.absdtheta = 4
		gstt.pa.main_speed = 1.5
		sounds.LoadBGM("Pirate_Manners_44k1.ogg", [17,44,98])

	def Start(self, first_time):
		'''Relancer le niveau'''
		gstt.pa.side_count = 5
		gstt.pa.dtheta = 0
		self.gen = GenBeginner(first_time)	

def GenBeginner(first_time):
	while True:
		for i in xrange(10):
			idx=random.randint(0,4)
			if random.randint(0,9):
				choix = random.randint(0,2)
				if choix == 0:
					lvt.SpawnCShapeBG(idx, lvt.MainSpeedGen(), 0,0)
					yield lvt.GetIntThicknessPlusSectorTime(0, 10)
				elif choix == 1:
					lvt.SpawnFrontalWallRingEx(lvt.MakeDashMask(idx, random.randint(2,5), False,5), 0, 0, lvt.MainSpeedGen())
					yield lvt.GetIntThicknessPlusSectorTime(0, 8)
				else:
# 					p = random.randint(1,2)
# 					p2 = random.randint(1,2)
# 					lvt.SpawnShapeThenOpposed(lvt.MakeDashMaskEx(idx, p, p+p2, False,5), 0, 1.8, 0, 6.2)
 					yield lvt.GetIntThicknessPlusSectorTime(0, 6)
					
			else:
				yield lvt.MakeSpiralZeroWidth(idx, 5, 5, random.randint(0,1), lvt.GetSectorTime()* lvt.MainSpeedGen().cur()*2,\
						random.randint(5,10), lvt.MainSpeedGen()) + 50
				idx=random.randint(0,4)
				lvt.SpawnFrontalWallRingEx(lvt.MakeDashMaskEx(idx, 3, 5, False, 5), 0, 0, lvt.MainSpeedGen())
				yield lvt.GetIntThicknessPlusSectorTime(0, 6)
				
		lvt.SpawnFrontalWallRingEx(lvt.MakeCShapeMask(5, 6), 60, 2, lvt.MainSpeedGen())		
		gstt.pa.ScheduleSideChange(100,1)
		yield 100

		for i in xrange(10):
			idx=random.randint(0,5)
			if random.randint(0,5):
				choix = random.randint(0,2)
				if choix == 0:
					lvt.SpawnCShapeBG(idx, lvt.MainSpeedGen(), 0,0)
					yield lvt.GetIntThicknessPlusSectorTime(0, 10)
				elif choix == 1:
					lvt.SpawnFrontalWallRingEx(lvt.MakeDashMask(idx, random.randint(2,6), False,6), 0, 0, lvt.MainSpeedGen())
					yield lvt.GetIntThicknessPlusSectorTime(0, 8)
				else:
					p = random.randint(1,2)
					p2 = random.randint(1,2)
					yield lvt.SpawnShapeThenOpposed(lvt.MakeDashMaskEx(idx, p, p+p2, False,6), 0, 2.8, 0, 5.2)
			else:
				dtheta = float(random.randint(0,2) - 1)
				
				gstt.wall_ring_list.append(obstacle.SideWallRing(gstt.play_area_rsize, 200, 0,\
						lvt.MainSpeedGen(), lvt.ConstantSpeedGen(dtheta), dtheta == 0, [1,1,1,1,1,1]))
				yield lvt.GetIntThicknessPlusSectorTime(200, 2)
		

		gstt.pa.ScheduleSideChange(100,-1)
		yield 300


		gstt.pa.dtheta = float(random.randint(0,6) - 3) / 12
