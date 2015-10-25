# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 17:32:32 2015

@author: User

Experimenting with a level-based drafting system

"""
import numpy as np
import matplotlib.pyplot as plt
#from matplotlib.widgets import Cursor
#http://central.scipy.org/item/22/4/building-a-simple-interactive-2d-data-viewer-with-matplotlib
"""

Have a map class that is esentially an array of room objects
with a draw map function that goes through and plots the rooms and the doorways and level
draw lines on the interor of the sqaure in the shape of a cross
As well as add a room to the map which randomly picks connecting rooms from the list of rooms and subtracts them from that list 



Have rooms classes that have doorways centered around the origin
Doorway requirments for each doorway and location at left, top, right. Bottom is always facing the room you are coming from.
generate room characteristics which randomly generates room info given a level stack.
Can further mod the room later

Create a for loop that populates the room deck (list of rooms) with a bell curve or semi expodental growth.

Legend for each room level preferably starting at 0 and going to 4 with different colors or shades of red
but leave room to go down to -4 as well with shades of blue.


"""

class room(object):
    def __init__(self,lvl):
        self.lvl = lvl
        self.orientation = None #Direction the room's bottom door is facing, 'N','S','E','W'
        self.door = [None]*3 #index 0: Left, 1: Far, 2: Right, this list contains the levels that the door can connect to
        self.directions = {'N':0,'E':1,'S':2,'W':3,'NORTH':0,'EAST':1,'SOUTH':2,'WEST':3}
        self.row = None
        self.col = None
        
    def show(self):
        print 'Level: {}'.format(self.lvl)
        print 'Located at ({},{})'.format(self.col,self.row)
        print 'Entry Door is {}'.format(self.orientation)
        #print self.door
        if self.orientation is None:
            door_text = ['Left','Far','Right']
        elif self.directions[self.orientation.upper()] == 0:
            door_text = ['East','South','West']
        elif self.directions[self.orientation.upper()] == 1:        
            door_text = ['South','West','North']
        elif self.directions[self.orientation.upper()] == 2:
            door_text = ['West','North','East']
        elif self.directions[self.orientation.upper()] == 3:
            door_text = ['North','East','South']
        
        for index in range(len(self.door)):
            if self.door[index] is not None:
                print '{} Door connects to lvls: {}'.format(door_text[index],''.join('{}  '.format(i) for i in self.door[index]))            
            
            
    def add_door(self,door, index=None):
        if index is None:
            if self.door.count(None) == 0:
                print 'The room already has the maximum amount of doors, room not added'            
                return 0
            else:
                index = self.door.index(None)
        if isinstance(door,int):
            door = [door]
        self.door[index]=door
        
    def remove_door(self,index):
        self.door[index] = None
     
    def rand_door(self,lvl=None,num_door=None):
        if num_door is None:
            num_door = np.random.randint(1,4)
        if lvl is None:
            lvl = np.add([self.lvl]*3,[-1,0,1])
        self.door = [None]*3
        for index in range(num_door):
            self.door[index] = lvl
        np.random.shuffle(self.door)
        
    def get_lvl(self):
        return self.lvl
    
    def set_orientation(self,orientation):
        self.orientation = orientation
    
    def get_door_index(self,direction):
        direction = self.directions[direction.upper()]
        if self.orientation is None: 
            orientation = 'S'
        else:
            orientation = self.orientation
        orientation = self.directions[orientation.upper()] #doing it this way in case additional directions values are added
        if orientation == direction:
            return []
        else:
            direction = 3 - orientation + direction#does door shifting based on direction
            direction = np.mod(direction,4) #wraps direction values >2 around to 0-3
            return direction
            
    def get_door_lvl(self,index):
        return self.door[index]
    def set_position(self, row,col):
        self.row = row
        self.col = col
    def get_position(self):
        return (self.row,self.col)
        
        
            

class room_deck(object):
    def __init__(self):
        self.deck = []
       
    def add_room(self,room):
        self.deck.append(room)
        
    def remove_room(self,index):
        del self.deck[index]
        
    def get_room(self,index):
        return self.deck[index]
        
    def shuffle_deck(self):
        np.random.shuffle(self.deck)
        
    def find_lvl(self,lvl): #Finds the next room with a level in the range indicated and returns the index 
        if isinstance(lvl,int):
            lvl=[lvl]
        matching_rooms = []        
        for index in range(len(self.deck)):
            if self.deck[index].get_lvl() in lvl:
                matching_rooms.append(index)
        return matching_rooms
                        
    def add_rand_room(self,lvl,num_room = 1,num_door=None):
        for index in range(num_room):
            r = room(lvl)
            if num_door is None:
                r.rand_door()
            elif isinstance(num_door,int):                                
                r.rand_door(num_door=num_door)
            else:#otherwise num_door is a list so pick one randomly
                r.rand_door(num_door=num_door[np.random.randint(0,len(num_door))])
            
            self.add_room(r)
            
    def show(self,index=None):
        if index is None: #show all the rooms
            index = range(len(self.deck))
        for i in index:
            print '\nRoom {}:'.format(i)
            self.deck[i].show()

        
class map(object):
    def __init__(self,rows,cols):
        self.direction = [['N','E','S','W'],[-1,0,1,0],[0,1,0,-1]] #text transform, row adjustment, col adjustment
        self.rows = rows
        self.cols = cols
        self.map=np.array([[None]*cols]*rows)
        self.lvl_map=np.array([[np.nan]*cols]*rows)
        self.current_position = np.ceil([rows-1, (cols)/2 ]).astype(int)
        self.fig = None        
        print 'Current Position: {}'.format(self.current_position)
        start_room = room(-1)
        start_room.add_door([0],1)
        start_room.set_position(self.current_position[0],self.current_position[1])
        start_room.set_orientation('S')
        self.add_room(start_room,self.current_position[0],self.current_position[1],'S')        
        
    def show(self):
        if self.fig is None:
            self.fig = plt.figure()
            self.fig.add_subplot(111, aspect='equal')
            plt.axis([0,self.cols,0,self.rows])
            self.map_plot = plt.imshow(self.lvl_map,interpolation='none',cmap='jet',vmin=-1,vmax=np.nanmax([5,np.nanmax(self.lvl_map)]))    #may need to use np.flipud
        else:
            self.fig.clear()
            self.fig.add_subplot(111, aspect='equal')
            plt.axis([0,self.cols,0,self.rows])
            self.map_plot = plt.imshow(self.lvl_map,interpolation='none',cmap='jet',vmin=-1,vmax=np.nanmax([5,np.nanmax(self.lvl_map)]))    #may need to use np.flipud
            
            #self.map_plot.set_data(self.lvl_map)
            #print self.lvl_map
        #Drawing doors
        for current_row in range(self.rows): 
            rooms_in_row = [i for i in self.map[current_row] if i is not None]
            if len(rooms_in_row) > 0:
                for index in rooms_in_row:
                    self.draw_room_doors(index) #Made a separate method just in case I wanted to make a fancier method than just lines
                    #index.show()
        self.fig.canvas.draw()
        
    def draw_room_doors(self,room): #Draws the room using only room info    
        for direction in range(4):
            door_index = room.get_door_index(self.direction[0][direction]) #Can be door_index of [] or an int
            
            if (not isinstance(door_index,int)) or (room.get_door_lvl(door_index) is not None) :  
                plt.plot([room.col,room.col + self.direction[2][direction]*.5],
                         [room.row,room.row + self.direction[1][direction]*.5],
                         'k-',linewidth=4)
                plt.plot([room.col,room.col + self.direction[2][direction]*.5],
                         [room.row,room.row + self.direction[1][direction]*.5],
                         'w-',linewidth=2)
    
    def add_room(self,room,row,col,orientation):
        if self.map[row][col] is not None:
            print 'Overriding room...'
            self.map[row][col].set_position(None,None) #removing the old room from the map
        room.set_orientation(orientation)
        room.set_position(row,col)
        self.map[row][col] = room
        self.lvl_map[row][col]=room.get_lvl() #For easier plotting later
        #Exploring each door to see of anything connects        
        for index in range(4):
            #check each direction and if there is a room
            current_door = room.get_door_index(self.direction[0][index])
            if not isinstance(current_door,int):
                continue
            elif room.get_door_lvl(current_door) is None:
                continue
            elif (row + self.direction[1][index] < 0) or (row + self.direction[1][index] >= np.size(self.map,0)): 
                room.add_door(None,current_door)
            elif (col + self.direction[2][index] < 0) or (col + self.direction[2][index] >= np.size(self.map,1)):
                room.add_door(None,current_door)
            elif self.map[row+self.direction[1][index]][col+self.direction[2][index]] is not None:
                room.add_door([],current_door) #Removes lvl limits but keeps door there since there is a room already there

        
    def expand_map(self,room_deck):#uses the current position to expand any unexplored hallways
        current_room = self.map[self.current_position[0]][self.current_position[1]] 
        for direction in range(4):
            current_door = current_room.get_door_index(self.direction[0][direction])
            if not isinstance(current_door,int): #if already connected
                continue
            door_lvl = current_room.get_door_lvl(current_door)
            if (door_lvl is None) : #If no door, move on
                continue
            elif len(door_lvl)==0:
                continue
            
            new_room_index = room_deck.find_lvl(door_lvl)
            #print new_room_index
            if len(new_room_index) == 0:#No valid rooms left so close the door
                current_room.add_door(None,current_door)
            else:
                current_room.add_door([],current_door)
                self.add_room(room_deck.get_room(new_room_index[0]),
                    self.current_position[0] + self.direction[1][direction],
                    self.current_position[1] + self.direction[2][direction],
                    self.direction[0][np.mod(direction+2,4)])
                room_deck.remove_room(new_room_index[0])
            
    def change_position(self,row,col):
        if self.map[row][col] is None:
            print 'There is no room at row {}, col {}. Position not changed'.format(row,col)
        else:
            self.current_position = [row,col]
            
    def manual_move(self,deck):
        new_position = plt.ginput(1)
        new_position = np.round(new_position[0]).astype(int)
        print 'Position Selected: {}'.format(new_position)
        self.change_position(new_position[1],new_position[0])
        self.expand_map(deck)
        

#Create room deck
deck = room_deck()
room_distb = [30,20,10,5,1]
for lvl in range(len(room_distb)):
    for index in range(room_distb[lvl]):
        r = room(lvl)
        r.rand_door()    
        deck.add_room(r)
deck.shuffle_deck()    
deck.show()


'''
Below creates a sample map to explore
Click on a room to expand it, 
Click on the starting blue room to exit
'''
        
test = map(15,15)
test.expand_map(deck)
test.change_position(test.current_position[0]-1,test.current_position[1])
test.expand_map(deck)
test.show()


print 'Objective: Get to the Red Room.'
print 'Controls: Click on a room to explore adjacent pathways. Click on the starting blue room to exit.'
print 'Each room leads to like colored rooms and rooms that are one level above and below it'
print 'Room Distributions:'
for i in range(len(room_distb)):
    print 'Lvl {}: {}'.format(i,room_distb[i])


while 1:
    test.manual_move(deck)
    test.show()
    if ((test.current_position == np.ceil([test.rows-1, (test.cols)/2 ]).astype(int)).all()) or (test.lvl_map[test.current_position[0],test.current_position[1]] == len(room_distb)-1):
        print 'Ending Exploration'
        print 'Total Rooms Explored: {} out of {}'.format(test.rows*test.cols - np.sum(np.isnan(test.lvl_map)),np.sum(room_distb))
        break

