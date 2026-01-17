# File Selection for Deletion

This skill explains how the Google Drive Trash Cleaner selects files for deletion.

## Selection Criteria

A file is selected for deletion when **all** of the following conditions are met:

1. **Explicitly Trashed**: The file must have been explicitly moved to trash by the user (`explicitlyTrashed = true`). Files that ended up in trash because their parent folder was trashed are not included.

2. **Owned by User**: The file must be owned by the authenticated user (`ownedByMe = true`). Shared files that were trashed are not deleted.

3. **Age Threshold**: The file must have been in trash for more than the specified number of days (default: 30 days, configurable via `--days` flag).

## How It Works

The selection process in `get_deletion_list()` (line 263-339) works as follows:

1. **Change List Scanning**: The cleaner uses Google Drive's Changes API to iterate through the change history, starting from a saved page token. This is more efficient than listing all trashed files.

2. **Time-Based Filtering**: Changes are processed in chronological order. The scanner stops when it encounters files trashed more recently than the threshold (`currentTime - itemTime < flags.days*24*3600`).

3. **Page Token Management**:
   - `pageTokenBefore`: Saved regardless of deletion success - marks the point before any files in the deletion list
   - `pageTokenAfter`: Only saved if all deletions succeed - marks the current position in the change list

## Optional Filters

- **`--mydriveonly`**: Restricts selection to files in "My Drive" hierarchy, excluding files from "Computers" and other locations (`restrictToMyDrive=true` in API call)

## Key Code Reference

```python
# From cleaner.py lines 321-334
for item in items:
    itemTime = parse_time(item['time'])
    if currentTime - itemTime < flags.days*24*3600:
        # Stop - remaining files are too recent
        return deletionList, pageTokenBefore, pageToken
    if item['file']['explicitlyTrashed'] and item['file']['ownedByMe']:
        # File meets criteria - add to deletion list
        deletionList.append({...})
```

## Summary

Files are selected based on: explicit trashing + ownership + age. The cleaner processes files in order of trash time and stops as soon as it reaches files within the retention period.
