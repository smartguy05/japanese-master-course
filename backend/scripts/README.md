# Content Import Scripts - Quick Reference

## 📚 Available Scripts

### 1. Generate Sample Data

Creates N5-level Japanese learning data for development/testing.

```bash
# Generate JSON file
python scripts/generate_sample_data.py --output sample_data.json

# Import directly to database
python scripts/generate_sample_data.py --import-db
```

**Generates:**
- 20 N5 kanji (日月火水木金土, numbers, etc.)
- 100 N5 vocabulary words (common nouns, verbs, adjectives)

---

### 2. Import JMDict (Vocabulary)

Import Japanese-English dictionary vocabulary data.

```bash
# Import N5 sample vocabulary (default)
python scripts/import_jmdict.py

# Import N5 and N4
python scripts/import_jmdict.py --level N5,N4

# Import with limit
python scripts/import_jmdict.py --level N5 --limit 50
```

**Options:**
- `--level N5,N4,N3` - JLPT levels to import
- `--limit 100` - Maximum entries
- `--sample` - Use sample data (default)
- `--real` - Use real JMDict (not implemented)

---

### 3. Import KANJIDIC2 (Kanji)

Import kanji dictionary data.

```bash
# Import N5 sample kanji (default)
python scripts/import_kanjidic2.py

# Import multiple levels
python scripts/import_kanjidic2.py --level N5,N4
```

**Options:**
- `--level N5,N4,N3` - JLPT levels to import
- `--sample` - Use sample data (default)
- `--real` - Use real KANJIDIC2 (not implemented)

---

## 🧪 Testing

### Run Unit Tests
```bash
# All unit tests
pytest tests/unit/test_content_utils.py -v

# Specific test
pytest tests/unit/test_content_utils.py::TestJMDictParsing -v
```

### Run Integration Tests
```bash
# Requires database running
pytest tests/integration/test_import_scripts.py -v
```

---

## 📊 Sample Data Contents

### Kanji (20 total)
- Days: 日月火水木金土
- Numbers: 一二三四五六七八九十百
- Common: 人本

### Vocabulary (100 total)
- Pronouns: 私、これ、それ、あれ、どれ
- Time: 今、今日、明日、昨日、毎日
- Verbs: 食べる、飲む、行く、来る、見る、聞く、話す、読む、書く、する
- Adjectives: 大きい、小さい、新しい、古い、良い、悪い
- Nouns: 日本、人、学校、先生、学生、家、駅、店、etc.

---

## 🎯 Quick Examples

### Populate Development Database
```bash
# Generate and import all N5 content
python scripts/generate_sample_data.py --import-db

# Or import via individual scripts
python scripts/import_kanjidic2.py --level N5
python scripts/import_jmdict.py --level N5
```

### Export Sample Data for Sharing
```bash
python scripts/generate_sample_data.py --output n5_sample.json
```

### Check What Was Imported
```bash
# From psql or your database tool
SELECT count(*) FROM kanji WHERE jlpt_level = 'N5';
SELECT count(*) FROM vocabulary WHERE jlpt_level = 'N5';
```

---

## ⚠️ Important Notes

- **Database Required:** `--import-db` requires PostgreSQL running
- **Sample Data:** Currently only N5 level is fully implemented
- **Real Dictionaries:** `--real` flag is a placeholder for future implementation
- **UTF-8:** All scripts use UTF-8 encoding for Japanese text
- **Async:** Import functions are async (use asyncio)

---

## 🔧 Troubleshooting

### "Connection refused" error
Database is not running. Start PostgreSQL:
```bash
docker-compose up -d postgres
```

### "Module not found" error
Activate virtual environment:
```bash
source venv/bin/activate
```

### Import runs but no data appears
Check database connection settings in `.env` file.

---

## 📖 For More Information

See `/home/user/japanese-master-course/backend/CONTENT_IMPORT_IMPLEMENTATION.md` for:
- Detailed implementation notes
- TDD process followed
- Test coverage reports
- Future enhancements
- Architecture details
