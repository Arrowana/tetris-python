"""
    Minimal Tetris game
"""
import curses
import numpy
import time

dt=0.01 #Loop time
speed=3. #Block descent per seconds

class Pose():
    def __init__(self):
        self.x=0
        self.y=0

class Tetrominoe():
    """Basic tetris block"""
    I=numpy.array([[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]])
    J=numpy.array([[0,1,0],[0,1,0],[1,1,0]])
    L=numpy.array([[0,0,1],[1,1,1],[0,0,0]])
    O=numpy.array([[0,1,1,0],[0,1,1,0],[0,0,0,0]])
    S=numpy.array([[0,1,1],[1,1,0],[0,0,0]])
    T=numpy.array([[0,1,0],[1,1,1],[0,0,0]])
    Z=numpy.array([[1,1,0],[0,1,1],[0,0,0]])
    tetrominoes = [I,J,L,O,S,T,Z]
    def __init__(self):
        self.pose=Pose()
        #Take a random shape
        self.shape=self.tetrominoes[int(len(self.tetrominoes)*numpy.random.rand())]

    def ccwrotate(self):
        self.shape=numpy.rot90(self.shape)

    def cwrotate(self):
        self.shape=numpy.rot90(self.shape,3)

def render_mat(screen, mat, off_x=0, off_y=0):
    for x,row in enumerate(mat):
        for y,cell in enumerate(row):
            if cell == 1: 
                screen.addstr(off_x+x,off_y+y+1, chr(35))

def render_tetrominoe(screen, tetrominoe):
    render_mat(screen, tetrominoe.shape, tetrominoe.pose.x, tetrominoe.pose.y)

def draw_box(screen):
    screen.addstr(18,0, "************")
    for i in range(18):
        screen.addstr(i,0,"*")
        screen.addstr(i,11,"*")

def add(world, tetrominoe):
    previous_world = numpy.array(world)
    x=tetrominoe.pose.x
    y=tetrominoe.pose.y
    mask_length=2 #Additional line below
    mask_width=4 #Additional lines on the side

    #Mask to prevent block to be out of bound of world
    block_mask=numpy.zeros((world.shape[0]+mask_length,world.shape[1]+mask_width))
    size=tetrominoe.shape.shape
    block_mask[x:x+size[0], y+mask_width/2:y+size[1]+mask_width/2]=tetrominoe.shape
    world = numpy.logical_or(world, block_mask[0:-mask_length,mask_width/2:-mask_width/2])
    return world

def reached_bottom(world, tetrominoe):
    if tetrominoe.pose.x+numpy.nonzero(tetrominoe.shape)[0][-1]>=world.shape[0]:
        return True
    else:
        return False

def check_collide(world, tetrominoe):
    world_mask=numpy.vstack(
        (numpy.hstack((numpy.ones((world.shape[0],1)), world, numpy.ones((world.shape[0],1)))),
        numpy.ones((1,world.shape[1]+2)))
        )
    for x,row in enumerate(tetrominoe.shape):
        for y,cell in enumerate(row):
            if cell == 1 and world_mask[tetrominoe.pose.x+x, tetrominoe.pose.y+y+1] == 1: 
                return True
    return False

def remove_completed(world):
    completed_lines=0
    new_world=numpy.array(world)
    i=17
    while i > 0:
        if numpy.all(new_world[i,:]>0):
            new_world[i,:]=0
            completed_lines+=1
            #Shift everything down
            for j in range(1,i+1)[::-1]:
                new_world[j,:]=new_world[j-1,:]
        else:
            i-=1
    return new_world, completed_lines
        
def main(scr):
    scr.nodelay(1) #Make non blocking getch
    T=0 #Total elapsed time since last drop
    #Screen of 10x18
    field=numpy.zeros((18,10))
    block = Tetrominoe()
    current_speed=speed
    lines=0
    while 1:
        #Input handling
        usr_input=scr.getch()
        if usr_input == curses.KEY_LEFT:
            block.pose.y-=1
            if check_collide(field, block):
                #Revert movement
                block.pose.y+=1
        elif usr_input == curses.KEY_RIGHT:
            block.pose.y+=1
            if check_collide(field, block):
                #Revert movement
                block.pose.y-=1
        elif usr_input == 110 or usr_input == curses.KEY_UP:
            #Counterclockwise
            block.ccwrotate()
        elif usr_input == 109:
            #Clockwise
            block.cwrotate()
        elif usr_input == ord(' '): #??curses.KEY_SPACE:
            #Instant drop of tetrominoe
            while check_collide(field, block) == False:
                block.pose.x+=1
            block.pose.x-=1
            field=add(field, block)
            block=Tetrominoe()
            field, comp_lines=remove_completed(field)
            lines+=comp_lines

        if usr_input == curses.KEY_DOWN:
            current_speed=speed*4
        else:
            current_speed=speed
         
        #Clear screen
        scr.clear()

        render_tetrominoe(scr, block)
        render_mat(scr, field)
        draw_box(scr)
        scr.addstr(5, 14, "Lines:")
        scr.addstr(6, 16, str(lines))

        if T > 1./current_speed:
            block.pose.x+=1
            T=0 #Reset timer
            #Check collision with previous blocks
            if check_collide(field, block):
                #scr.addstr(21,0,"Collision")
                block.pose.x-=1
                field=add(field, block)
                block=Tetrominoe()

            field, comp_lines=remove_completed(field)
            lines+=comp_lines

            if numpy.any(field[0,:]>0):
                break
        else:
            T+=dt
        scr.refresh()
        time.sleep(dt)

    scr.addstr(5,2,"GAME OVER")
    scr.refresh()
    while 1:
        time.sleep(2)
    
if __name__ == "__main__":
    curses.wrapper(main)
    
