# coding=UTF-8
import math

from globalVars import *
import gstt
import vectors
import frame
from vectors import Polar2D
import sounds

class PlayArea(object):
	def __init__(self):
		self.play_area_rsize = play_area_rsize
		self.black_hole_rsize = black_hole_rsize
		self.spokes = DEFAULT_SPOKES
		self.side_count = DEFAULT_SIDE_COUNT
		# Réarrangement nombre de côtés
		self.partial_side = 0.
		self.rearrange_sides = 0	# +-1 pour activer
		# Rotation
		self.theta = 0;
		self.dtheta = .6;
		# Effet de zoom
		self.zoom_bh = 1;
		self.zoom_game = 1;
		# offset pour secousse crash
		self.xy_offset = vectors.Vector2D(0,0)
		# matrice de rotation 3D pour effet d'inclinaison
		self.vx3D = vectors.Vector2D(0,0)
		self.vy3D = vectors.Vector2D(0,0)
		self.vz3D = vectors.Vector2D(0,0)
		# Echelle du z
		self.z_origin = 1
		# TODO : calculer le facteur en fonction de la taille du jeu
		# pour ne jamais tomber à 0 ou en-dessous
		self.z_factor = 0.001
		# Paramètres de l'effet d'inclinaison
		self.a_tilt = -0
		self.a_axis = 0
		# Mise en cache des coordonnées du centre de l'aire de jeu
		# (utilisées partout)
		# ce n'est pas optimal mais...
		self.xy_center = vectors.Vector2D(screen_size[0]/2, screen_size[1]/2)

		# Vitesse principale
		self.main_speed = 2
		
		# Planification réarrangement
		self.sidechanger_r = 0
		self.sidechanger_r_to_player = 0
		self.sidechanger_value = 0

	def GetCurrentSideCount(self):
		return self.side_count + int(math.ceil(self.partial_side))
	
	def Move(self):
		# Vitesse de rotation constante
		self.theta += self.dtheta
		if self.theta < 0.: self.theta += 360.
		elif self.theta >= 360.: self.theta -= 360.

		# Réarrangement nombre de côtés
		if self.rearrange_sides < 0:
			if self.side_count <= 3:
				self.rearrange_sides = 0
			else:
				self.partial_side -= DREARRANGE_SIDES
				if self.partial_side <= self.rearrange_sides:
					self.partial_side = 0
					self.side_count += self.rearrange_sides
					self.rearrange_sides = 0
		elif self.rearrange_sides > 0:
			self.partial_side += DREARRANGE_SIDES
			if self.partial_side >= self.rearrange_sides:
				self.partial_side = 0
				self.side_count += self.rearrange_sides
				self.rearrange_sides = 0
		# Re-calcul liste angles
				
		self.spokes = [i*360./(self.side_count + self.partial_side) for i in xrange(0,self.side_count + int(math.ceil(self.partial_side)))]

	def MoveSideChanger(self):
		# Déclenchement réarrangement
		if (self.sidechanger_r):
			self.sidechanger_r -= self.main_speed
			if self.sidechanger_r < player_r + self.sidechanger_r_to_player:
				self.rearrange_sides = self.sidechanger_value
				self.sidechanger_r = 0
				sounds.play_sndfx_area_resize(True)


	def ScheduleSideChange(self, r_to_player, rearrange_sides):
		# TODO : plutôt une file si jamais les changements de scène sont trop proches
		# et que l'un pas encore fait soit annulé par le suivant
		self.sidechanger_r = play_area_rsize
		self.sidechanger_r_to_player = r_to_player
		self.sidechanger_value = rearrange_sides
	
	def CancelSideChange(self):
		self.sidechanger_r = 0;
		self.rearrange_sides = 0;
	
	
	# Fonctions de transformation qui seront appelées par les routines de dessin
	# aussi bien de la scène que des murs et du joueur
	def CalcRotoZoom(self,p):
		return vectors.Polar2D(
		self.black_hole_rsize*self.zoom_bh + self.zoom_game * (p.r - self.black_hole_rsize),
		p.theta + self.theta)
		
	def Update3DEffectMatrix(self):
		a_tilt_rd = math.radians(self.a_tilt)
		a_axis_rd = math.radians(self.a_axis)
		c_tilt, s_tilt = math.cos(a_tilt_rd), math.sin(a_tilt_rd)
		c_axis, s_axis = math.cos(a_axis_rd), math.sin(a_axis_rd)
		c_tilt1 = 1-c_tilt
		
		self.vx3D.x = c_tilt + c_tilt1*c_axis*c_axis
		self.vx3D.y = c_tilt1*c_axis*s_axis
		self.vy3D.x = self.vx3D.y
		self.vy3D.y = c_tilt + c_tilt1*s_axis*s_axis
		self.vz3D.x = s_tilt*s_axis
		self.vz3D.y = s_tilt*c_axis
		
	def Calc3DEffect(self,v):
		zdiv = self.z_factor * v.ScalarProduct(self.vz3D) + self.z_origin
		return (v + self.xy_offset).MatrixProduct(self.vx3D,self.vy3D) / zdiv

	def Draw(self,f):
		pts_bh = []
	# SIMPLIFICATION : bien qu'on pourrait réaliser des transformations de scène bien tordues
		# (cf Super Polygon), on simplifie et on reste à celle de Super Hexagon
		for a in self.spokes:
			xy_bh = self.xy_center + self.Calc3DEffect(self.CalcRotoZoom(vectors.Polar2D(self.black_hole_rsize, a)).ToXY())
			xy_area = self.xy_center + self.Calc3DEffect(self.CalcRotoZoom(vectors.Polar2D(self.play_area_rsize, a)).ToXY())

			pt_bh = (xy_bh.x,xy_bh.y)
			pts_bh.append(pt_bh)

			f.Line(pt_bh,(xy_area.x,xy_area.y),gstt.lvl.SPOKE_COLOR)
			#f.Line((xy_area.x,xy_area.y),pt_bh,self.spoke_color)

		f.PolyLineOneColor(pts_bh,gstt.lvl.BLACK_HOLE_COLOR,True)

