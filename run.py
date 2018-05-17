from psychopy import visual, event
import ratcave as rc
import random
import time
import sys
import numpy as np
import csv
import config


# Make Psychopy visual stimuli
window = visual.Window(fullscr=config.FULLSCREEN, allowStencil=True, color=config.BGCOLOR)
fixcross = visual.TextStim(window, text='+', alignVert='center', alignHoriz='center')

# Make Ratcave stimuli
reader = rc.WavefrontReader('stimuli/rotstim.obj')
stim_orig = reader.get_mesh('OrigStim', position=(-.25, 0., -1), rotation=(0, config.YROT, 0), scale=config.SCALE)
stim_orig2 = reader.get_mesh('OrigStim', position = (.25, 0., -1), rotation=(0, config.YROT, 0), scale=config.SCALE)
stim_flipped = reader.get_mesh('FlippedStim', position = (.25, 0., -1), rotation=(0, config.YROT, 0), scale=config.SCALE)

scene = rc.Scene(meshes=[])
scene.light.position.z = 20
scene.camera.projection = rc.OrthoProjection(origin='center', coords='relative')

# Make Groups of Stimuli to refer to in experiment
stims = [stim_orig, stim_orig2, stim_flipped]
condA = [stim_orig, stim_orig2]
condB = [stim_orig, stim_flipped]



def show_instructions():
    msg = """
    3D Mental Rotation Study

    Press the left arrow if the two objects can be rotated into the same configuration, and the right if they are different.

    Feedback Color: Green means Correct, Red means Incorrect.
    """
    text = visual.TextStim(window, text=msg, alignVert='center')
    text.draw()
    window.flip()
    event.waitKeys()
show_instructions()


with open('data/explog.csv', 'w') as logfile:


    fieldnames = ['Trial', 'Match', 'RotationA', 'RotationB', 'Correct', 'RT']
    logwriter = csv.DictWriter(logfile, fieldnames=fieldnames)
    logwriter.writeheader()

    for tt in range(1, config.NUM_TRIALS + 1):

        xrot = random.choice(config.ROT_STARTS)
        xrot_offset = random.choice(config.ROT_OFFSETS)

        for stim in stims:
            stim.rotation.x = xrot
        for stim in [stim_orig2, stim_flipped]:
            stim.rotation.x += xrot_offset

        # Draw Fixation Cross
        scene.bgColor = config.BGCOLOR
        scene.clear()
        fixcross.draw()
        window.flip()
        time.sleep(1.)

        # Draw First set of stimuli
        scene.meshes = random.choice([condA, condB])
        with rc.default_shader:
            scene.draw()
        fixcross.draw()
        window.flip()

        # Collect Response
        start_time = time.clock()
        resp = event.waitKeys()
        response_time = time.clock() - start_time

        if 'escape' in resp:
            window.close()
            sys.exit()
        assert 'left' in resp or 'right' in resp

        correct_resp = 'left' if scene.meshes == condA else 'right'
        correct = correct_resp in resp

        # Log Trial Data
        trialdata = {'Trial': tt,
                     'Match': True if scene.meshes == condA else False,
                     'RotationA': xrot,
                     'RotationB': xrot + xrot_offset,
                     'Correct': correct,
                     'RT': response_time}
        logwriter.writerow(trialdata)

        # Provide Feedback for Response by rotating stimuli to same orientation
        for rot in np.linspace(xrot, xrot + xrot_offset, 15):
            stim_orig.rotation.x = rot
            with rc.default_shader:
                scene.draw()
            window.flip()
            time.sleep(.016)

        # Display green if correct and red if incorrect.
        scene.bgColor =  (0., .5, 0.) if correct else (.5, 0., 0.)
        with rc.default_shader:
            scene.draw()
        window.flip()
        time.sleep(1.5)

