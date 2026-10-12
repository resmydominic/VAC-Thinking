"""Scaffolds: step-by-step guides, sentence starters and improvement plans.

Everything here is plain data so teachers can edit wording easily.
"""

# The seven stages of the Critical Thinking Engine
STAGES = {
    "observe": {
        "title": "1 · Observe",
        "prompt": "What do you notice? List the facts only — no judgements yet.",
        "hint": "Write what anyone could check: who, what, when, where, how many. Avoid words like 'unfair', 'wrong', 'lazy' at this stage.",
        "starters": ["The facts are…", "I notice that…", "According to the situation, …"],
    },
    "question": {
        "title": "2 · Question",
        "prompt": "What information is missing? What would you want to know before judging?",
        "hint": "Ask questions that start with Why, Who, How many, What if. Think about whose voice is not heard.",
        "starters": ["We don't know whether…", "I would want to find out…", "It is not clear why…", "Whose view is missing?…"],
    },
    "analyse": {
        "title": "3 · Analyse",
        "prompt": "Separate facts, opinions, assumptions and inferences in the situation.",
        "hint": "Pick one statement from the scenario and label it: Is it a fact (checkable), an opinion (judgement), or an assumption (taken for granted)?",
        "starters": ["One fact is…, but one assumption is…", "The statement '…' is an opinion because…", "Someone is assuming that…"],
    },
    "perspectives": {
        "title": "4 · Perspectives",
        "prompt": "Describe at least two different perspectives: the person affected, the institution, the community, or someone with different priorities.",
        "hint": "For each person, ask: What do they want? What are they afraid of? What do they know that others don't?",
        "starters": ["From …'s point of view, …", "On the other hand, … might feel…", "The institution may be worried about…"],
    },
    "decide": {
        "title": "5 · Decide",
        "prompt": "What is your answer to the main question? Give your reasons.",
        "hint": "Use the pattern: Claim → Reason → Evidence/Example → So what. One clear decision is better than several vague ones.",
        "starters": ["I think … because…", "The best option is … since…", "Therefore, …", "For example, …"],
    },
    "challenge": {
        "title": "6 · Challenge your own answer",
        "prompt": "What is the strongest argument AGAINST your position? Answer it honestly.",
        "hint": "Imagine the smartest person who disagrees with you. What would they say? Do not choose a weak objection.",
        "starters": ["Someone might argue that…", "The strongest objection is…", "However, my position still holds because… / This makes me reconsider…"],
    },
    "reflect": {
        "title": "7 · Reflect",
        "prompt": "What new information could change your conclusion?",
        "hint": "Name a specific fact or piece of evidence. 'If I learned that…, I would change my view to…'",
        "starters": ["If I learned that…, I would…", "My view would change if…", "I am less sure about…"],
    },
}

STAGES_BY_LEVEL = {
    1: ["observe", "question", "decide", "challenge"],
    2: ["observe", "question", "analyse", "perspectives", "decide", "challenge"],
    3: ["observe", "question", "analyse", "perspectives", "decide", "challenge", "reflect"],
}

# Skill improvement plans (HOTS)
SKILL_PLANS = {
    "evidence": {
        "what": "Checking whether claims are supported, and using reasons and examples in your own answers.",
        "steps": [
            "After every claim you write, add 'because…' and one specific reason.",
            "Ask of any information: Who says this? How do they know? Can it be checked?",
            "Add one example from the scenario to support your point (a number, an event, a quotation).",
            "Prefer specific evidence ('70% of scholarships…') over general statements ('many people…').",
        ],
        "starters": ["This is supported by…", "For example, in the scenario…", "The evidence for this is…", "This claim needs evidence because…"],
    },
    "logic": {
        "what": "Connecting ideas so that your conclusion follows from your reasons.",
        "steps": [
            "Write your conclusion first in one sentence. Then check: does each reason actually support it?",
            "Use linking words that show logic: because, therefore, so, as a result, which means.",
            "Watch for common errors: 'everyone does it', 'either… or…' with no other options, and one example treated as proof.",
            "Read your answer backwards: start at the conclusion and ask 'why?' — your answer should already contain the reason.",
        ],
        "starters": ["Because …, it follows that…", "This means that…", "As a result, …", "If … then …"],
    },
    "assumptions": {
        "what": "Spotting what is taken for granted and what information is missing.",
        "steps": [
            "Underline judgement words (lazy, unfair, best, always, never) — each one hides an assumption.",
            "For each judgement, ask: 'What would have to be true for this to be correct?'",
            "Write two questions you would need answered before deciding.",
            "Generate at least three possible explanations before choosing one.",
        ],
        "starters": ["This assumes that…", "We don't actually know whether…", "Another explanation could be…", "Before deciding, I would need to know…"],
    },
    "perspectives": {
        "what": "Understanding how different people see the same situation.",
        "steps": [
            "List every person or group affected — including those who are not present.",
            "For two of them, write: what they want, what they fear, and what they might know.",
            "Describe the view you disagree with in a way its supporters would accept.",
            "Look for a shared interest that both sides have.",
        ],
        "starters": ["From …'s point of view, …", "… might feel … because …", "On the other hand, …", "Both groups want…"],
    },
    "ethics": {
        "what": "Reasoning about fairness, rights, duties, harm and consequences.",
        "steps": [
            "Name the values in conflict (e.g. honesty vs loyalty, freedom vs safety).",
            "Ask two questions: What are the consequences? What duty or right is involved?",
            "Consider who carries the cost of each option.",
            "Test your choice: would it be fair if you were the person most affected?",
        ],
        "starters": ["The values in conflict are…", "This would be unfair to … because…", "Each person has a right to…", "The consequence of this would be…"],
    },
    "problem": {
        "what": "Identifying the real problem and proposing practical solutions.",
        "steps": [
            "State the central problem in one sentence before anything else.",
            "Separate the main problem from side issues.",
            "List at least three options, not just two.",
            "For your chosen solution, say who would do what, and what could go wrong.",
        ],
        "starters": ["The central problem is…", "One option is…, another is…", "A practical solution would be…", "This could fail if…"],
    },
    "counterargument": {
        "what": "Finding and answering the strongest argument against your view.",
        "steps": [
            "After deciding, imagine a smart person who disagrees. Write their best argument.",
            "Avoid weak or silly objections — choose the one that worries you most.",
            "Respond: does the objection change your view, limit it, or can you answer it?",
            "Use words like 'however', 'although', 'admittedly'.",
        ],
        "starters": ["Someone might argue that…", "Admittedly, …", "Although…, I still believe… because…", "This objection shows that my view needs…"],
    },
    "reflection": {
        "what": "Being willing to revise your view when good evidence appears.",
        "steps": [
            "End every answer with: 'My view would change if…' and name a specific fact.",
            "Compare your first reaction with your final answer — what moved you?",
            "Say how certain you are (very sure / fairly sure / unsure) and why.",
            "Use the Revise button: improve one part of your answer using the feedback.",
        ],
        "starters": ["My view would change if…", "At first I thought…, but now…", "I am fairly sure, but…", "I am less certain about…"],
    },
}

# Language improvement plans
LANGUAGE_PLANS = {
    "vocabulary": {
        "tip": "Replace general words with precise ones. Instead of 'good/bad', try 'fair/unjust', 'reliable/misleading', 'beneficial/harmful'.",
        "steps": ["Circle words you repeat; find a more exact word for one of them.", "Learn 2 new reasoning words each week: e.g. 'assumption', 'evidence', 'consequence', 'perspective', 'trade-off'."],
        "bank": ["assumption", "evidence", "consequence", "perspective", "trade-off", "stakeholder", "unintended", "proportionate", "credible", "bias"],
    },
    "sentences": {
        "tip": "Write complete sentences that start with a capital letter and end with a full stop. Mix short and medium sentences (10–20 words).",
        "steps": ["Split very long sentences at 'and' or 'but'.", "Join very short ones with 'because', 'although' or 'which'.", "Read your answer aloud — where you pause, put a full stop or comma."],
        "bank": ["I believe that … because …", "Although …, …", "This is important because …"],
    },
    "cohesion": {
        "tip": "Link your ideas with connectives so the reader can follow your thinking.",
        "steps": ["Use at least one of each: a reason word (because), a contrast word (however), a result word (therefore).", "Start your second point with 'Furthermore' or 'In addition'."],
        "bank": ["because", "therefore", "however", "although", "as a result", "for example", "on the other hand", "in addition", "this means that", "in conclusion"],
    },
    "elaboration": {
        "tip": "Don't stop at the claim. Explain why, give an example, and say what follows.",
        "steps": ["Use the PEEL pattern: Point → Evidence → Explain → Link.", "For each point, ask yourself 'So what?' and write the answer."],
        "bank": ["This shows that…", "For instance, …", "This matters because…", "As a result, …"],
    },
    "tone": {
        "tip": "Avoid absolute words (always, never, everyone, obviously) unless you are sure. Use careful words: may, might, often, likely, some.",
        "steps": ["Replace 'always' with 'often' and 'everyone' with 'many people' where needed.", "Avoid text-message spelling (bcz, u, dont) in academic answers.", "Disagree with ideas, not with people."],
        "bank": ["may", "might", "it is likely that", "in some cases", "it seems that", "one possible reason is"],
    },
}

ENCOURAGEMENT = {
    "high": [
        "Excellent reasoning! You are thinking like a careful judge — weighing, not just reacting.",
        "Impressive work. Your answer shows depth and balance. Keep challenging yourself with harder levels.",
        "Superb! You considered more than one side and explained your thinking clearly.",
        "Outstanding. This is exactly what strong critical thinking looks like.",
    ],
    "good": [
        "Good thinking! You have a solid base — a little more depth will make it excellent.",
        "Well done. Your reasoning is on the right track. Look at the 'deeper thought' tips to level up.",
        "Nice work. You are building real thinking habits. One more step and you'll be there.",
        "Good effort! You're clearly engaging with the problem, not just guessing.",
    ],
    "growing": [
        "A good start! Every strong thinker began exactly here. Use the steps below and try again.",
        "You've taken the first step — now let's build on it. The scaffold below will guide you.",
        "Keep going! Thinking skills grow with practice, just like a muscle.",
        "Nice try. Look at one suggestion below, revise your answer, and see how much it improves.",
    ],
    "start": [
        "Let's begin together. Try writing just two or three sentences using the sentence starters below.",
        "Every answer is a chance to practise. Use the hints — they're there to help, not to test you.",
        "Don't worry about being 'right'. Focus on explaining what you think and why.",
    ],
}

CLOSING_REMINDER = "A strong thinker is not someone who always has the right answer, but someone who knows how to question, reason, and reconsider."
