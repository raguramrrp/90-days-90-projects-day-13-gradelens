"""
GradeLens Rule-Based Recommendation Engine.
Generates transparent, evidence-backed academic recommendations without black-box ML.
Enforces deduplication, priority assignment, and actionable learning steps.
"""

import uuid
from datetime import datetime
import pandas as pd
from typing import List, Dict, Any, Optional
from src.database.repository import Repository, repo
from src.analytics.weakness_engine import TopicWeaknessEngine, weakness_engine


class RecommendationEngine:
    """Deterministic, transparent academic recommendation engine."""

    def __init__(self, repository: Repository = repo, engine: TopicWeaknessEngine = weakness_engine):
        self.repo = repository
        self.weakness_engine = engine

    def generate_recommendations_for_student(self, student_id: str) -> List[Dict[str, Any]]:
        """
        Analyzes a student's responses, topic weaknesses, and mistakes to generate
        rule-based recommendations, persisting them with strict deduplication.
        """
        responses_df = self.repo.get_question_responses(student_id=student_id)
        if responses_df.empty:
            return []

        existing_recs = self.repo.get_recommendations(student_id=student_id)
        active_types_by_topic = set()
        if not existing_recs.empty:
            for _, r in existing_recs[existing_recs["status"] == "Active"].iterrows():
                active_types_by_topic.add((r["topic_id"], r["recommendation_type"]))

        topic_analysis = self.weakness_engine.analyze_all_topics(responses_df)
        new_recommendations = []

        for _, row in topic_analysis.iterrows():
            topic_id = row["topic_id"]
            topic_name = row["topic_name"]
            subject_name = row["subject_name"]
            classification = row["classification"]
            accuracy_pct = row["accuracy_pct"]
            marks_lost = row["marks_lost"]
            primary_mistake = row["primary_mistake"]
            primary_mistake_count = row["primary_mistake_count"]

            # Rule 1: Repeated Weakness -> Urgent Revision Priority
            if classification == "Repeated Weakness":
                rec_type = "Urgent Revision"
                if (topic_id, rec_type) not in active_types_by_topic:
                    rec = {
                        "recommendation_id": f"rec_{uuid.uuid4().hex[:8]}",
                        "student_id": student_id,
                        "topic_id": topic_id,
                        "topic_name": topic_name,
                        "subject_name": subject_name,
                        "recommendation_type": rec_type,
                        "priority": "High",
                        "explanation": (
                            f"Persistent weakness in '{topic_name}' ({accuracy_pct:.1f}% accuracy across assessments). "
                            f"Total marks lost: {marks_lost:.1f}."
                        ),
                        "suggested_action": f"Schedule two 45-minute revision sessions and re-attempt 5 previous exam questions on {topic_name}."
                    }
                    new_recommendations.append(rec)

            # Rule 2: Repeated Calculation or Formula Errors -> Arithmetic / Formula Drill
            elif primary_mistake in ["Calculation error", "Formula error"] and primary_mistake_count >= 2:
                rec_type = "Formula Drill"
                if (topic_id, rec_type) not in active_types_by_topic:
                    rec = {
                        "recommendation_id": f"rec_{uuid.uuid4().hex[:8]}",
                        "student_id": student_id,
                        "topic_id": topic_id,
                        "topic_name": topic_name,
                        "subject_name": subject_name,
                        "recommendation_type": rec_type,
                        "priority": "Medium",
                        "explanation": (
                            f"Identified {primary_mistake_count} '{primary_mistake}' occurrences in '{topic_name}'. "
                            f"Marks were forfeited due to execution slips rather than concept absence."
                        ),
                        "suggested_action": f"Compile a quick formula reference sheet and practice step-by-step calculation verification for {topic_name}."
                    }
                    new_recommendations.append(rec)

            # Rule 3: Declining Performance -> Early Intervention
            elif classification == "Declining":
                rec_type = "Refresher Practice"
                if (topic_id, rec_type) not in active_types_by_topic:
                    rec = {
                        "recommendation_id": f"rec_{uuid.uuid4().hex[:8]}",
                        "student_id": student_id,
                        "topic_id": topic_id,
                        "topic_name": topic_name,
                        "subject_name": subject_name,
                        "recommendation_type": rec_type,
                        "priority": "High",
                        "explanation": (
                            f"Performance on '{topic_name}' dropped by >= 15% in recent assessments compared to historical average."
                        ),
                        "suggested_action": f"Conduct a 30-minute concept review to prevent further knowledge decay."
                    }
                    new_recommendations.append(rec)

            # Rule 4: Improving Topic -> Consolidation
            elif classification == "Improving":
                rec_type = "Consolidation"
                if (topic_id, rec_type) not in active_types_by_topic:
                    rec = {
                        "recommendation_id": f"rec_{uuid.uuid4().hex[:8]}",
                        "student_id": student_id,
                        "topic_id": topic_id,
                        "topic_name": topic_name,
                        "subject_name": subject_name,
                        "recommendation_type": rec_type,
                        "priority": "Low",
                        "explanation": (
                            f"Positive trajectory detected in '{topic_name}' with recent score gains. Current mastery: {accuracy_pct:.1f}%."
                        ),
                        "suggested_action": f"Maintain momentum with one timed practice quiz this week."
                    }
                    new_recommendations.append(rec)

        # Rule 5: Check Unanswered Questions across all responses
        unanswered_count = (responses_df["answer_status"] == "Unanswered").sum()
        if unanswered_count >= 2:
            rec_type = "Time Management"
            first_topic = topic_analysis.iloc[0]["topic_id"] if not topic_analysis.empty else "gen"
            if (first_topic, rec_type) not in active_types_by_topic:
                rec = {
                    "recommendation_id": f"rec_{uuid.uuid4().hex[:8]}",
                    "student_id": student_id,
                    "topic_id": first_topic,
                    "topic_name": "Multiple Topics",
                    "subject_name": "General Strategy",
                    "recommendation_type": rec_type,
                    "priority": "Medium",
                    "explanation": (
                        f"Detected {unanswered_count} completely unanswered questions across recent examinations."
                    ),
                    "suggested_action": "Practice timed mock papers allocating maximum minutes per question section to avoid leaving blanks."
                }
                new_recommendations.append(rec)

        # Persist new non-duplicate recommendations to DB
        for r in new_recommendations:
            full_explanation = f"{r['explanation']} Action: {r['suggested_action']}"
            self.repo.create_recommendation(
                recommendation_id=r["recommendation_id"],
                student_id=r["student_id"],
                topic_id=r["topic_id"],
                recommendation_type=r["recommendation_type"],
                explanation=full_explanation,
                priority=r["priority"]
            )

        return new_recommendations


recommendation_engine = RecommendationEngine()
