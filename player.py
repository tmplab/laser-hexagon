# coding=UTF-8
'''
Created on 15 nov. 2014

@author: pclf
'''

from globalVars import *
import gstt
import vectors
import random
import sounds
#from main import *	# pour l'état du clavier


PLAYER_DRAWING = [(0,-4),(-4,-6),(0,2),(4,-6),(0,-4)]
PLAYER_TILT_MAX = 48
PLAYER_DTILT = 4
PLAYER_TCYCL_ONFIRE = 60
PLAYER_ONFIRE_MAX = 16
PLAYER_ONFIRE_MIN = 4
PLAYER_TDN_SWAP = 100
PLAYER_TDN_EXPLOSION = 50


class Shrapnel(object):
	
	def __init__(self, theta, dtheta):
		self.coord = vectors.Polar2D(0,random.uniform(theta-dtheta, theta+dtheta))
		self.spd = random.uniform(1,4)
		self.bar = vectors.Polar2D(random.randint(3,8),random.randint(0,359))
		self.bar_spd = random.uniform(6,12)* (2*random.randint(0,1)-1)
		
	def Move(self):
		self.coord.r += self.spd
		self.bar.theta += self.bar_spd
	
	# Pas de méthode Draw() ; on dessinera dans la méthode Draw() du joueur
		

class Player(object):
	'''
	classdocs
	'''


	def __init__(self, pa):
		'''
		Constructor
		'''
		self.theta = 0.
		self.theta_prev = 0.
		self.a_tilt = 0.
		self.tdn_swap = 0
		self.pa = pa
		# clignotement
		self.blinking = False
		self.tcycl_blink = 0
		# effet en feu
		self.tcycl_onfire = 0
		# explosion
		self.tdn_explosion = 0
		self.shrapnels = []
		self.crash_type = 0
		# Vitesse actuelle
		self.absdtheta = 4
	
	def GetXY(self):
		return vectors.Polar2D(player_r,self.theta).ToXY()
	
	def MoveTurn(self,keystate_left, keystate_right):
		# Déplacement G/D
		self.theta_prev = self.theta
		if keystate_left:
			self.theta -= self.absdtheta
			tilt = -PLAYER_TILT_MAX
		elif keystate_right:
			self.theta += self.absdtheta
			tilt = PLAYER_TILT_MAX
		else:
			tilt = 0
		# Inclinaison
		if self.a_tilt >= tilt + PLAYER_DTILT:
			self.a_tilt -= PLAYER_DTILT
		elif self.a_tilt <= tilt - PLAYER_DTILT:
			self.a_tilt += PLAYER_DTILT
		else:
			self.a_tilt = tilt
			
	def MoveSwap(self, keystate_swap):	
		if keystate_swap and self.tdn_swap == 0:
			self.tdn_swap = PLAYER_TDN_SWAP
			self.theta += 180
			sounds.play_sndfx_swap()
		if self.tdn_swap: self.tdn_swap -= 1

		if self.theta < 0.: self.theta += 360.
		elif self.theta >= 360.: self.theta -= 360.
	
	def Repell(self, dtheta):
		self.theta = self.theta_prev + dtheta 
		
	def Explode(self):
		self.tdn_explosion = PLAYER_TDN_EXPLOSION
		self.shrapnels = []
		if self.crash_type == 2:
			# Ecrasement
			for a in xrange(-6,12,6):
				self.shrapnels.append(Shrapnel(a,6))
				self.shrapnels.append(Shrapnel(a+180,6))
		else:
			# Crash frontal
			for a in xrange(-60,84,24):
				self.shrapnels.append(Shrapnel(a+180,15))
	
	def AnimateAfter(self):
		if self.tdn_swap or self.crash_type:
			self.tcycl_blink = 0 if self.tcycl_blink>=30 else self.tcycl_blink + 1
		else:
			self.tcycl_blink = 0

		if (self.crash_type):
			self.tcycl_onfire = 0 if self.tcycl_onfire>=PLAYER_TCYCL_ONFIRE else self.tcycl_onfire + 1
		else:
			self.tcycl_onfire = 0
			
		if self.tdn_explosion:
			for shrapnel in self.shrapnels:
				shrapnel.Move()
			self.tdn_explosion -= 1
	
	def Draw(self,f):
		# Dépendance à l'aire de jeu
		xy_center = self.pa.CalcRotoZoom(vectors.Polar2D(player_r,self.theta)).ToXY()
		# FLECHE
		# Angle de pivotement :
		theta = self.pa.theta + self.theta
		theta_tilt = theta + self.a_tilt
		# Base orthonormée pivotée
		vj = vectors.Polar2D(1,theta_tilt).ToXY()
		vi = vectors.Vector2D(vj.y, -vj.x)
		# couleur flèche
		c = gstt.lvl.PLAYER_FLASH_COLOR if (self.tdn_swap or self.crash_type) and self.tcycl_blink < 20 else gstt.lvl.PLAYER_COLOR
		# Dessin proprement dit
		f.PolyLineOneColor(((self.pa.xy_center + self.pa.Calc3DEffect(xy_center + vi * pt[0] + vj * pt[1])).ToTuple() for pt in PLAYER_DRAWING), c)
		
		# EFFET "EN FEU"
		if self.crash_type:
			for a in xrange(30,390,60):
				r = PLAYER_ONFIRE_MIN + self.tcycl_onfire * (PLAYER_ONFIRE_MAX - PLAYER_ONFIRE_MIN) / PLAYER_TCYCL_ONFIRE
				w = min(r * 0.6, PLAYER_ONFIRE_MIN)
				vj = vectors.Polar2D(1,theta + a).ToXY()
				vi = vectors.Vector2D(vj.y, -vj.x)
				f.Line((self.pa.xy_center + self.pa.Calc3DEffect(xy_center + vj*r + vi*w)).ToTuple(),
					(self.pa.xy_center + self.pa.Calc3DEffect(xy_center + vj*r - vi*w)).ToTuple(), DEFAULT_PLAYER_EXPLODE_COLOR)
		
		# EXPLOSION		
		if (self.tdn_explosion):
			for shrapnel in self.shrapnels:
				xy_shrp = vectors.Polar2D(shrapnel.coord.r,theta+shrapnel.coord.theta).ToXY() + xy_center
				xy_bar = vectors.Polar2D(shrapnel.bar.r,shrapnel.bar.theta).ToXY()
				f.Line((self.pa.xy_center + self.pa.Calc3DEffect(xy_shrp - xy_bar)).ToTuple(),\
						(self.pa.xy_center + self.pa.Calc3DEffect(xy_shrp + xy_bar)).ToTuple(),\
						DEFAULT_PLAYER_EXPLODE_COLOR)
				
				