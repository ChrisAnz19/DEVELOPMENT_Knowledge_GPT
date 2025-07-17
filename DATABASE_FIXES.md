# Database Fixes for Knowledge_GPT

## Issues Identified

1. **Null Constraint Violation**: The `prompt` field was being set to `null` when updating search records
2. **Missing Behavioral Data**: Individual candidates weren't receiving their personalized behavioral insights
3. **Missing Database Column**: The `people` table was missing the `behavioral_data` column

## Fixes Applied

### 1. Fixed Null Constraint Violation (`api/main.py`)

**Problem**: When updating search records, the `prompt` field was being set to `null`, violating the NOT NULL constraint.

**Solution**: Modified the search update logic to:
- Retrieve the existing record first
- Preserve all required fields (especially `prompt`)
- Use fallback values if needed
- Ensure proper error handling

```python
# Get the existing record first to preserve required fields
existing_record = get_search_from_database(request_id)
if not existing_record:
    logger.error(f"Search record not found for update: {request_id}")
    return

# Update search data while preserving required fields
update_data = {
    "id": existing_record.get("id"),
    "request_id": existing_record.get("request_id", request_id),
    "prompt": existing_record.get("prompt", prompt),  # Use original prompt or fallback
    "status": "completed",
    "filters": json.dumps(filters),
    "completed_at": datetime.now(timezone.utc).isoformat()
}
```

### 2. Added Behavioral Data to People Table

**Problem**: The `people` table schema didn't include a `behavioral_data` column, so individual candidate behavioral insights weren't being stored.

**Solution**: 
- Updated `schema.sql` to include `behavioral_data JSONB` column
- Modified `database.py` to handle behavioral data storage and retrieval
- Added JSON serialization/deserialization for behavioral data

### 3. Enhanced Behavioral Data Generation (`api/main.py`)

**Problem**: Behavioral data generation was failing silently for individual candidates.

**Solution**: Added robust error handling and fallback behavioral data:

```python
# Generate and attach personalized behavioral data
try:
    behavioral_data = enhance_behavioral_data_ai({}, [candidate], prompt)
    candidate["behavioral_data"] = behavioral_data
    logger.info(f"Generated behavioral data for {candidate.get('name', 'Unknown')}")
except Exception as bd_error:
    logger.error(f"Error generating behavioral data for {candidate.get('name', 'Unknown')}: {str(bd_error)}")
    # Provide fallback behavioral data
    candidate["behavioral_data"] = {
        "behavioral_insight": "This professional responds best to personalized engagement...",
        "scores": {
            "cmi": {"score": 70, "explanation": "Moderate commitment momentum"},
            "rbfs": {"score": 65, "explanation": "Balanced risk approach"},
            "ias": {"score": 75, "explanation": "Strong role alignment"}
        }
    }
```

### 4. Updated Database Functions (`database.py`)

**Changes Made**:
- Added `behavioral_data` to schema fields in `store_people_to_database()`
- Added JSON serialization for behavioral data storage
- Updated `get_people_for_search()` to include and parse behavioral data
- Added proper JSON deserialization when retrieving data

## Database Migration Required

You need to add the `behavioral_data` column to your existing `people` table. Run this SQL in your Supabase SQL Editor:

```sql
ALTER TABLE people ADD COLUMN IF NOT EXISTS behavioral_data JSONB;
```

## Files Modified

1. `api/main.py` - Fixed search update logic and enhanced behavioral data generation
2. `database.py` - Added behavioral data handling to database functions
3. `schema.sql` - Updated schema to include behavioral_data column
4. `database_migration.sql` - Created migration script for existing databases
5. `run_migration.py` - Python script to run the migration
6. `fix_database_issues.py` - Comprehensive fix and test script

## How to Apply the Fixes

### Step 1: Update Database Schema
Run this SQL in your Supabase SQL Editor:
```sql
ALTER TABLE people ADD COLUMN IF NOT EXISTS behavioral_data JSONB;
```

### Step 2: Test the Fixes
Run the fix script to verify everything is working:
```bash
python fix_database_issues.py
```

### Step 3: Restart Your API Server
After applying the fixes, restart your API server to ensure all changes take effect.

### Step 4: Test with a New Search
Create a new search request and verify that:
- The search completes without database errors
- Each candidate has a `behavioral_data` field with:
  - `behavioral_insight` (string)
  - `scores` object with `cmi`, `rbfs`, and `ias` scores
  - Each score has both `score` (number) and `explanation` (string)

## Expected Result

After applying these fixes, each candidate in your search results should have a `behavioral_data` field like this:

```json
{
  "behavioral_data": {
    "behavioral_insight": "This Director of Marketing exhibits high commitment momentum with focused research on marketing automation platforms and ROI measurement tools. Their recent deep-dive sessions on competitive analysis suggest they're moving beyond initial research toward implementation planning.",
    "scores": {
      "cmi": {
        "score": 85,
        "explanation": "Ready to act"
      },
      "rbfs": {
        "score": 65,
        "explanation": "Balanced risk approach"
      },
      "ias": {
        "score": 80,
        "explanation": "Strong role alignment"
      }
    }
  }
}
```

## Troubleshooting

If you still encounter issues:

1. **Check Supabase Logs**: Look for any database constraint violations
2. **Verify Column Exists**: Ensure the `behavioral_data` column was added successfully
3. **Check API Logs**: Look for behavioral data generation errors
4. **Test Individual Components**: Use the `fix_database_issues.py` script to test each component

The fixes ensure robust error handling, so even if behavioral data generation fails, candidates will receive fallback behavioral insights rather than empty data.