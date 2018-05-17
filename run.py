from psychopy import visual, event
import ratcave as rc
import random
import time
import sys
import numpy as np
import csv
import config


# Build Stimuli and Position them.s
reader = rc.WavefrontReader('stimuli/rotstim.obj')
stim_orig = reader.get_mesh('OrigStim', position=(-.25, 0., -1), rotation=(0, config.YROT, 0), scale=config.SCALE)
stim_orig2 = reader.get_mesh('OrigStim', position = (.25, 0., -1), rotation=(0, config.YROT, 0), scale=config.SCALE)
stim_flipped = reader.get_mesh('FlippedStim', position = (.25, 0., -1), rotation=(0, config.YROT, 0), scale=config.SCALE)

# Make Groups of Stimuli to refer to in experiment
stims = [stim_orig, stim_orig2, stim_flipped]
condA = [stim_orig, stim_orig2]
condB = [stim_orig, stim_flipped]


window = visual.Window(fullscr=config.FULLSCREEN, allowStencil=True)

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

scene = rc.Scene(meshes=[], bgColor=config.BGCOLOR)
scene.light.position.z = 20
scene.camera.projection = rc.OrthoProjection(origin='center', coords='relative')
camera = scene.camera


fixcross = visual.TextStim(window, text='+', alignVert='center', alignHoriz='center')


with open('data/explog.csv', 'w') as logfile:


    fieldnames = ['Trial', 'Match', 'RotationA', 'RotationB', 'Correct', 'RT']
    logwriter = csv.DictWriter(logfile, fieldnames=fieldnames)
    logwriter.writeheader()

    for tt in range(1, config.NUM_TRIALS + 1):

        xrot = random.choice(config.ROT_STARTS)
        for stim in stims:
            stim.rotation.x = xrot
        xrot_offset = random.choice(config.ROT_OFFSETS)
        for stim in [stim_orig2, stim_flipped]:
            stim.rotation.x += xrot_offset

        condition = random.choice([condA, condB])
        scene.meshes = condition

        # Draw Fixation Cross
        scene.clear()
        fixcross.draw()
        window.flip()
        time.sleep(1.)


        with rc.default_shader:
            scene.draw()
        window.flip()

        # Collect Response
        start_time = time.clock()
        resp = event.waitKeys()
        response_time = time.clock() - start_time

        if 'escape' in resp:
            window.close()
            sys.exit()
        assert 'left' in resp or 'right' in resp

        correct_resp = 'left' if condition == condA else 'right'
        correct = correct_resp in resp

        # Log Trial Data
        trialdata = {'Trial': tt,
                     'Match': True if condition == condA else False,
                     'RotationA': xrot,
                     'RotationB': xrot + xrot_offset,
                     'Correct': correct,
                     'RT': response_time}
        logwriter.writerow(trialdata)

        # Provide Feedback for Response
        for rot in np.linspace(xrot, xrot + xrot_offset, 15):
            stim_orig.rotation.x = rot
            stim_orig.update()
            with rc.default_shader:
                scene.draw()
            window.flip()

        feedback_color = (0., .5, 0.) if correct else (.5, 0., 0.)
        for color, pauseTime in zip([feedback_color, config.BGCOLOR], [1.5, .001]):
            scene.bgColor = color
            with rc.default_shader:
                scene.draw()

            window.flip()
            time.sleep(pauseTime)









