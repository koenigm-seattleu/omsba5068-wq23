from agents.intents import intent_agent_info, intent_find_dirt, intent_find_gold
from agents.intents import intent_turn, intent_forward_backward, intent_goto, intent_go_home
from agents.intents import intent_suck_dirt_at, intent_suck_some_dirt, intent_get_gold_at, intent_get_some_gold
from agents.intents import intent_unknown

from agents.coord import is_coord, to_coord
import pickle
import numpy as np

VECTORIZER_FILE_NAME = 'agents/intent_classification/vectorizer.sav'
CLASSIFIER_FILE_NAME = 'agents/intent_classification/classifier.sav'
           
class CommandProcessor:    
    def __init__(self, agent, worldmodel, log):
        self.agent = agent
        self.worldmodel = worldmodel
        self.log = log
        self.vectorizer = pickle.load(open(VECTORIZER_FILE_NAME, 'rb'))
        self.classifier = pickle.load(open(CLASSIFIER_FILE_NAME, 'rb'))
     
    # This method takes a command as input and produces the predicted
    # case label /intent, as well as a coordinate or a number if 
    # either was found in the command
    
    def classify_intent(self, cmd):
        if not cmd or len(cmd) == 0:
            return None
        
        # Extract the extra features:  ends_with_question,
        # has_coord, and has_number
        ends_with_question = cmd[-1] == '?'
        # get the coord if there is one
        has_coord = False
        coord = None
        for w in cmd.split():
            if is_coord(w):
                has_coord = True
                coord = to_coord(w)
        # get the number if there is one
        has_number = False
        number = None
        for w in cmd.split():
            if w.isdigit():
                has_number = True
                number = int(w)
        
        # Vectorize the input -- produces an array w/ one column per feature
        tarray = self.vectorizer.transform([cmd]).toarray()
        # Convert our "other" features to an array
        farray = np.reshape(np.asarray([ends_with_question, has_coord, has_number]), (1,3))
        # Concatenate our "other" features with the vectorized features.  The 
        # order is significant.  The classifier is expecting to see features in 
        # the same order as it saw them in training, and in training we 
        # happen to put the "other" features first
        carray = np.reshape(np.concatenate((farray, tarray), axis=None), (1,-1))
        # Call the classifier on the concatenated array
        return (self.classifier.predict(carray), coord, number)
        
    def interpret_command(self, cmd):
        
        # The intent returned here is guaranteed to be one of the training
        # case labels.  But beware ... if the training set case labels
        # changes, this code must change too.
        
        intent, coord, number = self.classify_intent(cmd)
        
        # This code is essentially the same as the manual case -- 
        # map inferred intents into intent commands implemented
        # in the agent code -- the intent_* functions produce
        # "executable" agent code
        
        command_sequence = None
        if intent == 'move_forward':
            command_sequence = intent_forward_backward(self, 'forward', number)
        elif intent == 'move_backward':
            command_sequence = intent_forward_backward(self, 'backward', number)
        elif intent == 'turn_left':
            command_sequence = intent_turn(self, 'left')
        elif intent == 'turn_right':
            command_sequence = intent_turn(self, 'right')
        elif intent == 'turn_around':
            command_sequence = intent_turn(self, 'around')
        elif intent == 'suck_dirt':
            if coord:
                command_sequence = intent_suck_dirt_at(self, coord)
            else:
                command_sequence = intent_suck_some_dirt(self)
        elif intent == 'go_to':
            command_sequence = intent_goto(self, coord) 
        elif intent == 'go_home':
            command_sequence = intent_go_home(self)
        elif intent == 'get_gold':
            if coord:
                command_sequence = intent_get_gold_at(self, coord)
            else:
                command_sequence = intent_get_some_gold(self)
        elif intent == 'find_gold':
            command_sequence = intent_find_gold(self)
        elif intent == 'find_dirt':
            command_sequence = intent_find_dirt(self)
        elif intent == 'agent_info':
            command_sequence = intent_agent_info(self)
        else:
            raise(Exception(f"Did not recognize intent {intent}"))
        return command_sequence
