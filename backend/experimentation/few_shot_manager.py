"""
Few-Shot Example Manager
Dynamically inject successful examples into prompts to improve LLM performance
"""

import json
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

class FewShotExampleManager:
    """
    Manages few-shot examples for each pipeline stage.
    Stores successful outputs and injects them into prompts.
    """

    def __init__(self, db_path: str = "few_shot_examples.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Create database for storing examples"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS examples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stage TEXT NOT NULL,
                input_context TEXT NOT NULL,
                output_example TEXT NOT NULL,
                quality_score REAL NOT NULL,
                brand_context TEXT,
                timestamp TEXT NOT NULL,
                notes TEXT,
                model_used TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def add_example(
        self,
        stage: str,
        input_context: Dict,
        output_example: Any,
        quality_score: float,
        brand_context: Optional[Dict] = None,
        notes: str = "",
        model_used: str = "gpt-4"
    ):
        """Add a successful example to the database"""

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''
            INSERT INTO examples
            (stage, input_context, output_example, quality_score, brand_context, timestamp, notes, model_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            stage,
            json.dumps(input_context),
            json.dumps(output_example) if isinstance(output_example, (dict, list)) else str(output_example),
            quality_score,
            json.dumps(brand_context) if brand_context else None,
            datetime.now().isoformat(),
            notes,
            model_used
        ))

        conn.commit()
        conn.close()

    def get_best_examples(
        self,
        stage: str,
        n_examples: int = 3,
        min_score: float = 0.8,
        brand_filter: Optional[str] = None
    ) -> List[Dict]:
        """Get the best examples for a stage"""

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        query = '''
            SELECT input_context, output_example, quality_score, brand_context, notes
            FROM examples
            WHERE stage = ? AND quality_score >= ?
        '''
        params = [stage, min_score]

        if brand_filter:
            query += " AND brand_context LIKE ?"
            params.append(f'%"{brand_filter}"%')

        query += " ORDER BY quality_score DESC LIMIT ?"
        params.append(n_examples)

        c.execute(query, params)
        results = c.fetchall()
        conn.close()

        examples = []
        for row in results:
            examples.append({
                "input": json.loads(row[0]),
                "output": json.loads(row[1]) if row[1].startswith('[') or row[1].startswith('{') else row[1],
                "score": row[2],
                "brand": json.loads(row[3]) if row[3] else None,
                "notes": row[4]
            })

        return examples

    def inject_into_prompt(
        self,
        prompt_template: str,
        stage: str,
        n_examples: int = 2,
        format_style: str = "detailed"
    ) -> str:
        """Inject few-shot examples into a prompt template"""

        examples = self.get_best_examples(stage, n_examples)

        if not examples:
            return prompt_template  # No examples available

        if format_style == "detailed":
            example_text = self._format_detailed_examples(examples, stage)
        elif format_style == "simple":
            example_text = self._format_simple_examples(examples, stage)
        else:
            example_text = self._format_json_examples(examples, stage)

        # Look for placeholder or inject at beginning
        if "{examples}" in prompt_template:
            return prompt_template.replace("{examples}", example_text)
        elif "{few_shot_examples}" in prompt_template:
            return prompt_template.replace("{few_shot_examples}", example_text)
        else:
            # Inject after first paragraph
            lines = prompt_template.split('\n')
            # Find first empty line
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.strip() == "" and i > 0:
                    insert_pos = i
                    break

            if insert_pos > 0:
                lines.insert(insert_pos, example_text)
                return '\n'.join(lines)
            else:
                return example_text + "\n\n" + prompt_template

    def _format_detailed_examples(self, examples: List[Dict], stage: str) -> str:
        """Format examples with detailed explanation"""

        formatted = f"\n=== HIGH-QUALITY EXAMPLES FOR {stage.upper()} ===\n\n"

        for i, ex in enumerate(examples, 1):
            formatted += f"EXAMPLE {i} (Quality Score: {ex['score']:.2f}):\n"

            if stage == "stage_1":
                formatted += f"Input: {ex['input'].get('report_excerpt', 'Report text...')[:200]}...\n"
                formatted += f"Output: {json.dumps(ex['output'], indent=2)}\n"

            elif stage == "stage_2":
                formatted += f"Trends Provided:\n{json.dumps(ex['input'].get('trends', []), indent=2)}\n"
                formatted += f"Brand Context: {ex['input'].get('brand_context', {}).get('name', 'Unknown')}\n"
                formatted += f"Generated Insight:\n{json.dumps(ex['output'], indent=2)}\n"

            elif stage == "stage_3":
                formatted += f"Insight: {ex['input'].get('insight', {}).get('statement', 'Unknown')}\n"
                formatted += f"Selected Technique: {ex['output'].get('primary_technique', 'Unknown')}\n"
                formatted += f"Application: {ex['output'].get('application', 'Unknown')}\n"

            elif stage == "stage_4":
                formatted += f"Technique: {ex['input'].get('technique', {}).get('primary_technique', 'Unknown')}\n"
                formatted += f"Concept Generated: {ex['output'].get('concept_name', 'Unknown')}\n"
                formatted += f"Tagline: {ex['output'].get('tagline', 'Unknown')}\n"

            if ex.get('notes'):
                formatted += f"Note: {ex['notes']}\n"

            formatted += "\n---\n\n"

        formatted += "=== END OF EXAMPLES ===\n\n"
        formatted += "Now, following the pattern of these high-quality examples:\n\n"

        return formatted

    def _format_simple_examples(self, examples: List[Dict], stage: str) -> str:
        """Format examples in simple input->output style"""

        formatted = "\nHere are successful examples to follow:\n\n"

        for i, ex in enumerate(examples, 1):
            formatted += f"Example {i}:\n"
            formatted += f"Input: {json.dumps(ex['input'], indent=2)[:500]}...\n"
            formatted += f"Output: {json.dumps(ex['output'], indent=2)[:500]}...\n\n"

        return formatted

    def _format_json_examples(self, examples: List[Dict], stage: str) -> str:
        """Format examples as JSON for structured prompts"""

        json_examples = [
            {
                "input": ex['input'],
                "output": ex['output'],
                "quality_score": ex['score']
            }
            for ex in examples
        ]

        return f"\nExamples (JSON format):\n{json.dumps(json_examples, indent=2)}\n\n"

    def auto_save_if_good(
        self,
        stage: str,
        input_context: Dict,
        output: Any,
        quality_scores: Dict,
        threshold: float = 0.8
    ):
        """Automatically save example if quality is high"""

        avg_score = sum(quality_scores.values()) / len(quality_scores)

        if avg_score >= threshold:
            self.add_example(
                stage=stage,
                input_context=input_context,
                output_example=output,
                quality_score=avg_score,
                notes=f"Auto-saved. Scores: {quality_scores}"
            )
            return True
        return False

    def get_statistics(self) -> Dict:
        """Get statistics about stored examples"""

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        stats = {}

        # Count by stage
        c.execute('''
            SELECT stage, COUNT(*), AVG(quality_score), MAX(quality_score)
            FROM examples
            GROUP BY stage
        ''')

        for row in c.fetchall():
            stats[row[0]] = {
                "count": row[1],
                "avg_score": row[2],
                "max_score": row[3]
            }

        # Overall stats
        c.execute('SELECT COUNT(*), AVG(quality_score) FROM examples')
        overall = c.fetchone()
        stats['overall'] = {
            "total_examples": overall[0],
            "avg_quality": overall[1]
        }

        conn.close()
        return stats


# Usage functions for integration
def enhance_prompt_with_examples(
    prompt: str,
    stage: str,
    manager: Optional[FewShotExampleManager] = None
) -> str:
    """Enhance a prompt with few-shot examples"""

    if manager is None:
        manager = FewShotExampleManager()

    return manager.inject_into_prompt(prompt, stage)


def save_successful_output(
    stage: str,
    input_data: Dict,
    output_data: Any,
    quality_scores: Dict,
    manager: Optional[FewShotExampleManager] = None
):
    """Save a successful output as an example"""

    if manager is None:
        manager = FewShotExampleManager()

    return manager.auto_save_if_good(
        stage=stage,
        input_context=input_data,
        output=output_data,
        quality_scores=quality_scores
    )


# Pre-loaded examples for immediate use
DEFAULT_EXAMPLES = {
    "stage_1": {
        "input": {"report_excerpt": "The Witherwill trend reflects consumer desire for simplification..."},
        "output": {
            "trend_name": "Witherwill",
            "lifecycle_stage": "ACCELERATING",
            "emotional_drivers": {
                "current_negative": ["overwhelmed", "fatigued"],
                "aspirational_positive": ["carefree", "grounded"]
            },
            "abstraction_levels": {
                "L1": "Minimalist packaging, curated SKU sets",
                "L2": "Food brands reducing choice architecture",
                "L3": "Simplification as self-care",
                "L4": "Restraint as luxury"
            }
        }
    },
    "stage_2": {
        "input": {
            "trends": ["Witherwill", "Strategic Joy"],
            "brand_context": {"name": "Boulangerie St-Méthode", "industry": "Bakery"}
        },
        "output": {
            "insight_statement": "Bread buyers overwhelmed by 47 SKUs want purchasing to feel like rediscovering childhood simplicity",
            "primary_trend": "Witherwill",
            "secondary_trend": "Strategic Joy",
            "consumer_needs": {
                "functional": "Reduce decision time from 3 minutes to 30 seconds",
                "emotional": "Feel confident and carefree when choosing",
                "social": "Be perceived as discerning, not indecisive"
            }
        }
    }
}


if __name__ == "__main__":
    # Test the manager
    manager = FewShotExampleManager()

    # Add default examples
    for stage, example in DEFAULT_EXAMPLES.items():
        manager.add_example(
            stage=stage,
            input_context=example["input"],
            output_example=example["output"],
            quality_score=0.9,
            notes="Default high-quality example"
        )

    # Test injection
    test_prompt = "Extract trends from this report.\n\n{examples}\n\nReport text: {report_text}"
    enhanced = manager.inject_into_prompt(test_prompt, "stage_1")
    print("Enhanced prompt:")
    print(enhanced[:500] + "...")

    # Show statistics
    print("\nExample Statistics:")
    print(json.dumps(manager.get_statistics(), indent=2))