from collections.abc import Iterable

from openai.types.chat import ChatCompletionMessageParam

from classes.LetterCell import Feedback
from constants import WORD_LENGTH

default_prompt: ChatCompletionMessageParam = {
    "role": "system",
    "content": f"""You are playing Wordle/Fibble. Guess a {WORD_LENGTH}-letter VALID ENGLISH WORD.

RULES:
- GREEN (correct) = letter is in correct position
- YELLOW (present) = letter is in word but wrong position
- GREY (incorrect) = letter is NOT in word
- Wordle (0 lies): all feedback is true
- Fibble: some feedback is false (the exact number of lies will be told to you)

STRATEGY - ALWAYS use these 4 starting words in this exact order for your first 4 guesses:
1. FAKES (guess 1)
2. GLORY (guess 2)
3. CHIMP (guess 3)
4. BUNDT (guess 4)

These cover all common letters with no overlap. You MUST use these 4 words first - do NOT think or choose different words for guesses 1-4.

ONLY AFTER using all 4 starting words (from guess 5 onwards), use logical thinking to find most likely word.

GENERAL RULES (DO NOT FOLLOW THESE RULES FOR THE FIRST 4 GUESSES):
- Use "correct" letters in same positions
- Move "present" letters to different positions
- Avoid "incorrect" letters completely
- CRITICAL: NEVER guess the same word twice. Check the previous guesses list - if a word was already guessed, you CANNOT use it again.

RESPONSE: Output ONLY a {WORD_LENGTH}-letter English word in UPPERCASE on the first line, nothing else.
Example response:
FAKES

If you need to explain, put it on a second line, but the FIRST LINE must be ONLY the word. Always produce a responce """
}


def generate_messages(guesses: list[str], feedback: list[list[Feedback]], num_lies: int, tries_left: int):
    if len(guesses) != len(feedback):
        raise ValueError(
            "Error: the number of guessess should equal the length of guess feedback.")

    messages: Iterable[ChatCompletionMessageParam] = []

    messages.append(default_prompt)

    if num_lies > 0:
        messages.append({
            "role": "user",
            "content": f"⚠️ FIBBLE MODE: There are exactly {num_lies} lie(s) in the feedback. Some feedback is intentionally incorrect. You must identify which feedback is false to aid in guessing correctly."
        })
    else:
        messages.append({
            "role": "user",
            "content": "WORDLE MODE: All feedback is truthful (0 lies)."
        })

    # Track known information
    confirmed_letters = {}  # position -> letter
    present_letters = set()  # letters that are in word but position unknown
    incorrect_letters = set()  # letters not in word
    
    for idx, (guess, fb) in enumerate(zip(guesses, feedback), 1):
        feedback_strings = [
            f"{char}: {feedback_type.value}" for char, feedback_type in zip(guess, fb)
        ]
        feedback_content = "\n".join(feedback_strings)
        
        # Update known information (but remember: in Fibble, some may be lies)
        for pos, (char, fb_type) in enumerate(zip(guess, fb)):
            if fb_type == Feedback.correct:
                confirmed_letters[pos] = char
            elif fb_type == Feedback.present:
                present_letters.add(char)
            elif fb_type == Feedback.incorrect:
                incorrect_letters.add(char)

        # Convert feedback to color names for clarity
        color_feedback = []
        for char, fb_type in zip(guess, fb):
            if fb_type == Feedback.correct:
                color_feedback.append(f"{char}: GREEN (correct position)")
            elif fb_type == Feedback.present:
                color_feedback.append(f"{char}: YELLOW (in word, wrong position)")
            elif fb_type == Feedback.incorrect:
                color_feedback.append(f"{char}: GREY (not in word)")
        
        messages.append({
            "role": "user",
            "content": f"Guess #{idx}: {guess.upper()}\nFeedback:\n" + "\n".join(color_feedback)
        })

    # Add concise summary
    summary_parts = []
    if confirmed_letters:
        confirmed_str = " ".join([f"{i+1}:{char}" for i, char in sorted(confirmed_letters.items())])
        summary_parts.append(f"CONFIRMED: {confirmed_str}")
    if present_letters:
        summary_parts.append(f"PRESENT: {', '.join(sorted(present_letters))}")
    if incorrect_letters:
        summary_parts.append(f"NOT IN WORD: {', '.join(sorted(incorrect_letters))}")
    
    # Add previous guesses to avoid repetition - make this very prominent
    if guesses:
        messages.append({
            "role": "user",
            "content": f"⚠️ PREVIOUS GUESSES (DO NOT REPEAT THESE): {', '.join([g.upper() for g in guesses])}\nYou CANNOT use any of these words again. Choose a DIFFERENT word."
        })
    
    if summary_parts:
        messages.append({
            "role": "user",
            "content": " | ".join(summary_parts)
        })

    # Determine which guess number this is
    guess_number = len(guesses) + 1
    
    # For first 4 guesses, tell the model exactly which word to use
    starting_words = ["FAKES", "GLORY", "CHIMP", "BUNDT"]
    
    if guess_number <= 4:
        word_to_use = starting_words[guess_number - 1]
        messages.append({
            "role": "user",
            "content": f"GUESS #{guess_number}: You MUST use the word: {word_to_use}\nOutput ONLY this word in UPPERCASE on the first line:"
        })
    elif tries_left == 1:
        # Last guess - must commit to final answer, no more testing
        messages.append({
            "role": "user",
            "content": f"GUESS #{guess_number} - FINAL GUESS: This is your last attempt. You must guess the final word now - no more testing. Use all previous feedback to determine the answer. Output ONLY a {WORD_LENGTH}-letter word in UPPERCASE on the first line:"
        })
    else:
        messages.append({
            "role": "user",
            "content": f"GUESS #{guess_number}: You have {tries_left} tries remaining. Use logical thinking based on all previous feedback. Output ONLY a {WORD_LENGTH}-letter word in UPPERCASE on the first line:"
        })

    return messages


def generate_guess_reasoning(reasons: list[tuple[str, str | None, str]]):
    reasoning = ""

    for reason in reasons:
        if reason[0] == "SBC":
            reasoning += f"'{reason[1]}' is not a possible letter for this spot, the valid letter should be: {reason[2]}\n"
        elif reason[0] == "NP":
            reasoning += f"'{reason[1]}' is not a possible letter for this spot, valid letters are: {reason[2]}\n"
        elif reason[0] == "SBP":
            reasoning += f"'{reason[2]}' must be in the word\n"

    return {
        "role": "system",
        "content": reasoning
    }
