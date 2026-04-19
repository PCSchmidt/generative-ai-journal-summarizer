"""Golden test set: 20 journal entries + 5 queries for RAG evaluation.

The entries simulate a realistic journaling history over ~3 weeks.
Queries are chosen to test whether RAG retrieves thematically relevant entries.
"""

# --- Corpus: 20 journal entries in chronological order ---

JOURNAL_ENTRIES = [
    {
        "text": "Started the new project at work today. The requirements are vague and the deadline is tight. Feeling a mix of excitement and anxiety about whether I can deliver.",
        "date": "2025-06-01",
        "themes": ["work", "anxiety", "new-project"],
    },
    {
        "text": "Went for a long run in the park after work. The weather was perfect and I felt all the tension drain away. Running is my therapy.",
        "date": "2025-06-02",
        "themes": ["exercise", "stress-relief", "positive"],
    },
    {
        "text": "Had a tough meeting with the client. They changed the scope again and my manager didn't push back. I'm frustrated and feel unsupported.",
        "date": "2025-06-03",
        "themes": ["work", "frustration", "conflict"],
    },
    {
        "text": "Cooked a new recipe tonight — Thai green curry from scratch. It turned out amazing and my partner loved it. Small wins matter.",
        "date": "2025-06-04",
        "themes": ["cooking", "positive", "relationship"],
    },
    {
        "text": "Couldn't sleep last night. My mind kept racing about the project timeline. I need to find better ways to disconnect from work.",
        "date": "2025-06-05",
        "themes": ["insomnia", "anxiety", "work-life-balance"],
    },
    {
        "text": "Great progress on the ML pipeline today. Got the data preprocessing working and the initial model shows promising accuracy. Feeling competent again.",
        "date": "2025-06-06",
        "themes": ["work", "achievement", "ML", "positive"],
    },
    {
        "text": "Spent the morning journaling and meditating. I realize I've been ignoring how stressed I've been. Writing it down helps me see patterns.",
        "date": "2025-06-07",
        "themes": ["self-reflection", "mindfulness", "stress"],
    },
    {
        "text": "My best friend called today after weeks of silence. We talked for two hours. I didn't realize how much I missed that connection.",
        "date": "2025-06-08",
        "themes": ["friendship", "connection", "positive"],
    },
    {
        "text": "Team standup was demoralizing. Everyone is behind schedule and the energy is low. I tried to be encouraging but I'm running on empty myself.",
        "date": "2025-06-09",
        "themes": ["work", "team", "burnout", "negative"],
    },
    {
        "text": "Took a mental health day. Stayed home, read a book, walked the dog. No screens, no Slack. I feel guilty but also genuinely better.",
        "date": "2025-06-10",
        "themes": ["rest", "mental-health", "guilt", "recovery"],
    },
    {
        "text": "The model evaluation results came back and accuracy is 94%. My manager actually acknowledged my work in the all-hands. Validation feels good.",
        "date": "2025-06-11",
        "themes": ["work", "achievement", "ML", "recognition"],
    },
    {
        "text": "Had an argument with my partner about how much time I spend working. They're right — I've been absent even when I'm physically here.",
        "date": "2025-06-12",
        "themes": ["relationship", "conflict", "work-life-balance"],
    },
    {
        "text": "Ran my first 10K without stopping. Six months ago I couldn't do 2K. Proof that consistency beats intensity every time.",
        "date": "2025-06-13",
        "themes": ["exercise", "achievement", "positive", "growth"],
    },
    {
        "text": "Project demo went well. The client loved the ML features and the scope creep conversation went smoothly. Maybe things are turning around.",
        "date": "2025-06-14",
        "themes": ["work", "positive", "client", "ML"],
    },
    {
        "text": "Woke up feeling flat for no reason. Everything is objectively fine but I just feel empty. I know it will pass but it's hard in the moment.",
        "date": "2025-06-15",
        "themes": ["low-mood", "emotional", "negative"],
    },
    {
        "text": "Started reading 'Atomic Habits'. The idea that identity drives behavior really clicked. I want to be someone who takes care of themselves.",
        "date": "2025-06-16",
        "themes": ["reading", "self-improvement", "insight"],
    },
    {
        "text": "Paired with a junior developer today. Teaching them about embeddings and vector search was fun. I learned as much as they did.",
        "date": "2025-06-17",
        "themes": ["work", "mentoring", "ML", "positive"],
    },
    {
        "text": "Date night with my partner. We actually talked — really talked — for the first time in weeks. We're going to do weekly check-ins.",
        "date": "2025-06-18",
        "themes": ["relationship", "positive", "communication"],
    },
    {
        "text": "Sprint retro revealed we've been underscopping consistently. I proposed a buffer system and the team agreed. Feels good to solve a systemic issue.",
        "date": "2025-06-19",
        "themes": ["work", "process", "leadership", "positive"],
    },
    {
        "text": "Reflected on the past three weeks. I've gone from anxious and overwhelmed to cautiously optimistic. The running, journaling, and honest conversations helped.",
        "date": "2025-06-20",
        "themes": ["self-reflection", "growth", "positive", "summary"],
    },
]

# --- Queries with expected retrieval targets ---

EVAL_QUERIES = [
    {
        "query": "I'm feeling anxious about a work deadline and can't sleep",
        "task_type": "sentiment",
        "expected_relevant_indices": [0, 4, 8],  # new-project anxiety, insomnia, demoralizing standup
        "description": "Work anxiety + insomnia — should retrieve stress/work entries",
    },
    {
        "query": "I went for a run today and felt great afterwards",
        "task_type": "insights",
        "expected_relevant_indices": [1, 12],  # park run, 10K achievement
        "description": "Exercise positive — should retrieve running entries",
    },
    {
        "query": "My relationship is suffering because of work. We had a fight.",
        "task_type": "sentiment",
        "expected_relevant_indices": [11, 17, 4],  # argument, date night (contrast), work-life-balance
        "description": "Relationship tension — should retrieve partner-related entries",
    },
    {
        "query": "The ML model I built is performing really well",
        "task_type": "insights",
        "expected_relevant_indices": [5, 10, 13, 16],  # ML pipeline, eval results, demo, mentoring
        "description": "ML achievement — should retrieve ML/work-achievement entries",
    },
    {
        "query": "I need to take better care of my mental health",
        "task_type": "summarize",
        "expected_relevant_indices": [6, 9, 15, 19],  # journaling/meditation, mental health day, atomic habits, reflection
        "description": "Mental health — should retrieve self-care/reflection entries",
    },
]
