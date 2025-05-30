import pygame

pygame.init()
gameover = False

screenX = 1200
screenY = 800
screen=pygame.display.set_mode([screenX,screenY])
pygame.display.set_caption("Wizard")
screen.fill(lBlue)# заменить  на пнг от уровней
clock = pygame.time.Clock()

Wizard = 0 #add png
Wizard_Move = 0 #add move anim when use fireball or shield
Wizard_Block_Move = 0 #Block movement while in dialogue
Wizard_Block_Move_Dial = 0 #Show that moving is currentrly blocked
Wizard_Death = 0 #If wizard dies rotate 90 degrees
Wizard_X = 0 #move
Wizard_Y = 0 #jump
Fireball = 0 #add 2 seconds timeout
Shield = 0 #holds for 5 sec, 5 sec timeout recharge
Shield_Recharge = 0 #Recharge timer
Shield_Recharge_Dial = 0 #Show that shield is recharging
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



while gameover == False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameover = True


