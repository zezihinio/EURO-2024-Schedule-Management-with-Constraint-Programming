# EURO 2024 Schedule Management with Constraint Programming

## Introduction

As part of my Master's degree in Engineering, for the Artificial Intelligence course, I have made a project focused on constraint programming. The main objective of this project is to create a match schedule for EURO 2024 using Python.

## Project Objective

The objective is to manage the schedule of EURO 2024 for the 24 participating teams, adhering to a set of predefined constraints using OR-Tools, a constraint programming package.

## Constraints

### Groups and Teams

1. Each team is assigned to only one group.
2. Each group contains exactly one team from each pot (four pots in total).
3. Germany must be in Group A.

### Stadiums and Matches

4. No stadium can host more than one match per day.
5. The Olympiastadion will host the final (match 51).
6. The opening match must take place at Allianz Arena on Friday, June 14 at 9 PM, with Germany playing against another team from Group A.
7. Each team must play three matches during the group stage, facing each other team in their group exactly once.

### Tournament Phases

- **Group Stage:**
  - Groups A to F, from Friday, June 14 to Wednesday, June 26.
  - Matches are scheduled at 3 PM, 6 PM, and 9 PM.
  - The last match for each group will be played simultaneously at 6 PM and 9 PM.

- **Knockout Stage:**
  - **Round of 16:** From Saturday, June 29 to Tuesday, July 2, with two matches per day at 6 PM and 9 PM.
  - **Quarter-Finals:** From Friday, July 5 to Saturday, July 6, with two matches per day at 6 PM and 9 PM.
  - **Semi-Finals:** Tuesday, July 9 and Wednesday, July 10, with one match per day at 9 PM.
  - **Final:** Sunday, July 14 at 9 PM at Olympiastadion.
### Pots and Teams
#### Pot 1:
Germany, 
Portugal, 
France, 
Spain, 
Belgium, 
England. 

#### Pot 2:

Hungary, 
Turkey, 
Romania, 
Denmark, 
Albania, 
Austria

#### Pot 3:

Netherlands, 
Scotland, 
Croatia, 
Slovenia, 
Slovakia, 
Czech Republic.

#### Pot 4:

Italy, 
Serbia,
Switzerland, 
Poland, 
Ukraine, 
Georgia.

### Stadiums :
Olympiastadion, RheinEnergieStadion, Signal Iduna Park, Merkur Spiel Arena,Deutsche Bank Park, Volksparkstadion, Allianz Arena, MHPArena, Red Bull Arena, Veltins Arena.

## Implementation

### Prerequisites

- Python 3.x
- OR-Tools
- PyCharm (or any other IDE)

### Dependency Installation

Install OR-Tools using pip:

```bash
pip install ortools
```

### Project Structure

The project mainly consists of the following files:

- `UEFA_EURO2024.py`: Contains the implementation of the constraint programming logic to generate the match schedule.

### Execution

To run the project, execute the `UEFA_EURO2024.py` file:

```bash
python UEFA_EURO2024.py
```

The program will generate the groups and schedule the matches according to the defined constraints. The results will be displayed in the console.

## Conclusion

This project demonstrates the use of constraint programming to solve complex scheduling problems for sports events. With OR-Tools and Python, it is possible to create an optimized schedule for EURO 2024 while adhering to the predefined constraints.


