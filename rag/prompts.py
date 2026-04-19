"""RAG-augmented prompt templates for journal analysis."""


def _format_context(entries: list[dict], max_entries: int = 3) -> str:
    """Format retrieved entries into a context block for prompt augmentation."""
    if not entries:
        return ""

    lines = []
    for i, entry in enumerate(entries[:max_entries], 1):
        date = entry.get("created_at", "unknown date")[:10]
        sim = entry.get("similarity", 0)
        text = entry["text"][:500]  # cap individual entry length
        lines.append(f"[Past Entry {i} — {date}, relevance {sim:.2f}]\n{text}")

    return "\n\n".join(lines)


def rag_sentiment_prompt(current_text: str, retrieved: list[dict]) -> str:
    context = _format_context(retrieved)
    if context:
        return f"""You are analysing a journal entry with access to the writer's relevant past entries for longitudinal context.

=== PAST JOURNAL ENTRIES (for context) ===
{context}

=== CURRENT JOURNAL ENTRY ===
"{current_text}"

Provide a detailed sentiment analysis that:
1. Identifies the primary emotional state and intensity in the current entry
2. Notes any emotional patterns or shifts compared to past entries
3. Highlights emotional triggers or catalysts
4. Offers suggestions for emotional wellbeing or reflection

Be specific to the writer's actual words. Reference past entries only when they reveal meaningful patterns."""
    else:
        return f"""Analyze the emotional tone and sentiment of this journal entry with deep psychological insight.

Journal Entry:
"{current_text}"

Provide a detailed sentiment analysis that includes:
1. Primary emotional state and intensity
2. Underlying emotional patterns or conflicts
3. Emotional triggers or catalysts mentioned
4. Suggestions for emotional wellbeing or reflection"""


def rag_insights_prompt(current_text: str, retrieved: list[dict]) -> str:
    context = _format_context(retrieved)
    if context:
        return f"""You are a thoughtful life coach analysing a journal entry with access to relevant past entries.

=== PAST JOURNAL ENTRIES (for context) ===
{context}

=== CURRENT JOURNAL ENTRY ===
"{current_text}"

Provide specific, actionable insights that:
1. Identify recurring patterns across entries (thinking, behaviour, emotions)
2. Highlight growth or regression since past entries
3. Suggest concrete next steps grounded in the writer's own experiences
4. Connect current themes to longer-term trajectories visible in the past entries

Be specific — avoid generic advice. Reference past entries when they illuminate patterns."""
    else:
        return f"""As an insightful life coach and psychologist, analyze this journal entry to provide personalized insights.

Journal Entry:
"{current_text}"

Provide specific, actionable insights that:
1. Identify key patterns in their thinking or behavior
2. Highlight strengths and growth opportunities
3. Suggest concrete next steps or reflections
4. Connect their experiences to broader life themes"""


def rag_summarize_prompt(current_text: str, retrieved: list[dict]) -> str:
    context = _format_context(retrieved)
    if context:
        return f"""Summarise this journal entry, noting connections to the writer's past entries where relevant.

=== PAST JOURNAL ENTRIES (for context) ===
{context}

=== CURRENT JOURNAL ENTRY ===
"{current_text}"

Create a summary (2–3 sentences) that:
1. Captures the main events and emotional core
2. Notes any continuation or evolution of themes from past entries
3. Highlights important realisations or decisions"""
    else:
        return f"""Create a concise but comprehensive summary of this journal entry.

Journal Entry:
"{current_text}"

Create a summary (2–3 sentences) that captures the main events, emotional core, and any important realisations or decisions."""
