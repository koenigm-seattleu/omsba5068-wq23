# Here are the sensor noise parameters.  Keys are distances, then values are 
# probability distributions.  For example, if the distance between the agent 
# and the ghost is 3, then 3% of the time the sensor will report "red",  7% of the time "orange",
# 80% of the time "yellow", and 10% of the time "green".

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

################################################################
#  Stores a probability distribution over coordinates:  a coordinate is
#  (3,4) for example, and the probability is the probability that the ghost
#  is at (3,4).  This class handles probabilistic updates (by Bayes Rule) when 
#  a new Probe percept is received and when a new Bust percept is received.

class GhostProbs:
    def __init__(self, probe_probs, size=10):
        probe_probs = probe_probs if probe_probs else default_probe_probs()
        self.probe_probs = probe_probs
        self.size = size
		# This is [(1,1), (1,2), ... (10,10)].  These are all the keys into the probability distribution
        self.all_coords = [(i,j) for i in range(1,size+1) for j in range(1,size+1)]
		# This holds the probability distribtion.  It should be initialized so each of the squares is equally 
		# likely to have the ghost.
        self.probs = self.ghost_prob_prior()
		
	# Point probability for a single coordinate -- for example coord_prob((2,3)) returns the probability
	# that the ghost is at (2,3)
    def coord_prob(self, coord):
        return self.probs[coord]
    
	# Return all coordinates and probabilities, in descending order of probability.
	#  For example   sorted_coords()  =>  [((2,2), .5), ((2,3), .01), ..... ((5,6), .0000000001)]
	
    def sorted_coords(self):
        return sorted(list(self.probs.items()), key = lambda t: t[1], reverse = True)
    
	# Update the probabilites in self.probs according to this probe report, which will be for example ("red", (2,2))
    def update_probe(self, probe_report):
        return None           # YOUR CODE HERE

	# Update the probabilities in self.probs according to this bust report, which will be for example (True, (2,2))
	#  Notice that for (True, (2,2)) the probablity entry for (2,2) should become 1, and all other probabilities will be 0
	#  For (False, (2,3)) the probability entry for (2,3) should become 0, and the other probabilities are adjusted so they
	#   sum to 1
	
    def update_bust(self, bust_report):
        return None # Your code here
                
    ############################################
    # Assign a uniform prior probability over all coordinates
    
    def ghost_prob_prior(self):
        prior = 1.0 / (self.size * self.size)
        priors = {}
        for coord in self.all_coords:
            priors[coord] = prior
        return priors
    
###################################################################
#  Here are some tests you can run on your Ghost Probabilities

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
    
    
# test_ghost_probs()  
