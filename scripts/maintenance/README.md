# Maintenance Scripts

This directory contains one-off maintenance and debugging scripts for database management and troubleshooting.

## Scripts

### 1. `check_completion_times.py`
**Purpose:** Audit completion timestamps to identify format issues

**Usage:**
```bash
python check_completion_times.py
```

**Output:**
- Shows count of completions with time vs date-only format
- Helps identify inconsistent timestamp storage

**When to use:**
- After data migration
- If timestamp format issues are suspected
- During database audits

---

### 2. `patch_habit_created_at.py`
**Purpose:** Fix missing `created_at` timestamps for habits

**Usage:**
```bash
python patch_habit_created_at.py
```

**What it does:**
- Finds habits with missing or empty `created_at` values
- Sets `created_at` to earliest completion date for that habit
- Falls back to current time if no completions exist

**When to use:**
- After data import/migration
- If legacy data is missing `created_at` fields
- Once per database recovery

---

### 3. `cleanup_duplicate_completions.py`
**Purpose:** Remove duplicate completion entries

**Usage:**
```bash
python cleanup_duplicate_completions.py
```

**What it does:**
- Scans all habits for duplicate completions
- For daily habits: removes duplicates on the same date
- For weekly habits: removes duplicates in the same week
- Preserves first occurrence, deletes subsequent duplicates

**When to use:**
- If duplicate completions were recorded
- After data merge/import operations
- To ensure data integrity

---

### 4. `list_habit_completions.py`
**Purpose:** Debug tool to view all completions for a specific habit

**Usage:**
```bash
python list_habit_completions.py
# Then enter habit name when prompted
```

**Output:**
- Lists all completion dates/times for a habit
- Shows ISO timestamp and date part separately
- Total completion count

**When to use:**
- Debugging completion records
- Verifying streak calculations
- Checking specific habit history

---

### 5. `import_refactor_tools.py`
**Purpose:** Consolidated utilities for normalizing Python import statements

**Usage:**
```bash
# Fix accidental relative imports of stdlib/third-party modules
python import_refactor_tools.py --fix-stdlib-relative

# Convert absolute local imports to relative within the package
python import_refactor_tools.py --make-relative

# Convert `import module` for local modules to `from . import module`
python import_refactor_tools.py --convert-imports

# Update tests to use the momentum_hub.* namespace
python import_refactor_tools.py --update-tests
```

**When to use:**
- After refactors that move files across modules
- When standardizing imports for packaging
- When tests need to align to package namespace

---

## Important Notes

⚠️ **Always back up the database before running these scripts:**
```bash
cp momentum.db momentum.db.backup
```

⚠️ **Run from the project root directory** (parent of `scripts/`)

⚠️ **These scripts modify the database directly** - use with caution

## Cross-Platform Support

All scripts work on:
- Windows (PowerShell, CMD)
- Linux (bash, zsh)
- macOS (bash, zsh)

## Examples

### Check if database needs patching
```bash
python scripts/maintenance/check_completion_times.py
```

### Fix missing created_at dates after import
```bash
cp momentum.db momentum.db.backup
python scripts/maintenance/patch_habit_created_at.py
python scripts/maintenance/check_completion_times.py
```

### Clean up duplicate records
```bash
cp momentum.db momentum.db.backup
python scripts/maintenance/cleanup_duplicate_completions.py
```

### Debug a specific habit
```bash
python scripts/maintenance/list_habit_completions.py
# Follow prompts...
```
