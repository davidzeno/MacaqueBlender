# -*- coding: utf-8 -*-
"""============================ RenderGazeStills.py ==================================

This script loops through the specified stimulus variables, rendering static images
for each condition requested.

06/07/2016 - Written by APM (murphyap@mail.nih.gov)
06/02/2017 - Updated for final rigged model (APM)
12/05/2017 - Updated to render stills for gaze direction stimuli
18/06/2018 - Updated to render depth maps for RDS
"""

import bpy
import mathutils as mu
import math
import numpy as np
import socket
#import AddDepthArray

from InitBlendScene import InitBlendScene
from GetOSpath import GetOSpath
import OrientAvatar as OA
from SetDepthMapMode import SetDepthMapMode


bpy.types.UserPreferencesEdit.keyframe_new_interpolation_type = 'LINEAR'    # F-curve interpolation defaults to linear


#============ Initialize scene
Prefix              = GetOSpath()                                   # Get path prefix for OS
BlenderDir          = Prefix[1] + '/murphya/Stimuli/MacaqueAvatar/3D_Renders/'            
RenderDir           = BlenderDir + "BodyHeadGaze" #"PositionInDepth"
SetupGeometry       = 2                                             # Specify which physical setup stimuli will be presented in
StereoFormat        = 1                                             # Render as stereo-pair?
ViewingDistance     = 100                                           # Distance of subject from screen (cm) 
InitBlendScene(SetupGeometry, StereoFormat, ViewingDistance)        # Initialize scene
#AddDepthArray()                                                     # Add depth array?

#============ Set rendering parameters						
GazeElAngles    = [0]#[-20,-10, 0, 10, 20]                              # Set elevation angles (degrees)
GazeAzAngles    = [0]#[-30, -20, -10, 0, 10, 20, 30]                    # Set azimuth angles (degrees)
HeadElAngles    = [0]
HeadAzAngles    = [0]
BodyElAngles    = [-20,-10, 0, 10, 20] 
BodyAzAngles    = [-30, -20, -10, 0, 10, 20, 30] 
#Distances       = [-20, 0, 20] 						             # Set object distance from origin (centimeters)
#Scales          = [0.666, 1.0, 1.333]                               # Physical scale of object (proportion)
Distances       = [0] 						                        # Set object distance from origin (centimeters)
Scales          = [1.0]                                             # Physical scale of object (proportion)
FurLengths      = [0.7]                                             # Set relative length of fur (0-1)
ExpStr          = ["Neutral","Fear","Threat","Coo","Yawn"]          # Expression names   
ExpNo           = [0] #[0, 1, 2, 3, 4]                              # Expression numbers
ExpWeights      = np.matrix([[0,0,0,0], [1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]])
ExpMicroWeights = np.matrix([[0,0,0,0.5],[1,0,0,0.5],[0,1,0,0.5],[0,0,1,0.5]])
mexp            = 0

ShowBody            = 1;                                            # Turn on/ off body visibility
IncludeEyesOnly     = 0;                                            # Include eyes only condition? 
InfiniteVergence    = 0;                                            # Fixate (vergence) at infinity?
GazeAtCamera        = 0;                                            # Update gaze direction to maintain eye contact with camera?

NoConditions        = len(HeadElAngles)*len(HeadAzAngles)*len(GazeElAngles)*len(GazeAzAngles)*len(Distances)*len(Scales)*len(ExpNo)        # Calculate total number of conditions
if IncludeEyesOnly == 1:
    NoConditions = NoConditions*2;                      
    
msg                 = "Total renders = %d" % NoConditions				
print(msg)


#=============== Set cyclopean eye as avatar origin point?
head                = bpy.data.objects["HeaDRig"]
body                = bpy.data.objects["Root"]
body.rotation_mode  = 'XYZ'
OffsetCyclopean     = 0                                         # Translate whole avatar so that cyclopean eye is always in the same position?
CyclopeanOrigin     = ((0,0,0))                                 # World coordinate to move cyclopean eye to (if OffsetCyclopean = 1)

bpy.context.scene.cursor_location   = CyclopeanOrigin           # Set current cursor position to cyclopean eye coordinates
bpy.context.scene.objects.active    = body                      # Set avatar rig as active object
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')                 # Set origin of avatar to cyclopean eye                                   

#bpy.ops.object.mode_set(mode='POSE')
OrigBodyLoc         = body.location 
OrigBodyScale       = body.scale


if ShowBody == 0:
    bpy.data.objects['BodyZremesh2'].hide_render = True                         # Hide body from rendering
    
# bpy.data.particles["ParticleSettings.003"].path_end           = fl            # Set fur length (0-1)
# head.pose.bones['Head'].constraints['IK'].mute                = True          # Turn off constraints on head orientation
# head.pose.bones['HeadTracker'].constraints['IK'].influence    = 0             


#========================== Begin rendering loop
for exp in ExpNo:

    #======= Set primary expression
    head.pose.bones['yawn'].location    = mu.Vector((0,0,0.02*ExpWeights[exp,3]))           # Wide mouthed 'yawn' expression
    head.pose.bones['Kiss'].location    = mu.Vector((0,0.02*ExpWeights[exp,2],0))           # Pursed lip 'coo' expression
    head.pose.bones['jaw'].location     = mu.Vector((0,0,0.02*ExpWeights[exp,1]))           # Open-mouthed 'threat' expression
    head.pose.bones['Fear'].location    = mu.Vector((0,-0.02*ExpWeights[exp,0],0))          # Bared-teeth 'fear' grimace

    #======= Set micro expression
    head.pose.bones['blink'].location   = mu.Vector((0,0,0.007*ExpMicroWeights[mexp, 0]))   # Close eye lids (blink)
    head.pose.bones['ears'].location    = mu.Vector((0,0.04*ExpMicroWeights[mexp, 1],0))    # Retract ears
    head.pose.bones['eyebrow'].location = mu.Vector((0,0,-0.02*ExpMicroWeights[mexp, 2]))   # Raise brow
    head.pose.bones['EyesTracker'].scale = mu.Vector((0, 1*ExpMicroWeights[mexp, 3], 0))    # Pupil dilation/ constriction

    for s in Scales:
        body.scale = mu.Vector((OrigBodyScale[0]*s, OrigBodyScale[1]*s, OrigBodyScale[2]*s))        # Apply scaling to entire avatar
    
        for d in Distances:
            body.location = mu.Vector((OrigBodyLoc[0], OrigBodyLoc[1]+d/100, OrigBodyLoc[2])) 

            for Bel in BodyElAngles:
                for Baz in BodyAzAngles:
                
                    
                    for Hel in HeadElAngles:
                        for Haz in HeadAzAngles:
                            
                            for Gel in GazeElAngles:
                                for Gaz in GazeAzAngles:

                                    #=========== Rotate body, head, and gaze
                                    if GazeAtCamera == 1:                                                           # Gaze in direction of camera?
                                        if InfiniteVergence == 0:                                                   # Gaze converges at camera distance?
                                            CamLocation = bpy.data.scenes["Scene"].camera.location
                                            head.pose.bones['EyesTracker'].location = mu.Vector((0, 0.1, 0.9))
                                            FixationDistance = ViewingDistance
                                            
                                        elif InfiniteVergence == 1:                                                 # Gaze converges at (approximately) infinity?
                                            FixationDistance = 100
                                            OA.OrientAvatar((Bel, Baz), (Hel, Haz), (Gel, Gaz, FixationDistance))   # Apply rotations to body, head and gaze
                                    else:
                                        FixationDistance = ViewingDistance
                                        
                                    OA.OrientAvatar((Bel, Baz), (Hel, Haz), (Gel, Gaz, FixationDistance))           # Apply rotations to body, head and gaze
                                    
                                    #=========== Perform any necessary translations
                                    if OffsetCyclopean == 1:
                                        EyeLocations = OA.GetEyeLocations()                                         # Get current world coordinates for eye objects
                                        OA.CenterCyclopean(CyclopeanOrigin)                                         # Shift avatar to maintain position of cycloean eye at requested coordinates

                                    #=========== Render color and Z-buffer images
                                    for z in [0,1]:
                                        FileFormat = SetDepthMapMode(z)
                                        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                                        Filename = "MacaqueGaze_%s_Baz%d_Bel%d_Haz%d_Hel%d_Gaz%d_Gel%d_dist%d_scale%d%s" % (ExpStr[exp], Baz, Bel, Haz, Hel, Gaz, Gel, d, s*100, FileFormat)
                                        print("Now rendering: " + Filename + " . . .\n")
                                        bpy.context.scene.render.filepath = RenderDir + "/" + Filename
                                        bpy.ops.render.render(write_still=True, use_viewport=True)

print("Rendering completed!\n")




