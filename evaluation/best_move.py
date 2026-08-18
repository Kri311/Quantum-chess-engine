import os
import sys
import random
import matplotlib.pyplot as plt
import numpy as np

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.board import Board
from engine.constants import Color, PieceType
from engine.piece import Piece
from engine.position import Position
from engine.state import GameState
from engine.move_generator import MoveGenerator
from ai.heuristic import HeuristicEvaluator
from ai.minimax import MinimaxEngine
from ai.quantum_search import QuantumMoveSearcher
import config

def generate_test_positions(num_positions=20):
    """Generate unique 3x3 game states using a random walk."""
    config.BOARD_SIZE = 3
    states = []
    seen = set()
    
    max_attempts = 1000
    attempts = 0
    while len(states) < num_positions and attempts < max_attempts:
        board = Board(size=3)
        w_col = random.choice([0, 1, 2])
        b_col = random.choice([0, 1, 2])
        board.place_piece(Position(2, w_col), Piece(Color.WHITE, PieceType.PAWN))
        board.place_piece(Position(0, b_col), Piece(Color.BLACK, PieceType.PAWN))
        state = GameState(board=board, current_turn=Color.WHITE)
        
        while len(states) < num_positions:
            attempts += 1
            legal_moves = MoveGenerator.generate_legal_moves(state)
            if not legal_moves:
                break
                
            state_str = str(state)
            if len(legal_moves) >= 1 and state_str not in seen:
                states.append(state)
                seen.add(state_str)
                
            move = random.choice(legal_moves)
            state = state.apply_move(move)
            
    return states

def evaluate_quality():
    print("Generating test positions...")
    states = generate_test_positions(20)
    print(f"Generated {len(states)} unique positions.")
    
    classical_engine = MinimaxEngine(max_depth=3)
    quantum_searcher = QuantumMoveSearcher()
    
    trials_per_state = 10
    
    classical_hits = 0
    hybrid_hits = 0
    pure_hits = 0
    
    classical_scores = []
    hybrid_scores = []
    pure_scores = []
    best_possible_scores = []
    
    total_trials = len(states) * trials_per_state
    
    print(f"Evaluating {len(states)} states with {trials_per_state} trials each...")
    
    for state_idx, state in enumerate(states):
        legal_moves = MoveGenerator.generate_legal_moves(state)
        
        # Score every legal move
        scored_moves = []
        for m in legal_moves:
            score = HeuristicEvaluator.score_move(state, m)
            scored_moves.append((score, m))
            
        best_score = max(score for score, m in scored_moves)
        optimal_moves = [m for score, m in scored_moves if score == best_score]
        
        for trial in range(trials_per_state):
            # Classical Engine (Minimax)
            c_move = classical_engine.search(state)
            if c_move in optimal_moves:
                classical_hits += 1
            if c_move:
                c_score = HeuristicEvaluator.score_move(state, c_move)
                classical_scores.append(c_score)
            else:
                classical_scores.append(0)
                
            # Hybrid Engine (Quantum Grover Search)
            q_move = quantum_searcher.search(state)
            if q_move in optimal_moves:
                hybrid_hits += 1
            if q_move:
                q_score = HeuristicEvaluator.score_move(state, q_move)
                hybrid_scores.append(q_score)
            else:
                hybrid_scores.append(0)
                
            # Pure Quantum Engine (Random legal move from legality oracle)
            p_move = random.choice(legal_moves) if legal_moves else None
            if p_move in optimal_moves:
                pure_hits += 1
            if p_move:
                p_score = HeuristicEvaluator.score_move(state, p_move)
                pure_scores.append(p_score)
            else:
                pure_scores.append(0)
                
            best_possible_scores.append(best_score)
            
        print(f"Completed state {state_idx+1}/{len(states)}")
        
    c_hit_rate = (classical_hits / total_trials) * 100
    q_hit_rate = (hybrid_hits / total_trials) * 100
    p_hit_rate = (pure_hits / total_trials) * 100
    
    c_avg_quality = np.mean([c / b if b != 0 else 1.0 for c, b in zip(classical_scores, best_possible_scores)])
    q_avg_quality = np.mean([q / b if b != 0 else 1.0 for q, b in zip(hybrid_scores, best_possible_scores)])
    p_avg_quality = np.mean([p / b if b != 0 else 1.0 for p, b in zip(pure_scores, best_possible_scores)])
    
    print("="*50)
    print("BEST-MOVE SELECTION / QUALITY RESULTS")
    print("="*50)
    print(f"Classical Engine Hit Rate: {c_hit_rate:.2f}%")
    print(f"Hybrid Quantum Hit Rate:   {q_hit_rate:.2f}%")
    print(f"Pure Quantum Hit Rate:     {p_hit_rate:.2f}%")
    print(f"Classical Avg Quality:     {c_avg_quality*100:.2f}%")
    print(f"Hybrid Quantum Avg Quality:{q_avg_quality*100:.2f}%")
    print(f"Pure Quantum Avg Quality:  {p_avg_quality*100:.2f}%")
    print("="*50)
    
    # Plotting
    labels = ['Classical', 'Hybrid Quantum', 'Pure Quantum']
    hit_rates = [c_hit_rate, q_hit_rate, p_hit_rate]
    qualities = [c_avg_quality * 100, q_avg_quality * 100, p_avg_quality * 100]
    
    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 6))
    rects1 = ax.bar(x - width/2, hit_rates, width, label='Best-Move Hit Rate (%)')
    rects2 = ax.bar(x + width/2, qualities, width, label='Average Quality (%)')

    ax.set_ylabel('Percentage (%)')
    ax.set_title('Move Selection Quality: Classical vs Hybrid Quantum (3x3)')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 110)
    ax.legend()
    
    for rects in [rects1, rects2]:
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    plot_path = os.path.join(os.path.dirname(__file__), 'evaluation_plot.png')
    plt.tight_layout()
    plt.savefig(plot_path)
    print(f"Plot saved to {plot_path}")

if __name__ == "__main__":
    evaluate_quality()
