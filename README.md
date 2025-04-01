# AI Crossword Generator

## Overview
This project is an AI-driven crossword puzzle generator that uses constraint satisfaction techniques to create valid crossword solutions based on a given puzzle structure and a word list.

## Features
- Generates crossword puzzles using constraint satisfaction algorithms.
- Ensures node consistency and arc consistency.
- Implements backtracking search for solution generation.
- Supports visualization of the crossword output.

## Usage
Run the script with the following command:
```sh
python generate.py data/structure1.txt data/words1.txt output.png
```
Where:
- `data/structure1.txt` defines the crossword structure.
- `data/words1.txt` contains the word list.
- `output.png` (optional) saves the generated crossword as an image.

## Example Output
```
██████████████
███████M████R█
█INTELLIGENCE█
█N█████N████S█
█F██LOGIC███O█
█E█████M████L█
█R███SEARCH█V█
███████X████E█
██████████████
```

## Implementation Details
The program follows a structured approach to solve the crossword puzzle:
1. **Node Consistency**: Ensures that words assigned to a variable match its length.
2. **Arc Consistency**: Implements the AC3 algorithm to remove invalid words from domains.
3. **Backtracking Search**: Finds a valid assignment of words to the puzzle variables.
4. **Heuristic Optimizations**:
   - Minimum Remaining Values (MRV)
   - Least-Constraining Value (LCV)
   - Degree Heuristic

## Dependencies
- Python 3
- Pillow (for image generation)

To install dependencies:
```sh
pip install pillow
```

## File Structure
- `crossword.py`: Defines the crossword structure and variables.
- `generate.py`: Implements constraint satisfaction and solving logic.
- `data/`: Contains example crossword structures and word lists.

## Results & Performance
The AI successfully generates crossword puzzles that satisfy all constraints, ensuring unique words and valid intersections. The backtracking search with heuristics significantly improves efficiency in finding solutions.

## Future Enhancements
- Improve runtime efficiency with more advanced constraint propagation.
- Extend support for larger crossword grids.
- Add interactive GUI for custom crossword creation.

## Credits
This project is part of an Harvard's CS80 AI coursework assignment exploring constraint satisfaction problems.

