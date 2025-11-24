"""Debug script to analyze stage output structure from database"""
import psycopg2
import psycopg2.extras
import json
import os

# Railway database URL
DATABASE_URL = "postgresql://postgres:bKHNBXhkZOvIOAQEGSvRrfWnAxVwQjkz@junction.proxy.rlwy.net:14838/railway"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Query for experiment ee75be44
    cur.execute('SELECT "stageOutputs" FROM "Experiment" WHERE "id" LIKE %s LIMIT 1', ('%ee75be44',))
    result = cur.fetchone()

    if result:
        stage_outputs = result['stageOutputs']

        # Analyze Stage 1
        print("=" * 80)
        print("STAGE 1 ANALYSIS")
        print("=" * 80)

        if 'stage_1' in stage_outputs:
            stage1 = stage_outputs['stage_1']
            print(f"\nStage 1 Keys: {list(stage1.keys())}")

            if 'output' in stage1:
                output = stage1['output']
                print(f"\nStage 1 Output Type: {type(output)}")

                if isinstance(output, dict):
                    print(f"Stage 1 Output Keys: {list(output.keys())}")
                    print(f"\nStage 1 Output Structure:")
                    print(json.dumps(output, indent=2)[:1000])
                elif isinstance(output, str):
                    print(f"\nStage 1 Output is a STRING (first 500 chars):")
                    print(output[:500])

            if 'markdown' in stage1:
                markdown = stage1['markdown']
                print(f"\n\nStage 1 Markdown Type: {type(markdown)}")
                print(f"\nStage 1 Markdown Content (first 1000 chars):")
                print(markdown[:1000])

                # Check if it's JSON wrapped in code blocks
                if markdown.strip().startswith('```json'):
                    print("\n⚠️  PROBLEM: Markdown contains JSON code block instead of formatted markdown!")
                elif markdown.strip().startswith('# Stage 1'):
                    print("\n✅ Good: Markdown is properly formatted")

        # Analyze Stage 5 (known to have issue)
        print("\n\n" + "=" * 80)
        print("STAGE 5 ANALYSIS")
        print("=" * 80)

        if 'stage_5' in stage_outputs:
            stage5 = stage_outputs['stage_5']
            print(f"\nStage 5 Keys: {list(stage5.keys())}")

            if 'output' in stage5:
                output = stage5['output']
                print(f"\nStage 5 Output Type: {type(output)}")

                if isinstance(output, dict):
                    print(f"Stage 5 Output Keys: {list(output.keys())}")

                    # Check for opportunities structure
                    if 'opportunities' in output:
                        opps = output['opportunities']
                        print(f"\nStage 5 has {len(opps)} opportunities")
                        if opps:
                            print(f"First opportunity keys: {list(opps[0].keys())}")
                            if 'markdown' in opps[0]:
                                print(f"\nFirst opportunity markdown (first 300 chars):")
                                print(opps[0]['markdown'][:300])

            if 'markdown' in stage5:
                markdown = stage5['markdown']
                print(f"\n\nStage 5 Markdown Type: {type(markdown)}")
                print(f"\nStage 5 Markdown Content (first 1000 chars):")
                print(markdown[:1000])

                # Check if it's JSON wrapped in code blocks
                if markdown.strip().startswith('```json'):
                    print("\n⚠️  PROBLEM: Markdown contains JSON code block instead of formatted markdown!")
                elif markdown.strip().startswith('# Stage 5'):
                    print("\n✅ Good: Markdown is properly formatted")

    cur.close()
    conn.close()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
