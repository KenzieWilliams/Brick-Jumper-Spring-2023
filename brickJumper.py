#importing necessary libraries
from pygame.locals import *
import math
import random
from pgzhelper import *
import json
import pygame

x = 50
y = 30
import os
#makes the program's window open at a specific place on the screen
os.environ['SDL_VIDEO_WINDOW_POS'] = f'{x},{y}'

import pgzrun #imported after os because it was causing some kind of conflict with the os operation
pygame.init()#initialize pygame

#define size of the window
WIDTH=600
HEIGHT=690
win = pygame.display.set_mode((WIDTH,HEIGHT))

#define the most basic game variables; these will change often throughout the game (highscore & players_coins change w/ load_data())
score=0.0#EXAMPLE: float variable (though it is cast as an int for user output purposes)
highscore=0
players_coins=0

##defining all of the actors that can be used in the game -- format is define actor
##--> actor id --> actor unlocked boolean --> define jump version of same actor --> arbitrary jump version id
genOC=Actor('gen_oc.png')
genOC.id=1#EXAMPLE: integer variable
genOC.unlocked=True#EXAMPLE: boolean variable
genOC_jump=Actor('gen_oc_jump.png')
genOC_jump.id=0
catOC=Actor('cat_oc.png')
catOC.id=2
catOC.unlocked=False
catOC_jump=Actor('cat_oc_jump.png')
catOC_jump.id=0
wonderw=Actor('ww_oc.png')
wonderw.id=3
wonderw.unlocked=False
wonderw_jump=Actor('ww_oc_jump.png')
wonderw_jump.id=0
pika=Actor('pikachu.png')
pika.id=4
pika.unlocked=False
pika_jump=Actor('pikachu_jump.png')
pika_jump.id=0

#place all game actors in an list
actors=[genOC,genOC_jump,catOC,catOC_jump,wonderw,wonderw_jump,pika,pika_jump]

#will display later
returnMsg='Returning to Main Screen in'#EXAMPLE: string variable

#defining variables for the currently selected actor -- selectActor stores player-selected actor
selectActor=genOC
selectActor.id=genOC.id
selectActor.vel=13
selectActor.x=200
selectActor.y=140
original_id=selectActor.id

#ground and background objects for game use
ground=Actor('ground.png')
ground.y=selectActor.y+330
bg1=Actor('game_bg1.png')
bg1.y=-150
bg2=Actor('game_bg2.png')
bg2.y=-3140

#icons and buttons for the store (+ their positioning & cost, if applicable)
gen_icon=Actor('gen_oc.png')
gen_icon.x,gen_icon.y=185,230
cat_icon=Actor('cat_icon.png')
cat_lock=Actor('cat_lock.png')
cat_icon.x,cat_icon.y=404,230
cat_lock.x,cat_lock.y=404,230
cat_icon.cost=100
ww_icon=Actor('ww_icon.png')
ww_lock=Actor('ww_lock.png')
ww_icon.x,ww_icon.y=185,524
ww_lock.x,ww_lock.y=185,524
ww_icon.cost=250
pika_icon=Actor('pika_icon.png')
pika_lock=Actor('pika_lock.png')
pika_icon.x,pika_icon.y=408,524
pika_lock.x,pika_lock.y=408,524
pika_icon.cost=400
icons=[gen_icon,gen_icon,cat_icon,cat_lock,ww_icon,ww_lock,pika_icon,pika_lock]
iconbg1=Actor('shop_bg_icon.png')
iconbg1.x,iconbg1.y=185,230
iconbg2=Actor('shop_bg_icon.png')
iconbg2.x,iconbg2.y=405,230
iconbg3=Actor('shop_bg_icon.png')
iconbg3.x,iconbg3.y=185,520
iconbg4=Actor('shop_bg_icon.png')
iconbg4.x,iconbg4.y=405,520
star=Actor('star.png')#star actor will be used to visually indicate which skin has been selected from the shop

#more variables for gameplay: lists for actor types, game velocity measurement, index for when to make a new platform
platforms=[]
coins=[]
coin_icon=Actor('coin_icon.png')
coin_icon.x=30
coin_icon.y=30
gameVel=.5
move_index=0

#booleans for different screens (note the shop screen had no boolean but is stored in 'else')
mainMenu=True
game=False

#variables used in the game function
jumpMotion=False#if the player is jumping/falling
jPress=False#if the player is jumping by intent OR falling from walking
lost=False
lostY=-60#position for 'lost game' text; will change
main_menu_countdown=4

#variables/actors used on the main menu & their positioning
main_bg=Actor('main_bg.png')
playButton=Actor('button_play.png')
playButton.x=180
playButton.y=375
shopButton=Actor('button_shop.png')
shopButton.x=410
shopButton.y=375

#variables/actors for use on the shop menu screen & their positioning
shop_bg=Actor('shop_bg.png')
returnButton=Actor('button_return.png')
returnButton.x=75
returnButton.y=52

#saves the game data to local storage
def save():
    save_file = open("brick_jump_data.json", "w")
    data = {"highscore": highscore,"selected": selectActor.id,"coinCount":players_coins,"cat_bought":catOC.unlocked,"ww_bought":wonderw.unlocked,"pika_bought":pika.unlocked}
    json.dump(data,save_file)
    save_file.close()

##loads the game data from local storage -- note that the player needs an empty JSON from the reset screen or there will be nothing to load & throw an error
##hence empty JSON is part of game files
def load_data():
    global selectActor
    global highscore
    global players_coins
    theData=json.load(open('brick_jump_data.json'))
    highscore=theData["highscore"]
    players_coins=theData["coinCount"]
    catOC.unlocked = theData["cat_bought"]
    wonderw.unlocked=theData["ww_bought"]
    pika.unlocked=theData["pika_bought"]
    for act in actors:
        if theData["selected"]==act.id:
            selectActor=act
            selectActor.id=act.id

##generates a new platform at the top of the screen with a random x variable
##1/3 of the time, a platform will have a coin above it for the player to collect
def gen_platform():
    global lost
    if not lost:
        x_pos=random.randint(40,520)#random x coordinate for unpredictability
        breakable_chance=random.randint(1,5)
        platform=Actor('platform.png')
        platform.x=x_pos
        platform.y=-10
        if breakable_chance==1:
            platform.breakable=True
        else:
            platform.breakable=False
        platform.breakIndex=0
        platforms.append(platform)
        coin_chance=random.randint(1,3)
        if coin_chance==3:
            coin=Actor('coin.png')
            coin.x=x_pos
            coin.y=-50
            coins.append(coin)

#resets the variables used in the game after a loss and returns to main menu
def resetGame():
    global score
    score=0
    global jumpMotion
    jumpMotion=False
    global jPress
    jPress=False
    global lost
    lost=False
    global move_index
    move_index=0
    global gameVel
    gameVel=.5
    global lostY
    lostY=-60
    global main_menu_countdown
    main_menu_countdown=4
    global original_id
    global selectActor
    selectActor=actors[2*(original_id-1)]#math to convert actor id into index location
    selectActor.id=original_id
    selectActor.vel=13
    selectActor.x=200
    selectActor.y=140
    ground.y=selectActor.y+330
    global coins
    coins.clear()
    global platforms
    platforms.clear()
    save() #savee once the game ends
    bg1.y=-150
    bg2.y=-3140
    global game
    global mainMenu
    game=False
    mainMenu=True

#this changes the falling actor back to the standing actor of the same skin type
def actor_change(key_id):
    global selectActor
    x=selectActor.x
    y=selectActor.y
    v=13
    i=selectActor.id
    selectActor=actors[(key_id)*2]
    selectActor.x=x
    selectActor.y=y
    selectActor.vel=v
    selectActor.id=i-1

#this changes from one selected skin to another using the selection made in the shop menu
def actor_change2(key_id):
    global selectActor
    global original_id
    x=selectActor.x
    y=selectActor.y
    v=13
    selectActor=actors[key_id]
    selectActor.x=x
    selectActor.y=y
    selectActor.vel=v
    selectActor.id=int((key_id/2)+1)
    original_id=selectActor.id

#before any output to the user, load whatever data may be stored
load_data()

#the general draw method for displaying screen output
def draw():
    screen.clear()
    global lostY
    global main_menu_countdown
    if mainMenu: #the main meny
        #draw all actors for this screen
        main_bg.draw()
        shopButton.draw()
        playButton.draw()
        #all math equations convert from id to list index
        x=actors[(selectActor.id-1)*2+1].x
        y=actors[(selectActor.id-1)*2+1].y
        actors[(selectActor.id-1)*2+1].x=292
        actors[(selectActor.id-1)*2+1].y=560
        actors[(selectActor.id-1)*2+1].draw()
        actors[(selectActor.id-1)*2+1].x=x
        actors[(selectActor.id-1)*2+1].y=y
    elif game: #the gameplay
        #draw the backgrounds & actors
        bg1.draw()
        bg2.draw()
        ground.draw()
        selectActor.draw()
        for plat in platforms: #draw each platform, or draw the more broken version if breakable and time spent standing on it
            if plat.breakIndex<12:
                plat.draw()
            elif plat.breakIndex>=12 and plat.breakIndex<24:
                newPlat=Actor('plat_bre_1.png')
                newPlat.y=plat.y
                newPlat.x=plat.x
                newPlat.draw()
            elif plat.breakIndex>=24 and plat.breakIndex<36:
                newPlat=Actor('plat_bre_2.png')
                newPlat.y=plat.y
                newPlat.x=plat.x
                newPlat.draw()
            else:
                platforms.remove(plat) #remove platforms that have fully broken
        for coin in coins: #draw all coins
            coin.draw()
        coin_icon.draw() #draw coin icon
        #display player values -- lose message only viewable once the lost condition is reached
        screen.draw.text(str(players_coins), (48,23), color='white', fontsize=25)
        screen.draw.text(str(int(score)), (23,48), color='white', fontsize=25)
        screen.draw.text('You Lose', (230,lostY), color='red', fontsize=45)
        if lostY==250: #once loss message reaches center of the screen, display end of game stats
            screen.draw.text('Score: '+str(int(score)), (246,285), color='white', fontsize=35)
            screen.draw.text('High score: '+str(int(highscore)), (225,325), color='white', fontsize=35)
            screen.draw.text(returnMsg, (140,360), color='red', fontsize=38)
            screen.draw.text(str(int(main_menu_countdown)), (280,395), color='red', fontsize=38)
    else: #the shop screen
        #display the options of skins to buy (locked if not purchased, starred if selected)
        shop_bg.draw()
        returnButton.draw()
        iconbg1.draw()
        screen.draw.text('Free!', (iconbg1.x-30,iconbg1.y+120), color='cyan4', fontsize=35)
        iconbg2.draw()
        screen.draw.text('100', (iconbg2.x-20,iconbg2.y+120), color='cyan4', fontsize=35)
        iconbg3.draw()
        screen.draw.text('250', (iconbg3.x-20,iconbg3.y+120), color='cyan4', fontsize=35)
        iconbg4.draw()
        screen.draw.text('400', (iconbg4.x-20,iconbg4.y+120), color='cyan4', fontsize=35)
        screen.draw.text('Coins: '+str(players_coins), (475,40), color='turquoise4', fontsize=28)
        for actor in actors:
            if actor.id>0:
                try: #was throwing errors with the fact that some don't have an unlocked variable, hence the try statement
                    if actor.unlocked:
                        icons[2*(actor.id-1)].draw()
                    else:
                        icons[2*(actor.id-1)+1].draw()
                except:
                    pass
        star.draw()
                

#this is the basis of the program (will call other functions)
def update():
    #bring in all global variables
    global move_index
    global gameVel
    global jumpMotion
    global selectActor
    global jPress
    global players_coins
    global score
    global highscore
    global lost
    global lostY
    global main_menu_countdown
    global game
    global mainMenu
    if mainMenu:
        pass #no constant functions, only event listeners and actors to be drawn
    elif game:
        onPlat=True
        move_index+=gameVel #game constantly moves faster
        if jumpMotion: #if player affected by gravity
            if selectActor.y>ground.y-330+1 and selectActor.y<ground.y-330+20: #if on a platform
                        jumpMotion=False
                        selectActor.y=ground.y-330
                        x=selectActor.x
                        if jPress: #if on a platform after intetionally jumping
                            actor_change(selectActor.id-2)
                            jPress=False
                        selectActor.vel=13
        for plat in platforms:
            plat.y+=gameVel #move down the screen
            if jumpMotion: #if in the jump/fall motion (this line) and on a platform (next line)
                if selectActor.y>=plat.y-110 and selectActor.y<=plat.y-80 and selectActor.x>=plat.x-55 and selectActor.x<=plat.x+55:
                    if jPress: #if jump (followed by land), change back to the standing png; maintain positioning variables
                        actor_change(selectActor.id-2)#-2
                        jPress=False
                    jumpMotion=False
                    selectActor.vel=13
                    selectActor.y=plat.y-94
                    selectActor.x=min(plat.x+53,max(selectActor.x,plat.x-53))
            if plat.y>830: #remove platforms below the visible screen
                platforms.remove(plat)
        for coin in coins:
            coin.y+=gameVel#move down the screen
            if coin.y>830: #remove coins below the visible screen
                coins.remove(coin)
            if selectActor.y>=coin.y-70 and selectActor.y<=coin.y-40 and selectActor.x>=coin.x-55 and selectActor.x<=coin.x+55:
                #when the player collides with a coin, they collect it: add to total & remove coin from screen
                coins.remove(coin)
                players_coins+=1
        #iterate all other object down the screen by the game velocity; increase game velocity
        selectActor.y+=gameVel
        ground.y=min(1300,ground.y+gameVel) #once ground is off screen, no need to continue moving
        gameVel+=.0015
        bg1.y+=gameVel
        bg2.y+=gameVel
        #following 2 if statements loop the backgrounds
        if bg1.top>690:
            bg1.y=-3690
        if bg2.top>690:
            bg2.y=-3690
        if not lost:
            score+=.03
        if int(score)>highscore:
            highscore=int(score)
        #every time the game objects move a distance approximately equal to player height, build a new platform
        if move_index>=170:
            move_index=0
            gen_platform()
        #if in jumping motion, make the actor jump (inlcudes acceleration and falling down again)
        if jumpMotion:
            selectActor.y-=selectActor.vel
            selectActor.vel-=.2+(gameVel/100)
        #if the player is not standing on the ground or a platform, set jumpMotion to True and velocity to 0 (initates a free fall)
        for plat in platforms:
            if selectActor.y>=plat.y-110 and selectActor.y<=plat.y-80 and selectActor.x>=plat.x-50:
                if plat.breakable:
                        plat.breakIndex+=.5
            if not jumpMotion:
                onPlat=(selectActor.y>=plat.y-110 and selectActor.y<=plat.y-80 and selectActor.x>=plat.x-50 and selectActor.x<=plat.x+55) or selectActor.bottom>ground.top-30
                if onPlat:
                    break
        #if not on a platform (or ground), actor should fall
        if not onPlat:
            jumpMotion=True
            selectActor.vel=0
        if selectActor.top>691: #if actor off screen, lose game
            lost=True
        if lost: #if lost, move lose screen down, give player countdown til return to main menu, reset game variables w/function
            lostY=min(lostY+1.5,250)
            if lostY==250:
                main_menu_countdown-=.015
                if main_menu_countdown<=1:
                    resetGame()
            
    else:
        pass #no constant functions, only event listeners and actors to be drawn

#directs player-keyboard interaction with effects on the program
def on_key_down(key):
    global jumpMotion
    global selectActor
    global jPress
    global players_coins
    #DEV COMMAND - PURPOSE IS DEMONSTRATION ONLY - press to gift yourself 50 coins per press
    if key==keys.P:
        players_coins+=50
        save()
    ##DEV COMMAND - PURPOSE IS DEMONSTRATION ONLY - press to reset the game completely as though you are a new player
    ##can also be used to generate original json file
    if key==keys.O:
        global original_id
        original_id=1
        save_file = open("brick_jump_data.json", "w")
        data = {"highscore": 0,"selected": 1,"coinCount":0,"cat_bought":False,"ww_bought":False,"pika_bought":False}
        json.dump(data,save_file)
        save_file.close()
        load_data()
    if game:
        if key==keys.UP:
            if not jumpMotion:
                #jPress variable will prevent changing to another image after landing from a fall (not jump)
                jPress=True
                jumpMotion=True
                selectActor.y-=25 #an initial boost of 25 pixels just to get the player decently away from generated structures
                #change actor to jump actor & maintain positioning
                x=selectActor.x
                y=selectActor.y
                v=selectActor.vel
                i=selectActor.id
                selectActor=actors[2*selectActor.id-1]#int((selectActor.id)/2)+1
                selectActor.x=x
                selectActor.y=y
                selectActor.vel=v
                selectActor.id=i+1
        if key==keys.LEFT: #move left, capped by screen
            if selectActor.x>=55:
                selectActor.x-=45
            else:
                selectActor.x=10
        if key==keys.RIGHT: #move right, capped by screen
            if selectActor.x<=580:
                selectActor.x+=40
            else:
                selectActor.x=581

def on_mouse_down():
    global mainMenu
    global game
    global players_coins
    if (mainMenu):
        x,y=pygame.mouse.get_pos()
        #if pressing shop button, open shop
        if x>shopButton.x-shopButton.width/2 and x<shopButton.x+shopButton.width/2 and y>shopButton.y-shopButton.height/2 and y<shopButton.y+shopButton.height/2:
            game=False
            mainMenu=False
            star.x,star.y=icons[2*(selectActor.id-1)].x-80,icons[2*(selectActor.id-1)].y-108
        #if pressing play button, open gameplay
        elif x>playButton.x-playButton.width/2 and x<playButton.x+playButton.width/2 and y>playButton.y-playButton.height/2 and y<playButton.y+playButton.height/2:
            mainMenu=False
            game=True
    #use of an elif just to make sure that this function doesn't occur on the other 2 pages
    elif (not mainMenu and not game):
        x,y=pygame.mouse.get_pos()
        #if clicking return to menu button, return to menu
        if x>returnButton.x-returnButton.width/2 and x<returnButton.x+returnButton.width/2 and y>returnButton.y-returnButton.height/2 and y<returnButton.y+returnButton.height/2:
            mainMenu=True
        i=0 #i used to track index of the list as we iterate
        for icon in icons:
            if i%2==0:
                if x>icon.x-icon.width/2 and x<icon.x+icon.width/2 and y>icon.y-icon.height/2 and y<icon.y+icon.height/2:
                    if actors[i].unlocked: #if the actor is unlocked, a click will make that the selected skin
                        actor_change2(i)
                        star.x,star.y=icons[2*(selectActor.id-1)].x-80,icons[2*(selectActor.id-1)].y-108
                        save()
                    else: #if the actor is locked and if the player has enough coins, click purchases & selects the skin
                        if players_coins>=icon.cost:
                            players_coins-=icon.cost
                            actors[i].unlocked=True
                            actor_change2(i)
                            star.x,star.y=icons[2*(selectActor.id-1)].x-80,icons[2*(selectActor.id-1)].y-108
                            save()
            i+=1
                            
                

pgzrun.go() #runs the game
