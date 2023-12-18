# Reinforcement Learning Implementation of Robot Tour

[Robot Tour](https://scioly.org/wiki/index.php/Robot_Tour) is a [Science Olympiad](https://www.soinc.org/) event in which student competitors aim to achieve the lowest score possible (as described later) by way of their pre-built autonomous robot navigating through a track, from a randomized starting point to a randomized ending point, that contains bonus zones and obstacles. This code takes the task virtual, recreating the environment and robot, then training a reinforcement learning (RL) model to determine the optimized path given starting and target points.

*Some Science Olympiad parameters/rules are not relevant to this code, and may have been omitted from the following descriptions.*

**Robot Parameters:**
Must completely fit in 30cm x 30cm square (no height limit)
A 1/4" to 3/8" dowel must be attached to the front of the robot

**Track Parameters:**
Track must be 2m x 2m, split into (16) 50cm x 50cm imaginary zones
Starting point to be placed on track perimeter, centered in a zone
Target point must be placed in the center of a zone
(8) random zone lines will be obstacles, with a penalty given for touching
Up to (3) zones will be "bonus zones," with a bonus given for entering

**Run Details:**
A random target time between 50 and 75 seconds is determined for each run
Obstacle touch penalties can only be given once per obstacle
Obstacles can be fully removed before a run for a penalty of 35 points
Bonus zones must be entered "dowel-first" to be awarded points
Bonus zones points can only be awarded once per bonus zone

**Scoring:**
Time Score + Distance Score + Gate Bonus + Penalties

Time Score:
If the run time is greater than the target time...
Time Score = (target time - run time) x 2
Otherwise...
Time Score = run time - target time
Hence, there is a larger penalty for "faster" times

Distance Score: +1 point for each cm between the robot dowel and the target point
Gate Bonus: -15 points for each bonus zone entered
Penalties: 
Penalty | Points
--- | ---
removing all obstacles | +35 
touching obstacle | +50 
stalling[^1] | +20 for stalling

[^1]: defined as being static for 3+ seconds
