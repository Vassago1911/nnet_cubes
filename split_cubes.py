class cube:
    lefts = list()
    rights = list()
    dimension = len(lefts)
    top_parent_boundaries = list()
    smallest_length = -1
    aspect_ratio = -1
    min_scale = .1
    max_aspect_ratio = 10.

    def __init__(self,ls=[1,], 
                      rs=[1,], 
                      min_scale = .1, 
                      max_ratio = 10.,
                      top_parent_boundaries = list()):
        def __test_for_number_type__(ls,rs):            
            assert (len(ls)==len(rs)),'Left and right boundaries need the same count!'
            #we need comparable coods, so lt = < needs to be implemented
            assert (all([getattr(i,'__lt__',False) for i in ls])),'Coordinates don\'t have order, no number type?'
            assert (all([getattr(i,'__lt__',False) for i in rs])),'Coordinates don\'t have order, no number type?'        
            #coods need to satisfy l[i] < r[i] \forall i
            assert (all([l<r for l,r in zip(ls,rs)])),'Not all left boundaries are smaller than their right boundaries'
            #we need as many lefts as rights
            #we furthermore need to be able to do (a+b)/2 on all coods
            assert (all([getattr(i,'__add__',False) for i in ls])), 'No addition on coordinates, no number type?'
            assert (all([getattr(i,'__add__',False) for i in rs])), 'No addition on coordinates, no number type?'
            assert (all([getattr(i,'__truediv__',False) for i in ls])), 'No division on coordinates, no number type?'
            assert (all([getattr(i,'__truediv__',False) for i in rs])), 'No division on coordinates, no number type?'
        __test_for_number_type__(ls,rs)
        #set up a cube [l1,r1]x[l2,r2]x..x[ln,rn] with default [-1,1]
        self.lefts = ls; self.rights = rs
        axes_lengths = [j-i for i,j in zip(self.lefts, self.rights)]
        self.smallest_length = min(axes_lengths)
        self.aspect_ratio = max(axes_lengths)/self.smallest_length
        self.dimension = len(self.lefts)
        self.min_scale = min_scale
        self.max_aspect_ratio = max_ratio
        if( len(top_parent_boundaries)==0):
            self.top_parent_boundaries = [self.lefts, self.rights]
        else:
            self.top_parent_boundaries = top_parent_boundaries

    #is a point part of this cube?
    def contains(self,x):
        assert(len(x) == self.dimension)
        return all([li <= xi for li,xi in zip(self.lefts,x)]+[xi <= ri for xi,ri in zip(x,self.rights)])

    def split(self,i):
        print('trying to split the cube: ', self)
        center_i = (self.lefts[i] + self.rights[i])/2
        new_left = list(self.lefts); new_left[i] = center_i
        new_right = list(self.rights); new_right[i] = center_i  
        cube1 = cube(self.lefts, new_right,\
                     self.min_scale, self.max_aspect_ratio, self.top_parent_boundaries)
        cube2 = cube(new_left, self.rights,\
                     self.min_scale, self.max_aspect_ratio, self.top_parent_boundaries)
        if((cube1.aspect_ratio <= self.max_aspect_ratio)\
            &(cube1.smallest_length >= self.min_scale)):      
            print('into: ', cube1,' and ', cube2)              
            return [cube1, cube2,]
        else:
            if(cube1.aspect_ratio>self.max_aspect_ratio):
                print(cube1.aspect_ratio)
                print('Aspect Ratio too big, returning original cube.')
                return [self,]
            else:
                print(cube1.smallest_length)
                print('Axis split below smallest length, returning original cube.')
                return [self,]

    def __str__(self):
        return 'x'.join([str([l,r]) for l,r in zip(self.lefts, self.rights)])

    def rectangle_coods(self):
        #for plots generate lower left (x,y) from dims 1,2 and width, height
        #from there too
        return ((self.lefts[0],self.lefts[1]), self.rights[0] - self.lefts[0], self.rights[1] - self.lefts[1])

test_cube = cube([0,0,0],[1,1,1])

from random import randint
rd = lambda : randint(0,test_cube.dimension-1)
rd1 = lambda : randint(0,1)

for i in range(10):
    x = test_cube.split(rd()) 
    ix = min(len(x)-1,rd1())        
    test_cube = x[ix]

import matplotlib; import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)
rect1 = matplotlib.patches.Rectangle((-200,-100), 400, 200, color='yellow')
rect2 = matplotlib.patches.Rectangle((0,150), 300, 20, color='red')
rect3 = matplotlib.patches.Rectangle((-300,-50), 40, 200, color='#0099FF')
ax.add_patch(rect1)
ax.add_patch(rect2)
ax.add_patch(rect3)
plt.xlim([-400, 400])
plt.ylim([-400, 400])
plt.show()

