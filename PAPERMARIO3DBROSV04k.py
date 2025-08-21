from ursina import *
from panda3d.core import ClockObject, loadPrcFileData
from direct.showbase.ShowBaseGlobal import globalClock

# Suppress specific warnings
loadPrcFileData('', 'notify-level-windisplay fatal')  # Suppress icon not found warning
loadPrcFileData('', 'notify-level-pnmimage fatal')    # Suppress iCCP PNG profile warning

# Set frame rate limit once at the start
app = Ursina(size=(600, 400), borderless=False, development_mode=False)
globalClock.setMode(ClockObject.MLimited)
globalClock.setFrameRate(60)

# Flatten entities to mimic 'paper' look by scaling Z very thin
class PaperEntity(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scale_z = 0.05  # Even thinner for Super Paper Mario effect

# Global mode: True for 2D, False for 3D
is_2d = True

# Player (Mario composed of parts for better graphics)
player = PaperEntity(model='quad', color=color.blue, scale=(0.8, 1.2), position=(0, 1, 0), collider='box')  # Overalls
player_head = PaperEntity(parent=player, model='circle', color=color.peach, scale=(0.8, 0.8), y=0.8)  # Head
player_hat = PaperEntity(parent=player, model='quad', color=color.red, scale=(0.9, 0.4), y=1.1)  # Hat
player_eye_left = PaperEntity(parent=player_head, model='circle', color=color.white, scale=(0.2, 0.3), x=-0.2)  # Left eye
player_eye_right = PaperEntity(parent=player_head, model='circle', color=color.white, scale=(0.2, 0.3), x=0.2)  # Right eye
player_pupil_left = PaperEntity(parent=player_eye_left, model='circle', color=color.black, scale=(0.5, 0.5))  # Left pupil
player_pupil_right = PaperEntity(parent=player_eye_right, model='circle', color=color.black, scale=(0.5, 0.5))  # Right pupil
player_mustache = PaperEntity(parent=player_head, model='quad', color=color.black, scale=(0.6, 0.2), y=-0.3)  # Mustache
player.velocity_y = 0
player.gravity = 0.03
player.jump_height = 0.5
player.grounded = False

# HUD like Super Mario Bros. (since SMB64 is a remake, HUD is similar to SMB: score, coins, world, time)
hud_mario = Text('MARIO', position=(-0.8, 0.45), scale=1.5, color=color.white)
hud_score = Text('000000', position=(-0.8, 0.4), scale=1.5, color=color.white)
hud_coins = Text('x00', position=(-0.4, 0.4), scale=1.5, color=color.white)  # Add coin icon if needed, but text for now
hud_world = Text('WORLD 1-1', position=(0, 0.45), scale=1.5, color=color.white)
hud_time = Text('400', position=(0.4, 0.4), scale=1.5, color=color.white)
time_remaining = 400  # Start time
score = 0
coins = 0

# List of collidable entities (grounds, platforms, blocks, pipes)
collidables = []

# Ground segments to create pits (adjusted for exact 1-1 pits)
# Main ground from 0 to ~58 (before first pit), pit ~58-62, then ~62 to ~134 (before second pit in pyramid), pit ~134-138, then ~138 to 200
ground1 = PaperEntity(model='cube', scale=(58, 1, 1), color=color.white, position=(29, 0, 0), collider='box', texture='grass')
collidables.append(ground1)
ground2 = PaperEntity(model='cube', scale=(72, 1, 1), color=color.white, position=(98, 0, 0), collider='box', texture='grass')  # 62 to 134
collidables.append(ground2)
ground3 = PaperEntity(model='cube', scale=(62, 1, 1), color=color.white, position=(169, 0, 0), collider='box', texture='grass')  # 138 to 200
collidables.append(ground3)

# Pipes (positions adjusted to match 1-1: first at ~28, 37, 46, 57 (fourth before pit), then 94 (bonus exit), 163 (inaccessible))
pipe1 = PaperEntity(model='cube', scale=(2, 4, 1), color=color.white, position=(28, 2, 0), collider='box', texture='brick')  # Height 2 tiles, but scale to 4 for height
collidables.append(pipe1)
pipe2 = PaperEntity(model='cube', scale=(2, 6, 1), color=color.white, position=(37, 3, 0), collider='box', texture='brick')  # Height 3
collidables.append(pipe2)
pipe3 = PaperEntity(model='cube', scale=(2, 8, 1), color=color.white, position=(46, 4, 0), collider='box', texture='brick')  # Height 4, bonus entry
collidables.append(pipe3)
pipe4 = PaperEntity(model='cube', scale=(2, 4, 1), color=color.white, position=(57, 2, 0), collider='box', texture='brick')  # Height 2
collidables.append(pipe4)
pipe5 = PaperEntity(model='cube', scale=(2, 4, 1), color=color.white, position=(94, 2, 0), collider='box', texture='brick')  # Bonus exit
collidables.append(pipe5)
pipe6 = PaperEntity(model='cube', scale=(2, 4, 1), color=color.white, position=(163, 2, 0), collider='box', texture='brick')  # Inaccessible
collidables.append(pipe6)

# ? blocks and bricks (adjusted positions to match 1-1)
# First ? at ~16 y=4
q1 = PaperEntity(model='cube', scale=(1, 1, 1), color=color.yellow, position=(16, 4, 0), collider='box', texture='white_cube')
Text(text='?', parent=q1, scale=10, color=color.black, billboard=True, position=(0,0,0.6))
collidables.append(q1)
# Six-block triangle ~22-25 y=4 bricks and ?, but based on desc, leftmost brick mushroom
brick_mushroom = PaperEntity(model='cube', scale=(1, 1, 1), color=color.white, position=(22, 4, 0), collider='box', texture='brick')  # Mushroom
collidables.append(brick_mushroom)
q_coin1 = PaperEntity(model='cube', scale=(1, 1, 1), color=color.yellow, position=(23, 4, 0), collider='box', texture='white_cube')
Text(text='?', parent=q_coin1, scale=10, color=color.black, billboard=True, position=(0,0,0.6))
collidables.append(q_coin1)
brick2 = PaperEntity(model='cube', scale=(1, 1, 1), color=color.white, position=(24, 4, 0), collider='box', texture='brick')
collidables.append(brick2)
q_coin2 = PaperEntity(model='cube', scale=(1, 1, 1), color=color.yellow, position=(25, 4, 0), collider='box', texture='white_cube')
Text(text='?', parent=q_coin2, scale=10, color=color.black, billboard=True, position=(0,0,0.6))
collidables.append(q_coin2)
# Upper in triangle
brick_multi = PaperEntity(model='cube', scale=(1, 1, 1), color=color.white, position=(23, 8, 0), collider='box', texture='brick')  # 10 coins? But desc has multi after pit
collidables.append(brick_multi)
q_upper = PaperEntity(model='cube', scale=(1, 1, 1), color=color.yellow, position=(24, 8, 0), collider='box', texture='white_cube')
Text(text='?', parent=q_upper, scale=10, color=color.black, billboard=True, position=(0,0,0.6))
collidables.append(q_upper)

# Hidden 1-Up between fourth pipe and pit ~ at x=59 y=4, invisible
hidden_1up = PaperEntity(model='cube', scale=(1, 1, 1), color=color.clear, position=(59, 4, 0), collider='box')
collidables.append(hidden_1up)

# After pit, ? with mushroom/flower at ~65 y=4
q_power = PaperEntity(model='cube', scale=(1, 1, 1), color=color.yellow, position=(65, 4, 0), collider='box', texture='white_cube')
Text(text='?', parent=q_power, scale=10, color=color.black, billboard=True, position=(0,0,0.6))
collidables.append(q_power)

# Long row of blocks ~70-85 y=8, Goombas falling, but add bricks
for x in range(70, 86):
    long_brick = PaperEntity(model='cube', scale=(1, 1, 1), color=color.white, position=(x, 8, 0), collider='box', texture='brick')
    collidables.append(long_brick)

# Multi-coin brick at ~79 y=4 (below row)
multi_coin = PaperEntity(model='cube', scale=(1, 1, 1), color=color.white, position=(79, 4, 0), collider='box', texture='brick')
collidables.append(multi_coin)

# Two bricks, second has star at ~80-81 y=4? But desc after multi
brick3 = PaperEntity(model='cube', scale=(1, 1, 1), color=color.white, position=(80, 4, 0), collider='box', texture='brick')
collidables.append(brick3)
brick_star = PaperEntity(model='cube', scale=(1, 1, 1), color=color.white, position=(81, 4, 0), collider='box', texture='brick')  # Star
collidables.append(brick_star)

# ? triangle ~85-88 y=4 and upper
q_tri1 = PaperEntity(model='cube', scale=(1, 1, 1), color=color.yellow, position=(85, 4, 0), collider='box', texture='white_cube')
Text(text='?', parent=q_tri1, scale=10, color=color.black, billboard=True, position=(0,0,0.6))
collidables.append(q_tri1)
q_tri2 = PaperEntity(model='cube', scale=(1, 1, 1), color=color.yellow, position=(86, 4, 0), collider='box', texture='white_cube')
Text(text='?', parent=q_tri2, scale=10, color=color.black, billboard=True, position=(0,0,0.6))
collidables.append(q_tri2)
q_tri3 = PaperEntity(model='cube', scale=(1, 1, 1), color=color.yellow, position=(87, 4, 0), collider='box', texture='white_cube')
Text(text='?', parent=q_tri3, scale=10, color=color.black, billboard=True, position=(0,0,0.6))
collidables.append(q_tri3)
q_tri_top = PaperEntity(model='cube', scale=(1, 1, 1), color=color.yellow, position=(86, 8, 0), collider='box', texture='white_cube')  # Flower
Text(text='?', parent=q_tri_top, scale=10, color=color.black, billboard=True, position=(0,0,0.6))
collidables.append(q_tri_top)

# Pyramid with gap ~100-110, 4 high
for i in range(1, 5):
    for j in range(i):
        pyr1_left = PaperEntity(model='cube', scale=(1, 1, 1), color=color.white, position=(100 + j, i, 0), collider='box', texture='brick')
        collidables.append(pyr1_left)
    for j in range(i):
        pyr1_right = PaperEntity(model='cube', scale=(1, 1, 1), color=color.white, position=(105 + (4 - i) + j, i, 0), collider='box', texture='brick')  # Gap in middle
        collidables.append(pyr1_right)

# Pyramid with pit ~120-130, gap/pit in middle
for i in range(1, 5):
    for j in range(i):
        pyr2_left = PaperEntity(model='cube', scale=(1, 1, 1), color=color.white, position=(120 + j, i, 0), collider='box', texture='brick')
        collidables.append(pyr2_left)
    for j in range(i):
        pyr2_right = PaperEntity(model='cube', scale=(1, 1, 1), color=color.white, position=(125 + (4 - i) + j, i, 0), collider='box', texture='brick')
        collidables.append(pyr2_right)

# Four blocks near end ~146-149 y=4, 3 bricks, 1 ? coin
brick4 = PaperEntity(model='cube', scale=(1, 1, 1), color=color.white, position=(146, 4, 0), collider='box', texture='brick')
collidables.append(brick4)
brick5 = PaperEntity(model='cube', scale=(1, 1, 1), color=color.white, position=(147, 4, 0), collider='box', texture='brick')
collidables.append(brick5)
q_coin3 = PaperEntity(model='cube', scale=(1, 1, 1), color=color.yellow, position=(148, 4, 0), collider='box', texture='white_cube')
Text(text='?', parent=q_coin3, scale=10, color=color.black, billboard=True, position=(0,0,0.6))
collidables.append(q_coin3)
brick6 = PaperEntity(model='cube', scale=(1, 1, 1), color=color.white, position=(149, 4, 0), collider='box', texture='brick')
collidables.append(brick6)

# Ending staircase ~179-186, 8 steps but desc 4, but in 1-1 it's 4 steps.
for step in range(1, 5):
    for height in range(1, step + 1):
        stair_block = PaperEntity(model='cube', scale=(1, 1, 1), color=color.white, position=(179 + step, height, 0), collider='box', texture='brick')
        collidables.append(stair_block)

# Flagpole at ~193
flagpole = PaperEntity(model='quad', scale=(0.5, 16, 0.05), color=color.white, position=(193, 8, 0), collider='box', texture='white_cube')
collidables.append(flagpole)

# Hidden platform in 3D at z=2, say at pit to bypass
hidden_platform = PaperEntity(model='cube', scale=(5, 1, 1), color=color.white, position=(60, 2, 2), collider='box', texture='noise')
collidables.append(hidden_platform)

# Enemies: 16 Goombas at various positions, 1 green Koopa
enemies = []
goomba_positions = [10, 30, 32, 39, 41, 66, 68, 70, 72, 74, 84, 86, 88, 90, 140, 142]  # Approximate 16 positions based on desc
for pos in goomba_positions:
    goomba = PaperEntity(model='quad', color=color.brown, scale=(1, 0.8), position=(pos, 1, 0), collider='sphere')  # Body
    goomba_eye_left = PaperEntity(parent=goomba, model='circle', color=color.white, scale=(0.3, 0.4), x=-0.3, y=0.2)
    goomba_eye_right = PaperEntity(parent=goomba, model='circle', color=color.white, scale=(0.3, 0.4), x=0.3, y=0.2)
    goomba_pupil_left = PaperEntity(parent=goomba_eye_left, model='circle', color=color.black, scale=(0.5, 0.5))
    goomba_pupil_right = PaperEntity(parent=goomba_eye_right, model='circle', color=color.black, scale=(0.5, 0.5))
    goomba_foot_left = PaperEntity(parent=goomba, model='quad', color=color.orange, scale=(0.4, 0.3), x=-0.3, y=-0.5)
    goomba_foot_right = PaperEntity(parent=goomba, model='quad', color=color.orange, scale=(0.4, 0.3), x=0.3, y=-0.5)
    goomba.direction = -1  # Move left
    goomba.type = 'goomba'
    enemies.append(goomba)

# Koopa at ~92
koopa = PaperEntity(model='circle', color=color.green, scale=(1, 1.2), position=(92, 1, 0), collider='sphere')  # Shell
koopa_head = PaperEntity(parent=koopa, model='circle', color=color.yellow, scale=(0.6, 0.6), y=0.8)  # Head
koopa_eye_left = PaperEntity(parent=koopa_head, model='circle', color=color.white, scale=(0.3, 0.4), x=-0.2)
koopa_eye_right = PaperEntity(parent=koopa_head, model='circle', color=color.white, scale=(0.3, 0.4), x=0.2)
koopa_pupil_left = PaperEntity(parent=koopa_eye_left, model='circle', color=color.black, scale=(0.5, 0.5))
koopa_pupil_right = PaperEntity(parent=koopa_eye_right, model='circle', color=color.black, scale=(0.5, 0.5))
koopa_foot_left = PaperEntity(parent=koopa, model='quad', color=color.orange, scale=(0.4, 0.5), x=-0.3, y=-0.6)
koopa_foot_right = PaperEntity(parent=koopa, model='quad', color=color.orange, scale=(0.4, 0.5), x=0.3, y=-0.6)
koopa.direction = -1
koopa.type = 'koopa'
koopa.shelled = False
koopa.shell_timer = 0
koopa.original_scale = koopa.scale
enemies.append(koopa)

# Camera setup
camera.orthographic = True
camera.fov = 20

def input(key):
    if key == 'f':
        global is_2d
        is_2d = not is_2d

def unshell_koopa(koopa):
    koopa.shelled = False
    koopa.scale = koopa.original_scale
    koopa.direction = -1
    for child in koopa.children:
        child.enabled = True

def update():
    global time_remaining, score, coins
    # Time countdown
    time_remaining -= time.dt
    hud_time.text = str(int(time_remaining))

    # Mode-specific movement
    if is_2d:
        player.x += (held_keys['d'] - held_keys['a']) * time.dt * 5
    else:
        player.x += (held_keys['d'] - held_keys['a']) * time.dt * 5
        player.z += (held_keys['w'] - held_keys['s']) * time.dt * 5

    # Jumping
    if held_keys['space'] and player.grounded:
        player.velocity_y = player.jump_height
        player.grounded = False

    # Gravity
    player.y += player.velocity_y
    player.velocity_y -= player.gravity

    # Collision with collidables (land on top)
    player.grounded = False
    if player.velocity_y <= 0:
        for c in collidables:
            hit_info = player.intersects(c)
            if hit_info.hit:
                player.y = hit_info.world_point[1] + player.scale_y / 2 + 0.01
                player.velocity_y = 0
                player.grounded = True
                break

    # Fall in pit reset
    if player.y < -2:
        player.position = (0, 1, 0)
        player.velocity_y = 0

    # Enemy movement and shell logic
    for e in enemies[:]:
        if hasattr(e, 'shelled') and e.shelled:
            e.shell_timer -= time.dt
            if e.shell_timer <= 0:
                unshell_koopa(e)
        else:
            e.x += e.direction * time.dt * 2
        if e.x < player.x - 20:
            enemies.remove(e)
            destroy(e)

    # Player-enemy collision with stomp logic
    for e in enemies[:]:
        hit_info = player.intersects(e)
        if hit_info.hit:
            # Check if stomping (player above enemy and falling)
            if player.y > e.y + e.scale_y / 2 and player.velocity_y < 0:
                # Stomp successful, bounce player
                player.velocity_y = player.jump_height / 2
                if e.type == 'goomba':
                    # Goomba disappears
                    enemies.remove(e)
                    destroy(e)
                elif e.type == 'koopa':
                    # Koopa goes into shell
                    e.shelled = True
                    e.scale_y = 0.5  # Flatten to shell
                    e.direction = 0  # Stop moving
                    for child in e.children:
                        child.enabled = False  # Hide head and feet
                    e.shell_timer = 5  # 5 seconds
            else:
                # Not stomp, player dies/reset
                player.position = (0, 1, 0)
                player.velocity_y = 0

    # Win condition
    if player.intersects(flagpole).hit:
        print("You Win! Level Complete.")
        player.position = (0, 1, 0)
        player.velocity_y = 0

    # Camera follow
    if is_2d:
        camera.position = (player.x, player.y + 2, -10)
        camera.rotation = (0, 0, 0)
    else:
        camera.position = (player.x - 10, player.y + 2, player.z)
        camera.rotation = (0, 90, 0)

app.run()
