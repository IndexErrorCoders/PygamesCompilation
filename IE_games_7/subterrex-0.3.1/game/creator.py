"""Creates caves randomly

Core code came from: 
    http://pixelenvy.ca/wa/ca_cave.html
    Dana Larose
    dana@pixelenvy.ca

Updated to integrate with the serge engine by Paul Paterson

"""

from random import randrange, seed

PERM_WALL = 0
WALL = 1
FLOOR = 2

class CA_CaveFactory:
    def __init__(self, length, width, initial_open=0.40, random_seed=None):
        self.__length = length
        self.__width = width
        self.__area = length * width
        self.__map = []
        self.__ds = DisjointSet()
        self.__up_loc = 0
        self.center_pt = (int(self.__length/2),int(self.__width/2))
        seed(random_seed)
        self.__gen_initial_map(initial_open)

    def get_map(self):
        """Return the map"""
        return [[v in (WALL,PERM_WALL) for v in row] for row in self.__map]

    def print_grid(self):
        x = 0
        row = ""

        for r in range(0,self.__length):
            for c in range(0,self.__width):
                if self.__map[r][c] in (WALL,PERM_WALL):
                    print '#',
                else:
                    print '.',

            print

    def gen_map(self):
        for r in range(1,self.__length-1):
            for c in range(1,self.__width-1):
                wall_count = self.__adj_wall_count(r,c)

                if self.__map[r][c] == FLOOR:
                    if wall_count > 5:
                        self.__map[r][c] = WALL
                elif wall_count < 4:
                    self.__map[r][c] = FLOOR

        self.__join_rooms()

        return self.__map

    def add_entrance(self, rows, width, buffer_width):
        """Adds an entrace to the cave"""
        #
        # Position the location of the entrance
        location = randrange(buffer_width, self.__width-buffer_width-width)
        #
        # Insert surface rows
        self.__map.insert(0, [FLOOR for i in range(self.__width)])
        for r in range(rows):
            self.__map.insert(0, [FLOOR for i in range(self.__width)])
            self.__length += 1
        #
        # Drill down
        for r in range(rows+1, self.__length):
            for c in range(width):
                if self.__map[r][location+c] == FLOOR:
                    # Broke through!
                    return (location+width/2, rows-1)
                else:
                    self.__map[r][location+c] = FLOOR
        #
        return (location+width/2, rows-1)                    
                            
    def add_exit(self, width, buffer_width):
        """Adds an exit to the cave"""
        #
        # Position the location of the entrance
        location = randrange(buffer_width, self.__width-buffer_width-width)
        #
        # Drill down
        for r in range(self.__length, 0, -1):
            for c in range(width):
                if self.__map[r][location+c] == FLOOR:
                    # Broke through!
                    return (location+width/2, self.__length)
                else:
                    self.__map[r][location+c] = FLOOR
        return (location+width/2, self.__length)
        
    # make all border squares walls
    # This could be moved to a superclass
    def __set_border(self):
        for j in range(0,self.__length):
            self.__map[j][0] = PERM_WALL
            self.__map[j][self.__width-1] = PERM_WALL

        for j in range(0,self.__width):
            self.__map[0][j] = PERM_WALL
            self.__map[self.__length-1][j] = PERM_WALL

    def __gen_initial_map(self,initial_open):
        for r in range(0,self.__length):
            row = []
            for c in range(0,self.__width):
                row.append(WALL)
            self.__map.append(row)

        open_count = int(self.__area * initial_open)
        self.__set_border()

        while open_count > 0:
            rand_r = randrange(1,self.__length-1)
            rand_c = randrange(1,self.__width-1)

            if self.__map[rand_r][rand_c] == WALL:
                self.__map[rand_r][rand_c] = FLOOR
                open_count -= 1

    def __adj_wall_count(self,sr,sc):
        count = 0

        for r in (-1,0,1):
            for c in (-1,0,1):
                if self.__map[(sr + r)][sc + c] != FLOOR and not(r == 0 and c == 0):
                    count += 1

        return count

    def __join_rooms(self):
        # divide the square into equivalence classes
        for r in range(1,self.__length-1):
            for c in range(1,self.__width-1):
                if self.__map[r][c] == FLOOR:
                    self.__union_adj_sqr(r,c)

        all_caves = self.__ds.split_sets()

        for cave in all_caves.keys():
            self.__join_points(all_caves[cave][0])

    def __join_points(self,pt1):
        next_pt = pt1

        while 1:
            dir = self.__get_tunnel_dir(pt1,self.center_pt)
            move = randrange(0,3)

            if move == 0:
                next_pt = (pt1[0] + dir[0],pt1[1])
            elif move == 1:
                next_pt = (pt1[0],pt1[1] + dir[1])
            else:
                next_pt = (pt1[0] + dir[0],pt1[1] + dir[1])


            if self.__stop_drawing(pt1,next_pt,self.center_pt):
                return
            
            root1 = self.__ds.find(next_pt)
            root2 = self.__ds.find(pt1)

            if root1 != root2:
                self.__ds.union(root1,root2)

            self.__map[next_pt[0]][next_pt[1]] = FLOOR
            
            # Avoid one-square diagonal tunnels which don't really connect
            if move == 2:
                try:
                    self.__map[next_pt[0]][next_pt[1]+1] = FLOOR
                except IndexError:
                    self.__map[next_pt[0]][next_pt[1]-1] = FLOOR
            

            pt1 = next_pt

    def __stop_drawing(self,pt,npt,cpt):
        if self.__ds.find(npt) == self.__ds.find(cpt):
            return 1
        if self.__ds.find(pt) != self.__ds.find(npt) and self.__map[npt[0]][npt[1]] == FLOOR:
            return 1
        else:
            return 0

    def __get_tunnel_dir(self,pt1,pt2):
        if pt1[0] < pt2[0]:
            h_dir = +1
        elif pt1[0] > pt2[0]:
            h_dir = -1
        else:
            h_dir = 0

        if pt1[1] < pt2[1]:
            v_dir = +1
        elif pt1[1] > pt2[1]:
            v_dir = -1
        else:
            v_dir = 0

        return (h_dir,v_dir)

    def __union_adj_sqr(self,sr,sc):
        loc = (sr,sc)

        for r in (-1,0):
            for c in (-1,0):
                nloc = (sr+r,sc+c)

                if self.__map[nloc[0]][nloc[1]] == FLOOR:
                    root1 = self.__ds.find(loc)
                    root2 = self.__ds.find(nloc)

                    if root1 != root2:
                        self.__ds.union(root1,root2)


# A simple disjoint set ADT which uses path compression on finds
# to speed things up

class DisjointSet:
    size = 0

    def __init__(self):
        self.__items = {}

    def union(self, root1, root2):
        if self.__items[root2] < self.__items[root1]:
            self.__items[root1] = root2
        else:
            if self.__items[root1] == self.__items[root2]:
                self.__items[root1] -= 1

            self.__items[root2] = root1
    
    def find(self, x):
        try:
            while self.__items[x] > 0:
                x = self.__items[x]
        
        except KeyError:
            self.__items[x] = -1

        return x

    def split_sets(self):
        sets = {}
        j = 0

        for j in self.__items.keys():
            root = self.find(j)
            
            if root > 0:
                if sets.has_key(root):
                    list = sets[root]
                    list.append(j)

                    sets[root] = list
                else:
                    sets[root] = [j]

        return sets

    def dump(self):
        print self.__items


if __name__ == '__main__':
    import profile
    caf = CA_CaveFactory(30,40,0.41)
    profile.run("caf.gen_map()")
    caf.print_grid()

