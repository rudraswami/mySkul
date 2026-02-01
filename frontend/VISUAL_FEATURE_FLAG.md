# 🎨 Visual Feature Flag Documentation

## Overview

The visual engine (NetraEngine) can be enabled/disabled using an environment variable for production deployments. This allows you to hide visuals in production and enable them when needed.

## Feature Flag

**Environment Variable:** `REACT_APP_ENABLE_VISUALS`

**Default:** `false` (visuals HIDDEN by default for production)

**Values:**
- `true`: Visuals are enabled (SmartBoard visible)
- `false` or unset: Visuals are disabled (SmartBoard hidden)

## How It Works

When `REACT_APP_ENABLE_VISUALS=false`:

1. **NetraEngine** (`frontend/src/netra/NetraEngine.jsx`):
   - Skips visual generation entirely
   - Shows empty state instead of loading/generating visuals

2. **SmartBoard** (`frontend/src/components/visuals/SmartBoard.jsx`):
   - Shows empty state instead of rendering visuals
   - SmartBoard panel still visible but displays empty state

3. **ClassroomLayout** (`frontend/src/components/layout/ClassroomLayout.jsx`):
   - SmartBoard visibility is tied to the visual flag
   - When visuals are disabled, SmartBoard is hidden

## Usage

### Production (Default - Visuals Hidden)

By default, visuals are **HIDDEN**. No environment variable needed:

```env
# Visuals hidden by default (no setting needed)
# Or explicitly:
REACT_APP_ENABLE_VISUALS=false
```

### Enable Visuals (Development or Demo)

To enable visuals, explicitly set the flag to `true`:

```env
# Enable visuals
REACT_APP_ENABLE_VISUALS=true
```

## Implementation Details

### NetraEngine Changes

- Added `VISUALS_ENABLED` constant that checks `process.env.REACT_APP_ENABLE_VISUALS !== 'false'`
- Early return in `useEffect` if visuals are disabled
- Early return in `renderContent()` to show empty state

### SmartBoard Changes

- Added `VISUALS_ENABLED` constant
- Early return with empty state UI if visuals are disabled
- Maintains SmartBoard UI structure but shows empty state

### ClassroomLayout Changes

- `SMARTBOARD_ENABLED` now tied to `VISUALS_ENABLED`
- When visuals disabled, SmartBoard panel is hidden

## Testing

1. **Enable visuals:**
   ```bash
   REACT_APP_ENABLE_VISUALS=true npm start
   ```
   - Visuals should render normally

2. **Disable visuals:**
   ```bash
   REACT_APP_ENABLE_VISUALS=false npm start
   ```
   - SmartBoard should be hidden
   - No visual generation should occur

## Notes

- The flag defaults to `false` (visuals hidden) for production safety
- When disabled, the SmartBoard panel is completely hidden
- Chat takes full width when visuals are disabled
- No visual generation API calls are made when disabled
- To enable visuals, you MUST explicitly set `REACT_APP_ENABLE_VISUALS=true`
- All existing visual gating logic (visual_needed, intent-based) still applies when visuals are enabled
