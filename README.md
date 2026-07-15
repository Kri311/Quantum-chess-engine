# Quantum Chess Engine
This project is made for learning quantum gates & circuits if implemented in chess engines.

before that we need to keep the below questions in mind:

- why do we use quantum computers in chess?
- how do you represent chess grids using qubits?
- how does Quantum computing knows if a chess move is legal or not?
- how does it know which pawn or piece is selected?
- how does it move a piece in the chess board?
- how does the board gets updated?
- understanding every Quantum circuits
- weakness of the base paper + ideas for novelty? seriously...
Let's just get to know what the base paper has implemented and why have they halted till 3x3 and just pawn pieces and if we understood what we are actually trying to do then we can implement more ideas to the system.

# Trial & Error
- Chess board consists of 8x8 grids with total of 64 boxes, where it consists of 2 Rook, 2 Knight, 2 Bishop, 1 Queen, 1 King, and 8 Pawns on both sides giving unbiased opportunities. Total of about 16 white/black pieces so about other 32 grids is your playground to capture the centre and defeat your opponent.

- The base paper has implemented 3x3 grids with pawn introduced in the grids, they have limited the no of grids and chess pieces in order to reduce the complexity of the quantum circuit. When the no of rows and columns increases the complexity and the chess piece placements increases exponentially creating about 1.8 billion possibilities of chess board pieces.

- So, first let's understand what the base paper is all about why did they stopped at 3x3 grids with pawn pieces alone. Then we'll come to a conclusion of the improvements we can make.

- And also need to get info bout' Game theory since it's used in here. 

# Tech Stack used:
- Python3
- numpy
- qiskit
- qiskit-aer
- python-chess
- matplotlib (in order to see the metrics of the complexity of the circuit)
- 
