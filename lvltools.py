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
import weakref
import gstt
import playarea
import player
import sounds

class SpeedGen(object):
	def __init__(self):
		self.parent = None
	
	def setParent(self, parent):
		self.parent = parent

class StatefulSpeedGen(SpeedGen):
	def __init__(self):
		super(StatefulSpeedGen, self).__init__()
		gstt.spd_gens.add(self)


class ConstantSpeedGen(SpeedGen):
	def __init__(self, spd):
		super(ConstantSpeedGen, self).__init__()
		self.spd = spd
	
	# Pour ce cas, c'est +- inutile...
	def __iter__(self):
		return self
	
	def cur(self):
		return self.spd

# class CurMainSpeedGen(SpeedGen):
# 	def __init__(self):
# 		super(CurMainSpeedGen, self).__init__()
# 		
# 	def cur(self):
# 		return gstt.pa.GetCurrentMainSpeed()

class MainSpeedGen(SpeedGen):
	def __init__(self):
		super(MainSpeedGen, self).__init__()
		
	def cur(self):
		return gstt.pa.main_speed
	
# On pourra définir d'autres profils de vitesses (sinusoïdaux, marche-arrêt-marche etc...)

# Arrêt/redémarrage radial
class StopRestartSpeedGen(StatefulSpeedGen):
	def __init__(self,r_stop,tdn_stop,restart_spdfactor):
		super(StopRestartSpeedGen, self).__init__()
		self.r_stop = r_stop
		self.tdn_stop = tdn_stop
		self.restart_spdfactor = restart_spdfactor
		self.fs = False
		self.spd = gstt.pa.main_speed

	def cur(self):
		return self.spd

	def Move(self):
		if self.fs:
			self.spd = 0 if self.tdn_stop else gstt.pa.main_speed * self.restart_spdfactor
		
		if not self.fs:
			if self.parent.r <= self.r_stop:
				self.fs = True
		else:
			if self.tdn_stop:
				self.tdn_stop -= 1
		print self.tdn_stop

# On hérite de SpeedGen pour la fonctionnalité lien parent
class DeferredStartAngularSpeedGen(StatefulSpeedGen):
	def __init__(self,r_start,dtheta, sound=False):
		super(DeferredStartAngularSpeedGen, self).__init__()
		self.r_start = r_start
		self.dtheta = dtheta
		self.sound = sound
		self.fs = False
		self.spd = 0
	
	def cur(self):
		return self.spd

	def Move(self):
		if not self.fs:
			if self.parent.r <= self.r_start:
				self.fs = True
				self.spd = self.dtheta
				if self.sound:
					sounds.play_sndfx_area_resize(True)


class SinusAngularSpeedGen(StatefulSpeedGen):
	def __init__(self,dthetamax,a,da):
		super(SinusAngularSpeedGen, self).__init__()
		self.dthetamax= dthetamax
		self.a = a
		self.da = da

	def cur(self):
		return self.dthetamax * math.sin(math.radians(self.a))

	def Move(self):
		self.a = (self.a + self.da) % 360


zero_speed_gen = ConstantSpeedGen(0)

# Fonctions auxiliaires utiles
def GetSectorTime(side_count = 0):
	'''
	Calcule la durée de franchissement d'un secteur par le joueur
	'''
	if not side_count:
		side_count = gstt.pa.GetCurrentSideCount()
	return 360 / side_count / gstt.plyr.absdtheta

def GetIntThicknessPlusSectorTime(thickness, sect_time_mult):
	'''
	Calcule la durée de défilement d'une épaisseur de mur + le franchissement d'u nombre de secteurs donné
	'''
	return int(math.ceil(thickness / MainSpeedGen().cur() + sect_time_mult * GetSectorTime()))

def GetSectorByThicknessAngularSpd(n_sector, dr, side_count = 0):
	'''
	Calcule la vitesse de rotation pour tourner d'un nombre de secteurs donné
	sur une certaine distance à la vitesse de défilement principale
	'''
	if not side_count:
		side_count = gstt.pa.GetCurrentSideCount()
	return float(n_sector) * 360 / side_count * MainSpeedGen().cur() / dr


def ModuloSide(idx, side_count = 0):
	if not side_count:
		side_count = gstt.pa.GetCurrentSideCount()
	return idx % side_count

# Idée : des fonctions pour créer les listes de booléens de chaque motif de mur

# Forme en "C"
def MakeCShapeMask(idx, side_count):
	idx = ModuloSide(idx, side_count)
	return [idx != i for i in xrange(0, side_count)]

# Traits pointillés 1 trou / period-1 murs (ou l'inverse)
# remarque : le 'C' est un cas particulier où period = side_count
def MakeDashMask(idx, period, invert, side_count):
	return [(((i - idx) % period) != 0) != invert for i in xrange(0, side_count)]

# Généralisation où le trou ou le mur ont une largeur variable
# (comme dans un signal PWM).
# L'inversion est inversée par rapport à dans l'ancienne routine
def MakeDashMaskEx(idx, period_on, period, invert, side_count):
	return [(((i - idx) % period) < period_on) != invert for i in xrange(0, side_count)]

def RotateMask(walls, idx):
	idx = idx % len(walls)
	return walls[idx:] + walls[:idx]

def InvertMask(walls):
	return [not wall for wall in walls]

# Calcul automatique du masque de murs latéraux qui correspond
def MakeSideWallMaskFromFrontalNoInner(frontal_walls):
	return [frontal_walls[i-1] != frontal_walls[i] for i in xrange(len(frontal_walls))]

def MakeSideWallMaskFromFrontalInner(frontal_walls):
	return [frontal_walls[i-1] or frontal_walls[i] for i in xrange(len(frontal_walls))]

# Routine générale d'envoi d'un anneau de murs :
# - masque en paramètre
# - option épaisseur pour avoir murs latéraux
# - option mur arrière et stries (si le laser suit)
# - option offset pour empiler plusieurs murs d'un coup
# Remarques : pas implémenté l'option "inner"
# Liaison ou non à la scène + paramètres : par défaut à la fin
def SpawnFrontalWallRingEx(walls, thickness, rear_walls_count, r_spd_gen, offset=0, linked_to_pa=True, theta=0, theta_spd_gen=None):
	if theta_spd_gen is None:
		theta_spd_gen = zero_speed_gen
	wr_main = obstacle.FrontalWallRing(play_area_rsize + offset,theta,r_spd_gen,theta_spd_gen,linked_to_pa,walls)
	gstt.wall_ring_list.append(wr_main)
	if thickness > 0:
		gstt.wall_ring_list.append(
					obstacle.SideWallRing(play_area_rsize + offset,thickness,theta,r_spd_gen,theta_spd_gen,linked_to_pa,
										MakeSideWallMaskFromFrontalNoInner(walls), wr_main, wr_main))
		for i in xrange(rear_walls_count):
			#TODO : répétition de code à éliminer (ex.: faire SpawnFrontalWallRing() sans options d'épaisseur)
			r = play_area_rsize + offset + thickness * (1 - float(i) / rear_walls_count)
			gstt.wall_ring_list.append(
					obstacle.FrontalWallRing(r ,theta,r_spd_gen,theta_spd_gen,linked_to_pa,walls, wr_main, wr_main))
			

def SpawnCShapeBG(idx, r_spd_gen, thickness, rear_walls_count):
	walls = MakeCShapeMask(idx, gstt.pa.GetCurrentSideCount())
	gstt.wall_ring_list.append(
							obstacle.FrontalWallRing(play_area_rsize,0,r_spd_gen,zero_speed_gen,True,walls))

def SpawnCShapeFree(idx, side_count, theta, r_spd_gen, theta_spd_gen):
	walls = MakeCShapeMask(idx, side_count)
	gstt.wall_ring_list.append(
							obstacle.FrontalWallRing(play_area_rsize,theta,r_spd_gen,theta_spd_gen,False,walls))
	


def GenTripleRandomOpposedCShapeBG(r_spd_gen, extra_sector_time_pct=1.1, thickness=40, rear_walls_count=0, side_count = 0):
	if not side_count:
		side_count = gstt.pa.GetCurrentSideCount()
	side_count2 = side_count // 2
	idx = random.randint(0,side_count)
	for i in xrange(0,3):
		walls = MakeCShapeMask(idx, side_count)
		SpawnFrontalWallRingEx(walls, thickness, rear_walls_count, r_spd_gen)
		idx += side_count2
		yield int(math.ceil(thickness / r_spd_gen.cur())) + (side_count2 + extra_sector_time_pct) * GetSectorTime()

# TODO : généraliser : le triple C et le multiple C4 sont des cas particuliers
def GenMultipleRandomOposedC4BG(r_spd_gen, n, extra_sector_time_pct=0.3, thickness=40, rear_walls_count=0):
	side_count = gstt.pa.GetCurrentSideCount()
	side_count2 = side_count // 2
	idx = random.randint(0,side_count)
	for i in xrange(0,n):
		walls = MakeDashMaskEx(idx, side_count2+1, side_count, False, side_count)
		SpawnFrontalWallRingEx(walls, thickness, rear_walls_count, r_spd_gen)
		idx += side_count2
		yield int(math.ceil(thickness / r_spd_gen.cur())) + (1 + extra_sector_time_pct) * GetSectorTime()

def GenMultipleRandomShiftingCBG(r_spd_gen, n, hole_size=1, extra_sector_time_pct=0.3, thickness=40, rear_walls_count=0):
	side_count = gstt.pa.GetCurrentSideCount()
	idx = random.randint(0,side_count)
	didx = -1 if random.randint(0,1) else 1
	for i in xrange(0,n):
		walls = MakeDashMaskEx(idx, side_count-hole_size, side_count, False, side_count)
		SpawnFrontalWallRingEx(walls, thickness, rear_walls_count, r_spd_gen)
		idx += didx
		yield int(math.ceil(thickness / r_spd_gen.cur())) + (1 + extra_sector_time_pct) * GetSectorTime()




def GenTripleRandomCShapeFree():
	for i in xrange(0,3):
		side_count = random.randint(4,7)
		theta = random.randint(0,360)
		dtheta = random.uniform(-1,1)
		SpawnCShapeFree(0, side_count, theta, MainSpeedGen(), ConstantSpeedGen(dtheta))
		yield 80


def MakeSpiralOneWidth(idx, period, side_count, left, step, length, r_spd_gen):
	'''
	Spirale faite de blocs de taille 1.
	Retourne le temps d'attente équivalent longueur, à YIELDer 
	'''
	wm_fronthead = MakeDashMaskEx(idx, 1, period, False, side_count)
	if (left):
		wm_sidehead = wm_fronthead[-1:] + wm_fronthead[:-1]	# rotation à droite
		offset_sidebody = 0
		di2 = -1
	else:
		wm_sidehead = wm_fronthead
		offset_sidebody = 1
		di2 = 1
	# Générer tête
	gstt.wall_ring_list.append(
			obstacle.FrontalWallRing(play_area_rsize,0,r_spd_gen,zero_speed_gen,True,wm_fronthead))
	gstt.wall_ring_list.append(
			obstacle.SideWallRing(play_area_rsize,step,0,r_spd_gen,zero_speed_gen,True,wm_sidehead))
	# Corps
	i2 = 0
	i = -1
	for i in xrange(length):
		wm_frontbody = MakeDashMaskEx(idx + i2 + offset_sidebody - 1, 2, period, False, side_count)
		wm_sidebody = MakeDashMaskEx(idx + i2 + offset_sidebody, 1, period, False, side_count)
		gstt.wall_ring_list.append(
				obstacle.FrontalWallRing(play_area_rsize + (i+1)* step,0,r_spd_gen,zero_speed_gen,True,wm_frontbody))
		gstt.wall_ring_list.append(
				obstacle.SideWallRing(play_area_rsize + i*step, 2*step,0,r_spd_gen,zero_speed_gen,True,wm_sidebody))
		i2 += di2

	# Générer queue
	wm_fronttail = MakeDashMaskEx(idx + i2, 1, period, False, side_count)
	if (left):
		wm_sidetail = wm_fronttail
	else:
		wm_sidetail = wm_fronttail[-1:] + wm_fronttail[:-1]	# rotation à droite
	gstt.wall_ring_list.append(
			obstacle.FrontalWallRing(play_area_rsize + (i+2)* step,0,r_spd_gen,zero_speed_gen,True,wm_fronttail))
	gstt.wall_ring_list.append(
			obstacle.SideWallRing(play_area_rsize + (i+1)*step,step,0,r_spd_gen,zero_speed_gen,True,wm_sidetail))
	# Retourner le temps à YIELDer
	return int(math.floor(step * (length+1) / r_spd_gen.cur()))

def MakeSpiralZeroWidth(idx, period, side_count, left, step, length, r_spd_gen):
	'''
	Spirale faite de murs de taille fine. Commence par un mur latéral
	Retourne le temps d'attente équivalent longueur, à YIELDer 
	'''
	if (left):
		offset_side = 1
		di2 = -1
	else:
		offset_side = 0
		di2 = 1
	# Corps
	i2 = 0
	for i in xrange(length):
		wm_front = MakeDashMaskEx(idx + i2, 1, period, False, side_count)
		wm_side = MakeDashMaskEx(idx + i2 + offset_side, 1, period, False, side_count)
		gstt.wall_ring_list.append(
				obstacle.FrontalWallRing(play_area_rsize + (i+1) * step,0,r_spd_gen,zero_speed_gen,True,wm_front))
		gstt.wall_ring_list.append(
				obstacle.SideWallRing(play_area_rsize + i * step, step,0,r_spd_gen,zero_speed_gen,True,wm_side))
		i2 += di2

	# Retourner le temps à YIELDer
	return int(math.floor(step * length / r_spd_gen.cur()))
	
def SpawnShapeThenOpposed(walls, thickness1, sct_time1, thickness2, sct_time2):
	SpawnFrontalWallRingEx(walls, thickness1 , 1, MainSpeedGen())
	SpawnFrontalWallRingEx(InvertMask(walls), thickness2 , 1, MainSpeedGen(),\
			thickness1+sct_time1*GetSectorTime()*MainSpeedGen().cur())
	return GetIntThicknessPlusSectorTime(thickness1+thickness2, sct_time1+sct_time2)

