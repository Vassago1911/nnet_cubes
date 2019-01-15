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

    #half the cube along the i-th axis
    def split(self,i):
        print('trying to split the cube: ', self)
        center_i = (self.lefts[i] + self.rights[i])/2
        new_left = list(self.lefts); new_left[i] = center_i
        new_right = list(self.rights); new_right[i] = center_i  
        cube1 = cube(self.lefts, new_right,\
                     self.min_scale, self.max_aspect_ratio, self.top_parent_boundaries)
        cube2 = cube(new_left, self.rights,\
                     self.min_scale, self.max_aspect_ratio, self.top_parent_boundaries)
        #too slim?             
        if(cube1.aspect_ratio>self.max_aspect_ratio):
            print(cube1.aspect_ratio)
            print('Aspect Ratio too big, returning original cube.')
            return [self,]
        #too small axes?    
        if(cube1.smallest_length<self.min_scale):
            print(cube1.smallest_length)
            print('Axis split below smallest length, returning original cube.')
            return [self,]                
        #neither, so split    
        print('into: ', cube1,' and ', cube2)              
        return [cube1, cube2,]                

    def __str__(self):
        return 'x'.join([str([l,r]) for l,r in zip(self.lefts, self.rights)])

    #generate matplotlib.rectangle 2d coods based on the first two dims 
    def rectangle_coods(self):                
        return ((self.lefts[0],self.lefts[1]), self.rights[0] - self.lefts[0], self.rights[1] - self.lefts[1])

def gen_random_2d_partition(split_tries = 32):
    from random import randint, shuffle
    test_cube = cube([0,0],[1,1],min_scale=.05)
    rd = lambda : randint(0,test_cube.dimension-1)
    rd1 = lambda : randint(0,1)
    l = [test_cube]
    for i in range(split_tries):
        x = l.pop()
        l = l + x.split(rd())
        shuffle(l)
    return l    

def plot_list_of_cubes(l=list()):
    import matplotlib; import matplotlib.pyplot as plt
    from random import random 
    if(len(l)==0):
        l = gen_random_2d_partition()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for c in l:
        rect = matplotlib.patches.Rectangle(*(c.rectangle_coods()), color=(random(),random(),random()))
        ax.add_patch(rect)
    plt.xlim([1.1*(c.top_parent_boundaries[0][0]-.1), 1.1*(c.top_parent_boundaries[1][0])+.1])
    plt.xlim([1.1*(c.top_parent_boundaries[0][1]-.1), 1.1*(c.top_parent_boundaries[1][1])+.1])
    plt.show()

plot_list_of_cubes();