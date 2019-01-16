class cube:
    lefts = list()
    rights = list()
    dimension = len(lefts)
    top_parent_boundaries = list()
    smallest_length = -1
    aspect_ratio = -1
    min_scale = .1
    max_aspect_ratio = 10.
    splittable = False

    #where are we allowed to split?
    def get_split_axes(self):
        def aspect_ratio(lgts):                
            return max(lgts)/min(lgts)
        halvable_lengths = [self.min_scale < (j-i)/2 for i,j in zip(self.lefts,self.rights)]
        ixs = [i for i,x in enumerate(halvable_lengths) if x]        
        lengths = [j-i for i,j in zip(self.lefts, self.rights)]
        jxs = list()
        for ix in ixs:
            l = lengths[:ix] + [lengths[ix]/2,] + lengths[ix+1:]            
            if(aspect_ratio(l)<self.max_aspect_ratio):
                jxs = jxs + [ix,]        
        return jxs

    def __init__(self,ls=[-1,], 
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
        if(len(self.get_split_axes())>0):
            self.splittable = True

    #is a point part of this cube?
    def contains(self,x):
        assert(len(x) == self.dimension)
        return all([li <= xi for li,xi in zip(self.lefts,x)]+[xi <= ri for xi,ri in zip(x,self.rights)])

    #half the cube along the i-th axis
    def split(self,i):
        if(not self.splittable):
            print('Cube is already too small, no split!')
            return [self,]
        print('Split the cube ',self,':')        
        center_i = (self.lefts[i] + self.rights[i])/2
        new_left = list(self.lefts); new_left[i] = center_i
        new_right = list(self.rights); new_right[i] = center_i  
        cube1 = cube(self.lefts, new_right,self.min_scale, self.max_aspect_ratio, self.top_parent_boundaries)
        cube2 = cube(new_left, self.rights,self.min_scale, self.max_aspect_ratio, self.top_parent_boundaries)           
        print('into: ', cube1,' and ', cube2)              
        return [cube1, cube2,]                

    def __str__(self):
        return 'x'.join([str([l,r]) for l,r in zip(self.lefts, self.rights)])

    #generate matplotlib.rectangle 2d coods based on the first two dims 
    def rectangle_coods(self):                
        return ((self.lefts[0],self.lefts[1]), self.rights[0] - self.lefts[0], self.rights[1] - self.lefts[1])

class data_cube(cube):    
    def get_classes(self,df,scaler):
        import pandas as pd
        df_target = df[df.columns[-1]]
        df = pd.DataFrame(scaler.transform(df[df.columns[:-1]]))
        df['target'] = df_target      
        ls = self.lefts; rs = self.rights  
        for i,_ in enumerate(ls):
            df = df[ls[i]<=df[i]]
            df = df[df[i]<=rs[i]] 
        self.classes = dict(df['target'].value_counts()) #this is why it's only classification!!
        self.homogeneous = len(self.classes) <= 1 #less than 1 class in the cube => homogeneous or empty

    def get_homogeneity(self,df,scaler):
        self.get_classes(df,scaler)
        class_pairs = [(i,j) for i in self.classes for j in self.classes if i!=j]
        #if there are no class_pairs, then there's either just one or no classes => homogeneous! 
        if(len(class_pairs)==0):
            self.homogeneity = 1 #maximally homogeneous       
            return 1
        f = lambda x,y: (x-y)/(x+y)
        res = list()        
        for i,j in class_pairs:
            res = res + [f(self.classes[i],self.classes[j]),]            
        self.homogeneity = min(res)    
        return min(res)    

    def split(self,i,df,scaler):
        if(not self.splittable):
            print('Cube is already too small, no split!')
            return [self,]
        print('Split the cube ',self,':')        
        center_i = (self.lefts[i] + self.rights[i])/2
        new_left = list(self.lefts); new_left[i] = center_i
        new_right = list(self.rights); new_right[i] = center_i  
        cube1 = data_cube(self.lefts, new_right,self.min_scale, self.max_aspect_ratio, self.top_parent_boundaries)
        cube2 = data_cube(new_left, self.rights,self.min_scale, self.max_aspect_ratio, self.top_parent_boundaries)           
        cube1.get_homogeneity(df,scaler)
        cube2.get_homogeneity(df,scaler)
        print('into: ', cube1,' and ', cube2)              
        return [cube1, cube2,]

    def best_split(self,df,scaler):
        #make sure they're set        
        self.get_homogeneity(df,scaler)

        #if the cube is already homogeneous, don't split
        if(self.homogeneous):
            print('Already homogeneous, don\'t split.')
            return [self,]
        if(not self.splittable):
            print('Too small to split.')
            return [self,]
        #we should never get here, but I want a transparent error if we ever do
        if(len(self.get_split_axes())==0):
            print('No valid axes for splitting!')
            return  [self,]
        #not homogeneous, still splittable per size, let's find the best axis
        if(len(self.get_split_axes())==1):
            #best axis known it's the only one :)
            return cube.split(self,self.get_split_axes()[0])
        #now we have more than one axis and want to find the best one to split 
        homogeneity_candidate = -1000
        candidates = [1,2]
        for ax in self.get_split_axes():
            #try to split, find maximal homogeneity among candidates
            c1,c2 = self.split(ax,df,scaler)
            if max(c1.homogeneity, c2.homogeneity) > homogeneity_candidate:
                candidates = [c1,c2]                
                homogeneity_candidate = max(c1.homogeneity, c2.homogeneity)
            else:
                pass
        return candidates      

#initial construction of a cube from a dataframe
def from_dataframe(df, min_scale=.1,max_ratio=10):
    import pandas as pd
    df = df.select_dtypes(include='number')                            
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    scaler.fit(df[df.columns[:-1]])               
    ls = len(df.columns[:-1])*(0,) #left boundaries are zeroes
    rs = len(df.columns[:-1])*(1,) #right boundaries are ones
    c = data_cube(ls, rs, min_scale, max_ratio, top_parent_boundaries = (ls,rs))     
    c.get_homogeneity(df,scaler)       
    return c, df, scaler #prepared for handoff to get_classes and get_homogeneity

def gen_random_2d_partition(split_tries = 32):
    from random import randint, shuffle
    test_cube = cube([0,0],[1,1],min_scale=.05)
    rd = lambda : randint(0,test_cube.dimension-1)    
    l = [test_cube]
    for _ in range(split_tries):
        x = l.pop()
        l = l + x.split(rd())
        shuffle(l)
    return l    

#plots a random example partition if called without parameters,
#otherwise meant to plot any list of cubes
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

def example_df_xor(length = 250):
    from random import random, randint
    from pandas import DataFrame
    l = [(round(i-.1 + .2*random(),4),round(j-.1+.2*random(),4),i^j) for i,j in  [(randint(0,1),randint(0,1)) for i in range(length)]]
    return DataFrame(l)

def partition_datacubes_for_df(df):
    from random import shuffle
    init_c,df,scaler = from_dataframe(df)
    inhom_stack = [init_c,]
    homog_stack = list()
    empty_stack = list()
    unsplit_stack = list()
    while len(inhom_stack) != 0:
        c = inhom_stack.pop()
        cs = c.best_split(df,scaler)        
        if(len(cs)==1): #couldn't split, find right stack / reason
            if(len(cs[0].classes)==0):
                empty_stack.append(cs[0])
            if(len(cs[0].classes)==1):
                homog_stack.append(cs[0])
            unsplit_stack.append(cs[0])
        else:    
            #did split, but not done
            inhom_stack = inhom_stack + cs
        shuffle(inhom_stack)
    return homog_stack, empty_stack, unsplit_stack

df = example_df_xor(10000) 
cc = from_dataframe(df)
#print(cc.classes)


