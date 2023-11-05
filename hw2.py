#Disease Simulation
from random import *

# You'll also need functions to check if files exist and are readable.
from os.path import isfile
from os import access, R_OK

######################################################################
# Specification: flip(p) flips a (weighted) coin. Returns True if a
# randomly generated float between 0 and 1 (inclusive) is less than or
# equal to the specified probability p.
#
def flip(p=0.5):
    return(random() <= p)

######################################################################
# Specification: newPop(N,I,vp,de,di) creates a new population
# agents. A population is an N-element tuple of agents, where each
# agent is represented by a dictionary with two entries. The 'state'
# of the agent (-1 <= s <= di+de) represents that agent's current
# disease condition, while the agent's 'vaccine' status (a Boolean)
# represents whether the agent has been vaccinated or not.
#
def newPop(N, I, vp, de, di):
    pop=tuple([ {'state':-1, 'vaccine':flip(vp)} for i in range(N) ])
    for i in sample(range(N), I):
        # Will be preemptively reduced on first call to update().
        pop[i]['state']=di+de+1
    return(pop)

######################################################################
# Specification: update(pop, rp) is called at the beginning of each
# simulation day to update each agent’s infection status. Agents with
# infection state 1 (i.e., at the end of their infectious period) are
# set to 0 (recovered state) with probability rp, and otherwise set to
# -1 (susceptible state). All other infectious agents have their
# infection state reduced by 1. Returns the number of active
# infections remaining.
#
def update(pop, rp):
    infections = 0
    for i in range(len(pop)):
        if pop[i]['state'] == 1:
            # Newly susceptible with p=(1-rp), else recovered. To
            # avoid 0's Boolean interpretation, we're using 1-rp so
            # that we can return -1 and default to 0. Might be more
            # easily interpretable using an explicit if/else here.
            pop[i]['state'] = (flip(1-rp) and -1) or 0
        elif pop[i]['state'] > 0:
            # Decrement state if still infectious
            pop[i]['state'] = pop[i]['state']-1
            infections = infections + 1
    return(infections)

def sim(N=100, I=1, m=5, vp=0, tp=(0.01, 0.02), de=3, di=5, rp=0.5, max=100, verbose=False):

    # Specification: susceptible(i) returns True if and only if agent
    # i is susceptible (unvaccinated and has state counter set to -1).
    #
    def susceptible(i):
        return(not pop[i]['vaccine'] and pop[i]['state'] == -1)

    # Specification: exposed(i) returns True if and only if agent i is
    # exposed (has state counter between di and di+de).
    #
    def exposed(i):
        return(di < pop[i]['state'] <= di+de)

    # Specification: infected(i) returns True if and only if agent i
    # is exposed (has state counter between 0 and di).
    #
    def infected(i):
        return(0 < pop[i]['state'] <= di)

    # Specification: infectious(i) returns True if and only if agent i
    # is infectious, that is, either infected or exposed.
    #
    def infectious(i):
        return(0 < pop[i]['state'] <= di+de)

    # Specification: recovered(i) returns True if and only if agent i
    # is in the recovered state.
    #
    def recovered(i):
        return(pop[i]['state'] == 0)

    # Create agents.
    pop = newPop(N, I, vp, de, di)

    # Good to go, now run the simulation. We'll use totinf to keep
    # track of infection events.
    totinf = I

    # Similarly, we’ll use curve, a list, to keep track of how many
    # infecteds there are each day, starting from day 0.
    curve = [totinf]

    # Run the simulation (i.e., keep looping) while there are
    # infecteds remaining (that is, while curve[-1] > 0) or until you
    # hit the failsafe number of rounds limit, max. 
    rounds = 0
    while rounds < max:
        # Beginning-of-day agent status update: returns the number of
        # active infections on the new day, which we append to the
        # pandemic curve.
        curve.append(update(pop, rp))

        # If verbose is True, show user feedback.
        if verbose:
            print("Day {}: {} of {} agents infected.".format(len(curve)-1, curve[-1], N))

        # Quit the simulation if there are no infections left.
        if curve[-1] == 0:
            print("Pandemic extinguished: {} days, {} infecteds, attack rate is {:3.1f}%.".format(len(curve), totinf, (100*totinf)/N))
            break

        # For each infected agent, sample the population to find who
        # they mix with, and then flip a coin to determine if a new
        # infection occurs.  For each new infection, update the
        # appropriate agent's status as well as totinf, the total
        # infection count.
        for i in range(N):
            # Only worry about infectious agents
            if infectious(i):
                # Generate a list encounters by random sampling
                # without replacement (see Python documentation).
                for j in sample(range(N), randint(0,m)):
                    # Is there a new infection?
                    if susceptible(j) and flip(tp[int(infected(i))]):
                        # Update totinf, the total infection count.
                        totinf = totinf + 1
                        pop[j]['state'] = di+de+1
                        # If verbose is True, show user feedback.
                        if verbose:
                            print("  Agent {} infected by agent {}.".format(j, i))

        # Update number of simulation rounds
        rounds = rounds + 1
    else:
        print("Pandemic persists: {} days, {} infecteds, attack rate is {:3.1f}%.".format(len(curve), totinf, (100*totinf)/N))

    # Return simulation curve.
    return(curve)
print(sim(N=100, I=1, m=5, vp=0, tp=(0.01, 0.02), de=3, di=5, rp=0.5, max=100, verbose=True))
