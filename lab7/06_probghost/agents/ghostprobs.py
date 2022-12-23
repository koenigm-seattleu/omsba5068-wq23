# Probability of a color given a distance from the ghost
def default_probe_probs():
    return {
        0:  {"red": .94, "orange": .03, "yellow": .02, "green": .01},
        1:	{"red": .15, "orange": .80, "yellow": .02, "green": .03},
        2:	{"red": .05, "orange": .85, "yellow": .06, "green": .04},
        3:	{"red": .05, "orange": .15, "yellow": .5,  "green": .3},
        4:	{"red": .01, "orange": .09, "yellow": .75, "green": .15},
        5:	{"red": .01, "orange": .04, "yellow": .10, "green": .85},
        6:	{"red": .001, "orange": .01, "yellow": .02, "green": .97},
        7:	{"red": .001, "orange": .01, "yellow": .01, "green": .98}
        }

#  Initialize -- give size of grid, and conditional probabilities for the 
#    probe sensor.  If None, assign the probabilities as in the class example

class GhostProbs:
    def __init__(self, probe_probs, size=10):
        probe_probs = probe_probs if probe_probs else default_probe_probs()
        self.probe_probs = probe_probs
        self.size = size
        self.all_coords = [(i,j) for i in range(1,size+1) for j in range(1,size+1)]
        self.probs = self.ghost_prob_prior()

    # Ghost probability for a single square
    def coord_prob(self, coord):
        return self.probs[coord]
    
    # Ghost probabilities for all squares, sorted in descending order of probability
    def sorted_coords(self):
        return sorted(list(self.probs.items()), key = lambda t: t[1], reverse = True)
    
    def update_probe(self, probe_report):
        old_probs = self.probs
        self.probs =  dict([self.calc_ghost_prob(coord, old_probs, probe_report) for coord in self.all_coords])

    # Update probabilities on the basis of a bust percept
    #   bust_report is (value, square)  where value is True or False
    def update_bust(self, bust_report):
        bust_val, bust_loc = bust_report
        if bust_val:
            for coord in self.all_coords:
                self.probs[coord] = 1 if coord == bust_loc else 0
        else:
            probsum = 0.0
            for coord in self.all_coords:
                probsum += self.probs[coord] if coord != bust_loc else 0.0
            for coord in self.all_coords:
                self.probs[coord] = 0.0 if coord == bust_loc else self.probs[coord] / probsum
                
    ############################################
    
    def ghost_prob_prior(self):
        prior = 1.0 / (self.size * self.size)
        priors = {}
        for coord in self.all_coords:
            priors[coord] = prior
        return priors
    
    def coord_distance(self, c1, c2):
        row1, col1 = c1
        row2, col2 = c2
        return abs(row1 - row2) + abs(col1 - col2)
            
    def calc_ghost_prob(self, coord, priors, probe_report):
        probe_val, probe_loc = probe_report
        dist = self.coord_distance(coord, probe_loc)
        dist = dist if dist <= 7 else 7
        return (coord, (self.probe_probs[dist][probe_val] * self.probs[coord]) / self.probe_prob(probe_report))
        
    def probe_prob(self, probe_report):
        priors = self.probs
        probe_val, probe_loc = probe_report
        prob_return = 0.0
        for coord in self.all_coords:
            prob_return += self.probe_probs[min(self.coord_distance(probe_loc, coord), 7)][probe_val]  * priors[coord]
        return prob_return
    
################

def test_ghost_probs():
    
    def reportTest(message, actual, expected):
        if abs(actual - expected) < .001:
            print(message + " succeeded")
        else:
            print(f"Test {message} failed -- expected {expected} got {actual}")
        
    gp = GhostProbs(default_probe_probs(), 10)
    gp.update_probe(('red', (5,5)))
    gp.update_probe(('orange', (4,5)))
    reportTest("Prob (4,6)", gp.coord_prob((4,6)), 0.025584935589924626)
    gp.update_probe(('orange', (6,5)))
    gp.update_probe(('red', (1,1)))
    gp.update_probe(('red', (1,2)))
    reportTest("Prob (2,4)", gp.coord_prob((2,4)), 0.01234617692400765)
    sp = gp.sorted_coords()
    reportTest("Most probable", sp[0][1], 0.2475820012494335)
    gp.update_bust((False, (3,10)))
    reportTest("Post false update (3,10)", gp.coord_prob((3,10)), 0.0)
    reportTest("Post false update (5,5)", gp.coord_prob((5,5)), 0.2475820114384043)
    gp.update_bust((True, (9,8)))
    reportTest("Post true update (9,8)", gp.coord_prob((9,8)), 1)
    reportTest("Post true update (9,9)", gp.coord_prob((9,9)), 0)
    
#test_ghost_probs()  

####################################
def test_ghost_probs_small():
    probe_probs = {
            0:  {"red": .95, "orange": .03, "yellow": .01, "green": .01},
            1:	{"red": .02, "orange": .95, "yellow": .02, "green": .01},
            2:	{"red": .05, "orange": .90, "yellow": .03, "green": .02}
            }
    gp = GhostProbs(probe_probs, 2)
    print(gp.sorted_coords())
    gp.update_probe(('orange', (2,2)))
    print(gp.sorted_coords())
    print(gp.probe_probs)
    
#test_ghost_probs_small()