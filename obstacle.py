# coding=UTF-8
'''
Created on 1 janv. 2015

@author: pclf
'''
from globalVars import *
import vectors
import gstt

def DiffAngle(a1,a2):
	return ((a1 + 180 - a2) % 360) - 180

class WallRing(object):
	'''
	Fonctionnalités communes des obstacles
	'''


	def __init__(self, r, theta, dr_gen, dtheta_gen, linked_to_pa, walls, dr_gen_parent=None, dtheta_gen_parent=None):
		'''
		Constructor
		'''
		self.r = r
		self.theta = theta
		self.dr_gen = dr_gen
		self.dr_gen.setParent(self if dr_gen_parent is None else dr_gen_parent)
		self.dtheta_gen = dtheta_gen
		self.dtheta_gen.setParent(self if dtheta_gen_parent is None else dtheta_gen_parent)
		self.linked_to_pa = linked_to_pa
# 		self.wall_count = 0
# 		if wall_count is None:
# 			self.linked_to_pa = True
# 		else:
# 			self.linked_to_pa = False
# 			self.wall_count = wall_count
		self.walls = walls
		self.angles = []
		# Données de collision du coup précédent, pour tests collisions
		# par transitions
		# (déterminants ou différences d'angles selon le cas)
		self.collision_data_prev = []

	def GetProcessedSideCount(self):
		'''
 		Retourne le nombre de faces à traiter pour les tests de collision ou l'affichage <- aire de jeu ou figé
 		'''
		wall_count = len(self.walls)
		if self.linked_to_pa:
			return min(wall_count, gstt.pa.GetCurrentSideCount())
		else:
			return wall_count

	def GetModuloSideCount(self):
		'''
 		Retourne le modulo qu'il faut faire sur l'indice de l'angle à choisir
 		'''
		wall_count = len(self.walls)
		if self.linked_to_pa:
			return gstt.pa.GetCurrentSideCount()
		else:
			return wall_count

	def RecalcAngles(self):
		if self.linked_to_pa:
			self.angles = gstt.pa.spokes
			self.theta = 0
		else:
			wall_count = len(self.walls)
			self.angles = [self.theta + i*360./wall_count for i in xrange(0,wall_count)]

	def GetColor(self):
		return gstt.lvl.LINKED_WALL_COLOR if self.linked_to_pa else gstt.lvl.FREE_WALL_COLOR

	def MoveAngular(self):
		'''
		Déplacement (angulaire et radial)
		'''
		self.theta += self.dtheta_gen.cur()

	def MoveRadial(self):
		'''
		Déplacement (angulaire et radial)
		'''
		# En dur car pas d'autre solution pour le moment :
		# pas de déplacement radial pendant que la scène se réarrange
		if gstt.pa.rearrange_sides == 0:
			self.r -=self.dr_gen.cur()

	def Move(self):
		'''
		Déplacement (angulaire et radial)
		'''
		self.MoveAngular()
		self.MoveRadial()


class FrontalWallRing(WallRing):
	'''
	Anneaux de murs frontaux
 	'''
	def __init__(self, r, theta, dr_gen, dtheta_gen, linked_to_pa, walls, dr_gen_parent=None, dtheta_gen_parent=None):
		super(FrontalWallRing, self).__init__(r, theta, dr_gen, dtheta_gen, linked_to_pa, walls, dr_gen_parent, dtheta_gen_parent)
		# Mise en cache des coordonnées de points pour faciliter
		self.cached_xy = []
	
	def IsSideType(self):
		return False
	
	def RecalcCachedPoints(self):
		self.cached_xy = [vectors.Polar2D(self.r, a).ToXY() for a in self.angles]
	
	def RecalcAngles(self):
		#WallRing.RecalcAngles(self)	
		super(FrontalWallRing, self).RecalcAngles()
		self.RecalcCachedPoints()
	
	def UpdateCollisionData(self, player):
		'''
		Recalcule les données de collision afin de disposer d'un "état précédent" pour
		détecter des franchissements
		'''
		self.RecalcCachedPoints()
		self.collision_data_prev = []
		modulo_side_count = self.GetModuloSideCount()
		for i in xrange(0,len(self.angles)):
			xy_i = self.cached_xy[i]
			self.collision_data_prev.append((player.GetXY()-xy_i).Det(self.cached_xy[(i+1) % modulo_side_count]-xy_i))

	def CollideWith(self, player):
		'''
		Teste la collision avec le joueur
		'''
		# Collision frontale :
		# trouver le secteur dans lequel le joueur se trouve.
		# Si un mur est présent et si le joueur change de demi-plan défini par la
		# droite contenant le mur, alors il y a collision.
		# Pour savoir dans quel dei-plan on se trouve, on utilise un déterminant.
		
		# Note : on doit itérer sur tous les secteurs pour chercher dans lequel
		# se trouve le joueur, au cas où l'on veuille avoir des secteurs
		# de tailles non uniformes
		modulo_side_count = self.GetModuloSideCount()
		for i in xrange(0,self.GetProcessedSideCount()):
			# Cas où on passe de n à n+1 murs dans un obstacle lié à la scène :
			# ignorer le côté dernièrement apparu (pas de valeur de collision précédente) 
			if i < len(self.collision_data_prev):
				if self.walls[i] and DiffAngle(player.theta, self.angles[i]) >= 0 and DiffAngle(player.theta, self.angles[(i+1) % modulo_side_count]) < 0:
					xy_i = self.cached_xy[i]
					collision_data = (player.GetXY()-xy_i).Det(self.cached_xy[(i+1) % modulo_side_count]-xy_i)
					if (collision_data >= 0) != (self.collision_data_prev[i] >= 0):
						return True
		return False

	def IsFullyInBH(self):
		'''
		Teste si l'élément a totalement été absorbé par le trou noir
		afin qu'il puisse être supprimé
		'''
		return self.r < black_hole_rsize

	def Draw(self,f):
		'''
		Dessine l'obstacle
		'''
		# Ne pas afficher si trop loin (éviter erreurs calcul transformation 3D par diviseur Z nul ou négatif)
		if self.r < black_hole_rsize or self.r > play_area_rsize:
			return
		pa = gstt.pa
		c_wall = self.GetColor()
		modulo_side_count = self.GetModuloSideCount()
		# Limite de boucle : une position de + pour dessiner le dernier côté
		for i in xrange(0,self.GetProcessedSideCount()+1):
			i2 = i % modulo_side_count
			# Couleur du sommet : 0 pour le 1er (repositionnement, laser éteint)
			# la couleur du mur pour les sommets suivants
			c = 0 if i == 0 or not self.walls[i-1] else c_wall
			# TODO : BUG à corriger : dans certains cas, i2 dépasse le nombre d'éléments de la liste d'angles.
			xy = pa.xy_center + pa.Calc3DEffect(pa.CalcRotoZoom(vectors.Polar2D(self.r, self.angles[i2])).ToXY())
			f.LineTo(xy.ToTuple(), c)


class SideWallRing(WallRing):
	'''
	Anneaux de murs latéraux
 	'''
	def __init__(self, r, l, theta, dr_gen, dtheta_gen, linked_to_pa, walls, dr_gen_parent=None, dtheta_gen_parent=None):
		super(SideWallRing, self).__init__(r, theta, dr_gen, dtheta_gen, linked_to_pa, walls, dr_gen_parent, dtheta_gen_parent)
		# Longueur des murs (doit être >0)
		self.l = l
		# Angles au coup d'avant, pour calculer variations servant à repousser le joueur
		# (la variation n'est pas seulement due à la rotation éventuelle du mur,
		# mais aussi au redimensionnement de la scène)
		self.angles_prev = []
		# Mise en cache des coordonnées de points pour faciliter
		self.cached_xy = []
	
	def IsSideType(self):
		return True
		
	def UpdateCollisionData(self, player):
		'''
		Recalcule les données de collision afin de disposer d'un "état précédent" pour
		détecter des franchissements
		'''
		# Recalcul points en cache, mais par rapport au rayon du haut.
		self.cached_xy = [vectors.Polar2D(self.r + self.l, a).ToXY() for a in self.angles]
		modulo_side_count = self.GetModuloSideCount()
		
		self.collision_data_prev = []
		for i in xrange(0,len(self.angles)):
			# Détermination de la limite supérieure de la zone de présence du joueur
			# où il faudra tester une collision de répoulsion.
			# Cette zone est délimitée par le prolongement de murs frontaux fictifs entre
			# les sommets supérieurs.
			# C'est nécessaire d'étendre le test jusque dans cette zone sinon le joueur
			# peut passer dans le secteur voisin et en cas de mur frontal qu'on est
			# censé contourner, un crash est détecté.
			xy_i = self.cached_xy[i]				
			front_coldata_left = (player.GetXY()-xy_i).Det(self.cached_xy[(i-1) % modulo_side_count]-xy_i)
			front_coldata_right = (player.GetXY()-xy_i).Det(self.cached_xy[(i+1) % modulo_side_count]-xy_i)
			# Données de collision précédentes = ici, présence dans secteur et dans "zone" ci-dessus
			self.collision_data_prev.append((front_coldata_left >= 0 or front_coldata_right <= 0,
										DiffAngle(player.theta, self.angles[i])))
		self.angles_prev = self.angles

	def CollideWith(self, player):
		'''
		Teste la collision avec le joueur.
		Au lieu de retourner True/False, retourne l'indice du mur (pour calculer la
		répulsion du joueur par rapport au bon mur), sinon None
		'''
		# Collision latérale :
		# vraie si le joueur passe d'un secteur à un autre là où il y a un mur,
		# et si le joueur se trouve à hauteur du mur
		# (attention, petite subtilité agrandissant la zone de test au voisinage du haut du mur
		# sinon si le mur radial est joint à un mur frontal adjacent, on arrive à se crasher dedans
		# par l'extérieur) 
		if player_r >= self.r:
			for i in xrange(0,self.GetProcessedSideCount()):
				# Cas où on passe de n à n+1 murs dans un obstacle lié à la scène :
				# ignorer le côté dernièrement apparu (pas de valeur de collision précédente) 
				if i < len(self.collision_data_prev) and self.collision_data_prev[i][0]:
					collision_data = DiffAngle(player.theta, self.angles[i])
					collision_data_prev = self.collision_data_prev[i][1]
					# Il faut aussi que le changement de signe ne se fasse pas par cyclage
					# au voisinage de 180
					if abs(collision_data) < 120 and abs(collision_data_prev) < 120:
						if self.walls[i] and (collision_data >= 0) != (collision_data_prev >= 0):
							return i
		return None

	def RepellAngle(self, idx_angle):
		return self.angles[idx_angle] - self.angles_prev[idx_angle]

	def IsFullyInBH(self):
		'''
		Teste si l'élément a totalement été absorbé par le trou noir
		afin qu'il puisse être supprimé
		'''
		return self.r + self.l < black_hole_rsize

	def Draw(self,f):
		'''
		Dessine l'obstacle
		'''
		r_bot = self.r
		r_top = r_bot + self.l
		if r_top < black_hole_rsize or r_bot > play_area_rsize:
			return
		# Tronquer bas ligne si dans le trou noir
		if r_bot < black_hole_rsize: r_bot = black_hole_rsize
		#... et haut ligne si au-delà de la taille de la scène
		if r_top > play_area_rsize: r_top = play_area_rsize
		pa = gstt.pa
		c_wall = self.GetColor()

		for i in xrange(0,self.GetProcessedSideCount()):
			if self.walls[i]:
				xy_bot = pa.xy_center + pa.Calc3DEffect(pa.CalcRotoZoom(vectors.Polar2D(r_bot, self.angles[i])).ToXY())
				xy_top = pa.xy_center + pa.Calc3DEffect(pa.CalcRotoZoom(vectors.Polar2D(r_top, self.angles[i])).ToXY())
				f.Line(xy_bot.ToTuple(), xy_top.ToTuple(), c_wall)

			
