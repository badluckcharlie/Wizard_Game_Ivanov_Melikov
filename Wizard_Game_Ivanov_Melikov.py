import pygame

pygame.init()
gameover = False

screenX = 1200
screenY = 800
screen=pygame.display.set_mode([screenX,screenY])
pygame.display.set_caption("keyboard input")
screen.fill((255,255,0))# заменить  на пнг от уровней
clock = pygame.time.Clock()

Wizard = 0 #add png
Wizard_Start= 50
Wizard_Move = 0 #add move anim when use fireball or shield
Wizard_Block_Move = 0 #Block movement while in dialogue
Wizard_Death = 0 #If wizard dies rotate 90 degrees
Wizard_X = 50 #move
Wizard_Y = 400 #jump
Fireball = 0 #add 2 seconds timeout
Shield = 0 #holds for 5 sec, 5 sec timeout recharge
Shield_Recharge = 0 #Recharge timer
Level = 0 # 0 - welcome 1 - tutorial 2 - walk level 3 - zombie fight 4 - skeleton fight 5 - frog good luck 6 boss fight

Frog = 0 #Add frog png
Frog_Dial = 0 #Frog Dialog box
Zombie = 0 #Add zombie png
Zombie_Move_X = 0 #Zombie horizontal movement
Zombie_Hit = 0 #Add zombie hit counter. if 1 zombie dies
Zombie_Death = 0 #Zombie dead animation rotate 90 degrees
Skeleton_1 = 0 #Add zombie png
Skeletion_1_Move_X = 0 #Skeleton horizontal movement
Skeleton_1_Hit = 0 #Skeleton hit counter. 2 = death
Skeleton_1_Death = 0 #Rotate 90 degrees
Skeleton_2 = 0 #Add zombie png
Skeletion_2_Move_X = 0 #Skeleton horizontal movement
Skeleton_2_Hit = 0 #Skeleton hit counter. 2 = death
Skeleton_2_Death = 0 #Rotate 90 degrees
Anti_Wiz = 0 #Add enemy wizard png
Anti_Wiz_Dial = 0 #Anti wiz dialog box
Anti_Wiz_Fireball = 0 #Add enemy wizard fireball/lighting
Anti_Wiz_Shield = 0 #Add enemy wizard shield
Anti_Wiz_Death = 0 #3 hits = death = rotate 90 degrees

m = 1 #move counter 
v = 10 #velocity of the wizard
jump = 0 #jump counter
clock = pygame.time.Clock()
directionx=0
pygame.draw.rect(screen,(255,0,0),(Wizard_X,Wizard_Y,90,90),5) # Draw the wizard as a red rectangle for now



while gameover == False:
    clock.tick(60) # Set the frame rate to 60 FPS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameover = True
        elif event.type ==pygame.KEYDOWN and Wizard_Block_Move==0:# Check for key presses and ensure the wizard can move
            if event.key == pygame.K_RIGHT: # Move the wizard to the right
                directionx="move_right"
            elif event.key == pygame.K_LEFT: # Move the wizard to the left
                directionx="move_left"
            elif jump == 0:
                if event.key==pygame.K_v: # Jump action
                 jump= 1
        elif event.type == pygame.KEYUP:
            if event.key==pygame.K_RIGHT or event.key   == pygame.K_LEFT:
                directionx=0
    if directionx == "move_left": # Move the wizard to the left
        if Wizard_X >0: # Ensure the wizard doesn't move off the screen
            Wizard_X -=3
    elif directionx == "move_right": # Move the wizard to the right
        if Wizard_X +50 <screenX: # Ensure the wizard doesn't move off the screen
            Wizard_X +=3
        if Wizard_X == screenX-100: # If the wizard reaches the right edge of the screen
            Wizard_X=Wizard_Start   # Reset the wizard's position to the starting point
            Level+=1  # Move to the next level when reaching the right edge of the screen


    if jump == 1:
        k = 0.5 * m * v**2  # Calculate the vertical displacement
        Wizard_Y -= k  # Update the sprite's vertical position
        v -= 1  # Simulate gravity by gradually decreasing velocity
        if v < 0:
            m = -1  # Change the direction of displacement for a realistic jump feel
        if v == -11:
            m = 1  # Reset parameters for subsequent jumps
            v = 10
            jump = 0 
    screen.fill((255, 255, 0))  # Clear the screen with yellow
    pygame.draw.rect(screen,(255,0,0),(Wizard_X,Wizard_Y,90,90),5) # Draw the wizard as a red rectangle
    pygame.display.update() # Update the display
    
pygame.quit()


