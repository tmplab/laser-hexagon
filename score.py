# coding=UTF-8
'''
Created on 25 janv. 2015

@author: pclf
'''

import gstt
import vectors
from globalVars import *


ZOOM_PLAYING = .5
ZOOM_GAMEOVER = 5.0
DZOOM_PLAYING = -.4
DZOOM_GAMEOVER = .1

# Finalement, on implémente le score ici
DIGITS_GRAPHICS = [
	[[(-10,10), (10,-10), (10,10), (0,20), (-10,10), (-10,-10), (0,-20), (10,-10)]],
	[[(-10,-10), (0,-20), (0,20)], [(-10,20), (10,20)]],
	[[(-10,-10), (0,-20), (10,-10), (10,0), (-10,20), (10,20)]],
	[[(-10,-20), (0,-20), (10,-10), (0,0), (10,10), (0,20), (-10,20)]],
	[[(10,10), (-10,10), (0,-20), (0,20)]],
	[[(10,-20), (-10,-20), (-10,0), (0,0), (10,10), (0,20), (-10,20)]],
	[[(10,-20), (0,-20), (-10,-10), (-10,20), (0,20), (10,10), (10,0), (-10,0)]],
	[[(-10,-20), (10,-20), (-10,20)]],
	[[(-10,10), (10,-10), (0,-20), (-10,-10), (10,10), (0,20), (-10,10)]],
	[[(10,0), (-10,0), (-10,-10), (0,-20), (10,-20), (10,10), (0,20), (-10,20)]],
	[[(-2,15), (2,15)]]	# Point
]


class Score(object):
	'''
	classdocs
	'''


	def __init__(self, play_area):
		'''
		Constructor
		'''
		self.value = 0
		self.play_area = play_area
		self.zoom = ZOOM_GAMEOVER
		
	def Reset(self):
		self.value = 0
		
	def Increase(self):
		self.value += 1
	
	def ZoomIn(self):
		self.zoom += DZOOM_GAMEOVER
		if self.zoom > ZOOM_GAMEOVER:
			self.zoom = ZOOM_GAMEOVER
	
	def ZoomOut(self):
		self.zoom += DZOOM_PLAYING
		if self.zoom < ZOOM_PLAYING:
			self.zoom = ZOOM_PLAYING

	def ZoomReset(self):
		self.zoom = ZOOM_PLAYING
		
	def Draw(self, f):
		value_temp = self.value
		rg_digit = 0
		chars = []
		while rg_digit < 4 or value_temp:
			chars.append(value_temp % 10)
			value_temp //= 10
			rg_digit += 1
		chars.insert(2, 10)
		if gstt.fs == GAME_FS_PLAY:
			del chars[0]
		self.DrawChars(f, chars)
	
	def DrawChars(self, f, chars):
		xy_center = self.play_area.xy_center
		l = len(chars)
		for i, ch in enumerate(chars):
			x_offset = 12 * (l- 1 - 2*i)
			digit_pl_list = DIGITS_GRAPHICS[ch]
			for pl in digit_pl_list:
				pl_draw = []
				for xy in pl:
					xy_draw = xy_center + self.play_area.Calc3DEffect(vectors.Vector2D(xy[0] + x_offset,xy[1]) * self.zoom)
					pl_draw.append(xy_draw.ToTuple())
				f.PolyLineOneColor(pl_draw, 0xFFFFFF)
		
		
		
		