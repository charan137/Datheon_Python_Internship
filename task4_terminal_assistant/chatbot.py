"""Run a rule-based terminal assistant using a JSON FAQ dataset."""

import argparse
import json
import re
from pathlib import Path

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "can", "do", "does",
    "for", "from", "how", "i", "in", "is", "it", "me", "my", "of",
    "on", "or", "the", "their", "them", "there", "this", "to", "was",
    "we", "what", "when", "where", "which", "who", "will", "with",
    "you", "your",
}

TOKEN_ALIASES = {
    "business": "hour",
    "certificate": "certificate",
    "certificates": "certificate",
    "closing": "hour",
    "close": "hour",
    "github": "project",
    "hour": "hour",
    "hours": "hour",
    "internships": "internship",
    "issued": "certificate",
    "issue": "certificate",
    "opening": "hour",
    "open": "hour",
    "projects": "project",
    "repo": "project",
    "repository": "project",
    "repositories": "project",
    "review": "certificate",
    "submission": "submit",
    "submissions": "submit",
    "submitted": "submit",
    "upload": "submit",
    "uploaded": "submit",
    "workspace": "project",
}

EXIT_PATTERN = re.compile(r"(?:bye|goodbye|exit|quit)(?:\s+please)?[.!?]*", re.I)
FOLLOW_UP_PATTERN = re.compile(r"\b(?:again|more|repeat|that|this|it)\b", re.I)
THANKS_PATTERN = re.compile(r"(?:thanks?|thank you|cheers)[.!?]*", re.I)


def meaningful_tokens(text):
    """Normalize text to a set of meaningful, canonical keyword tokens."""
    tokens = set()
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        token = TOKEN_ALIASES.get(token, token)
        if token not in STOP_WORDS and len(token) > 1:
            tokens.add(token)
    return tokens


def load_faq_data(path):
    """Load and validate greetings and FAQ entries from a JSON file."""
    with Path(path).expanduser().open(encoding="utf-8") as faq_file:
        data = json.load(faq_file)

    if not isinstance(data, dict):
        raise ValueError("FAQ data must be a JSON object.")
    greetings = data.get("greetings", [])
    faqs = data.get("faqs")
    if not isinstance(greetings, list) or not all(
        isinstance(greeting, str) and greeting.strip() for greeting in greetings
    ):
        raise ValueError("'greetings' must be a list of non-empty strings.")
    if not isinstance(faqs, list) or not faqs:
        raise ValueError("'faqs' must be a non-empty list.")

    validated_faqs = []
    for index, faq in enumerate(faqs, start=1):
        if not isinstance(faq, dict):
            raise ValueError(f"FAQ entry {index} must be an object.")
        question = faq.get("question")
        answer = faq.get("answer")
        keywords = faq.get("keywords", [])
        if not isinstance(question, str) or not question.strip():
            raise ValueError(f"FAQ entry {index} needs a non-empty question.")
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError(f"FAQ entry {index} needs a non-empty answer.")
        if not isinstance(keywords, list) or not all(
            isinstance(keyword, str) and keyword.strip() for keyword in keywords
        ):
            raise ValueError(f"FAQ entry {index} keywords must be a list of strings.")

        terms = meaningful_tokens(question)
        for keyword in keywords:
            terms.update(meaningful_tokens(keyword))
        validated_faqs.append(
            {"question": question.strip(), "answer": answer.strip(), "terms": terms}
        )

    return greetings, validated_faqs


class TerminalAssistant:
    """Match user messages to one or more FAQ answers."""

    def __init__(self, greetings, faqs):
        self.faqs = faqs
        self.greeting_patterns = [
            re.compile(r"\b" + re.escape(greeting.strip().lower()) + r"\b", re.I)
            for greeting in greetings
        ]
        self.last_answers = []
        self.fallback_count = 0

    def is_greeting(self, message):
        return any(pattern.search(message) for pattern in self.greeting_patterns)

    def matching_faqs(self, message):
        query_terms = meaningful_tokens(message)
        matches = []
        for faq in self.faqs:
            overlap = query_terms & faq["terms"]
            if not overlap:
                continue
            confidence = len(overlap) / len(faq["terms"])
            if confidence >= 0.30:
                matches.append((confidence, faq))
        matches.sort(key=lambda match: match[0], reverse=True)
        return [faq for _, faq in matches]

    def suggestions(self):
        return "\n".join(f"- {faq['question']}" for faq in self.faqs)

    def respond(self, message):
        """Return a response and whether the conversation should end."""
        message = message.strip()
        if EXIT_PATTERN.fullmatch(message):
            return "Goodbye! Thanks for reaching out.", True
        if not message:
            return "Type a question, or enter 'help' to see example questions.", False

        if re.fullmatch(r"help[.!?]*", message, re.I):
            return f"I can help with questions like:\n{self.suggestions()}", False

        if THANKS_PATTERN.fullmatch(message):
            return "You're welcome! Ask another question whenever you're ready.", False

        matches = self.matching_faqs(message)
        if matches:
            self.last_answers = matches
            self.fallback_count = 0
            answers = "\n\n".join(
                f"{faq['question']}\n{faq['answer']}" for faq in matches
            )
            if self.is_greeting(message):
                return f"Hello! Here's what I found:\n\n{answers}", False
            return answers, False

        if FOLLOW_UP_PATTERN.search(message) and self.last_answers:
            repeated = "\n\n".join(
                f"{faq['question']}\n{faq['answer']}" for faq in self.last_answers
            )
            return f"Here's the information from your last question:\n\n{repeated}", False

        self.fallback_count += 1
        if self.is_greeting(message):
            return (
                "Hello! I can help with these topics. You can ask about more than one at a time:\n"
                f"{self.suggestions()}",
                False,
            )

        retry_tip = " Try asking about one of these topics." if self.fallback_count > 1 else ""
        return (
            "I couldn't confidently match that question. You can rephrase it or ask:\n"
            f"{self.suggestions()}{retry_tip}",
            False,
        )

    def run(self):
        print("Assistant: Hello! Ask me a question, or type 'help' for examples.")
        print("Type 'bye', 'exit', or 'quit' to end the conversation.")
        while True:
            try:
                message = input("\nYou: ")
            except EOFError:
                print("\nAssistant: Goodbye!")
                break

            response, should_exit = self.respond(message)
            print(f"\nAssistant: {response}")
            if should_exit:
                break


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--faq",
        default=str(Path(__file__).with_name("sample_faq.json")),
        help="FAQ JSON file to load (default: sample_faq.json beside this script)",
    )
    args = parser.parse_args()

    try:
        greetings, faqs = load_faq_data(args.faq)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        parser.error(str(error))

    try:
        TerminalAssistant(greetings, faqs).run()
    except KeyboardInterrupt:
        print("\nAssistant: Goodbye!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())