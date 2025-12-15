# Device Temperature Refactor Summary

## Overview
Refactored the `device_temperature` field from text values to numeric values:

### Old Format (Text)
- `"nominal"`
- `"fair"`
- `"serious"`
- `"critical"`

### New Format (Numeric)
- `0` = nominal
- `1` = fair
- `2` = serious
- `3` = critical

---

## Changes Made

### 1. **dashboard/app.py**

#### Added Helper Functions
- `TEMP_MAP_NUM_TO_TEXT`: Dictionary to convert numeric values (0-3) to text labels
- `TEMP_MAP_TEXT_TO_NUM`: Dictionary for backward compatibility (text to numeric)
- `get_temp_label(temp_value)`: Function to safely convert numeric temperature to text label, with error handling

#### Updated Components

**Filters Section (Lines ~120-145)**
- Changed from text-based multiselect to numeric-based with display labels
- Converts numeric values to text labels for user-friendly display
- Maintains numeric values internally for filtering

**Metrics Display (Lines ~208-210)**
- Updated to use `get_temp_label()` to display temperature as text

**Summary Table (Lines ~217-232)**
- Modified temperature aggregation to return text labels using `get_temp_label()`

**Radar Chart (Lines ~293-334)**
- Removed old text-to-numeric mapping
- Temperature values are already numeric, just added +1 for visualization

**Temperature vs Latency Scatter Plot (Lines ~368-380)**
- No changes needed, works with numeric values directly

**Per-Run Analysis (Lines ~415-420)**
- Updated to use `get_temp_label()` for displaying most common temperature

**Temperature Timeline Chart (Lines ~459-475)**
- Simplified to use numeric values directly (0-3)
- Updated y-axis tick labels to show text descriptions

**Compare Runs Summary (Lines ~519-540)**
- Added `avg_temp_numeric` field to preserve numeric value for calculations
- Displays temperature as text using `get_temp_label()`

**Radar Chart in Compare Runs (Lines ~599-631)**
- Updated to use numeric temperature values directly
- Removed text-to-numeric mapping

**Correlation Heatmap (Lines ~641-656)**
- Simplified to use `device_temperature` directly (already numeric)

**Temperature Rise Calculation (Lines ~677-695)**
- Removed mapping, temperature is already numeric

---

### 2. **dashboard/sendlog_app.py**

#### Input Field Updated (Lines ~108-115)
**Before:**
```python
device_temperature = st.number_input(
    "Device Temperature (°C)",
    min_value=0.0,
    max_value=100.0,
    value=35.0,
    step=0.1,
    help="Device temperature at runtime (optional)"
)
```

**After:**
```python
device_temperature = st.selectbox(
    "Device Temperature",
    options=[
        ("0 - nominal", 0),
        ("1 - fair", 1),
        ("2 - serious", 2),
        ("3 - critical", 3)
    ],
    format_func=lambda x: x[0],
    index=0,
    help="Device temperature level (iOS thermal state)"
)
# Extract the numeric value
device_temperature = device_temperature[1]
```

---

### 3. **api/backend.py**

#### Data Model Updated (Line ~39)
**Before:**
```python
device_temperature: Optional[str] = None  # nominal | fair | serious | critical
```

**After:**
```python
device_temperature: Optional[int] = None  # 0: nominal, 1: fair, 2: serious, 3: critical
```

---

## Benefits

1. **Consistency**: All temperature values are stored as integers (0-3) in the CSV
2. **Performance**: Numeric comparisons and calculations are faster than string comparisons
3. **Visualization**: Easier to create charts and graphs with numeric values
4. **Maintainability**: Clear mapping between numeric values and their meanings
5. **Backward Compatibility**: `get_temp_label()` function handles both numeric and text values

---

## Testing Checklist

- [x] CSV file contains numeric temperature values (0-3)
- [x] Dashboard filters work with numeric values
- [x] Temperature displays as text labels in metrics
- [x] Summary tables show text labels
- [x] Charts and visualizations work correctly
- [x] Send log app uses selectbox with numeric values
- [x] Backend API accepts integer values
- [x] No linter errors

---

## Migration Notes

### For Existing Data
If you have old CSV files with text temperature values, you can use this Python script to migrate:

```python
import pandas as pd

# Temperature mapping
TEMP_MAP = {
    "nominal": 0,
    "fair": 1,
    "serious": 2,
    "critical": 3
}

# Read old CSV
df = pd.read_csv("latency_logs_old.csv")

# Convert temperature column
df['device_temperature'] = df['device_temperature'].map(TEMP_MAP)

# Save new CSV
df.to_csv("latency_logs_new.csv", index=False)
```

---

## Files Modified

1. `/dashboard/app.py` - Main dashboard application
2. `/dashboard/sendlog_app.py` - Log submission form
3. `/api/backend.py` - Backend API data model

---

## Date: December 15, 2025
## Status: ✅ Complete

