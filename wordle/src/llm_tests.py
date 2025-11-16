import time
<<<<<<< Updated upstream
import json

from pathlib import Path
=======
from datetime import datetime
>>>>>>> Stashed changes

import wandb

from classes.GameState import GameState, Status
from classes.LetterCell import Feedback
from constants import LLM_MODEL, MAX_LLM_CONTINUOUS_CALLS

<<<<<<< Updated upstream
LOG_DIR = Path("benchmarks/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"llm_wordle_results.json"

NUM_RUNS = 5
=======
NUM_RUNS = 100
SCENARIOS = [
    (0, "Wordle (0 lies)"),
    (1, "Fibble (1 lie)"),
    (2, "Fibble (2 lies)"),
    (3, "Fibble (3 lies)"),
    (4, "Fibble (4 lies)"),
    (5, "Fibble (5 lies)"),
]
>>>>>>> Stashed changes


# Modify run_game to append per-game stats
def run_game(game: GameState, run_id: int, total_tries: int, total_success: int, total_bad_guesses: int, total_latency: float, results_dict=None):
    print(f"Starting run {run_id + 1}")
    game.reset()
    total_completion = 0
    completion = 0
    game_start_time = time.time()


    while game.status != Status.end:
        game.enter_word_from_ai()

        # get the feedback
        offset = 0 if game.status == Status.end else 1
        feedback = game.words[game.current_word_index - offset].get_feedback()

        # check completion
        completion = 0
        for fdb in feedback:
            match fdb:
                case Feedback.incorrect:
                    completion += 0
                case Feedback.present:
                    completion += 0.5
                case Feedback.correct:
                    completion += 1

        if game.was_valid_guess:
            total_completion += completion
        else:
            total_bad_guesses += 1

    game_end_time = time.time()
    game_latency = game_end_time - game_start_time
    total_latency += game_latency

    avg_game_completion = total_completion / game.num_of_tries()
    total_success += 1 if game.success else 0
    total_tries += game.num_of_tries()
    num_tries = game.num_of_tries()


    print(f"Average game completion: {avg_game_completion} / 5")
    print(f"Average tries: {total_tries / (run_id + 1)}")
    print(f"Average success: {total_success / (run_id + 1)}")
    print(f"Average latency: {total_latency / (run_id + 1):.2f}s")
    print(f"Total bad guesses: {total_bad_guesses}")
    print()
    wandb.log(
        {
            "average_game_completion": avg_game_completion,
            "rolling_avg_tries": total_tries / (run_id + 1),
            "rolling_avg_success": total_success / (run_id + 1),
            "rolling_avg_latency": total_latency / (run_id + 1),
            "total_bad_guesses": total_bad_guesses
        },
        step=(run_id + 1)
    )
   
    if results_dict is not None:
        results_dict["games"].append({
            "run_id": run_id + 1,
            "average_game_completion": avg_game_completion,
            "tries": game.num_of_tries(),
            "success": game.success,
            "latency": game_latency,
            "bad_guesses": total_bad_guesses
        })

    return total_tries, total_success, total_bad_guesses, total_latency

<<<<<<< Updated upstream
=======
    return total_tries, total_success, num_tries, game.success
>>>>>>> Stashed changes


def test_games():
    game = GameState(show_window=False, logging=False)
<<<<<<< Updated upstream
    total_success = 0
    total_tries = 0
    total_bad_guesses = 0
    total_latency = 0.0

    results = {
        "num_runs": NUM_RUNS,
        "LLM_MODEL": LLM_MODEL,
        "MAX_LLM_CONTINUOUS_CALLS": MAX_LLM_CONTINUOUS_CALLS,
        "games": []
    }

    for i in range(NUM_RUNS):
        total_tries, total_success, total_bad_guesses, total_latency = run_game(game, i, total_tries, total_success, total_bad_guesses, total_latency, results)
        if i < NUM_RUNS - 1:
            time.sleep(1)

    # Calculate final averages
    win_rate = total_success / NUM_RUNS
    avg_tries = total_tries / NUM_RUNS
    avg_latency = total_latency / NUM_RUNS

    # Save the results
    results["total_bad_guesses"] = total_bad_guesses
    results["win_rate"] = win_rate
    results["avg_tries"] = avg_tries
    results["avg_latency"] = avg_latency
   
    with open(LOG_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*50}")
    print(f"FINAL RESULTS:")
    print(f"{'='*50}")
    print(f"Win Rate: {win_rate:.2%} ({total_success}/{NUM_RUNS})")
    print(f"Average Tries: {avg_tries:.2f}")
    print(f"Average Latency: {avg_latency:.2f}s")
    print(f"Total Bad Guesses: {total_bad_guesses}")
    print(f"{'='*50}")
    print(f"\nSaved benchmark results to {LOG_FILE}")
=======
    game.set_llm_platform("ollama")
    
    results = []
    
    for num_lies, scenario_name in SCENARIOS:
        print(f"\n{'='*60}")
        print(f"Testing {scenario_name}")
        print(f"{'='*60}\n")
        
        game.num_lies = num_lies
        # Give Fibble more guesses since it's harder with lies
        game.num_guesses = 9 if num_lies > 0 else 6
        total_success = 0
        total_tries = 0
        successful_tries = []
        
        for i in range(NUM_RUNS):
            total_tries, total_success, num_tries, was_successful = run_game(
                game, i, total_tries, total_success)
            
            if was_successful:
                successful_tries.append(num_tries)
        
        # Calculate statistics
        win_rate = (total_success / NUM_RUNS) * 100
        avg_tries_all = total_tries / NUM_RUNS
        avg_tries_successful = sum(successful_tries) / len(successful_tries) if successful_tries else 0
        
        results.append({
            "scenario": scenario_name,
            "num_lies": num_lies,
            "games": NUM_RUNS,
            "wins": total_success,
            "win_rate": win_rate,
            "avg_tries_all": avg_tries_all,
            "avg_tries_successful": avg_tries_successful
        })
        
        print(f"\n{scenario_name} Results:")
        print(f"  Wins: {total_success}/{NUM_RUNS} ({win_rate:.1f}%)")
        print(f"  Avg tries (all games): {avg_tries_all:.2f}")
        print(f"  Avg tries (successful): {avg_tries_successful:.2f}")
        print()
    
    # Generate markdown report
    report_lines = [
        "# LLM Wordle/Fibble Test Results",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Model: {LLM_MODEL}",
        f"Games per scenario: {NUM_RUNS}",
        "",
        "## Results by Scenario",
        "",
        "| Scenario | Lies | Games | Wins | Win Rate | Avg Tries (All) | Avg Tries (Successful) |",
        "|----------|------|-------|------|----------|-----------------|------------------------|"
    ]
    
    for result in results:
        report_lines.append(
            f"| {result['scenario']} | {result['num_lies']} | {result['games']} | "
            f"{result['wins']} | {result['win_rate']:.1f}% | {result['avg_tries_all']:.2f} | "
            f"{result['avg_tries_successful']:.2f} |"
        )
    
    report_content = "\n".join(report_lines)
    
    # Write report to file
    report_filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_filename, 'w') as f:
        f.write(report_content)
    
    print(f"\n{'='*60}")
    print("Report saved to:", report_filename)
    print(f"{'='*60}\n")
    print(report_content)
>>>>>>> Stashed changes


if __name__ == "__main__":
    wandb.init(
        project="llm-wordle",
        name=f"{LLM_MODEL}-{MAX_LLM_CONTINUOUS_CALLS}-retries"
    )
    test_games()
