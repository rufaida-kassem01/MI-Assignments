# This file contains the options that you should modify to solve Question 2
# to avoid noisy actions and achieve the desired policies decrease noise 
# to make the agent avoid  terminal states increase living reward to make the agent prefer living longer
#to get the maximum reward increase discount factor to make the agent consider future rewards more

def question2_1():
    #TODO: Choose options that would lead to the desired results 
    return {
        "noise": 0.2,          
        "discount_factor": 0.5,
        "living_reward": -4
    }

def question2_2():
    #TODO: Choose options that would lead to the desired results
    return {
        "noise": 0.2,
        "discount_factor":0.3,
        "living_reward": 0
    }

def question2_3():
    #TODO: Choose options that would lead to the desired results
    return {
        "noise": 0.2,
        "discount_factor": 1,
        "living_reward": -2
    }

def question2_4():
    #TODO: Choose options that would lead to the desired results
        return {
        "noise": 0.2,
        "discount_factor": 1,
        "living_reward": -0.1
    }

def question2_5():
    #TODO: Choose options that would lead to the desired results
    return {
        "noise": 0,
        "discount_factor": 1,
        "living_reward": 100
    }

def question2_6():
    #TODO: Choose options that would lead to the desired results
    return {
        "noise": 0,
        "discount_factor": 1,
        "living_reward": -100
    }