"""
Prompt Template Library
Save, load, and manage successful prompt templates for each pipeline stage
"""

import json
import sqlite3
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path


class PromptTemplateLibrary:
    """
    Manages a library of prompt templates with performance tracking.
    Allows quick switching between proven templates.
    """

    def __init__(self, db_path: str = "prompt_templates.db"):
        self.db_path = db_path
        self.init_database()
        self.load_default_templates()

    def init_database(self):
        """Initialize database for storing templates"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                id TEXT PRIMARY KEY,
                stage TEXT NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                prompt_template TEXT NOT NULL,
                description TEXT,
                performance_metrics TEXT,
                usage_count INTEGER DEFAULT 0,
                avg_quality_score REAL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                tags TEXT,
                author TEXT,
                model_optimized_for TEXT
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS template_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id TEXT NOT NULL,
                used_at TEXT NOT NULL,
                quality_score REAL,
                output_sample TEXT,
                notes TEXT,
                FOREIGN KEY (template_id) REFERENCES templates (id)
            )
        ''')

        conn.commit()
        conn.close()

    def generate_template_id(self, stage: str, name: str) -> str:
        """Generate unique ID for template"""
        content = f"{stage}_{name}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def save_template(
        self,
        stage: str,
        name: str,
        prompt_template: str,
        category: str = "custom",
        description: str = "",
        tags: List[str] = None,
        author: str = "user",
        model_optimized_for: str = "gpt-4"
    ) -> str:
        """Save a new template to the library"""

        template_id = self.generate_template_id(stage, name)

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''
            INSERT INTO templates
            (id, stage, name, category, prompt_template, description, tags,
             author, model_optimized_for, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            template_id,
            stage,
            name,
            category,
            prompt_template,
            description,
            json.dumps(tags) if tags else "[]",
            author,
            model_optimized_for,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

        return template_id

    def get_template(self, template_id: str = None, stage: str = None, name: str = None) -> Optional[Dict]:
        """Get a specific template by ID or stage+name"""

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        if template_id:
            c.execute('SELECT * FROM templates WHERE id = ?', (template_id,))
        elif stage and name:
            c.execute('SELECT * FROM templates WHERE stage = ? AND name = ?', (stage, name))
        else:
            return None

        row = c.fetchone()
        conn.close()

        if row:
            return {
                'id': row[0],
                'stage': row[1],
                'name': row[2],
                'category': row[3],
                'prompt_template': row[4],
                'description': row[5],
                'performance_metrics': json.loads(row[6]) if row[6] else {},
                'usage_count': row[7],
                'avg_quality_score': row[8],
                'created_at': row[9],
                'updated_at': row[10],
                'tags': json.loads(row[11]) if row[11] else [],
                'author': row[12],
                'model_optimized_for': row[13]
            }
        return None

    def list_templates(
        self,
        stage: str = None,
        category: str = None,
        min_quality_score: float = None
    ) -> List[Dict]:
        """List templates with optional filters"""

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        query = 'SELECT * FROM templates WHERE 1=1'
        params = []

        if stage:
            query += ' AND stage = ?'
            params.append(stage)

        if category:
            query += ' AND category = ?'
            params.append(category)

        if min_quality_score is not None:
            query += ' AND avg_quality_score >= ?'
            params.append(min_quality_score)

        query += ' ORDER BY avg_quality_score DESC, usage_count DESC'

        c.execute(query, params)
        rows = c.fetchall()
        conn.close()

        templates = []
        for row in rows:
            templates.append({
                'id': row[0],
                'stage': row[1],
                'name': row[2],
                'category': row[3],
                'description': row[5],
                'usage_count': row[7],
                'avg_quality_score': row[8],
                'tags': json.loads(row[11]) if row[11] else [],
                'model_optimized_for': row[13]
            })

        return templates

    def record_usage(
        self,
        template_id: str,
        quality_score: float = None,
        output_sample: str = None,
        notes: str = None
    ):
        """Record template usage and update performance metrics"""

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Record usage
        c.execute('''
            INSERT INTO template_usage
            (template_id, used_at, quality_score, output_sample, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            template_id,
            datetime.now().isoformat(),
            quality_score,
            output_sample[:500] if output_sample else None,  # Limit sample size
            notes
        ))

        # Update template statistics
        c.execute('UPDATE templates SET usage_count = usage_count + 1 WHERE id = ?', (template_id,))

        if quality_score is not None:
            # Recalculate average quality score
            c.execute('''
                UPDATE templates
                SET avg_quality_score = (
                    SELECT AVG(quality_score)
                    FROM template_usage
                    WHERE template_id = ? AND quality_score IS NOT NULL
                )
                WHERE id = ?
            ''', (template_id, template_id))

        conn.commit()
        conn.close()

    def get_best_template(self, stage: str, min_usage: int = 3) -> Optional[Dict]:
        """Get the best performing template for a stage"""

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''
            SELECT * FROM templates
            WHERE stage = ? AND usage_count >= ?
            ORDER BY avg_quality_score DESC
            LIMIT 1
        ''', (stage, min_usage))

        row = c.fetchone()
        conn.close()

        if row:
            return {
                'id': row[0],
                'stage': row[1],
                'name': row[2],
                'prompt_template': row[4],
                'avg_quality_score': row[8],
                'usage_count': row[7]
            }
        return None

    def get_template_variations(self, stage: str) -> Dict[str, str]:
        """Get all template variations for a stage (for A/B testing)"""

        templates = self.list_templates(stage=stage)
        variations = {}

        for template in templates:
            variation_name = f"{template['category']}_{template['name']}"
            variations[variation_name] = self.get_template(template['id'])['prompt_template']

        return variations

    def load_default_templates(self):
        """Load default templates if database is empty"""

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM templates')
        count = c.fetchone()[0]
        conn.close()

        if count == 0:
            # Load default templates
            for stage, templates in DEFAULT_TEMPLATES.items():
                for name, config in templates.items():
                    self.save_template(
                        stage=stage,
                        name=name,
                        prompt_template=config['template'],
                        category=config['category'],
                        description=config['description'],
                        tags=config.get('tags', []),
                        model_optimized_for=config.get('model', 'gpt-4')
                    )

    def export_templates(self, output_path: str):
        """Export all templates to JSON file"""

        templates = self.list_templates()
        full_templates = []

        for t in templates:
            full = self.get_template(t['id'])
            full_templates.append(full)

        with open(output_path, 'w') as f:
            json.dump(full_templates, f, indent=2)

    def import_templates(self, input_path: str):
        """Import templates from JSON file"""

        with open(input_path, 'r') as f:
            templates = json.load(f)

        for template in templates:
            self.save_template(
                stage=template['stage'],
                name=template['name'],
                prompt_template=template['prompt_template'],
                category=template.get('category', 'imported'),
                description=template.get('description', ''),
                tags=template.get('tags', []),
                author=template.get('author', 'imported')
            )


# Default template library
DEFAULT_TEMPLATES = {
    "stage_1": {
        "standard_extraction": {
            "category": "baseline",
            "template": """Extract all emotional trends from this report.
For each trend, provide 4 abstraction levels:

L1 (Domain-Specific): CPG-actionable application
L2 (Industry-Specific): Category-level pattern
L3 (Cross-Domain): Transferable mechanism
L4 (Universal Principle): Fundamental dynamic

Also extract:
- Lifecycle stage (EMERGING/ACCELERATING/PEAKING)
- Current negative emotions (what consumers feel now)
- Aspirational positive emotions (what they want to feel)

Report text:
{report_text}

Output as JSON array.""",
            "description": "Standard L1-L4 extraction with emotional drivers",
            "tags": ["baseline", "comprehensive"]
        },
        "evidence_focused": {
            "category": "detailed",
            "template": """Extract emotional trends with supporting evidence.

For each trend found:
1. Name and lifecycle stage
2. Direct quotes from the report supporting this trend
3. Specific examples or data points mentioned
4. L1-L4 abstraction levels
5. Emotional drivers (current negative → aspirational positive)

Focus on extracting verbatim evidence from:
{report_text}

Output as detailed JSON with evidence fields.""",
            "description": "Emphasizes evidence and quotes from source",
            "tags": ["evidence", "detailed", "validation"]
        }
    },
    "stage_2": {
        "emotional_convergence": {
            "category": "emotional",
            "template": """Identify consumer insights through EMOTIONAL CONVERGENCE.

Trends provided: {trends}
Brand context: {brand_context}

Instructions:
1. Map emotional territories where trends overlap
2. Find shared emotional journeys (negative → positive)
3. Create insights that address emotional convergence points
4. Each insight must resolve multiple emotional tensions

Focus on FEELINGS, not just functional needs.

Output as JSON array of emotionally-driven insights.""",
            "description": "Prioritizes emotional driver convergence",
            "tags": ["emotional", "convergence"],
            "model": "gpt-4"
        },
        "lifecycle_strategic": {
            "category": "strategic",
            "template": """Generate insights based on LIFECYCLE STRATEGY.

Trends: {trends}
Brand: {brand_context}

For each trend combination:
1. Identify lifecycle stage combination (e.g., EMERGING + ACCELERATING)
2. Determine strategic posture:
   - EMERGING + EMERGING = Pioneer (high risk/reward)
   - ACCELERATING + ACCELERATING = Validate (proven demand)
   - EMERGING + ACCELERATING = Hedge (balanced approach)
3. Create insight that leverages lifecycle timing
4. Specify execution timeline based on lifecycle

Output insights with clear lifecycle strategy.""",
            "description": "Uses lifecycle stages to determine timing",
            "tags": ["strategic", "lifecycle", "timing"]
        },
        "functional_jobs": {
            "category": "jobs-to-be-done",
            "template": """Apply JOBS-TO-BE-DONE framework to find insights.

Trends: {trends}
Brand: {brand_context}

For each trend convergence:
1. Identify the JOB consumers are trying to get done
2. Current solutions and their shortcomings
3. How trend convergence reveals new job or better solution
4. Functional, emotional, and social dimensions of the job

Frame insights as: "Help me [JOB] so I can [OUTCOME] without [PAIN]"

Output as JSON with JTBD structure.""",
            "description": "Jobs-to-be-done framework application",
            "tags": ["JTBD", "functional", "outcome-focused"]
        }
    },
    "stage_3": {
        "sit_comprehensive": {
            "category": "SIT",
            "template": """Match insight to SIT technique with detailed application.

Insight: {insight}
Brand: {brand_context}

For EACH of the 5 SIT techniques, evaluate fit:
1. Subtraction: What could we remove?
2. Task Unification: What could do double duty?
3. Multiplication: What could we copy and change?
4. Attribute Dependency: What could we correlate?
5. Division: What could we separate?

Select the BEST technique and provide:
- Specific application to this brand/category
- Step-by-step implementation
- Similar CPG example
- Resource requirements

Output detailed JSON with rationale.""",
            "description": "Comprehensive SIT evaluation",
            "tags": ["SIT", "comprehensive", "detailed"]
        },
        "quick_match": {
            "category": "fast",
            "template": """Quick SIT technique selection.

Insight: {insight}

Match to most appropriate SIT technique:
- Subtraction (remove)
- Task Unification (assign new task)
- Multiplication (copy and vary)
- Attribute Dependency (correlate)
- Division (reorganize)

Output: technique name, one-line application, feasibility.""",
            "description": "Rapid technique selection",
            "tags": ["fast", "simple"]
        }
    },
    "stage_4": {
        "conservative_concept": {
            "category": "conservative",
            "template": """Generate a SAFE, INCREMENTAL concept.

Insight: {insight}
Technique: {technique}
Brand: {brand_context}

Create a concept that:
- Requires minimal behavior change
- Uses existing infrastructure
- Can pilot in 1-2 stores
- Costs under $50K
- Shows results in 3-6 months

Avoid: New technology, radical changes, category disruption

Output as JSON with all required fields.""",
            "description": "Low-risk, incremental innovation",
            "tags": ["conservative", "safe", "incremental"],
            "model": "gpt-3.5-turbo"
        },
        "disruptive_concept": {
            "category": "disruptive",
            "template": """Generate a BOLD, CATEGORY-CHALLENGING concept.

Insight: {insight}
Technique: {technique}
Brand: {brand_context}
Creativity level: {creativity_level}

Create a concept that:
- Challenges category conventions
- Uses emerging technology or channels
- Creates new consumer behaviors
- Could become category standard
- Think 2-3 years ahead

Push boundaries while maintaining feasibility.

Include: Memorable name, bold tagline, disruptive elements.""",
            "description": "High-creativity, category-challenging",
            "tags": ["disruptive", "bold", "innovative"],
            "model": "gpt-4"
        }
    }
}


# Helper functions for integration
def get_template_for_experiment(
    library: PromptTemplateLibrary,
    stage: str,
    strategy: str = "best"
) -> str:
    """Get a template for experimentation"""

    if strategy == "best":
        # Get best performing template
        best = library.get_best_template(stage)
        if best:
            return best['prompt_template']

    elif strategy == "random":
        # Get random template for A/B testing
        templates = library.list_templates(stage=stage)
        if templates:
            import random
            selected = random.choice(templates)
            return library.get_template(selected['id'])['prompt_template']

    elif strategy.startswith("category:"):
        # Get template from specific category
        category = strategy.split(":")[1]
        templates = library.list_templates(stage=stage, category=category)
        if templates:
            return library.get_template(templates[0]['id'])['prompt_template']

    # Fallback to default
    return DEFAULT_TEMPLATES.get(stage, {}).get("standard_extraction", {}).get("template", "")


def save_successful_prompt(
    library: PromptTemplateLibrary,
    stage: str,
    prompt: str,
    quality_score: float,
    name: str = None
):
    """Save a successful prompt to the library"""

    if quality_score >= 0.8:  # Only save high-quality prompts
        if not name:
            name = f"auto_saved_{datetime.now().strftime('%Y%m%d_%H%M')}"

        template_id = library.save_template(
            stage=stage,
            name=name,
            prompt_template=prompt,
            category="successful",
            description=f"Auto-saved with quality score {quality_score:.2f}"
        )

        library.record_usage(template_id, quality_score)
        return template_id
    return None


if __name__ == "__main__":
    # Test the library
    library = PromptTemplateLibrary()

    # List available templates
    print("Available Stage 2 Templates:")
    for template in library.list_templates(stage="stage_2"):
        print(f"  - {template['name']} ({template['category']}): {template['description']}")

    # Get variations for A/B testing
    print("\nStage 2 Variations:")
    variations = library.get_template_variations("stage_2")
    for name, prompt in variations.items():
        print(f"  - {name}: {len(prompt)} chars")

    # Get best template
    best = library.get_best_template("stage_1")
    if best:
        print(f"\nBest Stage 1 template: {best['name']} (score: {best['avg_quality_score']:.2f})")