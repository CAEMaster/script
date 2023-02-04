import time
import math
import random    
from abaqus import*     
from abaqusConstants import *
import assembly
import displayGroupMdbToolset as dgm
import sys

W = float(getInput('请输入随机圆范围长度  :'))   
H = float(getInput('请输入随机圆范围宽度 :'))
R1 = float(getInput('请输入最小圆的半径 :')) 
gas_value = float(getInput('请输入圆与圆之间最小的间隙 :')) 
R_change =  float(getInput('请输入圆变型率 如:0 半径不变 0.1 0.2 ...... :')) 

HW, HH = W / 2, H / 2
AREA = W * H

class circle:
	def __init__(self, x, y, id):
		self.x = x
		self.y = y
		self.radius = R1
		self.id = id
		self.active = True

circles = []

find_space_attempts = 0
max_find_space_attempts = 500000
exit = False
gap = R1 + gas_value

area_covered = 0.0
percentage_covered = 0
last_reported_percentage = 20          #### -1

while True:
	while True:
		x = random.uniform(0+R1, W - R1)
		y = random.uniform(0+R1, H - R1)
		
		found_space = True
		for c in circles:
			distance = math.hypot(c.x - x, c.y - y)
			if distance <= c.radius + gap:
				found_space = False
				break
		if found_space: break
		find_space_attempts += 1
		if find_space_attempts >= max_find_space_attempts:
			exit = True
			break
	
	if exit: break
	circles.append(circle(x, y, len(circles)))
	
	for c in circles:
		if not c.active: continue
		for C in circles:
			if c.id == C.id: continue
			
			distance_between_circles = math.hypot(c.x - C.x, c.y - C.y)
			combined_radius = c.radius + C.radius
			
			if distance_between_circles - combined_radius <= gap:
				c.active = False
				if C.active:
					area_covered += (C.radius ** 2) * math.pi
				C.active = False
				
				area_covered += (c.radius ** 2) * math.pi
				percentage_covered = int((area_covered / AREA) * 100)
				if last_reported_percentage != percentage_covered:
					print ( percentage_covered )
					last_reported_percentage = percentage_covered
				break
				
		if c.active: c.radius += R_change ################max R

print ("Circles Generated!")
print ("Saving File.")

num = len(circles)
xyz = []
r_list = []
area_list = []
for i in range(num):
	xyz.append((circles[i].x,circles[i].y,circles[i].radius))
	r_list.append(circles[i].radius)
	area_list.append(math.pi*(circles[i].radius**2))

print ('done')
ratio_V = sum(area_list)/AREA



start_time =time.clock()

Mdb()
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=2000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0, 0), point2=(W, H))
p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-1']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['Part-1']
f, e, d1 = p.faces, p.edges, p.datums
t = p.MakeSketchTransform(sketchPlane=f[0], sketchPlaneSide=SIDE1, origin=(
    0.0, 0.0, 0.0))
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=223.6, gridSpacing=5.59, transform=t)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=SUPERIMPOSE)
p = mdb.models['Model-1'].parts['Part-1']
p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
for i in range(num):
	s.CircleByCenterPerimeter(center=(xyz[i][0], xyz[i][1]), point1=(xyz[i][0]+xyz[i][2], xyz[i][1]))

print ('done')
p = mdb.models['Model-1'].parts['Part-1']
pickedFaces = f[0:1]
e, d1 = p.edges, p.datums
p.PartitionFaceBySketch(faces=pickedFaces, sketch=s)
s.unsetPrimaryObject()
del mdb.models['Model-1'].sketches['__profile__']

print  '最大半径为：' ,max(r_list)
print (num)
print ( percentage_covered )
print(ratio_V)
print ('done')
