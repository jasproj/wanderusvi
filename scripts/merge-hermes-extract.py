#!/usr/bin/env python3
"""
Merge Hermes FareHarbor extraction with existing tours-data.json.

Strategy:
- Filter out non-USVI tours (route list for WPR)
- For tours in BOTH: keep existing price/description, take Hermes pk/gallery/tags where ours empty
- For tours only in Hermes (new): add them with needsEnrichment flag
- For tours only in current: keep them (may be manually added or FH missed them)

Output: tours-data-merged.json (review before replacing tours-data.json)
"""

import json
from datetime import datetime
from pathlib import Path

# USVI location mapping
ST_THOMAS = [
    'red-hook', 'charlotte-amalie', 'charlotte-amalie-west', 'charlotte-amalie-east',
    'havensight', 'smith-bay', 'frydendal', 'nadir', 'nazareth', 'estate-bovoni',
    'lovenlund', 'st-thomas', 'water-island'
]
ST_JOHN = ['cruz-bay', 'coral-bay', 'virgin-island-national-park', 'st-john']
ST_CROIX = ['christiansted', 'frederiksted', 'salt-river', 'saint-croix', 'st-croix']
USVI_GENERIC = ['vi', 'usvi', 'us-virgin-islands', '']

ALL_USVI = ST_THOMAS + ST_JOHN + ST_CROIX + USVI_GENERIC

def normalize_island(island_raw):
    """Map city/neighborhood to canonical island slug."""
    island = (island_raw or '').lower().strip()
    if island in ST_THOMAS:
        return 'st-thomas'
    elif island in ST_JOHN:
        return 'st-john'
    elif island in ST_CROIX:
        return 'st-croix'
    elif island in ['water-island']:
        return 'water-island'
    elif island in USVI_GENERIC:
        return ''  # Will need manual assignment
    return island  # Non-USVI, will be filtered

def is_usvi(island):
    """Check if island value is a USVI location."""
    return (island or '').lower() in ALL_USVI

def main():
    repo = Path(__file__).parent.parent
    
    # Load files
    with open(repo / 'tours-data.json') as f:
        current_data = json.load(f)
    with open(repo / 'tours-data-new.json') as f:
        hermes_data = json.load(f)
    
    current = current_data['tours']
    hermes = hermes_data['tours']
    
    print(f"Current tours: {len(current)}")
    print(f"Hermes tours: {len(hermes)}")
    
    # Index current by pk
    current_by_pk = {t['pk']: t for t in current if t.get('pk')}
    
    # Filter non-USVI and collect for WPR routing
    wpr_candidates = []
    usvi_hermes = []
    discarded = []
    
    for t in hermes:
        island = (t.get('island') or '').lower()
        if is_usvi(island):
            usvi_hermes.append(t)
        else:
            loc = t.get('location', '')
            if 'Puerto Rico' in loc or island in ['culebra', 'ceiba', 'san-juan', 'playa-sardinas-ii']:
                wpr_candidates.append(t)
            else:
                discarded.append(t)
    
    print(f"\nFiltered:")
    print(f"  USVI (keeping): {len(usvi_hermes)}")
    print(f"  Puerto Rico (route to WPR): {len(wpr_candidates)}")
    print(f"  Discarded: {len(discarded)}")
    
    # Print routing info
    if wpr_candidates:
        print(f"\n=== ROUTE TO WPR ===")
        for t in wpr_candidates:
            print(f"  pk={t['pk']} {t['name'][:50]}")
    
    if discarded:
        print(f"\n=== DISCARDED ===")
        for t in discarded:
            print(f"  pk={t['pk']} island={t.get('island')} {t['name'][:50]}")
    
    # Merge logic
    merged = []
    stats = {'updated': 0, 'new': 0, 'kept': 0}
    
    hermes_by_pk = {t['pk']: t for t in usvi_hermes if t.get('pk')}
    
    # Process Hermes tours
    for t in usvi_hermes:
        pk = t.get('pk')
        if pk and pk in current_by_pk:
            # Exists in both - merge
            existing = current_by_pk[pk]
            merged_tour = existing.copy()
            
            # Take Hermes data where current is empty
            if not existing.get('galleryImages') and t.get('galleryImages'):
                merged_tour['galleryImages'] = t['galleryImages']
            if not existing.get('tags') and t.get('tags'):
                merged_tour['tags'] = t['tags']
            if not existing.get('image') and t.get('image'):
                merged_tour['image'] = t['image']
            
            # Normalize island
            merged_tour['island'] = normalize_island(t.get('island'))
            
            # Keep existing price/description (our enrichment work)
            merged_tour['lastUpdated'] = datetime.now().isoformat()
            merged.append(merged_tour)
            stats['updated'] += 1
        else:
            # New tour from Hermes
            new_tour = t.copy()
            new_tour['island'] = normalize_island(t.get('island'))
            new_tour['needsEnrichment'] = True
            new_tour['lastUpdated'] = datetime.now().isoformat()
            merged.append(new_tour)
            stats['new'] += 1
    
    # Add tours only in current (not in Hermes) - may be manually added
    # But still filter non-USVI
    for pk, t in current_by_pk.items():
        if pk not in hermes_by_pk:
            island = (t.get('island') or '').lower()
            if is_usvi(island):
                merged.append(t)
                stats['kept'] += 1
            else:
                # Non-USVI in current but not in Hermes - these were legacy contamination
                loc = t.get('location', '')
                if 'Puerto Rico' in loc or island in ['culebra', 'ceiba', 'san-juan', 'playa-sardinas-ii']:
                    wpr_candidates.append(t)
                    print(f"  Legacy PR contamination removed: pk={pk} {t.get('name', '')[:40]}")
                else:
                    discarded.append(t)
                    print(f"  Legacy non-USVI removed: pk={pk} island={island} {t.get('name', '')[:40]}")
    
    print(f"\n=== MERGE STATS ===")
    print(f"Updated (in both): {stats['updated']}")
    print(f"New from Hermes: {stats['new']}")
    print(f"Kept from current (not in Hermes): {stats['kept']}")
    print(f"Total merged: {len(merged)}")
    
    # Data quality summary
    null_price = len([t for t in merged if not t.get('price')])
    null_image = len([t for t in merged if not t.get('image')])
    null_tags = len([t for t in merged if not t.get('tags')])
    needs_enrichment = len([t for t in merged if t.get('needsEnrichment')])
    
    print(f"\n=== DATA QUALITY ===")
    print(f"Null price: {null_price} ({100*null_price/len(merged):.1f}%)")
    print(f"Null image: {null_image} ({100*null_image/len(merged):.1f}%)")
    print(f"Null tags: {null_tags} ({100*null_tags/len(merged):.1f}%)")
    print(f"Needs enrichment: {needs_enrichment}")
    
    # Build output
    output = {
        'schemaVersion': hermes_data.get('schemaVersion', '1.0.8'),
        'lastNormalized': datetime.now().strftime('%Y-%m-%d'),
        'tours': merged
    }
    
    # Write merged file
    out_path = repo / 'tours-data-merged.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nWritten to: {out_path}")
    print(f"Review then: cp tours-data-merged.json tours-data.json")
    
    # Write WPR routing file
    if wpr_candidates:
        wpr_out = repo / 'wpr-routing-candidates.json'
        with open(wpr_out, 'w') as f:
            json.dump(wpr_candidates, f, indent=2)
        print(f"WPR candidates written to: {wpr_out}")

if __name__ == '__main__':
    main()
